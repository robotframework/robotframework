import unittest

from robot.utils.asserts import assert_equal
from robot.utils.escaping import escape, unescape, split_from_equals


def assert_unescape(inp, exp):
    assert_equal(unescape(inp), exp, repr(inp))


class TestUnEscape(unittest.TestCase):

    def test_no_backslash(self):
        for inp in ['no escapes', '', 42]:
            assert_unescape(inp, inp)

    def test_single_backslash(self):
        for inp, exp in [('\\', ''),
                         ('\\ ', ' '),
                         ('\\ ', ' '),
                         ('a\\', 'a'),
                         ('\\a', 'a'),
                         ('\\-', '-'),
                         ('\\ä', 'ä'),
                         ('\\0', '0'),
                         ('a\\b\\c\\d', 'abcd')]:
            assert_unescape(inp, exp)

    def test_multiple_backslash(self):
        for inp, exp in [('\\\\', '\\'),
                         ('\\\\\\', '\\'),
                         ('\\\\\\\\', '\\\\'),
                         ('\\\\\\\\\\', '\\\\'),
                         ('x\\\\x', 'x\\x'),
                         ('x\\\\\\x', 'x\\x'),
                         ('x\\\\\\\\x', 'x\\\\x')]:
            assert_unescape(inp, exp)

    def test_newline(self):
        for inp, exp in [('\\n', '\n'),
                         ('\\\\n', '\\n'),
                         ('\\\\\\n', '\\\n'),
                         ('\\n ', '\n '),
                         ('\\\\n ', '\\n '),
                         ('\\\\\\n ', '\\\n '),
                         ('\\nx', '\nx'),
                         ('\\\\nx', '\\nx'),
                         ('\\\\\\nx', '\\\nx'),
                         ('\\n x', '\n x'),
                         ('\\\\n x', '\\n x'),
                         ('\\\\\\n x', '\\\n x')]:
            assert_unescape(inp, exp)

    def test_carriage_return(self):
        for inp, exp in [('\\r', '\r'),
                         ('\\\\r', '\\r'),
                         ('\\\\\\r', '\\\r'),
                         ('\\r ', '\r '),
                         ('\\\\r ', '\\r '),
                         ('\\\\\\r ', '\\\r '),
                         ('\\rx', '\rx'),
                         ('\\\\rx', '\\rx'),
                         ('\\\\\\rx', '\\\rx'),
                         ('\\r x', '\r x'),
                         ('\\\\r x', '\\r x'),
                         ('\\\\\\r x', '\\\r x')]:
            assert_unescape(inp, exp)

    def test_tab(self):
        for inp, exp in [('\\t', '\t'),
                         ('\\\\t', '\\t'),
                         ('\\\\\\t', '\\\t'),
                         ('\\t ', '\t '),
                         ('\\\\t ', '\\t '),
                         ('\\\\\\t ', '\\\t '),
                         ('\\tx', '\tx'),
                         ('\\\\tx', '\\tx'),
                         ('\\\\\\tx', '\\\tx'),
                         ('\\t x', '\t x'),
                         ('\\\\t x', '\\t x'),
                         ('\\\\\\t x', '\\\t x')]:
            assert_unescape(inp, exp)

    def test_invalid_x(self):
        for inp in r'\x \xxx xx\xxx \x0 \x0g \X00 \x-1 \x+1'.split():
            assert_unescape(inp, inp.replace('\\', ''))

    def test_valid_x(self):
        for inp, exp in [(r'\x00', '\x00'),
                         (r'\xab\xBA', '\xab\xba'),
                         (r'\xe4iti', 'äiti')]:
            assert_unescape(inp, exp)

    def test_invalid_u(self):
        for inp in r'''\u
                       \ukekkonen
                       b\uu
                       \u0
                       \u123
                       \u123x
                       \u-123
                       \u+123
                       \u1.23'''.split():
            assert_unescape(inp, inp.replace('\\', ''))

    def test_valid_u(self):
        for inp, exp in [(r'\u0000', '\x00'),
                         (r'\uABba', '\uabba'),
                         (r'\u00e4iti', 'äiti')]:
            assert_unescape(inp, exp)

    def test_invalid_U(self):
        for inp in r'''\U
                       \Ukekkonen
                       b\Uu
                       \U0
                       \U1234567
                       \U1234567x
                       \U-1234567
                       \U+1234567
                       \U1.234567'''.split():
            assert_unescape(inp, inp.replace('\\', ''))

    def test_valid_U(self):
        for inp, exp in [(r'\U00000000', '\x00'),
                         (r'\U0000ABba', '\uabba'),
                         (r'\U0001f3e9', '\U0001f3e9'),
                         (r'\U0010FFFF', '\U0010ffff'),
                         (r'\U000000e4iti', 'äiti')]:
            assert_unescape(inp, exp)

    def test_U_above_valid_range(self):
        assert_unescape(r'\U00110000', 'U00110000')
        assert_unescape(r'\U12345678', 'U12345678')
        assert_unescape(r'\UffffFFFF', 'UffffFFFF')


class TestEscape(unittest.TestCase):

    def test_escape(self):
        for inp, exp in [('nothing to escape', 'nothing to escape'),
                         ('still nothing $ @', 'still nothing $ @' ),
                         ('1 backslash to 2: \\', '1 backslash to 2: \\\\'),
                         ('3 bs to 6: \\\\\\', '3 bs to 6: \\\\\\\\\\\\'),
                         ('\\' * 1000, '\\' * 2000 ),
                         ('${notvar}', '\\${notvar}'),
                         ('@{notvar}', '\\@{notvar}'),
                         ('${nv} ${nv} @{nv}', '\\${nv} \\${nv} \\@{nv}'),
                         ('\\${already esc}', '\\\\\\${already esc}'),
                         ('\\${ae} \\\\@{ae} \\\\\\@{ae}',
                          '\\\\\\${ae} \\\\\\\\\\@{ae} \\\\\\\\\\\\\\@{ae}'),
                         ('%{reserved}', '\\%{reserved}'),
                         ('&{reserved}', '\\&{reserved}'),
                         ('*{reserved}', '\\*{reserved}'),
                         ('x{notreserved}', 'x{notreserved}'),
                         ('named=arg', 'named\\=arg')]:
            assert_equal(escape(inp), exp, inp)

    def test_escape_control_words(self):
        for inp in ['ELSE', 'ELSE IF', 'AND', 'WITH NAME', 'AS']:
            assert_equal(escape(inp), '\\' + inp)
            assert_equal(escape(inp.lower()), inp.lower())
            assert_equal(escape('other' + inp), 'other' + inp)
            assert_equal(escape(inp + ' '), inp + ' ')


class TestSplitFromEquals(unittest.TestCase):

    def test_basics(self):
        for inp in 'foo=bar', '=', 'split=from=first', '===':
            self._test(inp, *inp.split('=', 1))

    def test_escaped(self):
        self._test(r'a\=b=c', r'a\=b', 'c')
        self._test(r'\=====', r'\=', '===')
        self._test(r'\=\\\=\\=', r'\=\\\=\\', '')

    def test_no_unescaped_equal(self):
        for inp in '', 'xxx', r'\=', r'\\\=', r'\\\\\=\\\\\\\=\\\\\\\\\=':
            self._test(inp, inp, None)

    def test_no_split_in_variable(self):
        self._test(r'${a=b}', '${a=b}', None)
        self._test(r'=${a=b}', '', '${a=b}')
        self._test(r'${a=b}=', '${a=b}', '')
        self._test(r'\=${a=b}', r'\=${a=b}', None)
        self._test(r'${a=b}=${c=d}', '${a=b}', '${c=d}')
        self._test(r'${a=b}\=${c=d}', r'${a=b}\=${c=d}', None)
        self._test(r'${a=b}${c=d}${e=f}\=${g=h}=${i=j}',
                   r'${a=b}${c=d}${e=f}\=${g=h}', '${i=j}')

    def test_broken_variable(self):
        self._test('${foo=bar', '${foo', 'bar')

    def _test(self, inp, *exp):
        assert_equal(split_from_equals(inp), exp)


if __name__ == '__main__':
    unittest.main()
