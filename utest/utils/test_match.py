import unittest
import sys

from robot.utils.match import *


class TestMatch(unittest.TestCase):

    def test_eq(self):
        assert eq("foo", "foo")
        assert eq("f OO\t\n", "  foo", caseless=True, spaceless=True)
        assert eq("-a-b-c-", "b", ignore=("-","a","c"))
        assert not eq("foo", "bar")
        assert not eq("foo", "FOO", caseless=False)
        assert not eq("foo", "foo ", spaceless=False)

    def test_eq_any(self):
        assert eq_any("foo", [ "a", "b", " F O O  " ], caseless=True, spaceless=True)
        assert not eq_any("foo", [ "f o o ", "hii", "hoo", "huu", "FOO" ],
                          caseless=False, spaceless=False)
                          
    def test_any_eq_any(self):
        assert any_eq_any(['foo','bar','zap'], ['hii','hoo','  F O o  '])
        assert any_eq_any(['fo\no'], ['hii','hoo','  F O o  '])
        assert not any_eq_any(['foo','bar','zap'], ['hii','hoo','FUU','FAA'])
        assert not any_eq_any(['foo','bar','zap'], ['b a r','hoo','FUU','Z a p'],
                              caseless=False, spaceless=False)
        
    def test_matches_with_string(self):
        for pattern in ['abc','ABC','*','a*','*C','a*c','*a*b*c*','AB?','???',
                        '?b*','*abc','abc*','*abc*']:
            assert matches('abc',pattern), pattern
        for pattern in ['def','?abc','????','*ed','b*' ]:
            assert not matches('abc',pattern), pattern
    
    def test_matches_with_multiline_string(self):
        for pattern in ['*', 'multi*string', 'multi?line?string', '*\n*']:
            assert matches('multi\nline\nstring', pattern, spaceless=False), pattern
            
    def test_matches_with_slashes(self):
        for pattern in ['a*','aa?b*','*c','?a?b?c']:
            assert matches('aa/b\\c', pattern), pattern
            
    def test_matches_no_pattern(self):
        for string in [ 'foo', '', ' ', '      ', 'what ever',
                        'multi\nline\string here', '=\\.)(/23.',
                        'forw/slash/and\\back\\slash' ]:
            assert matches(string, string), string
            
    def test_matches_any(self):
        assert matches_any('abc', ['asdf','foo','*b?'])
        assert matches_any('abc', ['*','asdf','foo','*b?'])
        assert not matches_any('abc', ['asdf','foo','*c?'])

# TODO: remove if unneeded        
#    def test_any_matches_any(self):
#        assert any_matches_any(['abc','xxx','yyy'], ['asdf','foo','*b?'])
#        assert any_matches_any(['abc','xxx','yyy'], ['*','asdf','foo','*b?'])
#        assert not any_matches_any(['abc','xxx','yyy'], ['asdf','foo','*c?'])
        
    def test_any_matches(self):
        assert any_matches(['foo','bar','zap'], '?o?')
        assert any_matches(['foo','bar','zap'], '*r')
        assert not any_matches(['foo','bar','zap'], '*r?')

# TODO: remove if unneeded
#    def test_starts(self):
#        assert starts("foo", "foo")
#        assert starts("f o o . . . .", "  F  O  O")
#        assert starts("foo ", "foo", caseless=False)
#        assert not starts("foo", "bar")
#        assert not starts("bfoo", "foo")
#        assert not starts("foo", " foo ", spaceless=False)
#
#    def test_starts_any(self):
#        assert starts_any("foola", [ "hii", "hoo", " F O O  " ])
#        assert not starts_any("foo", [ "bfoo", " foo", "FOO" ],
#                              caseless=False, spaceless=False)
#
#    def test_any_starts(self):
#        assert any_starts([ "hii", "hoo", " F O O L A " ], "foo")
#        assert not any_starts([ "bfoo", " foo", "FOO" ], "foo", 
#                              caseless=False, spaceless=False)
# TODO: remove if unneeded
#    def test_ends(self):
#        assert ends("foo", "foo")
#        assert ends(". . . f o o ", "  F  O  O")
#        assert ends(" foo", "foo", caseless=False)
#        assert not ends("foo", "bar")
#        assert not ends("foo", "foob")
#        assert not ends("foo", " foo ", spaceless=False)
#
#    def test_ends_any(self):
#        assert ends_any("asfoo", [ "hii", "hoo", " F O O  " ])
#        assert not ends_any("foo", [ "bfoo", " foo ", "FOO" ],
#                            caseless=False, spaceless=False)

            
if __name__ == "__main__":
    unittest.main()

