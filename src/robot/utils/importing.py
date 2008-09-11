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
import sys
import types 
if os.name == 'java':
    from java.lang import System
    
from robot.errors import DataError
from error import get_error_message, get_error_details
from robottypes import type_as_str
from normalizing import normpath

_VALID_IMPORT_TYPES = (types.ModuleType, types.ClassType, types.TypeType)


def simple_import(path_to_module):
    err_prefix = "Importing '%s' failed: " % path_to_module
    if not os.path.exists(path_to_module):
        raise DataError(err_prefix + 'File does not exist')
    moddir, modname = _split_path_to_module(path_to_module)
    sys.path.insert(0, moddir)
    try:
        module = __import__(modname)
        if normpath(moddir) != normpath(os.path.dirname(module.__file__)):
            reload(module)
    except:
        sys.path.pop(0)
        raise DataError(err_prefix + get_error_message())
    sys.path.pop(0)
    return module


def _split_path_to_module(path):
    moddir, modfile = os.path.split(path)
    modname = os.path.splitext(modfile)[0]
    return moddir, modname


def import_(name, type_='test library'):
    """Imports Python class/module or Java class with given name.

    'name' can also be a path to the library and in that case the directory
    containing the lib is automatically put into sys.path and removed there
    afterwards.

    'type_' is used in error message if importing fails.
        
    Class can either live in a module/package or be 'standalone'. In the former
    case tha name is something like 'MyClass' and in the latter it could be
    'your.package.YourLibrary'). Python classes always live in a module but if
    the module name is exactly same as the class name the former also works in
    Python.

    Example: If you have a Python class 'MyLibrary' in a module 'mymodule'
    it must be imported with name 'mymodule.MyLibrary'. If the name of
    the module is also 'MyLibrary' then it is possible to use only
    name 'MyLibrary'. 
    """
    if os.path.exists(name):
        moddir, name = _split_path_to_module(name)
        sys.path.insert(0, moddir)
        pop_sys_path = True
    else:
        pop_sys_path = False
    if name.count('.') > 0:
        parts = name.split('.')
        modname = '.'.join(parts[:-1])
        classname = parts[-1]
        fromlist = [ str(classname) ]
    else:
        modname = name
        classname = name
        fromlist = []
    try:
        # It seems that we get class when importing java class from file system
        # or from a default package of a jar file. Otherwise we get a module.
        module_or_class = __import__(modname, globals(), locals(), fromlist)
    except:
        if pop_sys_path:
            sys.path.pop(0)
        _raise_import_failed(type_, name)
    if pop_sys_path:
        sys.path.pop(0)
    try:
        code = getattr(module_or_class, classname)
    except AttributeError:
        if fromlist:
            _raise_no_lib_in_module(type_, modname, fromlist[0])
        code = module_or_class
    if not isinstance(code, _VALID_IMPORT_TYPES):
        _raise_invalid_type(type_, code)
    try:
        imported_from = module_or_class.__file__
        if not imported_from:
            raise AttributeError
    except AttributeError:
        # Java classes not packaged in a jar file do not have __file__. 
        imported_from = '<unknown>'
    return code, imported_from


def _raise_import_failed(type_, name):
    error_msg, error_details = get_error_details()
    msg = "Importing %s '%s' failed: %s\nPYTHONPATH: %s" \
            % (type_, name, error_msg, str(sys.path))
    if os.name == 'java':
        msg += '\nCLASSPATH: %s' % System.getProperty('java.class.path')
    msg += '\n%s' % (error_details)
    raise DataError(msg)


def _raise_no_lib_in_module(type_, modname, libname):
    raise DataError("%s module '%s' does not contain '%s'" 
            % (type_.capitalize(), modname, libname))
                        
                        
def _raise_invalid_type(type_, code):                        
    raise DataError("Imported %s is not a class or module, got '%s' instead" 
            % (type_, type_as_str(code)))
