import unittest
from collections import OrderedDict

from robot.utils import DotDict
from robot.utils.asserts import (assert_equal, assert_false, assert_not_equal,
                                 assert_raises, assert_true)


class TestDotDict(unittest.TestCase):

    def setUp(self):
        self.dd = DotDict([('z', 1), (2, 'y'), ('x', 3)])

    def test_init(self):
        assert_true(DotDict() == DotDict({}) == DotDict([]))
        assert_true(DotDict(a=1) == DotDict({'a': 1}) == DotDict([('a', 1)]))
        assert_true(DotDict({'a': 1}, b=2) ==
                    DotDict({'a': 1, 'b': 2}) ==
                    DotDict([('a', 1), ('b', 2)]))
        assert_raises(TypeError, DotDict, None)

    def test_get(self):
        assert_equal(self.dd[2], 'y')
        assert_equal(self.dd.x, 3)
        assert_raises(KeyError, self.dd.__getitem__, 'nonex')
        assert_raises(AttributeError, self.dd.__getattr__, 'nonex')

    def test_equality(self):
        assert_true(self.dd == self.dd)
        assert_false(self.dd != self.dd)
        assert_true(self.dd == DotDict(self.dd))
        assert_false(self.dd != DotDict(self.dd))
        assert_false(self.dd == DotDict())
        assert_true(self.dd != DotDict())

    def test_equality_with_normal_dict(self):
        assert_equal(self.dd, {'z': 1, 2: 'y', 'x': 3})

    def test_hash(self):
        assert_raises(TypeError, hash, self.dd)

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

    def test_same_str_and_repr_format_as_with_normal_dict(self):
        D = {'foo': 'bar', '"\'': '"\'', '\n': '\r', 1: 2, (): {}, True: False}
        for d in {}, {'a': 1}, D:
            for formatter in str, repr:
                result = formatter(DotDict(d))
                assert_equal(eval(result, {}), d)

    def test_is_ordered(self):
        assert_equal(list(self.dd), ['z', 2, 'x'])
        self.dd.z = 'new value'
        self.dd.a_new_item = 'last'
        self.dd.pop('x')
        assert_equal(list(self.dd.items()),
                     [('z', 'new value'), (2, 'y'), ('a_new_item', 'last')])
        self.dd.x = 'last'
        assert_equal(list(self.dd.items()),
                     [('z', 'new value'), (2, 'y'), ('a_new_item', 'last'), ('x', 'last')])

    def test_order_does_not_affect_equality(self):
        d = dict(a=1, b=2, c=3, d=4, e=5, f=6, g=7)
        od1 = OrderedDict(sorted(d.items()))
        od2 = OrderedDict(reversed(list(od1.items())))
        dd1 = DotDict(sorted(d.items()))
        dd2 = DotDict(reversed(list(dd1.items())))
        for d1, d2 in [(dd1, dd2), (dd1, d), (dd2, d), (dd1, od1), (dd2, od2)]:
            assert_equal(d1, d2)
            assert_equal(d2, d1)
        for d1, d2 in [(dd1, od2), (dd2, od1)]:
            assert_equal(d1, d2)
            assert_equal(d2, d1)
        assert_not_equal(od1, od2)


class TestNestedDotDict(unittest.TestCase):

    def test_nested_dicts_are_converted_to_dotdicts_at_init(self):
        leaf = {'key': 'value'}
        d = DotDict({'nested': leaf, 'deeper': {'nesting': leaf}}, nested2=leaf)
        assert_equal(d.nested.key, 'value')
        assert_equal(d.deeper.nesting.key, 'value')
        assert_equal(d.nested2.key, 'value')

    def test_dicts_inside_lists_are_converted(self):
        leaf = {'key': 'value'}
        d = DotDict(list=[leaf, leaf, [leaf]], deeper=[leaf, {'deeper': leaf}])
        assert_equal(d.list[0].key, 'value')
        assert_equal(d.list[1].key, 'value')
        assert_equal(d.list[2][0].key, 'value')
        assert_equal(d.deeper[0].key, 'value')
        assert_equal(d.deeper[1].deeper.key, 'value')

    def test_other_list_like_items_are_not_touched(self):
        value = ({'key': 'value'}, [{}])
        d = DotDict(key=value)
        assert_equal(d.key[0]['key'], 'value')
        assert_false(hasattr(d.key[0], 'key'))
        assert_true(isinstance(d.key[0], dict))
        assert_true(isinstance(d.key[1][0], dict))

    def test_items_inserted_outside_init_are_not_converted(self):
        d = DotDict()
        d['dict'] = {'key': 'value'}
        d['list'] = [{}]
        assert_equal(d.dict['key'], 'value')
        assert_false(hasattr(d.dict, 'key'))
        assert_true(isinstance(d.dict, dict))
        assert_true(isinstance(d.list[0], dict))

    def test_dotdicts_are_not_recreated(self):
        value = DotDict(key=1)
        d = DotDict(key=value)
        assert_true(d.key is value)
        assert_equal(d.key.key, 1)

    def test_lists_are_not_recreated(self):
        value = [{'key': 1}]
        d = DotDict(key=value)
        assert_true(d.key is value)
        assert_equal(d.key[0].key, 1)


if __name__ == '__main__':
    unittest.main()
