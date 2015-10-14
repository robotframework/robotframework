import unittest

from robot.utils import long
from robot.utils.asserts import *


AE = AssertionError


class MyExc(Exception):
    pass


class MyEqual(object):
    def __init__(self, attr=None):
        self.attr = attr
    def __eq__(self, obj):
        try:
            return self.attr == obj.attr
        except AttributeError:
            return False
    def __str__(self):
        return str(self.attr)
    __repr__ = __str__


def func(msg=None):
    if msg is not None:
        raise ValueError(msg)


class TestAsserts(unittest.TestCase):

    def test_fail_unless_raises(self):
        assert_raises(ValueError, int, 'not int')
        self.assertRaises(ValueError, fail_unless_raises, MyExc, int, 'not int')
        self.assertRaises(AssertionError, assert_raises, ValueError, int, '1')

    def test_fail_unless_raises_with_msg(self):
        fail_unless_raises_with_msg(ValueError, 'msg', func, 'msg')
        self.assertRaises(ValueError, assert_raises_with_msg, TypeError, 'msg',
                          func, 'msg')
        try:
            assert_raises_with_msg(ValueError, 'msg', func)
            error('No AssertionError raised')
        except AE as err:
            assert_equal(str(err), 'ValueError not raised')
        try:
            assert_raises_with_msg(ValueError, 'msg1', func, 'msg2')
            error('No AssertionError raised')
        except AE as err:
            expected = "Correct exception but wrong message: msg1 != msg2"
            assert_equal(str(err), expected)

    def test_fail_unless_equal(self):
        fail_unless_equal('str', 'str')
        fail_unless_equal(42, 42, 'hello', True)
        assert_equal(MyEqual('hello'), MyEqual('hello'))
        assert_equals(None, None)
        assert_raises(AE, fail_unless_equal, 'str', 'STR')
        assert_raises(AE, fail_unless_equal, 42, 43)
        assert_raises(AE, assert_equal, MyEqual('hello'), MyEqual('world'))
        assert_raises(AE, assert_equals, None, True)

    def test_fail_unless_equal_with_values_having_same_string_repr(self):
        for val, type_ in [(1, 'integer'),
                           (long(1), 'integer'),
                           (MyEqual(1), 'MyEqual')]:
            assert_raises_with_msg(AE, '1 (string) != 1 (%s)' % type_,
                                   fail_unless_equal, '1', val)
        assert_raises_with_msg(AE, '1.0 (float) != 1.0 (string)',
                               fail_unless_equal, 1.0, u'1.0')
        assert_raises_with_msg(AE, 'True (string) != True (boolean)',
                               fail_unless_equal, 'True', True)

    def test_fail_if_equal(self):
        fail_if_equal('abc', 'ABC')
        fail_if_equal(42, -42, 'hello', True)
        assert_not_equal(MyEqual('cat'), MyEqual('dog'))
        assert_not_equals(None, True)
        raise_msg = assert_raises_with_msg  # shorter to use here
        raise_msg(AE, "str == str", fail_if_equal, 'str', 'str')
        raise_msg(AE, "hello: 42 == 42", fail_if_equal, 42, 42, 'hello')
        raise_msg(AE, "hello", fail_if_equal, MyEqual('cat'), MyEqual('cat'),
                  'hello', False)

    def test_fail(self):
        assert_raises(AE, fail)
        assert_raises_with_msg(AE, 'hello', fail, 'hello')

    def test_error(self):
        assert_raises(Exception, error)
        assert_raises_with_msg(Exception, 'hello', error, 'hello')

    def test_fail_unless(self):
        fail_unless(True)
        assert_true('non-empty string is true')
        assert_(-1 < 0 < 1, 'my message')
        assert_raises(AE, fail_unless, False)
        assert_raises(AE, assert_true, '')
        assert_raises_with_msg(AE, 'message', assert_, 1 < 0, 'message')

    def test_fail_if(self):
        fail_if(False)
        assert_false('')
        assert_false([1,2] == (1,2), 'my message')
        assert_raises(AE, fail_if, True)
        assert_raises(AE, assert_false, 'non-empty')
        assert_raises_with_msg(AE, 'message', assert_false, 0 < 1, 'message')

    def test_fail_unless_none(self):
        fail_unless_none(None)
        assert_raises_with_msg(AE, "message: 'Not None' is not None",
                               assert_none, 'Not None', 'message')
        assert_raises_with_msg(AE, "message",
                               assert_none, 'Not None', 'message', False)

    def test_if_none(self):
        fail_if_none('Not None')
        assert_raises_with_msg(AE, "message: is None",
                               assert_not_none, None, 'message')
        assert_raises_with_msg(AE, "message",
                               assert_not_none, None, 'message', False)

    def test_fail_unless_almost_equal(self):
        fail_unless_almost_equal(1.0, 1.00000001)
        assert_almost_equal(10, 10.01, 1)
        assert_raises_with_msg(AE, 'hello: 1 != 2 within 3 places',
                               assert_almost_equals, 1, 2, 3, 'hello')
        assert_raises_with_msg(AE, 'hello',
                               assert_almost_equals, 1, 2, 3, 'hello', False)

    def test_fail_if_almost_equal(self):
        fail_if_almost_equal(1.0, 1.00000001, 10)
        assert_not_almost_equal(10, 11, 1, 'hello')
        assert_raises_with_msg(AE, 'hello: 1 == 1 within 7 places',
                               assert_not_almost_equals, 1, 1, msg='hello')
        assert_raises_with_msg(AE, 'hi',
                               assert_not_almost_equals, 1, 1.1, 0, 'hi', False)


if __name__ == '__main__':
    unittest.main()
