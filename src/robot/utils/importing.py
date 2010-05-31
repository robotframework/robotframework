#  Copyright 2008-2010 Nokia Siemens Networks Oyj
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
import inspect

from robot.errors import DataError
from error import get_error_message, get_error_details
from normalizing import normpath


def simple_import(path_to_module):
    err_prefix = "Importing '%s' failed: " % path_to_module
    if not os.path.exists(path_to_module):
        raise DataError(err_prefix + 'File does not exist')
    moddir, modname = _split_path_to_module(path_to_module)
    try:
        try:
            module = __import__(modname)
            if normpath(moddir) != normpath(os.path.dirname(module.__file__)):
                del sys.modules[modname]
                module = __import__(modname)
        except:
            raise DataError(err_prefix + get_error_message())
    finally:
        sys.path.pop(0)
    return module


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
        inserted_to_path, name = _split_path_to_module(name)
    else:
        inserted_to_path = None
    try:
        code, module = _import(name, type_)
    finally:
        if inserted_to_path:
            sys.path.pop(0)
    source = _get_module_source(module)
    return code, source


def _split_path_to_module(path):
    moddir, modfile = os.path.split(os.path.abspath(path))
    modname = os.path.splitext(modfile)[0]
    sys.path.insert(0, moddir)
    return moddir, modname

def _import(name, type_):
    modname, classname, fromlist = _get_import_params(name)
    try:
        try:
            # It seems that we get class when importing java class from file system
            # or from a default package of a jar file. Otherwise we get a module.
            imported = __import__(modname, {}, {}, fromlist)
        except ImportError:
            # Hack to support standalone Jython: 
            # http://code.google.com/p/robotframework/issues/detail?id=515
            if not sys.platform.startswith('java'):
                raise 
            __import__(name)
            imported = __import__(modname, {}, {}, fromlist)
    except:
        _raise_import_failed(type_, name)
    try:
        code = getattr(imported, classname)
    except AttributeError:
        if fromlist:
            _raise_no_lib_in_module(type_, modname, fromlist[0])
        code = imported
    if not (inspect.ismodule(code) or inspect.isclass(code)):
        if fromlist:
            _raise_invalid_type(type_, code)
        else:
            code = imported
    return code, imported

def _get_import_params(name):
    if '.' not in name:
        return name, name, []
    parts = name.split('.')
    modname = '.'.join(parts[:-1])
    classname = parts[-1]
    fromlist = [str(classname)]  # Unicode not generally accepted
    return modname, classname, fromlist

def _get_module_source(module):
    try:
        source = module.__file__
        if not source:
            raise AttributeError
    except AttributeError:
        # Java classes not packaged in a jar file do not have __file__.
        return '<unknown>'
    dirpath, filename = os.path.split(os.path.abspath(source))
    return os.path.join(normpath(dirpath), filename)

def _raise_import_failed(type_, name):
    error_msg, error_details = get_error_details()
    msg = ["Importing %s '%s' failed: %s" % (type_, name, error_msg),
           "PYTHONPATH: %s" % sys.path, error_details]
    if sys.platform.startswith('java'):
        from java.lang import System
        msg.insert(-1, 'CLASSPATH: %s' % System.getProperty('java.class.path'))
    raise DataError('\n'.join(msg))

def _raise_no_lib_in_module(type_, modname, libname):
    raise DataError("%s module '%s' does not contain '%s'."
                    % (type_.capitalize(), modname, libname))

def _raise_invalid_type(type_, code):
    raise DataError("Imported %s should be a class or module, got %s."
                    % (type_, type(code).__name__))
