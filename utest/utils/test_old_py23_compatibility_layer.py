import unittest

from robot.utils.asserts import assert_equal, assert_false, assert_true
from robot.utils import (PY2, PY3, JYTHON, IRONPYTHON, py2to3, py3to2,
                         is_unicode, unicode, unic)


class TestCompatibilityLayer(unittest.TestCase):

    def test_constants(self):
        assert_true(PY3 is True)
        for not_supported in PY2, JYTHON, IRONPYTHON:
            assert_true(not_supported is False)

    def test_py2to3(self):
        @py2to3
        class X:
            def __unicode__(self):
                return 'Hyvä!'
            def __nonzero__(self):
                return False

        assert_false(X())
        assert_equal(str(X()), 'Hyvä!')

    def test_py3to2(self):
        @py3to2
        class X:
            def __str__(self):
                return 'Hyvä!'
            def __bool__(self):
                return False

        assert_false(X())
        assert_equal(str(X()), 'Hyvä!')

    def test_is_unicode(self):
        assert_true(is_unicode('Hyvä'))
        assert_true(is_unicode('Paha'))
        assert_false(is_unicode(b'xxx'))
        assert_false(is_unicode(42))

    def test_unicode(self):
        assert_true(unicode is str)

    def test_unic(self):
        assert_equal(unic('Hyvä'), 'Hyvä')
        assert_equal(unic('Paha'), 'Paha')
        assert_equal(unic(42), '42')
        assert_equal(unic(b'Hyv\xe4'), r'Hyv\xe4')
        assert_equal(unic(b'Paha'), 'Paha')


if __name__ == '__main__':
    unittest.main()
