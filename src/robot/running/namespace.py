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


import os.path

from robot import utils
from robot.errors import FrameworkError, DataError
from robot.libraries import STDLIB_NAMES
from robot.variables import GLOBAL_VARIABLES
from robot.common import UserErrorHandler
from robot.output import SYSLOG
import robot

from importer import Importer
from runkwregister import RUN_KW_REGISTER


IMPORTER = Importer()


class Namespace:
    """A database for keywords and variables.
    
    A new instance of this class is created for each test suite.
    """

    def __init__(self, suite, parent):
        if suite is not None:
            SYSLOG.info("Initializing namespace for test suite '%s'" % suite.longname)
        self.variables = _VariableScopes(suite, parent)
        self.suite = suite
        self.test = None
        self.library_order = []
        self.uk_handlers = []
        self._testlibs = {}
        self._userlibs = []
        self._imported_resource_files = []
        self._imported_variable_files = []
        # suite is None only when used internally by copy 
        if suite is not None:
            self.import_library('BuiltIn')
            self.import_library('Reserved')
            if suite.source is not None:
                self._handle_imports(suite.imports)
            robot.running.NAMESPACES.start_suite(self)
            
    def copy(self):
        # Namespace is copied by ParallelKeyword
        ns = Namespace(None, None, None)
        ns.variables = self.variables.copy_all()
        ns.suite = self.suite
        ns.test = self.test
        ns.uk_handlers = self.uk_handlers[:]
        ns._testlibs = self._testlibs
        ns._userlibs = self._userlibs
        ns.library_order = self.library_order[:]
        return ns

    def _handle_imports(self, import_settings):
        for item in import_settings:
            try:
                item.replace_variables(self.variables.current)
                if item.name == 'Library':
                    self.import_library(item.value[0], item.value[1:])
                elif item.name == 'Resource':
                    self._import_resource(item.value[0])
                elif item.name == 'Variables':
                    self.import_variables(item.value[0], item.value[1:])
                else:
                    raise FrameworkError("Invalid import setting: %s" % item)
            except:
                item.report_invalid_syntax()
        
    def _import_resource(self, path):
        if path not in self._imported_resource_files:
            self._imported_resource_files.append(path)
            resource = IMPORTER.import_resource(path)
            self.variables.set_from_variable_table(resource.variables)
            self._userlibs.append(resource.user_keywords)
            self._handle_imports(resource.imports)
        else:
            SYSLOG.warn("Resource file '%s' already imported by suite '%s'"
                        % (path, self.suite.longname))

    def import_variables(self, path, args, overwrite=False):
        if (path,args) not in self._imported_variable_files:
            self._imported_variable_files.append((path,args))
            self.variables.set_from_file(path, args, overwrite)
        else:
            msg = "Variable file '%s'" % path
            if args:
                msg += " with arguments %s" % (utils.seq2str2(args))
            SYSLOG.warn("%s already imported by suite '%s'"
                        % (msg, self.suite.longname))

    def import_library(self, name, args=None):
        code_name, lib_name, args = self._get_lib_names_and_args(name, args)
        if self._testlibs.has_key(lib_name):
            SYSLOG.warn("Test library '%s' already imported by suite '%s'"
                        % (lib_name, self.suite.longname))
            return
        lib = IMPORTER.import_library(code_name, args)
        if code_name != lib_name:
            lib = lib.copy(lib_name)
            SYSLOG.info("Imported library '%s' with name '%s'"
                        % (code_name, lib_name))
        self._testlibs[lib_name] = lib
        lib.start_suite()
        if self.test is not None:
            lib.start_test()
        self._import_deprecated_standard_libs(lib_name)

    def _get_lib_names_and_args(self, name, args):
        # Ignore spaces unless importing by path
        if not os.path.exists(name):
            name = name.replace(' ', '')
        args = utils.to_list(args)
        if len(args) >= 2 and args[-2].upper() == 'WITH NAME':
            lib_name = args[-1].replace(' ', '')
            args = args[:-2]
        else:
            lib_name = name
        return name, lib_name, args
        
    def _import_deprecated_standard_libs(self, name):
        if name in ['BuiltIn', 'OperatingSystem']:
            self.import_library('Deprecated' + name)

    def start_test(self, test):
        self.variables.start_test(test)
        self.test = test
        for lib in self._testlibs.values():
            lib.start_test()
        
    def end_test(self):
        self.test = None
        self.variables.end_test()
        self.uk_handlers = []
        for lib in self._testlibs.values():
            lib.end_test()
        
    def end_suite(self):
        self.suite = None
        self.variables.end_suite()
        for lib in self._testlibs.values():
            lib.end_suite()
        robot.running.NAMESPACES.end_suite()
                    
    def start_user_keyword(self, handler):
        self.variables.start_uk(handler)
        self.uk_handlers.append(handler)
        
    def end_user_keyword(self):
        self.variables.end_uk()
        self.uk_handlers.pop()
        
    def get_library_instance(self, libname):
        return self._testlibs[libname].get_instance()
        
    def get_handler(self, name):
        try:
            handler = None
            if '.' in name:
                handler = self._get_explicit_handler(name)
            if handler is None:
                handler = self._get_implicit_handler(name)
            if handler is None:
                raise DataError("No keyword with name '%s' found." % name)
        except:
            error = utils.get_error_message()
            handler = UserErrorHandler(name, error)
        try:
            handler.replace_variables(self.variables)
        except AttributeError:  # only applicable for UserHandlers
            pass
        return handler

    def _get_implicit_handler(self, name):
        # 1) Try to find handler from test case file user keywords
        try:
            return self.suite.user_keywords.get_handler(name)
        except DataError:
            pass
        # 2) Try to find unique keyword from resource file user keywords
        found = [ lib.get_handler(name)
                  for lib in self._userlibs if lib.has_handler(name) ]
        if len(found) == 1:
            return found[0]
        if len(found) > 1:
            self._raise_multiple_keywords_found(name, found)
        # 3) Try to find unique keyword from base keywords
        found = [ lib.get_handler(name)
                  for lib in self._testlibs.values() if lib.has_handler(name) ]
        found = self._get_handler_based_on_default_library_order(found)
        if len(found) == 2:
            found = self._filter_stdlib_handler(found[0], found[1])
        if len(found) > 1:
            raise self._raise_multiple_keywords_found(name, found)
        if len(found) == 1:
            return found[0]
        return None

    def _get_handler_based_on_default_library_order(self, handlers):
        libraries = [handler.library.name for handler in handlers ]
        for name in self.library_order:
            if name in libraries:
                return [handler for handler in handlers if handler.library.name == name]
        return handlers             

    def _filter_stdlib_handler(self, hand1, hand2):
        if hand1.library.orig_name in STDLIB_NAMES:
            std_hand, ext_hand = hand1, hand2
        elif hand2.library.orig_name in STDLIB_NAMES:
            std_hand, ext_hand = hand2, hand1
        else:
            return [hand1, hand2]
        if not RUN_KW_REGISTER.is_run_keyword(ext_hand):
            SYSLOG.warn(
                "Keyword '%s' found both from a user created test library "
                "'%s' and Robot Framework standard library '%s'. The user "
                "created keyword is used. To select explicitly, and to get "
                "rid of this warning, use full format i.e. either '%s' or '%s'."
                % (std_hand.name,
                   ext_hand.library.orig_name, std_hand.library.orig_name,
                   ext_hand.longname, std_hand.longname))
        return [ext_hand]
    
    def _get_explicit_handler(self, name):
        libname, kwname = self._split_keyword_name(name)
        # 1) Find matching lib(s)
        libs = [ lib for lib in self._userlibs + self._testlibs.values() 
                 if utils.eq(lib.name, libname) ]
        if not libs:
            return None
        # 2) Find matching kw from found libs
        found = [ lib.get_handler(kwname)
                  for lib in libs if lib.has_handler(kwname) ]
        if len(found) > 1:
            self._raise_multiple_keywords_found(name, found, implicit=False)
        return found and found[0] or None

    def _split_keyword_name(self, name):
        parts = name.split('.')
        kwname = parts.pop()       # pop last part
        libname = '.'.join(parts)  # and rejoin rest
        return libname, kwname

    def _raise_multiple_keywords_found(self, name, found, implicit=True):
        error = "Multiple keywords with name '%s' found.\n" % name
        if implicit:
            error += "Give the full name of the keyword you want to use.\n"
        names = [ handler.longname for handler in found ]
        names.sort()
        error += "Found: %s" % utils.seq2str(names)
        raise DataError(error)


class _VariableScopes:
    
    def __init__(self, suite, parent):
        # suite and parent are None only when used by copy_all
        if suite is not None:
            suite.variables.update(GLOBAL_VARIABLES)
            self._suite = self.current = suite.variables
        self._parents = []
        if parent is not None:
            self._parents.append(parent.namespace.variables.current)
            self._parents.extend(parent.namespace.variables._parents)
        self._test = None
        self._uk_handlers = []

    def copy_all(self):
        vs = _VariableScopes(None, None)
        vs._suite = self._suite
        vs._test = self._test
        vs._uk_handlers = self._uk_handlers[:]
        vs._parents = self._parents[:]
        vs.current = self.current
        return vs
        
    def replace_list(self, items):
        return self.current.replace_list(items)

    def replace_scalar(self, items):
        return self.current.replace_scalar(items)

    def replace_string(self, string):
        return self.current.replace_string(string)
    
    def set_from_file(self, path, args, overwrite=False):
        variables = self._suite.set_from_file(path, args, overwrite)
        if self._test is not None:
            self._test._set_from_file(variables, overwrite=True)
        for varz in self._uk_handlers:
            varz._set_from_file(variables, overwrite=True)
        if self._uk_handlers:
            self.current._set_from_file(variables, overwrite=True)
            
    def set_from_variable_table(self, rawvariables):
        self._suite.set_from_variable_table(rawvariables)
    
    def replace_from_meta(self, name, item, errors):
        error = None
        for varz in [self.current] + self._parents:
            try:
                if name in ['Setup', 'Teardown']:
                    return varz.replace_list(item[:1]) + item[1:]
                if utils.is_list(item):
                    return varz.replace_list(item)
                return varz.replace_string(item)
            except DataError, err:
                if error is None:
                    error = str(err)
        errors.append("Replacing variables from metadata '%s' failed: %s" 
                      % (name, error))
        return utils.unescape(item)
        
    def __getitem__(self, name):
        return self.current[name]
    
    def __setitem__(self, name, value):
        self.current[name] = value
        
    def end_suite(self):
        self._suite = self._test = self.current = None
        
    def start_test(self, test):
        self._test = self.current = self._suite.copy()

    def end_test(self):
        self.current = self._suite
        
    def start_uk(self, handler):
        self._uk_handlers.append(self.current)
        self.current = self.current.copy()
    
    def end_uk(self):
        self.current = self._uk_handlers.pop()
        
    def set_global(self, name, value):
        GLOBAL_VARIABLES[name] = value
        self.set_suite(name, value)
        
    def set_suite(self, name, value):
        self._suite[name] = value
        self.set_test(name, value, False)
        
    def set_test(self, name, value, fail_if_no_test=True):
        if self._test is not None:
            self._test[name] = value
        elif fail_if_no_test:
            raise DataError("Cannot set test variable when no test is started")
        for varz in self._uk_handlers:
            varz[name] = value
        self.current[name] = value # latest uk handler is not in self._uk_handlers

    def keys(self):
        return self.current.keys()
    
    def has_key(self, key):
        return self.current.has_key(key)
