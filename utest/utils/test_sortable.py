import unittest

from robot.utils.asserts import assert_true, assert_raises
from robot.utils import Sortable


class MySortable(Sortable):

    def __init__(self, sort_key=NotImplemented):
        self._sort_key = sort_key


class TestSortable(unittest.TestCase):

    def setUp(self):
        self.a = MySortable('a')
        self.a2 = MySortable('a')
        self.b = MySortable('b')

    def test_eq(self):
        assert_true(self.a == self.a2)
        assert_true(not self.a == self.b)
        assert_true(not self.a == 1)

    def test_ne(self):
        assert_true(self.a != self.b)
        assert_true(not self.a != self.a2)
        assert_true(self.a != 1)

    def test_lt(self):
        assert_true(self.a < self.b)
        assert_true(not self.a < self.a2)
        assert_raises(TypeError, lambda: self.a < 1)

    def test_gt(self):
        assert_true(self.b > self.a)
        assert_true(not self.a > self.a2)
        assert_raises(TypeError, lambda: self.a > 1)

    def test_le(self):
        assert_true(self.a <= self.a)
        assert_true(self.a <= self.b)
        assert_true(not self.b <= self.a)
        assert_raises(TypeError, lambda: self.a <= 1)

    def test_ge(self):
        assert_true(self.a >= self.a)
        assert_true(self.b >= self.a)
        assert_true(not self.a >= self.b)
        assert_raises(TypeError, lambda: self.a >= 1)


if __name__ == '__main__':
    unittest.main()
