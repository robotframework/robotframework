from __future__ import with_statement
import unittest
import tempfile
import inspect
import shutil
import sys
import os
from os.path import abspath, dirname, exists, isabs, join, normpath

from robot.errors import DataError
from robot.utils.importing import Importer
from robot.utils.asserts import (assert_equals, assert_true, assert_raises,
                                 assert_raises_with_msg)


CURDIR = dirname(abspath(__file__))
LIBDIR = normpath(join(CURDIR, '..', '..', 'atest', 'testresources', 'testlibs'))
TEMPDIR = tempfile.gettempdir()
TESTDIR = join(TEMPDIR, 'robot-importer-testing')


def assert_prefix(error, expected):
    prefix = ':'.join(unicode(error).split(':')[:2]) + ':'
    assert_equals(prefix, expected)


class TestImportByPath(unittest.TestCase):

    def setUp(self):
        self.tearDown()
        os.mkdir(TESTDIR)

    def tearDown(self):
        if exists(TESTDIR):
            shutil.rmtree(TESTDIR)

    def test_python_file(self):
        path = self._create_file('test.py')
        self._import_and_verify(path)

    def test_python_directory(self):
        self._create_file('__init__.py')
        self._import_and_verify(TESTDIR + os.sep)

    def test_import_different_file_with_same_name(self):
        path1 = self._create_file('test.py', attr=1)
        self._import_and_verify(path1, attr=1)
        path2 = join(TESTDIR, 'test')
        os.mkdir(path2)
        self._create_file(join(path2, '__init__.py'), attr=2)
        self._import_and_verify(path2 + '/', attr=2, directory=path2)
        path3 = self._create_file(join(path2, 'test.py'), attr=3)
        self._import_and_verify(path3, attr=3, directory=path2)

    def test_import_class_from_file(self):
        path = self._create_file('test.py', extra_content='class test:\n def m(s): return 1')
        klass = Importer().import_module_by_path(path)
        assert_true(inspect.isclass(klass))
        assert_equals(klass.__name__, 'test')
        assert_equals(klass().m(), 1)

    def test_invalid_python_file(self):
        path = self._create_file('test.py', extra_content='invalid content')
        error = assert_raises(DataError, self._import_and_verify, path)
        assert_prefix(error, "Importing '%s' failed: SyntaxError:" % path)

    if sys.platform.startswith('java'):

        def test_java_class(self):
            self._import_and_verify(join(CURDIR, 'ImportByPath.java'))
            self._import_and_verify(join(CURDIR, 'ImportByPath.class'))

        def test_importing_java_package_fails(self):
            path = join(LIBDIR, 'javapkg') + os.sep
            assert_raises_with_msg(DataError,
                                   "Importing '%s' failed: Expected class or "
                                   "module, got <javapackage>." % path,
                                   self._import, path)

    def _create_file(self, name, attr=42, extra_content=''):
        path = join(TESTDIR, name)
        with open(path, 'w') as file:
            file.write('attr = %r\n' % attr)
            file.write('def func():\n  return attr\n')
            file.write(extra_content)
        return path

    def _import_and_verify(self, path, attr=42, directory=TESTDIR):
        module = self._import(path)
        assert_equals(module.attr, attr)
        assert_equals(module.func(), attr)
        if hasattr(module, '__file__'):
            assert_equals(dirname(abspath(module.__file__)), directory)

    def _import(self, path):
        sys_path_before = sys.path[:]
        try:
            return Importer().import_module_by_path(path)
        finally:
            assert_equals(sys.path, sys_path_before)


class TestInvalidImportPath(unittest.TestCase):

    def test_non_existing(self):
        assert_raises_with_msg(DataError,
            "Importing 'non-existing.py' failed: File or directory does not exist.",
            Importer().import_module_by_path, 'non-existing.py')
        assert_raises_with_msg(DataError,
            "Importing test file 'non-existing.py' failed: File or directory does not exist.",
            Importer('test file').import_module_by_path, 'non-existing.py')

    def test_invalid_format(self):
        assert_raises_with_msg(DataError,
            "Importing '%s' failed: Not a valid file or directory to import." % CURDIR,
            Importer().import_module_by_path, CURDIR)
        assert_raises_with_msg(DataError,
            "Importing xxx '%s' failed: Not a valid file or directory to import." % CURDIR,
            Importer('xxx').import_module_by_path, CURDIR)


class TestImportClassOrModule(unittest.TestCase):

    def test_import_module_file(self):
        module = self._import_module('classes')
        assert_equals(module.__version__, 'N/A')

    def test_import_module_directory(self):
        module = self._import_module('pythonmodule')
        assert_equals(module.some_string, 'Hello, World!')

    def test_import_non_existing(self):
        error = assert_raises(DataError, self._import, 'NonExisting')
        assert_prefix(error, "Importing 'NonExisting' failed: ImportError:")

    def test_import_sub_module(self):
        module = self._import_module('pythonmodule.library')
        assert_equals(module.keyword_from_submodule('Kitty'), 'Hello, Kitty!')
        module = self._import_module('pythonmodule.submodule')
        assert_equals(module.attribute, 42)
        module = self._import_module('pythonmodule.submodule.sublib')
        assert_equals(module.keyword_from_deeper_submodule(), 'hi again')

    def test_import_class_with_same_name_as_module(self):
        klass = self._import_class('ExampleLibrary')
        assert_equals(klass().return_string_from_library('xxx'), 'xxx')

    def test_import_class_from_module(self):
        klass = self._import_class('ExampleLibrary.ExampleLibrary')
        assert_equals(klass().return_string_from_library('yyy'), 'yyy')

    def test_import_class_from_sub_module(self):
        klass = self._import_class('pythonmodule.submodule.sublib.Sub')
        assert_equals(klass().keyword_from_class_in_deeper_submodule(), 'bye')

    def test_import_non_existing_item_from_existing_module(self):
        assert_raises_with_msg(DataError,
                               "Importing 'pythonmodule.NonExisting' failed: "
                               "Module 'pythonmodule' does not contain 'NonExisting'.",
                               self._import, 'pythonmodule.NonExisting')
        assert_raises_with_msg(DataError,
                               "Importing test library 'pythonmodule.none' failed: "
                               "Module 'pythonmodule' does not contain 'none'.",
                               self._import, 'pythonmodule.none', 'test library')

    def test_invalid_item_from_existing_module(self):
        assert_raises_with_msg(DataError,
                               "Importing 'pythonmodule.some_string' failed: "
                               "Expected class or module, got <str>.",
                               self._import, 'pythonmodule.some_string')
        assert_raises_with_msg(DataError,
                               "Importing xxx 'pythonmodule.submodule.attribute' failed: "
                               "Expected class or module, got <int>.",
                               self._import, 'pythonmodule.submodule.attribute', 'xxx')

    def test_item_from_non_existing_module(self):
        error = assert_raises(DataError, self._import, 'nonex.item')
        assert_prefix(error, "Importing 'nonex.item' failed: ImportError:")

    def test_import_file_by_path(self):
        import bytelib as expected
        module = self._import_module(join(LIBDIR, 'bytelib.py'))
        assert_equals(module.__name__, expected.__name__)
        assert_equals(normpath(module.__file__), normpath(expected.__file__))
        assert_equals(dir(module), dir(expected))

    def test_import_class_from_file_by_path(self):
        klass = self._import_class(join(LIBDIR, 'ExampleLibrary.py'))
        assert_equals(klass().return_string_from_library('test'), 'test')

    def test_invalid_file_by_path(self):
        path = join(TEMPDIR, 'robot_import_invalid_test_file.py')
        try:
            with open(path, 'w') as file:
                file.write('invalid content')
            error = assert_raises(DataError, self._import, path)
            assert_prefix(error, "Importing '%s' failed: SyntaxError:" % path)
        finally:
            os.remove(path)

    if sys.platform.startswith('java'):

        def test_import_java_class(self):
            klass = self._import_class('ExampleJavaLibrary', has_source=False)
            assert_equals(klass().getCount(), 1)

        def test_import_java_class_in_package(self):
            klass = self._import_class('javapkg.JavaPackageExample', has_source=False)
            assert_equals(klass().returnValue('xmas'), 'xmas')

        def test_import_java_file_by_path(self):
            import ExampleJavaLibrary as expected
            klass = self._import_class(join(LIBDIR, 'ExampleJavaLibrary.java'))
            assert_equals(klass().getCount(), 1)
            assert_equals(klass.__name__, expected.__name__)
            assert_equals(dir(klass), dir(expected))

        def test_importing_java_package_fails(self):
            assert_raises_with_msg(DataError,
                                   "Importing test library 'javapkg' failed: "
                                   "Expected class or module, got <javapackage>.",
                                   self._import, 'javapkg', 'test library')

    def _import_module(self, name, type=None, has_source=True):
        module = self._import(name, type, has_source)
        assert_true(inspect.ismodule(module))
        return module

    def _import_class(self, name, type=None, has_source=True):
        klass = self._import(name, type, has_source)
        assert_true(inspect.isclass(klass))
        return klass

    def _import(self, name, type=None, has_source=True):
        item, source = Importer(type).import_class_or_module(name)
        if has_source:
            assert_true(isabs(source))
        else:
            assert_true(source is None)
        return item


if __name__ == '__main__':
    unittest.main()
