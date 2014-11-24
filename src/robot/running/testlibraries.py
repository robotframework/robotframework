#  Copyright 2008-2014 Nokia Solutions and Networks
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
import inspect
import os
import sys

from robot.errors import DataError
from robot.output import LOGGER
from robot.utils import (getdoc, get_error_details, Importer,
                         is_java_init, is_java_method, normalize,
                         NormalizedDict, seq2str2, unic)

from .baselibrary import BaseLibrary
from .dynamicmethods import (GetKeywordArguments, GetKeywordDocumentation,
                             GetKeywordNames, RunKeyword)
from .handlers import Handler, InitHandler, DynamicHandler
from .outputcapture import OutputCapturer

if sys.platform.startswith('java'):
    from java.lang import Object
else:
    Object = None


def TestLibrary(name, args=None, variables=None, create_handlers=True):
    with OutputCapturer(library_import=True):
        importer = Importer('test library')
        libcode = importer.import_class_or_module(name)
    libclass = _get_lib_class(libcode)
    lib = libclass(libcode, name, args or [], variables)
    if create_handlers:
        lib.create_handlers()
    return lib


def _get_lib_class(libcode):
    if inspect.ismodule(libcode):
        return _ModuleLibrary
    if GetKeywordNames(libcode):
        if RunKeyword(libcode):
            return _DynamicLibrary
        else:
            return _HybridLibrary
    return _ClassLibrary


class _BaseTestLibrary(BaseLibrary):
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
        self.has_listener = None  # Set when first instance is created
        self._libinst = None
        if libcode is not None:
            self._doc = None
            self.doc_format = self._get_doc_format(libcode)
            self.scope = self._get_scope(libcode)
            self._libcode = libcode
            self.init = self._create_init_handler(libcode)
            self.positional_args, self.named_args \
                = self.init.resolve_arguments(args, variables)

    @property
    def doc(self):
        if self._doc is None:
            self._doc = getdoc(self.get_instance())
        return self._doc

    @property
    def listener(self):
        if self.has_listener:
            return self._get_listener(self.get_instance())
        return None

    def _get_listener(self, inst):
        return getattr(inst, 'ROBOT_LIBRARY_LISTENER', None)

    def create_handlers(self):
        if self._libcode:
            self.handlers = self._create_handlers(self.get_instance())
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
        value = unic(getattr(object, attr, default))
        if upper:
            value = normalize(value, ignore='_').upper()
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

    def _valid_init(self, method):
        return inspect.ismethod(method) or is_java_init(method)

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
        if self.has_listener is None:
            self.has_listener = self._get_listener(self._libinst) is not None
        return self._libinst

    def _get_instance(self):
        with OutputCapturer(library_import=True):
            try:
                return self._libcode(*self.positional_args, **self.named_args)
            except:
                self._raise_creating_instance_failed()

    def _create_handlers(self, libcode):
        handlers = NormalizedDict(ignore='_')
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
        msg, details = get_error_details()
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
        msg, details = get_error_details()
        if self.positional_args or self.named_args:
            args = self.positional_args \
                + ['%s=%s' % item for item in self.named_args.items()]
            args_text = 'arguments %s' % seq2str2(args)
        else:
            args_text = 'no arguments'
        raise DataError("Initializing test library '%s' with %s failed: %s\n%s"
                        % (self.name, args_text, msg, details))


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
        return inspect.isroutine(handler) or is_java_method(handler)

    def _is_implicit_java_or_jython_method(self, handler):
        if not is_java_method(handler):
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
        if self.has_listener is None:
            self.has_listener = self._get_listener(self._libcode) is not None
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
    _log_failure = LOGGER.warn

    def __init__(self, libcode, name, args, variables=None):
        _BaseTestLibrary.__init__(self, libcode, name, args, variables)

    @property
    def doc(self):
        if self._doc is None:
            self._doc = (self._get_kw_doc('__intro__') or
                         _BaseTestLibrary.doc.fget(self))
        return self._doc

    def _get_kw_doc(self, name, instance=None):
        getter = GetKeywordDocumentation(instance or self.get_instance())
        return getter(name)

    def _get_kw_args(self, name, instance=None):
        getter = GetKeywordArguments(instance or self.get_instance())
        return getter(name)

    def _get_handler_names(self, instance):
        return GetKeywordNames(instance)()

    def _get_handler_method(self, instance, name):
        return RunKeyword(instance)

    def _create_handler(self, name, method):
        doc = self._get_kw_doc(name)
        argspec = self._get_kw_args(name)
        return DynamicHandler(self, name, method, doc, argspec)

    def _create_init_handler(self, libcode):
        docgetter = lambda: self._get_kw_doc('__init__')
        return InitHandler(self, self._resolve_init_method(libcode), docgetter)
