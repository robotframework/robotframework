import unittest

from robot.utils.match import *
from robot.utils.asserts import assert_equals


class TestMatch(unittest.TestCase):

    def test_eq(self):
        assert eq("foo", "foo")
        assert eq("f OO\t\n", "  foo", caseless=True, spaceless=True)
        assert eq("-a-b-c-", "b", ignore=("-","a","c"))
        assert not eq("foo", "bar")
        assert not eq("foo", "FOO", caseless=False)
        assert not eq("foo", "foo ", spaceless=False)

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

    def test_matcher(self):
        matcher = Matcher('F *', ignore=['-'], caseless=False, spaceless=True)
        assert matcher.pattern == 'F *'
        assert matcher.match('Foo')
        assert matcher.match('--Foo')
        assert not matcher.match('foo')


class TestMultiMatcher(unittest.TestCase):

    def test_match_pattern(self):
        matcher = MultiMatcher(['xxx', 'f*'], ignore=['.', ':'])
        assert matcher.match('xxx')
        assert matcher.match('foo')
        assert matcher.match('..::FOO::..')
        assert not matcher.match('bar')

    def test_match_when_no_patterns_by_default(self):
        matcher = MultiMatcher([])
        assert matcher.match('xxx')

    def test_configure_no_match_when_no_patterns(self):
        matcher = MultiMatcher(match_if_no_patterns=False)
        assert not matcher.match('xxx')

    def test_len(self):
        assert_equals(len(MultiMatcher()), 0)
        assert_equals(len(MultiMatcher(['one', 'two'])), 2)

    def test_iter(self):
        assert_equals(list(MultiMatcher()), [])
        assert_equals([m.pattern for m in MultiMatcher(['1', 'xxx', '3'])],
                      ['1', 'xxx', '3'])


if __name__ == "__main__":
    unittest.main()
