import unittest

from robot.utils.asserts import (assert_almost_equal, assert_equal,
                                 assert_false, assert_none,
                                 assert_not_almost_equal, assert_not_equal,
                                 assert_not_none, assert_raises,
                                 assert_raises_with_msg, assert_true, fail)


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

    def test_assert_raises(self):
        assert_raises(ValueError, int, 'not int')
        self.assertRaises(ValueError, assert_raises, MyExc, int, 'not int')
        self.assertRaises(AssertionError, assert_raises, ValueError, int, '1')

    def test_assert_raises_with_msg(self):
        assert_raises_with_msg(ValueError, 'msg', func, 'msg')
        self.assertRaises(ValueError, assert_raises_with_msg, TypeError, 'msg',
                          func, 'msg')
        try:
            assert_raises_with_msg(ValueError, 'msg', func)
        except AE as err:
            assert_equal(str(err), 'ValueError not raised')
        else:
            raise AssertionError('No AssertionError raised')
        try:
            assert_raises_with_msg(ValueError, 'msg1', func, 'msg2')
        except AE as err:
            expected = "Correct exception but wrong message: msg1 != msg2"
            assert_equal(str(err), expected)
        else:
            raise AssertionError('No AssertionError raised')

    def test_assert_equal(self):
        assert_equal('str', 'str')
        assert_equal(42, 42, 'hello', True)
        assert_equal(MyEqual('hello'), MyEqual('hello'))
        assert_equal(None, None)
        assert_raises(AE, assert_equal, 'str', 'STR')
        assert_raises(AE, assert_equal, 42, 43)
        assert_raises(AE, assert_equal, MyEqual('hello'), MyEqual('world'))
        assert_raises(AE, assert_equal, None, True)

    def test_assert_equal_with_values_having_same_string_repr(self):
        for val, type_ in [(1, 'integer'),
                           (MyEqual(1), 'MyEqual')]:
            assert_raises_with_msg(AE, '1 (string) != 1 (%s)' % type_,
                                   assert_equal, '1', val)
        assert_raises_with_msg(AE, '1.0 (float) != 1.0 (string)',
                               assert_equal, 1.0, '1.0')
        assert_raises_with_msg(AE, 'True (string) != True (boolean)',
                               assert_equal, 'True', True)

    def test_assert_equal_with_custom_formatter(self):
        assert_equal('hyv\xe4', 'hyv\xe4', formatter=repr)
        assert_raises_with_msg(AE, "'hyv\xe4' != 'paha'",
                               assert_equal, 'hyv\xe4', 'paha', formatter=repr)
        assert_raises_with_msg(AE, "'hyv\\xe4' != 'paha'",
                               assert_equal, 'hyv\xe4', 'paha', formatter=ascii)

    def test_assert_not_equal(self):
        assert_not_equal('abc', 'ABC')
        assert_not_equal(42, -42, 'hello', True)
        assert_not_equal(MyEqual('cat'), MyEqual('dog'))
        assert_not_equal(None, True)
        raise_msg = assert_raises_with_msg  # shorter to use here
        raise_msg(AE, "str == str", assert_not_equal, 'str', 'str')
        raise_msg(AE, "hello: 42 == 42", assert_not_equal, 42, 42, 'hello')
        raise_msg(AE, "hello", assert_not_equal, MyEqual('cat'), MyEqual('cat'),
                  'hello', False)

    def test_assert_not_equal_with_custom_formatter(self):
        assert_not_equal('hyv\xe4', 'paha', formatter=repr)
        assert_raises_with_msg(AE, "'\xe4' == '\xe4'",
                               assert_not_equal, '\xe4', '\xe4', formatter=repr)

    def test_fail(self):
        assert_raises(AE, fail)
        assert_raises_with_msg(AE, 'hello', fail, 'hello')

    def test_assert_true(self):
        assert_true(True)
        assert_true('non-empty string is true')
        assert_true(-1 < 0 < 1, 'my message')
        assert_raises(AE, assert_true, False)
        assert_raises(AE, assert_true, '')
        assert_raises_with_msg(AE, 'message', assert_true, 1 < 0, 'message')

    def test_assert_false(self):
        assert_false(False)
        assert_false('')
        assert_false([1,2] == (1,2), 'my message')
        assert_raises(AE, assert_false, True)
        assert_raises(AE, assert_false, 'non-empty')
        assert_raises_with_msg(AE, 'message', assert_false, 0 < 1, 'message')

    def test_assert_none(self):
        assert_none(None)
        assert_raises_with_msg(AE, "message: 'Not None' is not None",
                               assert_none, 'Not None', 'message')
        assert_raises_with_msg(AE, "message",
                               assert_none, 'Not None', 'message', False)

    def test_assert_not_none(self):
        assert_not_none('Not None')
        assert_raises_with_msg(AE, "message: is None",
                               assert_not_none, None, 'message')
        assert_raises_with_msg(AE, "message",
                               assert_not_none, None, 'message', False)

    def test_assert_almost_equal(self):
        assert_almost_equal(1.0, 1.00000001)
        assert_almost_equal(10, 10.01, 1)
        assert_raises_with_msg(AE, 'hello: 1 != 2 within 3 places',
                               assert_almost_equal, 1, 2, 3, 'hello')
        assert_raises_with_msg(AE, 'hello',
                               assert_almost_equal, 1, 2, 3, 'hello', False)

    def test_assert_not_almost_equal(self):
        assert_not_almost_equal(1.0, 1.00000001, 10)
        assert_not_almost_equal(10, 11, 1, 'hello')
        assert_raises_with_msg(AE, 'hello: 1 == 1 within 7 places',
                               assert_not_almost_equal, 1, 1, msg='hello')
        assert_raises_with_msg(AE, 'hi',
                               assert_not_almost_equal, 1, 1.1, 0, 'hi', False)


if __name__ == '__main__':
    unittest.main()
