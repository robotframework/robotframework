import unittest
import os

from robot.utils import *
from robot.utils.asserts import *


class TestNormalizing(unittest.TestCase):
    
    def test_normpath(self):
        if os.sep == '/':
            inputs = [ ('/tmp/', '/tmp'),
                       ('/tmp', '/tmp'),
                       ('/tmp/foo/..', '/tmp'),
                       ('/tmp//', '/tmp'),
                       ('/tmp/./', '/tmp'),
                       ('/var/../opt/../tmp/.', '/tmp'),
                       ('/non/Existing/..', '/non'),
                       ('/', '/') ]
        else:
            inputs = [ ('c:\\temp', 'c:\\temp'),
                       ('C:\\TEMP\\', 'c:\\temp'),
                       ('c:\\Temp\\foo\..', 'c:\\temp'),
                       ('c:\\temp\\\\', 'c:\\temp'),
                       ('c:\\temp\\.\\', 'c:\\temp'),
                       ('C:\\xxx\\..\\yyy\\..\\temp\\.', 'c:\\temp'),
                       ('c:\\Non\\Existing\\..', 'c:\\non') ]
            for x in 'ABCDEFGHIJKLMNOPQRSTUVXYZ':
                base = '%s:\\' % x
                exp = base.lower()
                inputs.append((base, exp))
                inputs.append((base[:2], exp))
                inputs.append((base + '\\foo\\..\\.\\BAR\\\\', exp + 'bar'))

        for inp, exp in inputs:
            assert_equal(normpath(inp), exp, inp)
    
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

    def test_normalize_list(self):
        for inp, exp in [ ([], []),
                          (['nothingtodo'], ['nothingtodo']),
                          (['UPPERgoesLower'], ['uppergoeslower']),
                          (['Spaces & unds removed'], ['spaces&undsremoved']),
                          (['empty\trem','  ','\n',''], ['emptyrem']),
                          (['dublic rem','DUBLICREM','dubliCREM'],['dublicrem']),
                          (['SORT','1','B','2','a'], ['1','2','a','b','sort']),
                          (['ALL','all','10','1','A','a','','A LL',' '],
                           ['1','10','a','all']) ]:
            assert_equals(normalize_list(inp), exp)


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
        fail_unless(nd.has_key('Foo') and nd.has_key(' f O o '))
        fail_unless('Foo' in nd and 'foo' in nd and 'FOO' in nd)

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


if __name__ == '__main__':
    unittest.main()
        
