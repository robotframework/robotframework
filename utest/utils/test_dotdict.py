import unittest

from robot.utils.asserts import assert_equal, assert_raises
from robot.utils import DotDict


class TestDotDict(unittest.TestCase):

    def setUp(self):
        self.dd = DotDict([('z', 1), (2, 'y'), ('x', 3)])

    def test_get(self):
        assert_equal(self.dd[2], 'y')
        assert_equal(self.dd.x, 3)
        assert_raises(KeyError, self.dd.__getitem__, 'nonex')
        assert_raises(AttributeError, self.dd.__getattr__, 'nonex')

    def test_equality_with_normal_dict(self):
        assert_equal(self.dd, {'z': 1, 2: 'y', 'x': 3})

    def test_set(self):
        self.dd.x = 42
        self.dd.new = 43
        self.dd[2] = 44
        self.dd['n2'] = 45
        assert_equal(self.dd, {'z': 1, 2: 44, 'x': 42, 'new': 43, 'n2': 45})

    def test_del(self):
        del self.dd.x
        del self.dd[2]
        self.dd.pop('z')
        assert_equal(self.dd, {})
        assert_raises(KeyError, self.dd.__delitem__, 'nonex')
        assert_raises(AttributeError, self.dd.__delattr__, 'nonex')

    def test_same_str_and_repr_as_with_normal_dict(self):
        d = {'foo': 'bar', '"\'': '"\'', '\n': '\r', 1: 2, (): {}, True: False}
        assert_equal(str(DotDict(d)), str(d))
        assert_equal(repr(DotDict(d)), repr(d))

    def test_is_ordered(self):
        assert_equal(list(self.dd), ['z', 2, 'x'])
        self.dd.z = 'new value'
        self.dd.a_new_item = 'last'
        self.dd.pop('x')
        assert_equal(self.dd.items(), [('z', 'new value'), (2, 'y'),
                                       ('a_new_item', 'last')])
        self.dd.x = 'last'
        assert_equal(self.dd.items(), [('z', 'new value'), (2, 'y'),
                                       ('a_new_item', 'last'), ('x', 'last')])


if __name__ == '__main__':
    unittest.main()
