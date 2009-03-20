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
        
    def test_has_key(self):
        nd = NormalizedDict()
        nd['Foo'] = 'bar'
        fail_unless(nd.has_key('Foo'))
        fail_unless(nd.has_key(' f O o '))
        
            
if __name__ == '__main__':
    unittest.main()
        
