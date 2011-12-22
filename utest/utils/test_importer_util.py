from __future__ import with_statement
import unittest
import tempfile
import shutil
import sys
import os
from os.path import abspath, dirname, exists, join

from robot.errors import DataError
from robot.utils.importing import Importer
from robot.utils.asserts import assert_equals, assert_raises, assert_raises_with_msg


CURDIR = dirname(abspath(__file__))
TEMPDIR = tempfile.gettempdir()
TESTDIR = join(TEMPDIR, 'robot-importer-testing')


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

    def test_invalid_python_file(self):
        path = self._create_file('test.py', extra_content='invalid content')
        err = assert_raises(DataError, self._import_and_verify, path)
        prefix = ':'.join(unicode(err).split(':')[:2])
        assert_equals(prefix, "Importing '%s' failed: SyntaxError" % path)

    if sys.platform.startswith('java'):

        def test_java_class(self):
            self._import_and_verify(join(CURDIR, 'ImportByPath.java'))
            self._import_and_verify(join(CURDIR, 'ImportByPath.class'))

        def test_invalid_java_class(self):
            path = join(CURDIR, 'ImportByPathInvalid.java')
            err = assert_raises(DataError, self._import_and_verify, path)
            prefix = ':'.join(unicode(err).split(':')[:2])
            assert_equals(prefix, "Importing '%s' failed: TypeError" % path)

    def _create_file(self, name, attr=42, extra_content=''):
        path = join(TESTDIR, name)
        with open(path, 'w') as file:
            file.write('attr = %r\n' % attr)
            file.write('def func():\n  return attr\n')
            file.write(extra_content)
        return path

    def _import_and_verify(self, path, attr=42, directory=TESTDIR):
        sys_path_before = sys.path[:]
        try:
            module = Importer().import_module_by_path(path)
        finally:
            assert_equals(sys.path, sys_path_before)
        assert_equals(module.attr, attr)
        assert_equals(module.func(), attr)
        if hasattr(module, '__file__'):
            assert_equals(dirname(abspath(module.__file__)), directory)


class TestInvalidImportPath(unittest.TestCase):

    def test_non_existing(self):
        assert_raises_with_msg(
            DataError,
            "Importing 'non-existing.py' failed: File or directory does not exist.",
            Importer().import_module_by_path, 'non-existing.py'
        )
        assert_raises_with_msg(
            DataError,
            "Importing test file 'non-existing.py' failed: File or directory does not exist.",
            Importer('test file').import_module_by_path, 'non-existing.py'
        )

    def test_invalid_format(self):
        assert_raises_with_msg(
            DataError,
            "Importing '%s' failed: Not a valid file or directory to import." % CURDIR,
            Importer().import_module_by_path, CURDIR
        )
        assert_raises_with_msg(
            DataError,
            "Importing xxx '%s' failed: Not a valid file or directory to import." % CURDIR,
            Importer('xxx').import_module_by_path, CURDIR
        )


if __name__ == '__main__':
    unittest.main()
