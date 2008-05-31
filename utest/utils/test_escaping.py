import unittest, sys, os

if __name__ == "__main__":
    sys.path.insert(0, "../../../src")

from robot.utils.asserts import *

from robot.utils.escaping import *


class TestUnEscape(unittest.TestCase):

    def test_no_unescape(self):
        for inp in [ 'no escapes', '' ]:
            assert_equals(unescape(inp), inp)
            
    def test_single_backslash(self):
        for inp, exp in [ ('\\', ''),
                          ('\\ ', ' '),
                          ('a\\', 'a'),
                          ('\\a', 'a'),
                          ('a\\b\\c\\d', 'abcd') ]:
            assert_equals(unescape(inp), exp, inp)
            
    def test_multiple_backslash(self):
        for inp, exp in [ ('\\\\', '\\'),
                          ('\\\\\\', '\\'),
                          ('\\\\\\\\', '\\\\'),
                          ('x\\\\x', 'x\\x'),
                          ('x\\\\\\x', 'x\\x'),
                          ('x\\\\\\\\x', 'x\\\\x') ]:
            assert_equals(unescape(inp), exp, inp)
            
    def test_lf(self):
        for inp, exp in [ ('\\n', '\n'),
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
                          ('\\\\\\n x', '\\\nx') ]:
            assert_equals(unescape(inp), exp, "'%s'" % inp)

    def test_cr(self):
        for inp, exp in [ ('\\r', '\r'),
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
                          ('\\\\\\r x', '\\\r x') ]:
            assert_equals(unescape(inp), exp, inp)            
                                   
    def test_tab(self):
        for inp, exp in [ ('\\t', '\t'),
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
                          ('\\\\\\t x', '\\\t x') ]:
            assert_equals(unescape(inp), exp, inp)
            
            
class TestEscape(unittest.TestCase):
            
    def test_escape(self):
        for inp, exp in [ ('nothing to escape', 'nothing to escape'),
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
                          ]:
            assert_equals(escape(inp), exp, inp)


if __name__ == '__main__':
    unittest.main()
            