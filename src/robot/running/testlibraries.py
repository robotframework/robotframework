#  Copyright 2008 Nokia Siemens Networks Oyj
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


import os
import types
import inspect

from robot import utils
from robot.errors import DataError
from robot.common import BaseLibrary
from robot.output import SystemLogger

from handlers import Handler, InitHandler, DynamicHandler

if utils.is_jython:
    from org.python.core import PyReflectedFunction, PyReflectedConstructor
    from java.lang import Object


def TestLibrary(name, args=None, syslog=None):
    if syslog is None:
        syslog = SystemLogger()
    libcode, source = utils.import_(name)
    libclass = _get_lib_class(libcode)
    return libclass(libcode, source, name, utils.to_list(args), syslog)


def _get_lib_class(libcode):
    if isinstance(libcode, types.ModuleType):
        return _ModuleLibrary
    if _get_dynamic_method(libcode, 'get_keyword_names'):
        if _get_dynamic_method(libcode, 'run_keyword'):
            return _DynamicLibrary
        else:
            return _HybridLibrary
    return _ClassLibrary

def _get_dynamic_method(code, underscore_name):
    tokens = underscore_name.split('_')
    tokens = [tokens[0]] + [ t.capitalize() for t in tokens[1:] ]
    camelCaseName = ''.join(tokens)
    for name in underscore_name, camelCaseName:
        if hasattr(code, name):
            method = getattr(code, name)
            if callable(method):
                return method
    return None


class _BaseTestLibrary(BaseLibrary):

    def __init__(self, libcode, source, name, args, syslog):
        if os.path.exists(name):
            name = os.path.splitext(os.path.basename(name))[0]
        self.source = source
        self.version = self._get_version(libcode)
        self.name = name
        self.orig_name = name # Stores original name also after copying
        self.args = args
        self._instance_cache = []
        if libcode is not None:
            self.doc = utils.get_doc(libcode)
            self.scope = self._get_scope(libcode)
            self._libcode = libcode
            self.init =  self._create_init_handler(libcode)
            self._libinst = self.get_instance()
            self.handlers = self._create_handlers(self._libinst, syslog)
            self._init_scope_handling()

    def copy(self, name):
        lib = _BaseTestLibrary(None, self.version, name, self.args, None)
        lib.orig_name = self.name
        lib.doc = self.doc
        lib.scope = self.scope
        lib._libcode = self._libcode
        lib._libinst = self._libinst
        lib.init = self.init
        lib._init_scope_handling()
        lib.handlers = utils.NormalizedDict(ignore=['_'])
        for handler_name, handler in self.handlers.items():
            lib.handlers[handler_name] = handler.copy(lib)
        return lib
    
    def start_suite(self):
        pass
    
    def end_suite(self):
        pass
    
    def start_test(self):
        pass
    
    def end_test(self):
        pass

    def _get_version(self, code):
        try:
            return str(code.ROBOT_LIBRARY_VERSION)
        except AttributeError:
            try:
                return str(code.__version__)
            except AttributeError:
                return '<unknown>'

    def _create_init_handler(self, libcode):
        init_method =  getattr(libcode, '__init__', None)
        if not self._valid_init(init_method):
            init_method = None
        return InitHandler(self, init_method)
    
    def _valid_init(self, init_method):
        if utils.is_jython and isinstance(init_method, PyReflectedConstructor):
            return True
        if isinstance(init_method, (types.MethodType, types.FunctionType)):
            return True
        return False
    
    def _init_scope_handling(self):
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
    
    def _get_scope(self, libcode):
        try:
            scope = libcode.ROBOT_LIBRARY_SCOPE
            scope = utils.normalize(scope, ignore=['_']).upper()
        except:
            scope = 'TESTCASE'
        return scope in ['GLOBAL','TESTSUITE'] and scope or 'TESTCASE'
        
    def get_instance(self):
        try:
            if self._libinst is None:
                self._libinst = self._get_instance()
        except AttributeError:
            self._libinst = self._get_instance()
        return self._libinst

    def _get_instance(self):
        self.init.check_arg_limits(self.args)
        try:
            return self._libcode(*self.args)
        except:
            self._raise_creating_instance_failed()

    def _create_handlers(self, libinst, syslog):
        success, failure, details = self._get_reporting_methods(syslog)
        handlers = utils.NormalizedDict(ignore=['_'])
        for name in self._get_handler_names(libinst):
            err_pre = "Adding keyword '%s' to library '%s' failed: " % (name, self.name) 
            try:
                method = self._get_handler_method(self._libinst, name)
                success("Got handler method '%s'" % (name))
            except TypeError:
                failure(err_pre + 'Not a method or function')
                continue
            except:
                err_msg, err_details = utils.get_error_details()
                failure(err_pre + 'Getting handler method failed: ' + err_msg) 
                details('Details:\n%s' % err_details)
                continue
            try:
                handlers[name] = self._create_handler(name, method)
                success("Created keyword '%s'" % handlers[name].name)
            except:
                err_msg, err_details = utils.get_error_details()
                failure(err_pre + 'Creating keyword failed: ' + err_msg)
                details('Details:\n%s' % err_details)
        return handlers

    def _get_reporting_methods(self, syslog):
        # success, failure, details
        return syslog.debug, syslog.info, syslog.debug
                    
    def _get_handler_names(self, libcode):
        return [ name for name in dir(libcode) 
                 if not (name.startswith('_') or 
                         name.startswith('ROBOT_LIBRARY_')) ]
        
    def _get_handler_method(self, libcode, name):
        method = getattr(libcode, name)
        if inspect.isroutine(method):
            return method
        raise TypeError('Not a method or function')
    
    def _create_handler(self, handler_name, handler_method):
        return Handler(self, handler_name, handler_method)

    def _raise_creating_instance_failed(self):
        msg, details = utils.get_error_details()
        if self.args:
            args = "argument%s %s" % (utils.plural_or_not(self.args),
                                      utils.seq2str(self.args))
        else:
            args = "no arguments"
        raise DataError("Creating an instance of the test library '%s' with %s "
                        "failed: %s\n%s" % (self.name, args, msg, details))


class _ClassLibrary(_BaseTestLibrary):
    
    def _get_handler_method(self, libcode, name):
        # Type is checked before using getattr to avoid calling properties, most
        # importantly bean properties generated by Jython (issue 188).
        for item in (libcode,) + inspect.getmro(libcode.__class__):
            try:
                attr = item.__dict__[name]
                if self._isroutine(attr) and \
                     (item is libcode or self._is_valid_handler(item, attr)):
                    return getattr(libcode, name)
            except (KeyError, AttributeError): 
                # Java classes don't always have __dict__
                pass
        raise TypeError('Not a method or function')
    
    def _isroutine(self, item):
        return inspect.isroutine(item) \
                or (utils.is_jython and isinstance(item, PyReflectedFunction))
            
    def _is_valid_handler(self, handler_class, handler):
        "Filters methods defined in java.lang.Object or generated by Jython."
        if not utils.is_jython or not isinstance(handler, PyReflectedFunction):
            return True
        if handler_class is Object:
            return False
        # signature is an instance of org.python.ReflectedArgs
        for signature in handler.argslist[:handler.nargs]:
            # 'getName' may raise an exception -- not sure why but that happens
            # at least with handlers declared in class extending JUnit TestCase.
            # Would be better to investigate but just not excluding these
            # should be an ok workaround.
            try:
                name = signature.declaringClass.getName()
                if not name.startswith('org.python.proxies.'):
                    return True
            except:
                return True
        return False


class _ModuleLibrary(_BaseTestLibrary):
    
    def _get_scope(self, libcode):
        return 'GLOBAL'
        
    def get_instance(self):
        self.init.check_arg_limits(self.args)
        return self._libcode

    def _create_init_handler(self, libcode):
        return InitHandler(self, None)


class _HybridLibrary(_BaseTestLibrary):
    
    def _get_handler_names(self, instance):
        try:
            return instance.get_keyword_names()
        except AttributeError:
            return instance.getKeywordNames()

    def _get_reporting_methods(self, syslog):
        # Use syslog.warn for reporting possible failures when creating kws 
        # to make them visible. With hybrid libraries kw names are returned 
        # explicitly so creating them should also pass.
        return syslog.debug, syslog.warn, syslog.info
    
        
class _DynamicLibrary(_BaseTestLibrary):
    
    def __init__(self, libcode, source, name, args, syslog):
        self._get_kw_doc = _get_dynamic_method(libcode, 'get_keyword_documentation')
        self._get_kw_args = _get_dynamic_method(libcode, 'get_keyword_arguments')
        _BaseTestLibrary.__init__(self, libcode, source, name, args, syslog)
     
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
        if self._get_kw_doc:
            doc = self._get_kw_doc(self._libinst, handler_name)
        else:
            doc = ''
        if self._get_kw_args:
            argspec = self._get_kw_args(self._libinst, handler_name)
        else:
            argspec = None
        return DynamicHandler(self, handler_name, handler_method, doc, argspec)
