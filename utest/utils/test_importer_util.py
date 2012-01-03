from __future__ import with_statement
import unittest
import tempfile
import inspect
import shutil
import sys
import os
import re
from os.path import abspath, dirname, exists, isabs, join, normpath

from robot.errors import DataError
from robot.utils.importer import Importer
from robot.utils.asserts import (assert_equals, assert_true, assert_raises,
                                 assert_raises_with_msg)


CURDIR = dirname(abspath(__file__))
LIBDIR = normpath(join(CURDIR, '..', '..', 'atest', 'testresources', 'testlibs'))
TEMPDIR = tempfile.gettempdir()
TESTDIR = join(TEMPDIR, 'robot-importer-testing')
WINDOWS_PATH_IN_ERROR = re.compile(r"'\w:\\")


def assert_prefix(error, expected):
    message = unicode(error)
    count = 3 if WINDOWS_PATH_IN_ERROR.search(message) else 2
    prefix = ':'.join(message.split(':')[:count]) + ':'
    assert_equals(prefix, expected)

def create_temp_file(name, attr=42, extra_content=''):
    if not exists(TESTDIR):
        os.mkdir(TESTDIR)
    path = join(TESTDIR, name)
    with open(path, 'w') as file:
        file.write('attr = %r\n' % attr)
        file.write('def func():\n  return attr\n')
        file.write(extra_content)
    return path

class LoggerStub(object):

    def __init__(self, remove_extension=False):
        self.messages = []
        self.remove_extension = remove_extension

    def info(self, msg):
        if self.remove_extension:
            for ext in '$py.class', '.pyc', '.py':
                msg = msg.replace(ext, '')
        self.messages.append(msg)

    def assert_message(self, msg):
        assert_equals(self.messages, [msg])


class TestImportByPath(unittest.TestCase):

    def setUp(self):
        self.tearDown()

    def tearDown(self):
        if exists(TESTDIR):
            shutil.rmtree(TESTDIR)

    def test_python_file(self):
        path = create_temp_file('test.py')
        self._import_and_verify(path)

    def test_python_directory(self):
        create_temp_file('__init__.py')
        self._import_and_verify(TESTDIR + os.sep)

    def test_import_different_file_and_directory_with_same_name(self):
        path1 = create_temp_file('test.py', attr=1)
        self._import_and_verify(path1, attr=1)
        path2 = join(TESTDIR, 'test')
        os.mkdir(path2)
        create_temp_file(join(path2, '__init__.py'), attr=2)
        self._import_and_verify(path2, attr=2, directory=path2)
        path3 = create_temp_file(join(path2, 'test.py'), attr=3)
        self._import_and_verify(path3, attr=3, directory=path2)

    def test_import_class_from_file(self):
        path = create_temp_file('test.py', extra_content='class test:\n def m(s): return 1')
        klass = Importer().import_class_or_module_by_path(path)
        assert_true(inspect.isclass(klass))
        assert_equals(klass.__name__, 'test')
        assert_equals(klass().m(), 1)

    def test_invalid_python_file(self):
        path = create_temp_file('test.py', extra_content='invalid content')
        error = assert_raises(DataError, self._import_and_verify, path)
        assert_prefix(error, "Importing '%s' failed: SyntaxError:" % path)

    def test_logging_when_importing_module(self):
        path = join(LIBDIR, 'classes.py')
        self._import(path, name='lib')
        self.logger.assert_message("Imported lib module 'classes' from '%s'." % path)

    def test_logging_when_importing_python_class(self):
        path = join(LIBDIR, 'ExampleLibrary.py')
        self._import(path)
        self.logger.assert_message("Imported class 'ExampleLibrary' from '%s'." % path)

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

        def test_logging_when_importing_java_class(self):
            path = join(CURDIR, 'ImportByPath.java')
            self._import(path, name='java')
            self.logger.assert_message("Imported java class 'ImportByPath' from '%s'." % path)

    def _import_and_verify(self, path, attr=42, directory=TESTDIR):
        module = self._import(path)
        assert_equals(module.attr, attr)
        assert_equals(module.func(), attr)
        if hasattr(module, '__file__'):
            assert_equals(dirname(abspath(module.__file__)), directory)

    def _import(self, path, name=None):
        self.logger = LoggerStub()
        importer = Importer(name, self.logger)
        sys_path_before = sys.path[:]
        try:
            return importer.import_class_or_module_by_path(path)
        finally:
            assert_equals(sys.path, sys_path_before)


class TestInvalidImportPath(unittest.TestCase):

    def test_non_existing(self):
        path = 'non-existing.py'
        assert_raises_with_msg(DataError,
            "Importing '%s' failed: File or directory does not exist." % path,
            Importer().import_class_or_module_by_path, path)
        path = abspath(path)
        assert_raises_with_msg(DataError,
            "Importing test file '%s' failed: File or directory does not exist." % path,
            Importer('test file').import_class_or_module_by_path, path)

    def test_non_absolute(self):
        path = os.listdir('.')[0]
        assert_raises_with_msg(DataError,
            "Importing '%s' failed: Import path must be absolute." % path,
            Importer().import_class_or_module_by_path, path)
        assert_raises_with_msg(DataError,
            "Importing file '%s' failed: Import path must be absolute." % path,
            Importer('file').import_class_or_module_by_path, path)

    def test_invalid_format(self):
        path = join(CURDIR, '..', '..', 'README.txt')
        assert_raises_with_msg(DataError,
            "Importing '%s' failed: Not a valid file or directory to import." % path,
            Importer().import_class_or_module_by_path, path)
        assert_raises_with_msg(DataError,
            "Importing xxx '%s' failed: Not a valid file or directory to import." % path,
            Importer('xxx').import_class_or_module_by_path, path)


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
        assert_equals(dirname(normpath(module.__file__)),
                      dirname(normpath(expected.__file__)))
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

    def test_logging_when_importing_module(self):
        logger = LoggerStub(remove_extension=True)
        self._import_module('classes', 'test library', logger)
        logger.assert_message("Imported test library module 'classes' from '%s'."
                              % join(LIBDIR, 'classes'))

    def test_logging_when_importing_python_class(self):
        logger = LoggerStub(remove_extension=True)
        self._import_class('ExampleLibrary', logger=logger)
        logger.assert_message("Imported class 'ExampleLibrary' from '%s'."
                              % join(LIBDIR, 'ExampleLibrary'))

    if sys.platform.startswith('java'):

        def test_import_java_class(self):
            klass = self._import_class('ExampleJavaLibrary')
            assert_equals(klass().getCount(), 1)

        def test_import_java_class_in_package(self):
            klass = self._import_class('javapkg.JavaPackageExample')
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

        def test_logging_when_importing_java_class(self):
            logger = LoggerStub()
            self._import_class('ExampleJavaLibrary', 'java', logger)
            logger.assert_message("Imported java class 'ExampleJavaLibrary' "
                                  "from unknown location.")

    def _import_module(self, name, type=None, logger=None):
        module = self._import(name, type, logger)
        assert_true(inspect.ismodule(module))
        return module

    def _import_class(self, name, type=None, logger=None):
        klass = self._import(name, type, logger)
        assert_true(inspect.isclass(klass))
        return klass

    def _import(self, name, type=None, logger=None):
        return Importer(type, logger).import_class_or_module(name)


class TestErrorDetails(unittest.TestCase):

    def test_no_traceback(self):
        error = self._failing_import('NoneExisting')
        assert_equals(self._get_traceback(error),
                      'Traceback (most recent call last):\n  None')

    def test_traceback(self):
        path = create_temp_file('tb.py', extra_content='import nonex')
        try:
            error = self._failing_import(path)
        finally:
            shutil.rmtree(TESTDIR)
        assert_equals(self._get_traceback(error),
                      'Traceback (most recent call last):\n'
                      '  File "%s", line 4, in <module>\n'
                      '    import nonex' % path)

    def test_pythonpath(self):
        error = self._failing_import('NoneExisting')
        lines = self._get_pythonpath(error).splitlines()
        assert_equals(lines[0], 'PYTHONPATH:')
        for line in lines[1:]:
            assert_true(line.startswith('  '))

    if sys.platform.startswith('java'):

        def test_classpath(self):
            error = self._failing_import('NoneExisting')
            lines = self._get_classpath(error).splitlines()
            assert_equals(lines[0], 'CLASSPATH:')
            for line in lines[1:]:
                assert_true(line.startswith('  '))

    def test_structure(self):
        error = self._failing_import('NoneExisting')
        message = "Importing 'NoneExisting' failed: ImportError: No module named NoneExisting"
        expected = (message, self._get_traceback(error),
                    self._get_pythonpath(error), self._get_classpath(error))
        assert_equals(unicode(error), '\n'.join(expected).strip())

    def _failing_import(self, name):
        importer = Importer().import_class_or_module
        return assert_raises(DataError, importer, name)

    def _get_traceback(self, error):
        return '\n'.join(self._block(error, 'Traceback (most recent call last):',
                                     'PYTHONPATH:'))

    def _get_pythonpath(self, error):
        return '\n'.join(self._block(error, 'PYTHONPATH:', 'CLASSPATH:'))

    def _get_classpath(self, error):
        return '\n'.join(self._block(error, 'CLASSPATH:'))

    def _block(self, error, start, end=None):
        include = False
        for line in unicode(error).splitlines():
            if line == end:
                return
            if line == start:
                include = True
            if include:
                yield line


if __name__ == '__main__':
    unittest.main()
