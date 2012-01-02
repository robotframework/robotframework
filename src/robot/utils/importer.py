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
if sys.platform.startswith('java'):
    from java.lang.System import getProperty

from robot.errors import DataError

from .error import get_error_details
from .robotpath import abspath


# TODO:
# - test and possibly prune tracebacks
# - test PYTHONPATH and CLASSPATH
# - acceptance tests for issue 979
# - test can variable files be implemented with java/python classes nowadays
#   (possibly returning class when importing by path is bwic anyway)


class Importer(object):

    def __init__(self, type=None, logger=None):
        self._type = type or ''
        self._logger = logger
        self._importers = [ByPathImporter(), NonDottedImporter(), DottedImporter()]
        self._by_path_importer = self._importers[0]

    def import_class_or_module(self, name):
        """Imports Python class/module or Java class with given name.

        Class can either live in a module/package or be standalone Java class.
        In the former case the name is something like 'MyClass' and in the
        latter it could be 'your.package.YourLibrary'. Python classes always
        live in a module, but if the module name is exactly same as the class
        name then simple 'MyLibrary' will import a class.

        Python modules can be imported both using format 'MyModule' and
        'mymodule.submodule'.

        `name` can also be a path to the imported file/directory. In that case
        importing is done using `import_class_or_module_by_path` method.
        """
        try:
            imported, source = self._import_class_or_module(name)
        except DataError, err:
            self._raise_import_failed(name, err)
        else:
            self._log_import_succeeded(imported, name, source)
            return imported

    def _import_class_or_module(self, name):
        for importer in self._importers:
            if importer.handles(name):
                return importer.import_(name)

    def import_class_or_module_by_path(self, path):
        """Import a Python module or Java class using a file system path.

        When importing a Python file, the path must end with '.py' and the
        actual file must also exist. When importing a Python module implemented
        as a directory, the path must end with '/' or, on Windows, with '\\'.

        When importing Java classes, the path must end with '.java' or '.class'.
        The class file must exist in both cases and in the former case also
        the source file must exist.
        """
        try:
            imported, source = self._by_path_importer.import_(path)
        except DataError, err:
            self._raise_import_failed(path, err)
        else:
            self._log_import_succeeded(imported, imported.__name__, source)
            return imported

    def _raise_import_failed(self, name, error):
        import_type = '%s ' % self._type if self._type else ''
        msg = "Importing %s'%s' failed: %s" % (import_type, name, error.message)
        if not error.details:
            raise DataError(msg)
        msg = [msg, '', error.details]
        msg.extend(self._get_items_in('PYTHONPATH', sys.path))
        if sys.platform.startswith('java'):
            classpath = getProperty('java.class.path').split(os.path.pathsep)
            msg.extend(self._get_items_in('CLASSPATH', classpath))
        raise DataError('\n'.join(msg))

    def _log_import_succeeded(self, item, name, source):
        if self._logger:
            import_type = '%s ' % self._type if self._type else ''
            item_type = 'module' if inspect.ismodule(item) else 'class'
            location = ("'%s'" % source) if source else 'unknown location'
            self._logger.info("Imported %s%s '%s' from %s."
                              % (import_type, item_type, name, location))

    def _get_items_in(self, type, items):
        yield '\n%s:' % type
        for item in items:
            yield '  %s' % item


class _Importer(object):

    def _import(self, name, fromlist=None, retry=True):
        try:
            try:
                return __import__(name, fromlist=fromlist)
            except ImportError:
                # Hack to support standalone Jython:
                # http://code.google.com/p/robotframework/issues/detail?id=515
                if fromlist and retry and sys.platform.startswith('java'):
                    __import__(name)
                    return self._import(name, fromlist, retry=False)
                raise
        except:
            raise DataError(*get_error_details())

    def _verify_type(self, imported):
        if inspect.isclass(imported) or inspect.ismodule(imported):
            return imported
        raise DataError('Expected class or module, got <%s>.' % type(imported).__name__)

    def _get_class_from_module(self, module):
        klass = getattr(module, module.__name__, None)
        return klass if inspect.isclass(klass) else None

    def _get_source(self, module):
        source = getattr(module, '__file__', None)
        return abspath(source) if source else None


class ByPathImporter(_Importer):
    _import_path_endings = ('.py', '.java', '.class', '/', os.sep)

    def handles(self, path):
        return os.path.exists(path) and path.endswith(self._import_path_endings)

    def import_(self, path):
        self._verify_import_path(path)
        module = self._import_by_path(path)
        imported = self._get_class_from_module(module) or module
        return self._verify_type(imported), path

    def _import_by_path(self, path):
        module_dir, module_name = self._split_path_to_module(path)
        sys.path.insert(0, module_dir)
        if module_name in sys.modules:
            del sys.modules[module_name]
        try:
            return self._import(module_name)
        finally:
            sys.path.pop(0)

    def _verify_import_path(self, path):
        if not os.path.exists(path):
            raise DataError('File or directory does not exist.')
        if not path.endswith(self._import_path_endings):
            raise DataError('Not a valid file or directory to import.')

    def _split_path_to_module(self, path):
        module_dir, module_file = os.path.split(abspath(path))
        module_name = os.path.splitext(module_file)[0]
        return module_dir, module_name


class NonDottedImporter(_Importer):

    def handles(self, name):
        return '.' not in name

    def import_(self, name):
        module = self._import(name)
        imported = self._get_class_from_module(module) or module
        return self._verify_type(imported), self._get_source(module)


class DottedImporter(_Importer):

    def handles(self, name):
        return '.' in name

    def import_(self, name):
        parent_name, lib_name = name.rsplit('.', 1)
        parent = self._import(parent_name, [str(lib_name)])
        try:
            imported = getattr(parent, lib_name)
        except AttributeError:
            raise DataError("Module '%s' does not contain '%s'."
                            % (parent_name, lib_name))
        return self._verify_type(imported), self._get_source(parent)
