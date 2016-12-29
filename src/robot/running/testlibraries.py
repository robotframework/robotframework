#  Copyright 2008-2015 Nokia Networks
#  Copyright 2016-     Robot Framework Foundation
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

import inspect
import os

from robot.errors import DataError
from robot.libraries import STDLIBS
from robot.output import LOGGER
from robot.utils import (getdoc, get_error_details, Importer, is_java_init,
                         is_java_method, JYTHON, normalize, seq2str2, unic,
                         is_list_like, type_name)

from .arguments import EmbeddedArguments
from .context import EXECUTION_CONTEXTS
from .dynamicmethods import (GetKeywordArguments, GetKeywordDocumentation,
                             GetKeywordNames, RunKeyword)
from .handlers import Handler, InitHandler, DynamicHandler, EmbeddedArgumentsHandler
from .handlerstore import HandlerStore
from .libraryscopes import LibraryScope
from .outputcapture import OutputCapturer


if JYTHON:
    from java.lang import Object
else:
    Object = None


def TestLibrary(name, args=None, variables=None, create_handlers=True):
    if name in STDLIBS:
        import_name = 'robot.libraries.' + name
    else:
        import_name = name
    with OutputCapturer(library_import=True):
        importer = Importer('test library')
        libcode, source = importer.import_class_or_module(import_name,
                                                          return_source=True)
    libclass = _get_lib_class(libcode)
    lib = libclass(libcode, name, args or [], source, variables)
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


class _BaseTestLibrary(object):
    _failure_level = 'INFO'

    def __init__(self, libcode, name, args, source, variables):
        if os.path.exists(name):
            name = os.path.splitext(os.path.basename(os.path.abspath(name)))[0]
        self.version = self._get_version(libcode)
        self.name = name
        self.orig_name = name  # Stores original name when importing WITH NAME
        self.source = source
        self.handlers = HandlerStore(self.name, HandlerStore.TEST_LIBRARY_TYPE)
        self.has_listener = None  # Set when first instance is created
        self._doc = None
        self.doc_format = self._get_doc_format(libcode)
        self.scope = LibraryScope(libcode, self)
        self.init = self._create_init_handler(libcode)
        self.positional_args, self.named_args \
            = self.init.resolve_arguments(args, variables)
        self._libcode = libcode
        self._libinst = None

    def __len__(self):
        return len(self.handlers)

    @property
    def doc(self):
        if self._doc is None:
            self._doc = getdoc(self.get_instance())
        return self._doc

    def create_handlers(self):
        self._create_handlers(self.get_instance())
        self.reset_instance()

    def reload(self):
        self.handlers = HandlerStore(self.name, HandlerStore.TEST_LIBRARY_TYPE)
        self._create_handlers(self.get_instance())

    def start_suite(self):
        self.scope.start_suite()

    def end_suite(self):
        self.scope.end_suite()

    def start_test(self):
        self.scope.start_test()

    def end_test(self):
        self.scope.end_test()

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

    def _create_init_handler(self, libcode):
        return InitHandler(self, self._resolve_init_method(libcode))

    def _resolve_init_method(self, libcode):
        init_method = getattr(libcode, '__init__', None)
        return init_method if self._valid_init(init_method) else lambda: None

    def _valid_init(self, method):
        return (inspect.ismethod(method) or     # PY2
                inspect.isfunction(method) or   # PY3
                is_java_init(method))

    def reset_instance(self, instance=None):
        prev = self._libinst
        if not self.scope.is_global:
            self._libinst = instance
        return prev

    def get_instance(self, create=True):
        if not create:
            return self._libinst
        if self._libinst is None:
            self._libinst = self._get_instance(self._libcode)
        if self.has_listener is None:
            self.has_listener = bool(self.get_listeners(self._libinst))
        return self._libinst

    def _get_instance(self, libcode):
        with OutputCapturer(library_import=True):
            try:
                return libcode(*self.positional_args, **dict(self.named_args))
            except:
                self._raise_creating_instance_failed()

    def get_listeners(self, libinst=None):
        if not libinst:
            libinst = self.get_instance()
        listeners = getattr(libinst, 'ROBOT_LIBRARY_LISTENER', None)
        if listeners is None:
            return []
        if is_list_like(listeners):
            return listeners
        return [listeners]

    def register_listeners(self):
        if self.has_listener:
            try:
                listeners = EXECUTION_CONTEXTS.current.output.library_listeners
                listeners.register(self.get_listeners(), self)
            except DataError as err:
                self.has_listener = False
                # Error should have information about suite where the
                # problem occurred but we don't have such info here.
                LOGGER.error("Registering listeners for library '%s' failed: %s"
                             % (self.name, err))

    def unregister_listeners(self, close=False):
        if self.has_listener:
            listeners = EXECUTION_CONTEXTS.current.output.library_listeners
            listeners.unregister(self, close)

    def close_global_listeners(self):
        if self.scope.is_global:
            for listener in self.get_listeners():
                self._close_listener(listener)

    def _close_listener(self, listener):
        method = (getattr(listener, 'close', None) or
                  getattr(listener, '_close', None))
        try:
            if method:
                method()
        except:
            message, details = get_error_details()
            name = getattr(listener, '__name__', None) or type_name(listener)
            LOGGER.error("Calling method '%s' of listener '%s' failed: %s"
                         % (method.__name__, name, message))
            LOGGER.info("Details:\n%s" % details)

    def _create_handlers(self, libcode):
        try:
            names = self._get_handler_names(libcode)
        except:
            message, details = get_error_details()
            raise DataError("Getting keyword names from library '%s' failed: %s"
                            % (self.name, message), details)
        for name in names:
            method = self._try_to_get_handler_method(libcode, name)
            if method:
                handler, embedded = self._try_to_create_handler(name, method)
                if handler:
                    try:
                        self.handlers.add(handler, embedded)
                    except DataError as err:
                        LOGGER.error("Error in test library '%s': "
                                     "Creating keyword '%s' failed: %s"
                                     % (self.name, handler.name, err.message))
                    else:
                        LOGGER.debug("Created keyword '%s'" % handler.name)

    def _get_handler_names(self, libcode):
        return [name for name in dir(libcode)
                if not name.startswith(('_', 'ROBOT_'))]

    def _try_to_get_handler_method(self, libcode, name):
        try:
            return self._get_handler_method(libcode, name)
        except:
            self._report_adding_keyword_failed(name)
            return None

    def _report_adding_keyword_failed(self, name, message=None, details=None,
                                      level=None):
        if not message:
            message, details = get_error_details()
        LOGGER.write("Adding keyword '%s' to library '%s' failed: %s"
                     % (name, self.name, message), level or self._failure_level)
        if details:
            LOGGER.debug('Details:\n%s' % details)

    def _get_handler_method(self, libcode, name):
        method = getattr(libcode, name)
        if not inspect.isroutine(method):
            raise DataError('Not a method or function')
        return method

    def _try_to_create_handler(self, name, method):
        try:
            handler = self._create_handler(name, method)
        except DataError as err:
            self._report_adding_keyword_failed(name, err.message, level='ERROR')
            return None, False
        except:
            self._report_adding_keyword_failed(name)
            return None, False
        try:
            return self._get_possible_embedded_args_handler(handler)
        except DataError as err:
            self._report_adding_keyword_failed(handler.name, err.message,
                                               level='ERROR')
            return None, False

    def _create_handler(self, handler_name, handler_method):
        return Handler(self, handler_name, handler_method)

    def _get_possible_embedded_args_handler(self, handler):
        embedded = EmbeddedArguments(handler.name)
        if embedded:
            self._validate_embedded_count(embedded, handler.arguments)
            return EmbeddedArgumentsHandler(embedded.name, handler), True
        return handler, False

    def _validate_embedded_count(self, embedded, arguments):
        if not (arguments.minargs <= len(embedded.args) <= arguments.maxargs):
            raise DataError('Embedded argument count does not match number of '
                            'accepted arguments.')

    def _raise_creating_instance_failed(self):
        msg, details = get_error_details()
        if self.positional_args or self.named_args:
            args = self.positional_args \
                + ['%s=%s' % item for item in self.named_args]
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

    def _get_handler_method(self, libcode, name):
        method = _BaseTestLibrary._get_handler_method(self, libcode, name)
        if hasattr(libcode, '__all__') and name not in libcode.__all__:
            raise DataError('Not exposed as a keyword')
        return method

    def get_instance(self, create=True):
        if not create:
            return self._libcode
        if self.has_listener is None:
            self.has_listener = bool(self.get_listeners(self._libcode))
        return self._libcode

    def _create_init_handler(self, libcode):
        return InitHandler(self, lambda: None)


class _HybridLibrary(_BaseTestLibrary):
    _failure_level = 'ERROR'

    def _get_handler_names(self, instance):
        return GetKeywordNames(instance)()


class _DynamicLibrary(_BaseTestLibrary):
    _failure_level = 'ERROR'

    def __init__(self, libcode, name, args, source, variables=None):
        _BaseTestLibrary.__init__(self, libcode, name, args, source, variables)

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
