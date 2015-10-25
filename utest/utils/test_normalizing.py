import unittest
try:
    from UserDict import UserDict
except ImportError:
    from collections import UserDict

from robot.utils import normalize, NormalizedDict, PY2
from robot.utils.asserts import (assert_equals, assert_true, assert_false,
                                 assert_raises)


class TestNormalizing(unittest.TestCase):

    def test_normalize_with_defaults(self):
        for inp, exp in [('', ''),
                         ('            ', ''),
                         (' \n\t\r', ''),
                         ('foo', 'foo'),
                         ('BAR', 'bar'),
                         (' f o o ', 'foo'),
                         ('_BAR', '_bar'),
                         ('Fo OBar\r\n', 'foobar'),
                         ('foo\tbar', 'foobar'),
                         ('\n \n \n \n F o O \t\tBaR \r \r \r   ', 'foobar')]:
            assert_equals(normalize(inp), exp)

    def test_normalize_with_caseless(self):
        assert_equals(normalize('Fo o BaR', caseless=False), 'FooBaR')
        assert_equals(normalize('Fo O B AR', caseless=True), 'foobar')

    def test_normalize_with_caseless_non_ascii(self):
        assert_equals(normalize(u'\xc4iti', caseless=False), u'\xc4iti')
        for mother in [u'\xc4ITI', u'\xc4iTi', u'\xe4iti', u'\xe4iTi']:
            assert_equals(normalize(mother, caseless=True), u'\xe4iti')

    def test_normalize_with_spaceless(self):
        assert_equals(normalize('Fo o BaR', spaceless=False), 'fo o bar')
        assert_equals(normalize('Fo O B AR', spaceless=True), 'foobar')

    def test_normalize_with_ignore(self):
        assert_equals(normalize('Foo_ bar', ignore=['_']), 'foobar')
        assert_equals(normalize('Foo_ bar', ignore=['_', 'f', 'o']), 'bar')
        assert_equals(normalize('Foo_ bar', ignore=['_', 'F', 'o']), 'bar')
        assert_equals(normalize('Foo_ bar', ignore=['_', 'f', 'o'],
                                caseless=False), 'Fbar')
        assert_equals(normalize('Foo_\n bar\n', ignore=['\n'],
                                spaceless=False), 'foo_ bar')


class TestNormalizedDict(unittest.TestCase):

    def test_default_constructor(self):
        nd = NormalizedDict()
        nd['foo bar'] = 'value'
        assert_equals(nd['foobar'], 'value')
        assert_equals(nd['F  oo\nBar'], 'value')

    def test_initial_values_as_dict(self):
        nd = NormalizedDict({'key': 'value', 'F O\tO': 'bar'})
        assert_equals(nd['key'], 'value')
        assert_equals(nd['K EY'], 'value')
        assert_equals(nd['foo'], 'bar')

    def test_initial_values_as_name_value_pairs(self):
        nd = NormalizedDict([('key', 'value'), ('F O\tO', 'bar')])
        assert_equals(nd['key'], 'value')
        assert_equals(nd['K EY'], 'value')
        assert_equals(nd['foo'], 'bar')

    def test_setdefault(self):
        nd = NormalizedDict({'a': NormalizedDict()})
        nd.setdefault('a', 'whatever').setdefault('B', []).append(1)
        nd.setdefault('A', 'everwhat').setdefault('b', []).append(2)
        assert_equals(nd['a']['b'], [1, 2])
        assert_equals(list(nd), ['a'])
        assert_equals(list(nd['a']), ['B'])

    def test_ignore(self):
        nd = NormalizedDict(ignore=['_'])
        nd['foo_bar'] = 'value'
        assert_equals(nd['foobar'], 'value')
        assert_equals(nd['F  oo\nB   ___a r'], 'value')

    def test_caseless_and_spaceless(self):
        nd1 = NormalizedDict({'F o o BAR': 'value'})
        nd2 = NormalizedDict({'F o o BAR': 'value'}, caseless=False,
                             spaceless=False)
        assert_equals(nd1['F o o BAR'], 'value')
        assert_equals(nd2['F o o BAR'], 'value')
        nd1['FooBAR'] = 'value 2'
        nd2['FooBAR'] = 'value 2'
        assert_equals(nd1['F o o BAR'], 'value 2')
        assert_equals(nd2['F o o BAR'], 'value')
        assert_equals(nd1['FooBAR'], 'value 2')
        assert_equals(nd2['FooBAR'], 'value 2')
        for key in ['foobar', 'f o o b ar', 'Foo BAR']:
            assert_equals(nd1[key], 'value 2')
            assert_raises(KeyError, nd2.__getitem__, key)
            assert_true(key not in nd2)

    def test_caseless_with_non_ascii(self):
        nd1 = NormalizedDict({u'\xe4': 1})
        assert_equals(nd1[u'\xe4'], 1)
        assert_equals(nd1[u'\xc4'], 1)
        assert_true(u'\xc4' in nd1)
        nd2 = NormalizedDict({u'\xe4': 1}, caseless=False)
        assert_equals(nd2[u'\xe4'], 1)
        assert_true(u'\xc4' not in nd2)

    def test_contains(self):
        nd = NormalizedDict({'Foo': 'bar'})
        assert_true('Foo' in nd and 'foo' in nd and 'FOO' in nd)

    def test_original_keys_are_preserved(self):
        nd = NormalizedDict({'low': 1, 'UP': 2})
        nd['up'] = nd['Spa Ce'] = 3
        assert_equals(list(nd.keys()), ['low', 'Spa Ce', 'UP'])
        assert_equals(list(nd.items()), [('low', 1), ('Spa Ce', 3), ('UP', 3)])

    def test_deleting_items(self):
        nd = NormalizedDict({'A': 1, 'b': 2})
        del nd['A']
        del nd['B']
        assert_equals(nd._data, {})
        assert_equals(list(nd.keys()), [])

    def test_pop(self):
        nd = NormalizedDict({'A': 1, 'b': 2})
        assert_equals(nd.pop('A'), 1)
        assert_equals(nd.pop('B'), 2)
        assert_equals(nd._data, {})
        assert_equals(list(nd.keys()), [])

    def test_pop_with_default(self):
        assert_equals(NormalizedDict().pop('nonex', 'default'), 'default')

    def test_popitem(self):
        items = [(str(i), i) for i in range(9)]
        nd = NormalizedDict(items)
        for i in range(9):
            assert_equals(nd.popitem(), items[i])
        assert_equals(nd._data, {})
        assert_equals(list(nd.keys()), [])

    def test_popitem_empty(self):
        assert_raises(KeyError, NormalizedDict().popitem)

    def test_len(self):
        nd = NormalizedDict()
        assert_equals(len(nd), 0)
        nd['a'] = nd['b'] = nd['c'] = 1
        assert_equals(len(nd), 3)

    def test_truth_value(self):
        assert_false(NormalizedDict())
        assert_true(NormalizedDict({'a': 1}))

    def test_copy(self):
        nd = NormalizedDict({'a': 1, 'B': 1})
        cd = nd.copy()
        assert_equals(nd, cd)
        assert_equals(nd._data, cd._data)
        assert_equals(nd._keys, cd._keys)
        assert_equals(nd._normalize, cd._normalize)
        nd['C'] = 1
        cd['b'] = 2
        assert_equals(nd._keys, {'a': 'a', 'b': 'B', 'c': 'C'})
        assert_equals(nd._data, {'a': 1, 'b': 1, 'c': 1})
        assert_equals(cd._keys, {'a': 'a', 'b': 'B'})
        assert_equals(cd._data, {'a': 1, 'b': 2})

    def test_str(self):
        nd = NormalizedDict({'a': 1, 'B': 1, 'c': 3, 'd': 4, 'E': 5, 'F': 6})
        expected = "{'a': 1, 'B': 1, 'c': 3, 'd': 4, 'E': 5, 'F': 6}"
        assert_equals(str(nd), expected)

    def test_unicode(self):
        nd = NormalizedDict({'a': u'\xe4', u'\xe4': 'a'})
        if PY2:
            assert_equals(unicode(nd), "{'a': u'\\xe4', u'\\xe4': 'a'}")
        else:
            assert_equals(str(nd), u"{'a': '\xe4', '\xe4': 'a'}")

    def test_update(self):
        nd = NormalizedDict({'a': 1, 'b': 1, 'c': 1})
        nd.update({'b': 2, 'C': 2, 'D': 2})
        for c in 'bcd':
            assert_equals(nd[c], 2)
            assert_equals(nd[c.upper()], 2)
        keys = list(nd)
        assert_true('b' in keys)
        assert_true('c' in keys)
        assert_true('C' not in keys)
        assert_true('d' not in keys)
        assert_true('D' in keys)

    def test_update_using_another_norm_dict(self):
        nd = NormalizedDict({'a': 1, 'b': 1})
        nd.update(NormalizedDict({'B': 2, 'C': 2}))
        for c in 'bc':
            assert_equals(nd[c], 2)
            assert_equals(nd[c.upper()], 2)
        keys = list(nd)
        assert_true('b' in keys)
        assert_true('B' not in keys)
        assert_true('c' not in keys)
        assert_true('C' in keys)

    def test_update_with_kwargs(self):
        nd = NormalizedDict({'a': 0, 'c': 1})
        nd.update({'b': 2, 'c': 3}, b=4, d=5)
        for k, v in [('a', 0), ('b', 4), ('c', 3), ('d', 5)]:
            assert_equals(nd[k], v)
            assert_equals(nd[k.upper()], v)
            assert_true(k in nd)
            assert_true(k.upper() in nd)
            assert_true(k in nd.keys())

    def test_iter(self):
        keys = list('123_aBcDeF')
        nd = NormalizedDict((k, 1) for k in keys)
        assert_equals(list(nd), keys)
        assert_equals([key for key in nd], keys)

    def test_keys_are_sorted(self):
        nd = NormalizedDict((c, None) for c in 'aBcDeFg123XyZ___')
        assert_equals(list(nd.keys()), list('123_aBcDeFgXyZ'))

    if PY2:

        def test_iterkeys_and_keys(self):
            nd = NormalizedDict({'A': 1, 'b': 3, 'C': 2})
            iterator = nd.iterkeys()
            assert_false(isinstance(iterator, list))
            assert_equals(list(iterator), ['A', 'b', 'C'])
            assert_equals(list(iterator), [])
            assert_equals(list(nd.iterkeys()), nd.keys())

        def test_itervalues_and_values(self):
            nd = NormalizedDict({'A': 1, 'b': 3, 'C': 2})
            iterator = nd.itervalues()
            assert_false(isinstance(iterator, list))
            assert_equals(list(iterator), [1, 3, 2])
            assert_equals(list(iterator), [])
            assert_equals(list(nd.itervalues()), nd.values())

        def test_iteritems_and_items(self):
            nd = NormalizedDict({'A': 1, 'b': 2, 'C': 3})
            iterator = nd.iteritems()
            assert_false(isinstance(iterator, list))
            assert_equals(list(iterator), [('A', 1), ('b', 2), ('C', 3)])
            assert_equals(list(iterator), [])
            assert_equals(list(nd.iteritems()), nd.items())

    def test_keys_values_and_items_are_returned_in_same_order(self):
        nd = NormalizedDict()
        for i, c in enumerate('abcdefghijklmnopqrstuvwxyz0123456789!"#%&/()=?'):
            nd[c.upper()] = i
            nd[c+str(i)] = 1
        assert_equals(list(nd.items()), list(zip(nd.keys(), nd.values())))
        if PY2:
            assert_equals(list(nd.iteritems()), list(zip(nd.iterkeys(), nd.itervalues())))

    def test_eq(self):
        self._verify_eq(NormalizedDict(), NormalizedDict())

    def test_eq_with_normal_dict(self):
        self._verify_eq(NormalizedDict(), {})

    def test_eq_with_user_dict(self):
        self._verify_eq(NormalizedDict(), UserDict())

    def _verify_eq(self, d1, d2):
        assert_true(d1 == d1 == d2 == d2)
        d1['a'] = 1
        assert_true(d1 == d1 != d2 == d2)
        d2['a'] = 1
        assert_true(d1 == d1 == d2 == d2)
        d1['B'] = 1
        d2['B'] = 1
        assert_true(d1 == d1 == d2 == d2)
        d1['c'] = d2['C'] = 1
        d1['D'] = d2['d'] = 1
        assert_true(d1 == d1 == d2 == d2)

    def test_eq_with_other_objects(self):
        nd = NormalizedDict()
        for other in ['string', 2, None, [], self.test_clear]:
            assert_true(nd != other, other)

    def test_clear(self):
        nd = NormalizedDict({'a': 1, 'B': 2})
        nd.clear()
        assert_equals(nd._data, {})
        assert_equals(nd._keys, {})


if __name__ == '__main__':
    unittest.main()
