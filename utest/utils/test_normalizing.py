import unittest

from robot.utils import normalize, normalize_tags, NormalizedDict
from robot.utils.asserts import (assert_equals, assert_true, assert_false,
                                 assert_raises)


class TestNormalizing(unittest.TestCase):

    def test_normalize_with_defaults(self):
        for inp, exp in [ ('', ''),
                          ('            ', ''),
                          (' \n\t\r', ''),
                          ('foo', 'foo'),
                          (' f o o ', 'foo'),
                          ('_BAR', '_bar'),
                          ('Fo OBar\r\n', 'foobar'),
                          ('foo\tbar', 'foobar'),
                          ('\n \n \n \n F o O \t\tBaR \r \r \r   ', 'foobar') ]:
            assert_equals(exp, normalize(inp))

    def test_normalize_with_caseless(self):
        assert_equals(normalize('Fo o BaR', caseless=False), 'FooBaR')
        assert_equals(normalize('Fo O B AR', caseless=True), 'foobar')

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


class TestNormalizeTags(unittest.TestCase):

    def test_no_tasg(self):
        assert_equals(normalize_tags([]), [])

    def test_case_and_space(self):
        for inp in ['lower'], ['MiXeD', 'UPPER'], ['a few', 'spaces here']:
            assert_equals(normalize_tags(inp), inp)

    def test_underscore(self):
        assert_equals(normalize_tags(['a_tag', 'a tag', 'ATag']), ['a_tag'])
        assert_equals(normalize_tags(['tag', '_t_a_g_']), ['tag'])

    def test_remove_empty_and_none(self):
        for inp in ['', 'X', '', '  ', '\n'], ['none', 'N O N E', 'X', '', '_']:
            assert_equals(normalize_tags(inp), ['X'])

    def test_remove_dupes(self):
        for inp in ['dupe', 'DUPE', ' d u p e '], ['d U', 'du', 'DU', 'Du']:
            assert_equals(normalize_tags(inp), [inp[0]])

    def test_sorting(self):
        for inp, exp in [(['SORT','1','B','2','a'], ['1','2','a','B','SORT']),
                         (['all', 'A L L', 'NONE', '10', '1', 'A', 'a', ''],
                           ['1', '10', 'A', 'all'])]:
            assert_equals(normalize_tags(inp), exp)


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

    def test_has_key_and_contains(self):
        nd = NormalizedDict({'Foo': 'bar'})
        assert_true(nd.has_key('Foo') and nd.has_key(' f O o '))
        assert_true('Foo' in nd and 'foo' in nd and 'FOO' in nd)

    def test_original_keys_are_preserved(self):
        nd = NormalizedDict({'low': 1, 'UP': 2})
        nd['up'] = nd['Spa Ce'] = 3
        assert_equals(nd.keys(), ['low', 'Spa Ce', 'UP'])
        assert_equals(nd.items(), [('low', 1), ('Spa Ce', 3), ('UP', 3)])

    def test_deleting_items(self):
        nd = NormalizedDict({'A': 1, 'b': 2})
        del nd['A']
        del nd['B']
        assert_equals(nd.data, {})
        assert_equals(nd.keys(), [])

    def test_popping_items(self):
        nd = NormalizedDict({'A': 1, 'b': 2})
        assert_equals(nd.pop('A'), 1)
        assert_equals(nd.pop('B'), 2)
        assert_equals(nd.data, {})
        assert_equals(nd.keys(), [])

    def test_keys_are_sorted(self):
        nd = NormalizedDict((c, None) for c in 'aBcDeFg123XyZ___')
        assert_equals(nd.keys(), list('123_aBcDeFgXyZ'))

    def test_keys_values_and_items_are_returned_in_same_order(self):
        nd = NormalizedDict()
        for i, c in enumerate('abcdefghijklmnopqrstuvwxyz'):
            nd[c.upper()] = i
            nd[c+str(i)] = 1
        assert_equals(nd.items(), zip(nd.keys(), nd.values()))

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
        assert_equals(nd.data, cd.data)
        assert_equals(nd._keys, cd._keys)
        assert_equals(nd._normalize, cd._normalize)
        nd['C'] = 1
        cd['b'] = 2
        assert_equals(nd._keys, {'a': 'a', 'b': 'B', 'c': 'C'})
        assert_equals(nd.data, {'a': 1, 'b': 1, 'c': 1})
        assert_equals(cd._keys, {'a': 'a', 'b': 'B'})
        assert_equals(cd.data, {'a': 1, 'b': 2})

    def test_str(self):
        nd = NormalizedDict({'a': 1, 'B': 1})
        assert_true(str(nd) in ("{'a': 1, 'B': 1}", "{'B': 1, 'a': 1}"))

    def test_update(self):
        nd = NormalizedDict({'a': 1})
        nd.update({'b': 2})
        assert_equals(nd['b'], 2)
        assert_true('b' in nd.keys())

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

    def test_cmp(self):
        n1 = NormalizedDict()
        n2 = NormalizedDict()
        assert_true(n1 == n1 == n2 == n2)
        n1['a'] = 1
        assert_true(n1 == n1 != n2 == n2)
        n2['a'] = 1
        assert_true(n1 == n1 == n2 == n2)
        n1['b'] = 1
        n2['B'] = 1
        assert_true(n1 == n1 == n2 == n2)
        n1['C'] = 1
        n2['C'] = 2
        assert_true(n1 == n1 != n2 == n2)


if __name__ == '__main__':
    unittest.main()

