import unittest
import tempfile
import inspect
import shutil
import sys
import os
import re
from os.path import basename, dirname, exists, join, normpath

from robot.errors import DataError
from robot.utils import abspath, JYTHON, WINDOWS, PY3, unicode
from robot.utils.importer import Importer, ByPathImporter
from robot.utils.asserts import (assert_equal, assert_true, assert_raises,
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
    if 'ImportError:' in expected and sys.version_info >= (3, 6):
        expected = expected.replace('ImportError:', 'ModuleNotFoundError:')
    assert_equal(prefix, expected)


def create_temp_file(name, attr=42, extra_content=''):
    if not exists(TESTDIR):
        os.mkdir(TESTDIR)
    path = join(TESTDIR, name)
    with open(path, 'w') as file:
        file.write('''
attr = %r
def func():
    return attr
''' % attr)
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
        self.messages.append(self._normalize_drive_letter(msg))

    def assert_message(self, msg, index=0):
        assert_equal(self.messages[index], self._normalize_drive_letter(msg))

    def _normalize_drive_letter(self, msg):
        if not WINDOWS:
            return msg
        return re.sub("'\\w:", lambda match: match.group().upper(), msg)


class TestImportByPath(unittest.TestCase):

    def setUp(self):
        self.tearDown()

    def tearDown(self):
        if exists(TESTDIR):
            shutil.rmtree(TESTDIR)

    def test_python_file(self):
        path = create_temp_file('test.py')
        self._import_and_verify(path, remove='test')
        self._assert_imported_message('test', path)

    def test_python_directory(self):
        create_temp_file('__init__.py')
        module_name = basename(TESTDIR)
        self._import_and_verify(TESTDIR, remove=module_name)
        self._assert_imported_message(module_name, TESTDIR)

    def test_import_same_file_multiple_times(self):
        path = create_temp_file('test.py')
        self._import_and_verify(path, remove='test')
        self._assert_imported_message('test', path)
        self._import_and_verify(path)
        self._assert_imported_message('test', path)
        self._import_and_verify(path, name='library')
        self._assert_imported_message('test', path, type='library module')

    def test_import_different_file_and_directory_with_same_name(self):
        path1 = create_temp_file('test.py', attr=1)
        self._import_and_verify(path1, attr=1, remove='test')
        self._assert_imported_message('test', path1)
        path2 = join(TESTDIR, 'test')
        os.mkdir(path2)
        create_temp_file(join(path2, '__init__.py'), attr=2)
        self._import_and_verify(path2, attr=2, directory=path2)
        self._assert_removed_message('test')
        self._assert_imported_message('test', path2, index=1)
        path3 = create_temp_file(join(path2, 'test.py'), attr=3)
        self._import_and_verify(path3, attr=3, directory=path2)
        self._assert_removed_message('test')
        self._assert_imported_message('test', path3, index=1)

    def test_import_class_from_file(self):
        path = create_temp_file('test.py', extra_content='''
class test:
    def method(self):
        return 42
''')
        klass = self._import(path, remove='test')
        self._assert_imported_message('test', path, type='class')
        assert_true(inspect.isclass(klass))
        assert_equal(klass.__name__, 'test')
        assert_equal(klass().method(), 42)

    def test_invalid_python_file(self):
        path = create_temp_file('test.py', extra_content='invalid content')
        error = assert_raises(DataError, self._import_and_verify, path, remove='test')
        assert_prefix(error, "Importing '%s' failed: SyntaxError:" % path)

    if JYTHON:

        def test_java_class_with_java_extension(self):
            path = join(CURDIR, 'ImportByPath.java')
            self._import_and_verify(path, remove='ImportByPath')
            self._assert_imported_message('ImportByPath', path, type='class')

        def test_java_class_with_class_extension(self):
            path = join(CURDIR, 'ImportByPath.class')
            self._import_and_verify(path, remove='ImportByPath', name='java')
            self._assert_imported_message('ImportByPath', path, type='java class')

        def test_importing_java_package_fails(self):
            path = join(LIBDIR, 'javapkg')
            assert_raises_with_msg(DataError,
                                   "Importing '%s' failed: Expected class or "
                                   "module, got javapackage." % path,
                                   self._import, path, remove='javapkg')

        def test_removing_from_sys_modules_when_importing_multiple_times(self):
            path = join(CURDIR, 'ImportByPath.java')
            self._import(path, name='java', remove='ImportByPath')
            self._assert_imported_message('ImportByPath', path, 'java class')
            self._import(path)
            self._assert_removed_message('ImportByPath')
            self._assert_imported_message('ImportByPath', path, 'class', index=1)

    def _import_and_verify(self, path, attr=42, directory=TESTDIR,
                           name=None, remove=None):
        module = self._import(path, name, remove)
        assert_equal(module.attr, attr)
        assert_equal(module.func(), attr)
        if hasattr(module, '__file__'):
            assert_equal(dirname(abspath(module.__file__)), directory)

    def _import(self, path, name=None, remove=None):
        if remove and remove in sys.modules:
            sys.modules.pop(remove)
        self.logger = LoggerStub()
        importer = Importer(name, self.logger)
        sys_path_before = sys.path[:]
        try:
            return importer.import_class_or_module_by_path(path)
        finally:
            assert_equal(sys.path, sys_path_before)

    def _assert_imported_message(self, name, source, type='module', index=0):
        msg = "Imported %s '%s' from '%s'." % (type, name, source)
        self.logger.assert_message(msg, index=index)

    def _assert_removed_message(self, name, index=0):
        msg = "Removed module '%s' from sys.modules to import fresh module." % name
        self.logger.assert_message(msg, index=index)


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
        path = join(CURDIR, '..', '..', 'README.rst')
        assert_raises_with_msg(DataError,
            "Importing '%s' failed: Not a valid file or directory to import." % path,
            Importer().import_class_or_module_by_path, path)
        assert_raises_with_msg(DataError,
            "Importing xxx '%s' failed: Not a valid file or directory to import." % path,
            Importer('xxx').import_class_or_module_by_path, path)


class TestImportClassOrModule(unittest.TestCase):

    def test_import_module_file(self):
        module = self._import_module('classes')
        assert_equal(module.__version__, 'N/A')

    def test_import_module_directory(self):
        module = self._import_module('pythonmodule')
        assert_equal(module.some_string, 'Hello, World!')

    def test_import_non_existing(self):
        error = assert_raises(DataError, self._import, 'NonExisting')
        assert_prefix(error, "Importing 'NonExisting' failed: ImportError:")

    def test_import_sub_module(self):
        module = self._import_module('pythonmodule.library')
        assert_equal(module.keyword_from_submodule('Kitty'), 'Hello, Kitty!')
        module = self._import_module('pythonmodule.submodule')
        assert_equal(module.attribute, 42)
        module = self._import_module('pythonmodule.submodule.sublib')
        assert_equal(module.keyword_from_deeper_submodule(), 'hi again')

    def test_import_class_with_same_name_as_module(self):
        klass = self._import_class('ExampleLibrary')
        assert_equal(klass().return_string_from_library('xxx'), 'xxx')

    def test_import_class_from_module(self):
        klass = self._import_class('ExampleLibrary.ExampleLibrary')
        assert_equal(klass().return_string_from_library('yyy'), 'yyy')

    def test_import_class_from_sub_module(self):
        klass = self._import_class('pythonmodule.submodule.sublib.Sub')
        assert_equal(klass().keyword_from_class_in_deeper_submodule(), 'bye')

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
                               "Expected class or module, got string.",
                               self._import, 'pythonmodule.some_string')
        assert_raises_with_msg(DataError,
                               "Importing xxx 'pythonmodule.submodule.attribute' failed: "
                               "Expected class or module, got integer.",
                               self._import, 'pythonmodule.submodule.attribute', 'xxx')

    def test_item_from_non_existing_module(self):
        error = assert_raises(DataError, self._import, 'nonex.item')
        assert_prefix(error, "Importing 'nonex.item' failed: ImportError:")

    def test_import_file_by_path(self):
        import module_library as expected
        module = self._import_module(join(LIBDIR, 'module_library.py'))
        assert_equal(module.__name__, expected.__name__)
        assert_equal(dirname(normpath(module.__file__)),
                      dirname(normpath(expected.__file__)))
        assert_equal(dir(module), dir(expected))

    def test_import_class_from_file_by_path(self):
        klass = self._import_class(join(LIBDIR, 'ExampleLibrary.py'))
        assert_equal(klass().return_string_from_library('test'), 'test')

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

    if JYTHON:

        def test_import_java_class(self):
            klass = self._import_class('ExampleJavaLibrary')
            assert_equal(klass().getCount(), 1)

        def test_import_java_class_in_package(self):
            klass = self._import_class('javapkg.JavaPackageExample')
            assert_equal(klass().returnValue('xmas'), 'xmas')

        def test_import_java_file_by_path(self):
            import ExampleJavaLibrary as expected
            klass = self._import_class(join(LIBDIR, 'ExampleJavaLibrary.java'))
            assert_equal(klass().getCount(), 1)
            assert_equal(klass.__name__, expected.__name__)
            assert_equal(dir(klass), dir(expected))

        def test_importing_java_package_fails(self):
            assert_raises_with_msg(DataError,
                                   "Importing test library 'javapkg' failed: "
                                   "Expected class or module, got javapackage.",
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
        return Importer(type, logger or LoggerStub()).import_class_or_module(name)


class TestErrorDetails(unittest.TestCase):

    def test_no_traceback(self):
        error = self._failing_import('NoneExisting')
        assert_equal(self._get_traceback(error),
                      'Traceback (most recent call last):\n  None')

    def test_traceback(self):
        path = create_temp_file('tb.py', extra_content='import nonex')
        try:
            error = self._failing_import(path)
        finally:
            shutil.rmtree(TESTDIR)
        assert_equal(self._get_traceback(error),
                      'Traceback (most recent call last):\n'
                      '  File "%s", line 5, in <module>\n'
                      '    import nonex' % path)

    def test_pythonpath(self):
        error = self._failing_import('NoneExisting')
        lines = self._get_pythonpath(error).splitlines()
        assert_equal(lines[0], 'PYTHONPATH:')
        for line in lines[1:]:
            assert_true(line.startswith('  '))

    def test_non_ascii_bytes_in_pythonpath(self):
        sys.path.append('hyv\xe4')
        try:
            error = self._failing_import('NoneExisting')
        finally:
            sys.path.pop()
        last_line = self._get_pythonpath(error).splitlines()[-1].strip()
        assert_true(last_line.startswith('hyv'))

    if JYTHON:

        def test_classpath(self):
            error = self._failing_import('NoneExisting')
            lines = self._get_classpath(error).splitlines()
            assert_equal(lines[0], 'CLASSPATH:')
            for line in lines[1:]:
                assert_true(line.startswith('  '))

    def test_structure(self):
        error = self._failing_import('NoneExisting')
        quote = "'" if PY3 else ''
        type = 'Import' if sys.version_info < (3, 6) else 'ModuleNotFound'
        message = ("Importing 'NoneExisting' failed: {type}Error: No module "
                   "named {q}NoneExisting{q}".format(q=quote, type=type))
        expected = (message, self._get_traceback(error),
                    self._get_pythonpath(error), self._get_classpath(error))
        assert_equal(unicode(error), '\n'.join(expected).strip())

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


class TestSplitPathToModule(unittest.TestCase):

    def _verify(self, file_name, expected_name):
        path = abspath(file_name)
        actual = ByPathImporter(None)._split_path_to_module(path)
        assert_equal(actual, (dirname(path), expected_name))

    def test_normal_file(self):
        self._verify('hello.py', 'hello')
        self._verify('hello.class', 'hello')
        self._verify('hello.world.java', 'hello.world')

    def test_jython_class_file(self):
        self._verify('hello$py.class', 'hello')
        self._verify('__init__$py.class', '__init__')

    def test_directory(self):
        self._verify('hello', 'hello')
        self._verify('hello'+os.sep, 'hello')


class TestInstantiation(unittest.TestCase):

    def setUp(self):
        self.tearDown()

    def tearDown(self):
        if exists(TESTDIR):
            shutil.rmtree(TESTDIR)

    def test_when_importing_by_name(self):
        from ExampleLibrary import ExampleLibrary
        lib = Importer().import_class_or_module('ExampleLibrary',
                                                instantiate_with_args=())
        assert_true(not inspect.isclass(lib))
        assert_true(isinstance(lib, ExampleLibrary))

    def test_with_arguments(self):
        lib = Importer().import_class_or_module('libswithargs.Mixed', range(5))
        assert_equal(lib.get_args(), (0, 1, '2 3 4'))

    def test_when_importing_by_path(self):
        path = create_temp_file('args.py', extra_content='class args: a=1')
        lib = Importer().import_class_or_module_by_path(path, ())
        assert_true(not inspect.isclass(lib))
        assert_equal(lib.__class__.__name__, 'args')
        assert_equal(lib.a, 1)

    def test_instantiate_failure(self):
        err = assert_raises(DataError, Importer().import_class_or_module,
                            'ExampleLibrary', ['accepts', 'no', 'args'])
        assert_true(unicode(err).startswith("Importing 'ExampleLibrary' failed: "
                                            "Creating instance failed: TypeError:"))

    def test_modules_do_not_take_arguments(self):
        path = create_temp_file('no_args_allowed.py')
        assert_raises_with_msg(DataError,
                               "Importing '%s' failed: Modules do not take arguments." % path,
                               Importer().import_class_or_module_by_path,
                               path, ['invalid'])


if __name__ == '__main__':
    unittest.main()
