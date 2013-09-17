import unittest


from robot.utils.asserts import assert_equals
from robot.utils.escaping import escape, unescape


def assert_unescape(inp, exp):
    assert_equals(unescape(inp), exp, repr(inp))


class TestUnEscape(unittest.TestCase):

    def test_no_unescape(self):
        for inp in ['no escapes', '']:
            assert_unescape(inp, inp)

    def test_single_backslash(self):
        for inp, exp in [('\\', ''),
                         ('\\ ', ' '),
                         ('\\ ', ' '),
                         ('a\\', 'a'),
                         ('\\a', 'a'),
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
                         ('\\n ', '\n'),
                         ('\\\\n ', '\\n '),
                         ('\\\\\\n ', '\\\n'),
                         ('\\nx', '\nx'),
                         ('\\\\nx', '\\nx'),
                         ('\\\\\\nx', '\\\nx'),
                         ('\\n x', '\nx'),
                         ('\\\\n x', '\\n x'),
                         ('\\\\\\n x', '\\\nx')]:
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
            assert_equals(escape(inp), exp, inp)


if __name__ == '__main__':
    unittest.main()
