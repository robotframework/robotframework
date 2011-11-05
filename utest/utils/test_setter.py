import unittest
from robot.utils.asserts import assert_equal, assert_raises

from robot.utils import setter


class Example(object):
    @setter
    def attr(self, value):
        return value * 2


class TestSetter(unittest.TestCase):

    def test_setting(self):
        e = Example()
        e.attr = 1
        assert_equal(e.attr, 2)

    def test_notset(self):
        assert_raises(AttributeError, getattr, Example(), 'attr')


if __name__ == '__main__':
    unittest.main()
