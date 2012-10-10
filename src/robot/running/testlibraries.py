#  Copyright 2008-2012 Nokia Siemens Networks Oyj
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

from __future__ import with_statement
import os
import inspect

from robot import utils
from robot.errors import DataError
from robot.common import BaseLibrary
from robot.output import LOGGER

from handlers import Handler, InitHandler, DynamicHandler
from outputcapture import OutputCapturer

if utils.is_jython:
    from org.python.core import PyReflectedFunction, PyReflectedConstructor
    from java.lang import Object
else:
    Object = None


def TestLibrary(name, args=None, variables=None, create_handlers=True):
    with OutputCapturer(library_import=True):
        importer = utils.Importer('test library')
        libcode = importer.import_class_or_module(name)
    libclass = _get_lib_class(libcode)
    lib = libclass(libcode, name, args or [], variables)
    if create_handlers:
        lib.create_handlers()
    return lib


def _get_lib_class(libcode):
    if inspect.ismodule(libcode):
        return _ModuleLibrary
    if _DynamicMethod(libcode, 'get_keyword_names'):
        if _DynamicMethod(libcode, 'run_keyword'):
            return _DynamicLibrary
        else:
            return _HybridLibrary
    return _ClassLibrary


class _DynamicMethod(object):

    def __init__(self, libcode, underscore_name, default=None):
        self._method = self._get_method(libcode, underscore_name)
        self._default = default

    def __call__(self, *args):
        if not self._method:
            return self._default
        try:
            value = self._method(*args)
        except:
            raise DataError("Calling dynamic method '%s' failed: %s" %
                            (self._method.__name__, utils.get_error_message()))
        else:
            return self._to_unicode(value) if value is not None else self._default

    def _to_unicode(self, value):
        if isinstance(value, unicode):
            return value
        if isinstance(value, str):
            return utils.unic(value, 'UTF-8')
        return [self._to_unicode(v) for v in value]

    def __nonzero__(self):
        return self._method is not None

    def _get_method(self, libcode, underscore_name):
        for name in underscore_name, self._getCamelCaseName(underscore_name):
            method = getattr(libcode, name, None)
            if callable(method):
                return method
        return None

    def _getCamelCaseName(self, underscore_name):
        tokens = underscore_name.split('_')
        return ''.join([tokens[0]] + [t.capitalize() for t in tokens[1:]])


class _BaseTestLibrary(BaseLibrary):
    supports_named_arguments = True # this attribute is for libdoc
    _log_success = LOGGER.debug
    _log_failure = LOGGER.info
    _log_failure_details = LOGGER.debug

    def __init__(self, libcode, name, args, variables):
        if os.path.exists(name):
            name = os.path.splitext(os.path.basename(os.path.abspath(name)))[0]
        self.version = self._get_version(libcode)
        self.name = name
        self.orig_name = name # Stores original name also after copying
        self.positional_args = []
        self.named_args = {}
        self._instance_cache = []
        self._libinst = None
        if libcode is not None:
            self._doc = utils.getdoc(libcode)
            self.doc_format = self._get_doc_format(libcode)
            self.scope = self._get_scope(libcode)
            self._libcode = libcode
            self.init =  self._create_init_handler(libcode)
            self.positional_args, self.named_args = self.init.arguments.resolve(args, variables)

    @property
    def doc(self):
        return self._doc

    def create_handlers(self):
        if self._libcode:
            self._libinst = self.get_instance()
            self.handlers = self._create_handlers(self._libinst)
            self.init_scope_handling()

    def start_suite(self):
        pass

    def end_suite(self):
        pass

    def start_test(self):
        pass

    def end_test(self):
        pass

    def _get_version(self, libcode):
        return self._get_attr(libcode, 'ROBOT_LIBRARY_VERSION') \
            or self._get_attr(libcode, '__version__')

    def _get_attr(self, object, attr, default='', upper=False):
        value = utils.unic(getattr(object, attr, default))
        if upper:
            value = utils.normalize(value, ignore='_').upper()
        return value

    def _get_doc_format(self, libcode):
        return self._get_attr(libcode, 'ROBOT_LIBRARY_DOC_FORMAT', upper=True)

    def _get_scope(self, libcode):
        scope = self._get_attr(libcode, 'ROBOT_LIBRARY_SCOPE', upper=True)
        return scope if scope in ['GLOBAL','TESTSUITE'] else 'TESTCASE'

    def _create_init_handler(self, libcode):
        return InitHandler(self, self._resolve_init_method(libcode))

    def _resolve_init_method(self, libcode):
        init_method = getattr(libcode, '__init__', None)
        return init_method if self._valid_init(init_method) else lambda: None

    def _valid_init(self, init_method):
        if inspect.ismethod(init_method):
            return True
        if utils.is_jython and isinstance(init_method, PyReflectedConstructor):
            return True
        return False

    def init_scope_handling(self):
        if self.scope == 'GLOBAL':
            return
        self._libinst = None
        self.start_suite = self._caching_start
        self.end_suite = self._restoring_end
        if self.scope == 'TESTCASE':
            self.start_test = self._caching_start
            self.end_test = self._restoring_end

    def _caching_start(self):
        self._instance_cache.append(self._libinst)
        self._libinst = None

    def _restoring_end(self):
        self._libinst = self._instance_cache.pop()

    def get_instance(self):
        if self._libinst is None:
            self._libinst = self._get_instance()
        return self._libinst

    def _get_instance(self):
        capturer = OutputCapturer(library_import=True)
        try:
            return self._libcode(*self.positional_args, **self.named_args)
        except:
            self._raise_creating_instance_failed()
        finally:
            capturer.release_and_log()

    def _create_handlers(self, libcode):
        handlers = utils.NormalizedDict(ignore=['_'])
        for name in self._get_handler_names(libcode):
            method = self._try_to_get_handler_method(libcode, name)
            if method:
                handler = self._try_to_create_handler(name, method)
                if handler:
                    handlers[name] = handler
                    self._log_success("Created keyword '%s'" % handler.name)
        return handlers

    def _get_handler_names(self, libcode):
        return [name for name in dir(libcode)
                if not name.startswith(('_', 'ROBOT_LIBRARY_'))]

    def _try_to_get_handler_method(self, libcode, name):
        try:
            return self._get_handler_method(libcode, name)
        except:
            self._report_adding_keyword_failed(name)

    def _report_adding_keyword_failed(self, name):
        msg, details = utils.get_error_details()
        self._log_failure("Adding keyword '%s' to library '%s' failed: %s"
                          % (name, self.name, msg))
        if details:
            self._log_failure_details('Details:\n%s' % details)

    def _get_handler_method(self, libcode, name):
        method = getattr(libcode, name)
        if not inspect.isroutine(method):
            raise DataError('Not a method or function')
        return method

    def _try_to_create_handler(self, name, method):
        try:
            return self._create_handler(name, method)
        except:
            self._report_adding_keyword_failed(name)

    def _create_handler(self, handler_name, handler_method):
        return Handler(self, handler_name, handler_method)

    def _raise_creating_instance_failed(self):
        msg, details = utils.get_error_details()
        if self.positional_args:
            args = "argument%s %s" % (utils.plural_or_not(self.positional_args),
                                      utils.seq2str(self.positional_args))
        else:
            args = "no arguments"
        raise DataError("Creating an instance of the test library '%s' with %s "
                        "failed: %s\n%s" % (self.name, args, msg, details))


class _ClassLibrary(_BaseTestLibrary):

    def _get_handler_method(self, libinst, name):
        # Type is checked before using getattr to avoid calling properties,
        # most importantly bean properties generated by Jython (issue 188).
        for item in (libinst,) + inspect.getmro(libinst.__class__):
            if item in (object, Object):
                continue
            if not (hasattr(item, '__dict__') and name in item.__dict__):
                continue
            self._validate_handler(item.__dict__[name])
            return getattr(libinst, name)
        raise DataError('No non-implicit implementation found')

    def _validate_handler(self, handler):
        if not self._is_routine(handler):
            raise DataError('Not a method or function')
        if self._is_implicit_java_or_jython_method(handler):
            raise DataError('Implicit methods are ignored')

    def _is_routine(self, handler):
        # inspect.isroutine doesn't work with methods from Java classes
        # prior to Jython 2.5.2: http://bugs.jython.org/issue1223
        return inspect.isroutine(handler) or self._is_java_method(handler)

    def _is_java_method(self, handler):
        return utils.is_jython and isinstance(handler, PyReflectedFunction)

    def _is_implicit_java_or_jython_method(self, handler):
        if not self._is_java_method(handler):
            return False
        for signature in handler.argslist[:handler.nargs]:
            cls = signature.declaringClass
            if not (cls is Object or self._is_created_by_jython(handler, cls)):
                return False
        return True

    def _is_created_by_jython(self, handler, cls):
        proxy_methods = getattr(cls, '__supernames__', []) + ['classDictInit']
        return handler.__name__ in proxy_methods


class _ModuleLibrary(_BaseTestLibrary):

    def _get_scope(self, libcode):
        return 'GLOBAL'

    def _get_handler_method(self, libcode, name):
        method = _BaseTestLibrary._get_handler_method(self, libcode, name)
        if hasattr(libcode, '__all__') and name not in libcode.__all__:
            raise DataError('Not exposed as a keyword')
        return method

    def get_instance(self):
        self.init.arguments.check_arg_limits(self.positional_args)
        return self._libcode

    def _create_init_handler(self, libcode):
        return InitHandler(self, lambda: None)


class _HybridLibrary(_BaseTestLibrary):
    _log_failure = LOGGER.warn

    def _get_handler_names(self, instance):
        try:
            return instance.get_keyword_names()
        except AttributeError:
            return instance.getKeywordNames()


class _DynamicLibrary(_BaseTestLibrary):
    supports_named_arguments = False # this attribute is for libdoc
    _log_failure = LOGGER.warn

    def __init__(self, libcode, name, args, variables=None):
        _BaseTestLibrary.__init__(self, libcode, name, args, variables)
        self._get_kw_doc = \
            _DynamicMethod(libcode, 'get_keyword_documentation', default='')
        self._get_kw_args = \
            _DynamicMethod(libcode, 'get_keyword_arguments', default=None)

    @property
    def doc(self):
        return self._get_kw_doc(self.get_instance(), '__intro__') or self._doc

    def _get_handler_names(self, instance):
        try:
            return instance.get_keyword_names()
        except AttributeError:
            return instance.getKeywordNames()

    def _get_handler_method(self, instance, name_is_ignored):
        try:
            return instance.run_keyword
        except AttributeError:
            return instance.runKeyword

    def _create_handler(self, handler_name, handler_method):
        doc = self._get_kw_doc(self._libinst, handler_name)
        argspec = self._get_kw_args(self._libinst, handler_name)
        return DynamicHandler(self, handler_name, handler_method, doc, argspec)

    def _create_init_handler(self, libcode):
        docgetter = lambda: self._get_kw_doc(self.get_instance(), '__init__')
        return InitHandler(self, self._resolve_init_method(libcode), docgetter)
