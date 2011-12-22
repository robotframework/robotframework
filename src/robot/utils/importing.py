#  Copyright 2008-2011 Nokia Siemens Networks Oyj
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
import sys
import inspect

from robot.errors import DataError

from .error import get_error_message, get_error_details
from .robotpath import abspath


class Importer(object):
    _valid_to_import_by_path = ('.py', '.java', '.class', '/', os.sep)

    def __init__(self, type=None):
        type = ' %s ' % type if type else ' '
        self._error_template = 'Importing' + type + "'%s' failed: %s"

    def import_module_by_path(self, path):
        try:
            self._verify_import_path(path)
            module = self._import_by_path(path)
            if inspect.isclass(module):
                return self._instantiate_java_class(module)
            return module
        except DataError, err:
            raise DataError(self._error_template % (path, unicode(err)))

    def _verify_import_path(self, path):
        if not os.path.exists(path):
            raise DataError('File or directory does not exist.')
        if not path.endswith(self._valid_to_import_by_path):
            raise DataError('Not a valid file or directory to import.')

    def _import_by_path(self, path):
        module_dir, module_name = self._split_path_to_module(path)
        sys.path.insert(0, module_dir)
        if module_name in sys.modules:
            del sys.modules[module_name]
        try:
            return __import__(module_name)
        except:
            raise DataError('%s\n%s' % get_error_details())
        finally:
            sys.path.pop(0)

    def _split_path_to_module(self, path):
        module_dir, module_file = os.path.split(abspath(path))
        module_name = os.path.splitext(module_file)[0]
        return module_dir, module_name

    def _instantiate_java_class(self, jclass):
        try:
            return jclass()
        except:
            raise DataError(get_error_message())

    def import_class_or_module(self):
        pass


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
    if '.' not in name or os.path.exists(name):
        code, module = _non_dotted_import(name, type_)
    else:
        code, module = _dotted_import(name, type_)
    source = _get_module_source(module)
    return code, source

def _non_dotted_import(name, type_):
    try:
        if os.path.exists(name):
            module = Importer(type_).import_module_by_path(name)
        else:
            module = __import__(name)
    except:
        _raise_import_failed(type_, name)
    try:
        code = getattr(module, module.__name__)
        if not inspect.isclass(code):
            raise AttributeError
    except AttributeError:
        code = module
    return code, module

def _dotted_import(name, type_):
    parentname, libname = name.rsplit('.', 1)
    try:
        try:
            module = __import__(parentname, fromlist=[str(libname)])
        except ImportError:
            # Hack to support standalone Jython:
            # http://code.google.com/p/robotframework/issues/detail?id=515
            if not sys.platform.startswith('java'):
                raise
            __import__(name)
            module = __import__(parentname, fromlist=[str(libname)])
    except:
        _raise_import_failed(type_, name)
    try:
        code = getattr(module, libname)
    except AttributeError:
        _raise_no_lib_in_module(type_, parentname, libname)
    if not (inspect.ismodule(code) or inspect.isclass(code)):
        _raise_invalid_type(type_, code)
    return code, module

def _get_module_source(module):
    source = getattr(module, '__file__', None)
    return abspath(source) if source else '<unknown>'

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
