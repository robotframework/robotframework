import unittest
from collections import UserDict

from robot.utils import normalize, NormalizedDict
from robot.utils.asserts import assert_equal, assert_true, assert_false, assert_raises


class TestNormalize(unittest.TestCase):

    def _verify(self, string, expected, **config):
        assert_equal(normalize(string, **config), expected)

    def test_defaults(self):
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
            self._verify(inp, exp)

    def test_caseless(self):
        self._verify('Fo o BaR', 'FooBaR', caseless=False)
        self._verify('Fo o BaR', 'foobar', caseless=True)

    def test_caseless_non_ascii(self):
        self._verify('\xc4iti', '\xc4iti', caseless=False)
        for mother in ['\xc4ITI', '\xc4iTi', '\xe4iti', '\xe4iTi']:
            self._verify(mother, '\xe4iti', caseless=True)

    def test_spaceless(self):
        self._verify('Fo o BaR', 'fo o bar', spaceless=False)
        self._verify('Fo o BaR', 'foobar', spaceless=True)

    def test_ignore(self):
        self._verify('Foo_ bar', 'fbar', ignore=['_', 'x', 'o'])
        self._verify('Foo_ bar', 'fbar', ignore=('_', 'x', 'o'))
        self._verify('Foo_ bar', 'fbar', ignore='_xo')
        self._verify('Foo_ bar', 'bar', ignore=['_', 'f', 'o'])
        self._verify('Foo_ bar', 'bar', ignore=['_', 'F', 'O'])
        self._verify('Foo_ bar', 'Fbar', ignore=['_', 'f', 'o'], caseless=False)
        self._verify('Foo_\n bar\n', 'foo_ bar', ignore=['\n'], spaceless=False)

    def test_bytes(self):
        self._verify(b'FOO & Bar', b'foo&bar')
        self._verify(b'FOO & Bar', b'oobar', ignore=[b'F', b'&'])
        self._verify(b'FOO & Bar', b'oo  bar', ignore=[b'F', b'&'], spaceless=False)
        self._verify(b'FOO & Bar', b'bar', ignore=b'F&o')
        self._verify(b'FOO & Bar', b'OOBar', ignore=b'F&o', caseless=False)

    def test_string_subclass_without_compatible_init(self):
        class BrokenLikeSudsText(str):
            def __new__(cls, value):
                return str.__new__(cls, value)
        self._verify(BrokenLikeSudsText('suds.sax.text.Text is BROKEN'),
                     'suds.sax.text.textisbroken')
        self._verify(BrokenLikeSudsText(''), '')


class TestNormalizedDict(unittest.TestCase):

    def test_default_constructor(self):
        nd = NormalizedDict()
        nd['foo bar'] = 'value'
        assert_equal(nd['foobar'], 'value')
        assert_equal(nd['F  oo\nBar'], 'value')

    def test_initial_values_as_dict(self):
        nd = NormalizedDict({'key': 'value', 'F O\tO': 'bar'})
        assert_equal(nd['key'], 'value')
        assert_equal(nd['K EY'], 'value')
        assert_equal(nd['foo'], 'bar')

    def test_initial_values_as_name_value_pairs(self):
        nd = NormalizedDict([('key', 'value'), ('F O\tO', 'bar')])
        assert_equal(nd['key'], 'value')
        assert_equal(nd['K EY'], 'value')
        assert_equal(nd['foo'], 'bar')

    def test_setdefault(self):
        nd = NormalizedDict({'a': NormalizedDict()})
        nd.setdefault('a', 'whatever').setdefault('B', []).append(1)
        nd.setdefault('A', 'everwhat').setdefault('b', []).append(2)
        assert_equal(nd['a']['b'], [1, 2])
        assert_equal(list(nd), ['a'])
        assert_equal(list(nd['a']), ['B'])

    def test_ignore(self):
        nd = NormalizedDict(ignore=['_'])
        nd['foo_bar'] = 'value'
        assert_equal(nd['foobar'], 'value')
        assert_equal(nd['F  oo\nB   ___a r'], 'value')

    def test_caseless_and_spaceless(self):
        nd1 = NormalizedDict({'F o o BAR': 'value'})
        nd2 = NormalizedDict({'F o o BAR': 'value'}, caseless=False,
                             spaceless=False)
        assert_equal(nd1['F o o BAR'], 'value')
        assert_equal(nd2['F o o BAR'], 'value')
        nd1['FooBAR'] = 'value 2'
        nd2['FooBAR'] = 'value 2'
        assert_equal(nd1['F o o BAR'], 'value 2')
        assert_equal(nd2['F o o BAR'], 'value')
        assert_equal(nd1['FooBAR'], 'value 2')
        assert_equal(nd2['FooBAR'], 'value 2')
        for key in ['foobar', 'f o o b ar', 'Foo BAR']:
            assert_equal(nd1[key], 'value 2')
            assert_raises(KeyError, nd2.__getitem__, key)
            assert_true(key not in nd2)

    def test_caseless_with_non_ascii(self):
        nd1 = NormalizedDict({'\xe4': 1})
        assert_equal(nd1['\xe4'], 1)
        assert_equal(nd1['\xc4'], 1)
        assert_true('\xc4' in nd1)
        nd2 = NormalizedDict({'\xe4': 1}, caseless=False)
        assert_equal(nd2['\xe4'], 1)
        assert_true('\xc4' not in nd2)

    def test_contains(self):
        nd = NormalizedDict({'Foo': 'bar'})
        assert_true('Foo' in nd and 'foo' in nd and 'FOO' in nd)

    def test_original_keys_are_preserved(self):
        nd = NormalizedDict({'low': 1, 'UP': 2})
        nd['up'] = nd['Spa Ce'] = 3
        assert_equal(list(nd.keys()), ['low', 'Spa Ce', 'UP'])
        assert_equal(list(nd.items()), [('low', 1), ('Spa Ce', 3), ('UP', 3)])

    def test_deleting_items(self):
        nd = NormalizedDict({'A': 1, 'b': 2})
        del nd['A']
        del nd['B']
        assert_equal(nd._data, {})
        assert_equal(list(nd.keys()), [])

    def test_pop(self):
        nd = NormalizedDict({'A': 1, 'b': 2})
        assert_equal(nd.pop('A'), 1)
        assert_equal(nd.pop('B'), 2)
        assert_equal(nd._data, {})
        assert_equal(list(nd.keys()), [])

    def test_pop_with_default(self):
        assert_equal(NormalizedDict().pop('nonex', 'default'), 'default')

    def test_popitem(self):
        items = [(str(i), i) for i in range(9)]
        nd = NormalizedDict(items)
        for i in range(9):
            assert_equal(nd.popitem(), items[i])
        assert_equal(nd._data, {})
        assert_equal(list(nd.keys()), [])

    def test_popitem_empty(self):
        assert_raises(KeyError, NormalizedDict().popitem)

    def test_len(self):
        nd = NormalizedDict()
        assert_equal(len(nd), 0)
        nd['a'] = nd['b'] = nd['c'] = 1
        assert_equal(len(nd), 3)

    def test_truth_value(self):
        assert_false(NormalizedDict())
        assert_true(NormalizedDict({'a': 1}))

    def test_copy(self):
        nd = NormalizedDict({'a': 1, 'B': 1})
        cd = nd.copy()
        assert_equal(nd, cd)
        assert_equal(nd._data, cd._data)
        assert_equal(nd._keys, cd._keys)
        assert_equal(nd._normalize, cd._normalize)
        nd['C'] = 1
        cd['b'] = 2
        assert_equal(nd._keys, {'a': 'a', 'b': 'B', 'c': 'C'})
        assert_equal(nd._data, {'a': 1, 'b': 1, 'c': 1})
        assert_equal(cd._keys, {'a': 'a', 'b': 'B'})
        assert_equal(cd._data, {'a': 1, 'b': 2})

    def test_str(self):
        nd = NormalizedDict({'a': 1, 'B': 1, 'c': 3, 'd': 4, 'E': 5, 'F': 6})
        expected = "{'a': 1, 'B': 1, 'c': 3, 'd': 4, 'E': 5, 'F': 6}"
        assert_equal(str(nd), expected)

    def test_unicode(self):
        nd = NormalizedDict({'a': '\xe4', '\xe4': 'a'})
        assert_equal(str(nd), "{'a': '\xe4', '\xe4': 'a'}")

    def test_update(self):
        nd = NormalizedDict({'a': 1, 'b': 1, 'c': 1})
        nd.update({'b': 2, 'C': 2, 'D': 2})
        for c in 'bcd':
            assert_equal(nd[c], 2)
            assert_equal(nd[c.upper()], 2)
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
            assert_equal(nd[c], 2)
            assert_equal(nd[c.upper()], 2)
        keys = list(nd)
        assert_true('b' in keys)
        assert_true('B' not in keys)
        assert_true('c' not in keys)
        assert_true('C' in keys)

    def test_update_with_kwargs(self):
        nd = NormalizedDict({'a': 0, 'c': 1})
        nd.update({'b': 2, 'c': 3}, b=4, d=5)
        for k, v in [('a', 0), ('b', 4), ('c', 3), ('d', 5)]:
            assert_equal(nd[k], v)
            assert_equal(nd[k.upper()], v)
            assert_true(k in nd)
            assert_true(k.upper() in nd)
            assert_true(k in nd.keys())

    def test_iter(self):
        keys = list('123_aBcDeF')
        nd = NormalizedDict((k, 1) for k in keys)
        assert_equal(list(nd), keys)
        assert_equal([key for key in nd], keys)

    def test_keys_are_sorted(self):
        nd = NormalizedDict((c, None) for c in 'aBcDeFg123XyZ___')
        assert_equal(list(nd.keys()), list('123_aBcDeFgXyZ'))

    def test_keys_values_and_items_are_returned_in_same_order(self):
        nd = NormalizedDict()
        for i, c in enumerate('abcdefghijklmnopqrstuvwxyz0123456789!"#%&/()=?'):
            nd[c.upper()] = i
            nd[c+str(i)] = 1
        assert_equal(list(nd.items()), list(zip(nd.keys(), nd.values())))

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
            assert_false(nd == other, other)
            assert_true(nd != other, other)

    def test_ne(self):
        assert_false(NormalizedDict() != NormalizedDict())
        assert_false(NormalizedDict({'a': 1}) != NormalizedDict({'a': 1}))
        assert_false(NormalizedDict({'a': 1}) != NormalizedDict({'A': 1}))

    def test_hash(self):
        assert_raises(TypeError, hash, NormalizedDict())

    def test_clear(self):
        nd = NormalizedDict({'a': 1, 'B': 2})
        nd.clear()
        assert_equal(nd._data, {})
        assert_equal(nd._keys, {})


if __name__ == '__main__':
    unittest.main()
