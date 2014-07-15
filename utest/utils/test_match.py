import unittest

from robot.utils.match import eq, Matcher, MultiMatcher
from robot.utils.asserts import assert_equals


class TestEq(unittest.TestCase):

    def test_eq(self):
        assert eq("foo", "foo")
        assert eq("f OO\t\n", "  foo", caseless=True, spaceless=True)
        assert eq("-a-b-c-", "b", ignore=("-", "a", "c"))
        assert not eq("foo", "bar")
        assert not eq("foo", "FOO", caseless=False)
        assert not eq("foo", "foo ", spaceless=False)


class TestMatcher(unittest.TestCase):

    def test_matcher(self):
        matcher = Matcher('F *', ignore=['-'], caseless=False, spaceless=True)
        assert matcher.pattern == 'F *'
        assert matcher.match('Foo')
        assert matcher.match('--Foo')
        assert not matcher.match('foo')

    def test_regexp_matcher(self):
        matcher = Matcher('F .*', ignore=['-'], caseless=False, spaceless=True,
                          regexp=True)
        assert matcher.pattern == 'F .*'
        assert matcher.match('Foo')
        assert matcher.match('--Foo')
        assert not matcher.match('foo')

    def test_matches_with_string(self):
        for pattern in ['abc', 'ABC', '*', 'a*', '*C', 'a*c', '*a*b*c*', 'AB?',
                        '???', '?b*', '*abc', 'abc*', '*abc*']:
            self._matches('abc', pattern)
        for pattern in ['def', '?abc', '????', '*ed', 'b*']:
            self._matches_not('abc', pattern)

    def test_regexp_matches_with_string(self):
        for pattern in ['abc', 'ABC', '.*', 'a.*', '.*C', 'a.*c', '.*a.*b.*c.*',
                        'AB.',
                        '...', '.b.*', '.*abc', 'abc.*', '.*abc.*']:
            self._matches('abc', pattern, regexp=True)
        for pattern in ['def', '.abc', '....', '.*ed', 'b.*']:
            self._matches_not('abc', pattern, regexp=True)

    def test_matches_with_multiline_string(self):
        for pattern in ['*', 'multi*string', 'multi?line?string', '*\n*']:
            self._matches('multi\nline\nstring', pattern, spaceless=False)

    def test_regexp_matches_with_multiline_string(self):
        for pattern in ['.*', 'multi.*string', 'multi.line.string', '.*\n.*']:
            self._matches('multi\nline\nstring', pattern, spaceless=False,
                          regexp=True)

    def test_matches_with_slashes(self):
        for pattern in ['a*','aa?b*','*c','?a?b?c']:
            self._matches('aa/b\\c', pattern)

    def test_regexp_matches_with_slashes(self):
        for pattern in ['a.*', 'aa.b.*', '.*c', '.a.b.c']:
            self._matches('aa/b\\c', pattern, regexp=True)

    def test_matches_no_pattern(self):
        for string in ['foo', '', ' ', '      ', 'what ever',
                       'multi\nline\string here', '=\\.)(/23.',
                       'forw/slash/and\\back\\slash']:
            self._matches(string, string), string

    def test_regexp_matches_no_pattern(self):
        for string in ['foo', '', ' ', '      ', 'what ever']:
            self._matches(string, string, regexp=True), string

    def test_match_any(self):
        matcher = Matcher('H?llo')
        assert matcher.match_any(('Hello', 'world'))
        assert matcher.match_any(['jam', 'is', 'hillo'])
        assert not matcher.match_any(('no', 'match', 'here'))
        assert not matcher.match_any(())

    def test_regexp_match_any(self):
        matcher = Matcher('H.llo', regexp=True)
        assert matcher.match_any(('Hello', 'world'))
        assert matcher.match_any(['jam', 'is', 'hillo'])
        assert not matcher.match_any(('no', 'match', 'here'))
        assert not matcher.match_any(())

    def _matches(self, string, pattern, **config):
        assert Matcher(pattern, **config).match(string), pattern

    def _matches_not(self, string, pattern, **config):
        assert not Matcher(pattern, **config).match(string), pattern


class TestMultiMatcher(unittest.TestCase):

    def test_match_pattern(self):
        matcher = MultiMatcher(['xxx', 'f*'], ignore='.:')
        assert matcher.match('xxx')
        assert matcher.match('foo')
        assert matcher.match('..::FOO::..')
        assert not matcher.match('bar')

    def test_match_regexp_pattern(self):
        matcher = MultiMatcher(['xxx', 'f.*'], ignore='_:', regexp=True)
        assert matcher.match('xxx')
        assert matcher.match('foo')
        assert matcher.match('__::FOO::__')
        assert not matcher.match('bar')

    def test_do_not_match_when_no_patterns_by_default(self):
        assert not MultiMatcher().match('xxx')

    def test_configure_to_match_when_no_patterns(self):
        assert MultiMatcher(match_if_no_patterns=True).match('xxx')
        assert MultiMatcher(match_if_no_patterns=True, regexp=True).match('xxx')

    def test_len(self):
        assert_equals(len(MultiMatcher()), 0)
        assert_equals(len(MultiMatcher([])), 0)
        assert_equals(len(MultiMatcher(['one', 'two'])), 2)
        assert_equals(len(MultiMatcher(regexp=True)), 0)
        assert_equals(len(MultiMatcher([], regexp=True)), 0)
        assert_equals(len(MultiMatcher(['one', 'two'], regexp=True)), 2)

    def test_iter(self):
        assert_equals(tuple(MultiMatcher()), ())
        assert_equals(list(MultiMatcher(['1', 'xxx', '3'])), ['1', 'xxx', '3'])
        assert_equals(tuple(MultiMatcher(regexp=True)), ())
        assert_equals(list(MultiMatcher(['1', 'xxx', '3'], regexp=True)),
                      ['1', 'xxx', '3'])

    def test_single_string_is_converted_to_list(self):
        matcher = MultiMatcher('one string')
        assert matcher.match('one string')
        assert not matcher.match('o')
        assert_equals(len(matcher), 1)

    def test_regexp_single_string_is_converted_to_list(self):
        matcher = MultiMatcher('one string', regexp=True)
        assert matcher.match('one string')
        assert not matcher.match('o')
        assert_equals(len(matcher), 1)

    def test_match_any(self):
        matcher = MultiMatcher(['H?llo', 'w*'])
        assert matcher.match_any(('Hi', 'world'))
        assert matcher.match_any(['jam', 'is', 'hillo'])
        assert not matcher.match_any(('no', 'match', 'here'))
        assert not matcher.match_any(())

    def test_regexp_match_any(self):
        matcher = MultiMatcher(['H.llo', 'w.*'], regexp=True)
        assert matcher.match_any(('Hi', 'world'))
        assert matcher.match_any(['jam', 'is', 'hillo'])
        assert not matcher.match_any(('no', 'match', 'here'))
        assert not matcher.match_any(())

if __name__ == '__main__':
    unittest.main()
