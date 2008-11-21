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

from robot import utils
from robot.errors import DataError
from robot.common import BaseLibrary
from robot.output import SystemLogger

from handlers import PythonHandler, JavaHandler, DynamicHandler


def TestLibrary(name, args=None, syslog=None):
    if syslog is None:
        syslog = SystemLogger()
    libcode, source = utils.import_(name)
    args = utils.to_list(args)
    if isinstance(libcode, types.ModuleType):
        if args:
            raise DataError('Libraries implemented as modules do not take '
                            'arguments, got: %s' % str(args))
        return ModuleLibrary(libcode, source, name, args, syslog)
    if _has_method(libcode, ['get_keyword_names', 'getKeywordNames']):
        if _has_method(libcode, ['run_keyword', 'runKeyword']):
            return DynamicLibrary(libcode, source, name, args, syslog)
        else:
            return HybridLibrary(libcode, source, name, args, syslog)
    # Using type check and not isinstance for ClassType, because it does not 
    # match Java classes whose type is javaclass. 
    if type(libcode) is types.ClassType or isinstance(libcode, types.TypeType):
        return PythonLibrary(libcode, source, name, args, syslog)
    return JavaLibrary(libcode, source, name, args, syslog)
    

def _has_method(code, names):
    for name in names:
        if hasattr(code, name) and _is_method(getattr(code, name)):
            return True
    return False

def _is_method(code):
    return isinstance(code, types.MethodType) or \
            (utils.is_jython and 'reflectedfunction' in str(type(code)))


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
            self._libinst = self.get_instance()
            self.handlers = self._create_handlers(self._libinst, syslog)
            self.init =  self._get_init(self._libinst)
            self._init_scope_handling()

    def _get_version(self, code):
        try:
            return str(code.ROBOT_LIBRARY_VERSION)
        except AttributeError:
            try:
                return str(code.__version__)
            except AttributeError:
                return '<unknown>'
            
    def _init_scope_handling(self):
        if self.scope == 'GLOBAL':
            return
        self._libinst = None
        self.start_suite = self._caching_start
        self.end_suite = self._restoring_end
        if self.scope == 'TESTCASE':
            self.start_test = self._caching_start
            self.end_test = self._restoring_end
            
    def copy(self, name):
        lib = _BaseTestLibrary(None, self.version, name, self.args, None)
        lib.orig_name = self.name
        lib.doc = self.doc
        lib.scope = self.scope
        lib._libcode = self._libcode
        lib._libinst = self._libinst
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
        try:  
            return self._libcode(*self.args)
        except:
            self._raise_creating_instance_failed()

    def _get_init(self, libinst):
        if hasattr(libinst, '__init__'):
            try:
                return self._create_handler('__init__', libinst.__init__)
            except TypeError:
                pass
        return None

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
        if not isinstance(method, (types.MethodType, types.FunctionType)):
            raise TypeError('Not a method or function')
        return method
    
    def _raise_creating_instance_failed(self):
        error_msg, error_details = utils.get_error_details()
        msg = "Creating an instance of the test library '%s' " % self.name
        if len(self.args) == 0:
            msg += "with no arguments "
        elif len(self.args) == 1:
            msg += "with argument '%s' " % self.args[0]
        else:
            msg += "with arguments %s " % utils.seq2str(self.args)
        msg += "failed: " + error_msg
        msg += "\n" + error_details
        raise DataError(msg)
    

class ModuleLibrary(_BaseTestLibrary):
    
    def _get_scope(self, libcode):
        return 'GLOBAL'
        
    def get_instance(self):
        return self._libcode

    def _get_init(self, libinst):
        return None
    
    def _create_handler(self, handler_name, handler_method):
        return PythonHandler(self, handler_name, handler_method)
    
    
class PythonLibrary(_BaseTestLibrary):
        
    def _create_handler(self, handler_name, handler_method):
        if self._is_java_method(handler_method):
            return JavaHandler(self, handler_name, handler_method)
        return PythonHandler(self, handler_name, handler_method)
        
    def _is_java_method(self, method):
        if not utils.is_jython:
            return False
        try:
            return 'reflectedfunction' in str(type(method.im_func)) or \
                   'reflectedconstructor' in str(type(method.im_func))
        except AttributeError:
            return False


class HybridLibrary(PythonLibrary):
    
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
    
        
class DynamicLibrary(_BaseTestLibrary):
    
    _get_kw_doc_names = ['get_keyword_documentation', 'getKeywordDocumentation']
    _get_kw_args_names = ['get_keyword_arguments', 'getKeywordArguments']
    
    def __init__(self, libcode, source, name, args, syslog):
        self._get_keyword_documentation = self._get_method(libcode, *self._get_kw_doc_names)
        self._get_keyword_arguments = self._get_method(libcode, *self._get_kw_args_names)
        _BaseTestLibrary.__init__(self, libcode, source, name, args, syslog)
        
    def _get_method(self, libcode, name, alternative):
        try:
            code = getattr(libcode, name)
            return code
        except AttributeError:
            try:
                code = getattr(libcode, alternative)
                return code
            except:
                return None
     
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
        doc = self._get_kw_doc(handler_name)
        argspec = self._get_kw_argspec(handler_name)
        return DynamicHandler(self, handler_name, handler_method, doc, argspec)
    
    def _get_kw_doc(self, name):
        if self._get_keyword_documentation is not None:
            return self._get_keyword_documentation(self._libinst, name)
        return ''
    
    def _get_kw_argspec(self, name):
        if self._get_keyword_arguments is not None:
            return self._get_keyword_arguments(self._libinst, name)
        return None
    
    
class JavaLibrary(_BaseTestLibrary):
    
    def _create_handler(self, handler_name, handler_method):
        return JavaHandler(self, handler_name, handler_method)
    
