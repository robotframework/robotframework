import unittest
import warnings
from contextlib import contextmanager
from pathlib import Path
from xml.etree import ElementTree as ET

from robot.utils.asserts import assert_equal, assert_false, assert_raises, assert_true
from robot import utils


class TestDeprecations(unittest.TestCase):

    @contextmanager
    def validate_deprecation(self, name):
        with warnings.catch_warnings(record=True) as w:
            yield
        assert_equal(str(w[0].message),
                     f"'robot.utils.{name}' is deprecated and will be removed "
                     f"in Robot Framework 9.0.")
        assert_equal(w[0].category, DeprecationWarning)

    def test_constants(self):
        with self.validate_deprecation('PY3'):
            assert_true(utils.PY3 is True)
        with self.validate_deprecation('PY2'):
            assert_true(utils.PY2 is False)
        with self.validate_deprecation('JYTHON'):
            assert_true(utils.JYTHON is False)
        with self.validate_deprecation('IRONPYTHON'):
            assert_true(utils.IRONPYTHON is False)

    def test_py2_under_platform(self):
        # https://github.com/robotframework/SSHLibrary/issues/401
        with self.validate_deprecation('platform.PY2'):
            assert_true(utils.platform.PY2 is False)

    def test_py2to3(self):
        with self.validate_deprecation('py2to3'):
            @utils.py2to3
            class X:
                def __unicode__(self):
                    return 'Hyvä!'
                def __nonzero__(self):
                    return False

        assert_false(X())
        assert_equal(str(X()), 'Hyvä!')

    def test_py3to2(self):
        with self.validate_deprecation('py3to2'):
            @utils.py3to2
            class X:
                def __str__(self):
                    return 'Hyvä!'
                def __bool__(self):
                    return False

        assert_false(X())
        assert_equal(str(X()), 'Hyvä!')

    def test_is_string_unicode(self):
        with self.validate_deprecation('is_string'):
            is_string = utils.is_string
        with self.validate_deprecation('is_unicode'):
            is_unicode = utils.is_unicode
        for meth in is_string, is_unicode:
            assert_true(meth('Hyvä'))
            assert_true(meth('Paha'))
            assert_false(meth(b'xxx'))
            assert_false(meth(42))

    def test_is_bytes(self):
        with self.validate_deprecation('is_bytes'):
            assert_true(utils.is_bytes(b'xxx'))
        with self.validate_deprecation('is_bytes'):
            assert_true(utils.is_bytes(bytearray()))
        with self.validate_deprecation('is_bytes'):
            assert_false(utils.is_bytes('xxx'))

    def test_is_number(self):
        with self.validate_deprecation('is_number'):
            assert_true(utils.is_number(1))
        with self.validate_deprecation('is_number'):
            assert_true(utils.is_number(1.2))
        with self.validate_deprecation('is_number'):
            assert_false(utils.is_number('xxx'))

    def test_is_integer(self):
        with self.validate_deprecation('is_integer'):
            assert_true(utils.is_integer(1))
        with self.validate_deprecation('is_integer'):
            assert_false(utils.is_integer(1.2))
        with self.validate_deprecation('is_integer'):
            assert_false(utils.is_integer('xxx'))

    def test_is_pathlike(self):
        with self.validate_deprecation('is_pathlike'):
            assert_true(utils.is_pathlike(Path('xxx')))
        with self.validate_deprecation('is_pathlike'):
            assert_false(utils.is_pathlike('xxx'))

    def test_roundup(self):
        with self.validate_deprecation('roundup'):
            assert_true(utils.roundup is round)

    def test_unicode(self):
        with self.validate_deprecation('unicode'):
            assert_true(utils.unicode is str)

    def test_unic(self):
        with self.validate_deprecation('unic'):
            assert_equal(utils.unic('Hyvä'), 'Hyvä')
        with self.validate_deprecation('unic'):
            assert_equal(utils.unic('Paha'), 'Paha')
        with self.validate_deprecation('unic'):
            assert_equal(utils.unic(42), '42')
        with self.validate_deprecation('unic'):
            assert_equal(utils.unic(b'Hyv\xe4'), 'Hyvä')
        with self.validate_deprecation('unic'):
            assert_equal(utils.unic(b'Paha'), 'Paha')

    def test_stringio(self):
        import io
        with self.validate_deprecation('StringIO'):
            assert_true(utils.StringIO is io.StringIO)

    def test_ET(self):
        with self.validate_deprecation('ET'):
            assert_true(utils.ET is ET)

    def test_non_existing_attribute(self):
        assert_raises(AttributeError, getattr, utils, 'xxx')


if __name__ == '__main__':
    unittest.main()
