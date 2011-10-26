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

    def test_references_are_cleared(self):
        e = Example()
        f = Example()
        self._assert_references({})
        e.attr = 1
        f.attr = 2
        self._assert_references({e: 2, f: 4})
        e.attr = 3
        del f
        self._assert_references({e: 6})
        del e
        self._assert_references({})

    def _assert_references(self, expected):
        assert_equal(dict(Example.attr.values), expected)


if __name__ == '__main__':
    unittest.main()
