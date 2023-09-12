import inspect
import os
import re
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

from robot.errors import DataError
from robot.utils import abspath, WINDOWS
from robot.utils.asserts import (assert_equal, assert_raises, assert_raises_with_msg,
                                 assert_true)
from robot.utils.importer import ByPathImporter, Importer


CURDIR = Path(__file__).absolute().parent
LIBDIR = CURDIR.parent.parent / 'atest/testresources/testlibs'
TEMPDIR = Path(tempfile.gettempdir())
TESTDIR = TEMPDIR / 'robot-importer-testing'
WINDOWS_PATH_IN_ERROR = re.compile(r"'\w:\\")


def assert_prefix(error, expected):
    message = str(error)
    count = 3 if WINDOWS_PATH_IN_ERROR.search(message) else 2
    prefix = ':'.join(message.split(':')[:count]) + ':'
    assert_equal(prefix, expected)


def create_temp_file(name, attr=42, extra_content=''):
    TESTDIR.mkdir(exist_ok=True)
    path = TESTDIR / name
    with open(path, 'w') as file:
        file.write(f'''
attr = {attr}
def func():
    return attr
''')
        file.write(extra_content)
    return path


class LoggerStub:

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
        if TESTDIR.exists():
            shutil.rmtree(TESTDIR)

    def test_python_file(self):
        path = create_temp_file('test.py')
        self._import_and_verify(path, remove='test')
        self._assert_imported_message('test', path)

    def test_python_directory(self):
        create_temp_file('__init__.py')
        self._import_and_verify(TESTDIR, remove=TESTDIR.name)
        self._assert_imported_message(TESTDIR.name, TESTDIR)

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
        path2 = TESTDIR / 'test'
        path2.mkdir()
        create_temp_file(path2 / '__init__.py', attr=2)
        self._import_and_verify(path2, attr=2, directory=path2)
        self._assert_removed_message('test')
        self._assert_imported_message('test', path2, index=1)
        path3 = create_temp_file(path2 / 'test.py', attr=3)
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
        assert_prefix(error, f"Importing '{path}' failed: SyntaxError:")

    def _import_and_verify(self, path, attr=42, directory=TESTDIR,
                           name=None, remove=None):
        module = self._import(path, name, remove)
        assert_equal(module.attr, attr)
        assert_equal(module.func(), attr)
        if hasattr(module, '__file__'):
            assert_true(Path(module.__file__).parent.samefile(directory))

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
        msg = f"Imported {type} '{name}' from '{source}'."
        self.logger.assert_message(msg, index=index)

    def _assert_removed_message(self, name, index=0):
        msg = f"Removed module '{name}' from sys.modules to import fresh module."
        self.logger.assert_message(msg, index=index)


class TestInvalidImportPath(unittest.TestCase):

    def test_non_existing(self):
        path = 'non-existing.py'
        assert_raises_with_msg(
            DataError,
            f"Importing '{path}' failed: File or directory does not exist.",
            Importer().import_class_or_module_by_path, path
        )
        path = abspath(path)
        assert_raises_with_msg(
            DataError,
            f"Importing test file '{path}' failed: File or directory does not exist.",
            Importer('test file').import_class_or_module_by_path, path
        )

    def test_non_absolute(self):
        path = os.listdir('.')[0]
        assert_raises_with_msg(
            DataError,
            f"Importing '{path}' failed: Import path must be absolute.",
            Importer().import_class_or_module_by_path, path
        )
        assert_raises_with_msg(
            DataError,
            f"Importing file '{path}' failed: Import path must be absolute.",
            Importer('file').import_class_or_module_by_path, path
        )

    def test_invalid_format(self):
        path = CURDIR / '../../README.rst'
        assert_raises_with_msg(
            DataError,
            f"Importing '{path}' failed: Not a valid file or directory to import.",
            Importer().import_class_or_module_by_path, path
        )
        assert_raises_with_msg(
            DataError,
            f"Importing xxx '{path}' failed: Not a valid file or directory to import.",
            Importer('xxx').import_class_or_module_by_path, path
        )


class TestImportClassOrModule(unittest.TestCase):

    def test_import_module_file(self):
        module = self._import_module('classes')
        assert_equal(module.__version__, 'N/A')

    def test_import_module_directory(self):
        module = self._import_module('pythonmodule')
        assert_equal(module.some_string, 'Hello, World!')

    def test_import_non_existing(self):
        error = assert_raises(DataError, self._import, 'NonExisting')
        assert_prefix(error, "Importing 'NonExisting' failed: ModuleNotFoundError:")

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
        assert_prefix(error, "Importing 'nonex.item' failed: ModuleNotFoundError:")

    def test_import_file_by_path(self):
        import module_library as expected
        module = self._import_module(LIBDIR / 'module_library.py')
        assert_equal(module.__name__, expected.__name__)
        assert_equal(Path(module.__file__).resolve().parent,
                     Path(expected.__file__).resolve().parent)
        assert_equal(dir(module), dir(expected))

    def test_import_class_from_file_by_path(self):
        klass = self._import_class(LIBDIR / 'ExampleLibrary.py')
        assert_equal(klass().return_string_from_library('test'), 'test')

    def test_invalid_file_by_path(self):
        path = TEMPDIR / 'robot_import_invalid_test_file.py'
        try:
            with open(path, 'w') as file:
                file.write('invalid content')
            error = assert_raises(DataError, self._import, path)
            assert_prefix(error, f"Importing '{path}' failed: SyntaxError:")
        finally:
            os.remove(path)

    def test_logging_when_importing_module(self):
        logger = LoggerStub(remove_extension=True)
        self._import_module('classes', 'test library', logger)
        logger.assert_message(f"Imported test library module 'classes' from "
                              f"'{LIBDIR / 'classes'}'.")

    def test_logging_when_importing_python_class(self):
        logger = LoggerStub(remove_extension=True)
        self._import_class('ExampleLibrary', logger=logger)
        logger.assert_message(f"Imported class 'ExampleLibrary' from "
                              f"'{LIBDIR / 'ExampleLibrary'}'.")

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


class TestImportModule(unittest.TestCase):

    def test_import_module(self):
        module = Importer().import_module('ExampleLibrary')
        assert_equal(module.ExampleLibrary().return_string_from_library('xxx'), 'xxx')

    def test_logging(self):
        logger = LoggerStub(remove_extension=True)
        Importer(logger=logger).import_module('ExampleLibrary')
        logger.assert_message(f"Imported module 'ExampleLibrary' from "
                              f"'{LIBDIR / 'ExampleLibrary'}'.")


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
        assert_equal(self._get_traceback(error), f'''\
Traceback (most recent call last):
  File "{path}", line 5, in <module>
    import nonex''')

    def test_pythonpath(self):
        error = self._failing_import('NoneExisting')
        lines = self._get_pythonpath(error).splitlines()
        assert_equal(lines[0], 'PYTHONPATH:')
        for line in lines[1:]:
            assert_true(line.startswith('  '))

    def test_non_ascii_entry_in_pythonpath(self):
        sys.path.append('hyvä')
        try:
            error = self._failing_import('NoneExisting')
        finally:
            sys.path.pop()
        last_line = self._get_pythonpath(error).splitlines()[-1].strip()
        assert_true(last_line.startswith('hyv'))

    def test_structure(self):
        error = self._failing_import('NoneExisting')
        message = ("Importing 'NoneExisting' failed: ModuleNotFoundError: "
                   "No module named 'NoneExisting'")
        expected = (message, self._get_traceback(error), self._get_pythonpath(error))
        assert_equal(str(error), '\n'.join(expected))

    def _failing_import(self, name):
        importer = Importer().import_class_or_module
        return assert_raises(DataError, importer, name)

    def _get_traceback(self, error):
        return '\n'.join(self._block(error, 'Traceback (most recent call last):',
                                     'PYTHONPATH:'))

    def _get_pythonpath(self, error):
        return '\n'.join(self._block(error, 'PYTHONPATH:', 'CLASSPATH:'))

    def _block(self, error, start, end=None):
        include = False
        for line in str(error).splitlines():
            if line == end:
                return
            if line == start:
                include = True
            if include and line.strip('^ '):
                yield line


class TestSplitPathToModule(unittest.TestCase):

    def _verify(self, file_name, expected_name):
        path = Path(file_name).absolute()
        actual = ByPathImporter(None)._split_path_to_module(path)
        assert_equal(actual, (str(path.parent), expected_name))

    def test_normal_file(self):
        self._verify('hello.py', 'hello')
        self._verify('hello.world.pyc', 'hello.world')

    def test_directory(self):
        self._verify('hello', 'hello')
        self._verify('hello'+os.sep, 'hello')


class TestInstantiation(unittest.TestCase):

    def setUp(self):
        self.tearDown()

    def tearDown(self):
        if TESTDIR.exists():
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

    def test_named_arguments(self):
        lib = Importer().import_class_or_module('libswithargs.Mixed',
                                                ['default=b', 'mandatory=a'])
        assert_equal(lib.get_args(), ('a', 'b', ''))

    def test_escape_equals(self):
        lib = Importer().import_class_or_module('libswithargs.Mixed',
                                                [r'default\=b', r'mandatory\=a'])
        assert_equal(lib.get_args(), (r'default\=b', r'mandatory\=a', ''))
        lib = Importer().import_class_or_module('libswithargs.Mixed',
                                                [r'default\=b', 'default=a'])
        assert_equal(lib.get_args(), (r'default\=b', 'a', ''))

    def test_escaping_not_needed_if_args_do_not_match_names(self):
        lib = Importer().import_class_or_module('libswithargs.Mixed',
                                                ['foo=b', 'bar=a'])
        assert_equal(lib.get_args(), ('foo=b', 'bar=a', ''))

    def test_arguments_when_importing_by_path(self):
        path = create_temp_file('args.py', extra_content='''
class args:
    def __init__(self, arg='default'):
        self.arg = arg
''')
        importer = Importer().import_class_or_module_by_path
        for args, expected in [((), 'default'),
                               (['positional'], 'positional'),
                               (['arg=named'], 'named')]:
            lib = importer(path, args)
            assert_true(not inspect.isclass(lib))
            assert_equal(lib.__class__.__name__, 'args')
            assert_equal(lib.arg, expected)

    def test_instantiate_failure(self):
        assert_raises_with_msg(
            DataError,
            "Importing xxx 'ExampleLibrary' failed: Xxx 'ExampleLibrary' expected 0 arguments, got 3.",
            Importer('XXX').import_class_or_module, 'ExampleLibrary', ['accepts', 'no', 'args']
        )

    def test_argument_conversion(self):
        path = create_temp_file('conversion.py', extra_content='''
class conversion:
    def __init__(self, arg: int):
        self.arg = arg
''')
        lib = Importer().import_class_or_module_by_path(path, ['42'])
        assert_true(not inspect.isclass(lib))
        assert_equal(lib.__class__.__name__, 'conversion')
        assert_equal(lib.arg, 42)
        assert_raises_with_msg(
            DataError,
            f"Importing xxx '{path}' failed: "
            f"Argument 'arg' got value 'invalid' that cannot be converted to integer.",
            Importer('XXX').import_class_or_module, path, ['invalid']
        )

    def test_modules_do_not_take_arguments(self):
        path = create_temp_file('no_args_allowed.py')
        assert_raises_with_msg(
            DataError,
            f"Importing '{path}' failed: Modules do not take arguments.",
            Importer().import_class_or_module_by_path, path, ['invalid']
        )


if __name__ == '__main__':
    unittest.main()
