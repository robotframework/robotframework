import unittest

from robot.utils import normalize, normalize_tags, NormalizedDict
from robot.utils.asserts import assert_equals, assert_true, assert_false


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

    def test_remove_empty_and_none(self):
        for inp in ['', 'X', '', '  ', '\n'], ['none', 'N O N E', 'X', '']:
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

    def test_initial_values(self):
        nd = NormalizedDict({'key': 'value', 'F O\tO': 'bar'})
        assert_equals(nd['key'], 'value')
        assert_equals(nd['K EY'], 'value')
        assert_equals(nd['foo'], 'bar')

    def test_ignore(self):
        nd = NormalizedDict(ignore=['_'])
        nd['foo_bar'] = 'value'
        assert_equals(nd['foobar'], 'value')
        assert_equals(nd['F  oo\nB   ___a r'], 'value')

    def test_caseless_and_spaceless(self):
        nd = NormalizedDict(caseless=False, spaceless=False)
        nd['F o o B AR'] = 'value'
        for key in ['foobar', 'f o o b ar', 'FooBAR']:
            assert_false(nd.has_key(key))
        assert_equals(nd['F o o B AR'], 'value')

    def test_has_key_and_contains(self):
        nd = NormalizedDict({'Foo': 'bar'})
        assert_true(nd.has_key('Foo') and nd.has_key(' f O o '))
        assert_true('Foo' in nd and 'foo' in nd and 'FOO' in nd)

    def test_original_keys_are_kept(self):
        nd = NormalizedDict()
        nd['Foo'] = nd['a b c'] = nd['UP'] = 1
        keys = nd.keys()
        items = nd.items()
        keys.sort()
        items.sort()
        assert_equals(keys, ['Foo', 'UP', 'a b c'])
        assert_equals(items, [('Foo', 1), ('UP', 1), ('a b c', 1)])

    def test_removing_values(self):
        nd = NormalizedDict({'A':1, 'b':2})
        del nd['a']
        del nd['B']
        assert_equals(nd.data, {})
        assert_false(nd.has_key('a') or nd.has_key('b'))

    def test_removing_values_removes_also_original_keys(self):
        nd = NormalizedDict({'a':1})
        del nd['a']
        assert_equals(nd.data, {})
        assert_equals(nd.keys(), [])

    def test_keys_values_and_items_are_returned_in_same_order(self):
        nd = NormalizedDict()
        for i, c in enumerate('abcdefghijklmnopqrstuvwxyz'):
            nd[c.upper()] = i
            nd[c+str(i)] = 1
        items = nd.items()
        keys = nd.keys()
        values = nd.values()
        assert_equals(items, zip(keys, values))

    def test_len(self):
        nd = NormalizedDict()
        assert_equals(len(nd), 0)
        nd['a'] = nd['b'] = nd['c'] = 1
        assert_equals(len(nd), 3)

    def test_true_and_false(self):
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
        assert_equals(cd._keys, {'a': 'a', 'b': 'B'})

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
            assert_true(k in nd)
            assert_true(k in nd.keys())

    def test_iter(self):
        nd = NormalizedDict({'a': 0, 'B': 1, 'c': 2})
        assert_equals(sorted(list(nd)), ['B', 'a', 'c'])
        keys = []
        for key in nd:
            keys.append(key)
        assert_equals(sorted(keys), ['B', 'a', 'c'])


if __name__ == '__main__':
    unittest.main()

