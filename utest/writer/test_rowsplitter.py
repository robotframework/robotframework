import unittest

from robot.writer.rowsplitter import RowSplitter
from robot.utils.asserts import assert_equals


class TestRowSplitter(unittest.TestCase):

    def _test(self, data, expected, cols=3, table_type='settings'):
        splitter = RowSplitter(cols=cols)
        actual = list(splitter.split(data, table_type))
        assert_equals(actual, expected)

    def test_escaping_empty_cells_at_eol(self):
        self._test(['First', 'second', ''],
                   [['First', 'second', '${EMPTY}']])
        self._test(['First', 'second', '', 'next line'],
                   [['First', 'second', '${EMPTY}'],
                    ['...', 'next line']])
        self._test(['1.1', '1.2', '1.3', '', '2.1', '2.2', '', '3.1', '', ''],
                   [['1.1', '1.2', '1.3', '${EMPTY}'],
                    ['...', '2.1', '2.2', '${EMPTY}'],
                    ['...', '3.1', '', '${EMPTY}']], cols=4)

    def test_splitting_inside_comment(self):
        self._test(['Kw', 'Arg', '#Comment in', 'many cells'],
                   [['Kw', 'Arg', '#Comment in'],
                    ['...', '# many cells']])
        self._test(['Kw', 'Arg', '# Comment', 'in', 'very', 'many', 'cells', '!'],
                   [['Kw', 'Arg', '# Comment'],
                    ['...', '# in', 'very'],
                    ['...', '# many', 'cells'],
                    ['...', '# !']])
        self._test(['Kw', 'Arg', '# Comment in', 'many cells'],
                   [['Kw', 'Arg'],
                    ['...', '# Comment in'],
                    ['...', '# many cells']], cols=2)

    def test_no_extra_comment_marker(self):
        self._test(['1', '2', '3', '# Comment'],
                   [['1', '2', '3'],
                    ['...', '# Comment']])
        self._test(['1', '2', '# C 1', '# C 2'],
                   [['1', '2', '# C 1'],
                    ['...', '# C 2']])

    def test_splitting_whitespace_rows(self):
        data = ['', '', '', '', 'foo', '# Comment']
        for cols, expected in [(4, [['', '', '', '${EMPTY}'],
                                    ['...', 'foo', '# Comment']]),
                               (3, [['', '', '${EMPTY}'],
                                    ['...', '', 'foo'],
                                    ['...', '# Comment']]),
                               (2, [['', '${EMPTY}'],
                                    ['...', '${EMPTY}'],
                                    ['...', '${EMPTY}'],
                                    ['...', 'foo'],
                                    ['...', '# Comment']])]:
            self._test(data, expected, cols)

    def test_min_indent(self):
        self._test(['1', '2', '3', '4'],
                   [['1', '2', '3'], ['...', '4']])
        self._test(['1', '2', '3', '4'],
                   [['1', '2', '3'], ['', '...', '4']], table_type='keyword')
        self._test(['1', '2', '3', '4'],
                   [['1', '2', '3'], ['', '...', '4']], table_type='test case')

    def test_split_else(self):
        self._test(['Run Keyword If', 'expression', 'Kw 1', 'ELSE', 'Kw 2'],
                   [['Run Keyword If', 'expression', 'Kw 1'],
                    ['...', 'ELSE', 'Kw 2']], cols=100)
        self._test(['Run Keyword If', 'e1', 'Kw 1', 'ELSE IF', 'e2', 'Kw 2'],
                   [['Run Keyword If', 'e1', 'Kw 1'],
                    ['...', 'ELSE IF', 'e2', 'Kw 2']], cols=100)
        self._test(['1', '2', 'ELSE IF', '3', '4', 'ELSE IF', '5', 'ELSE', '6'],
                   [['1', '2'],
                     ['...', 'ELSE IF', '3', '4'],
                     ['...', 'ELSE IF', '5'],
                     ['...', 'ELSE', '6']], cols=100)

    def test_split_also_and(self):
        self._test(['Run Keywords', 'k1', 'AND', 'k2', 'a', 'b', 'AND', 'k3'],
                   [['Run Keywords', 'k1'],
                    ['...', 'AND', 'k2', 'a', 'b'],
                    ['...', 'AND', 'k3']], cols=100)
        self._test(['', '1', 'AND', '2', 'ELSE', '3', 'ELSE IF', '4', 'AND', '5'],
                   [['', '1'],
                    ['', '...', 'AND', '2'],
                    ['', '...', 'ELSE', '3'],
                    ['', '...', 'ELSE IF', '4'],
                    ['', '...', 'AND', '5']], cols=100)

    def test_dont_split_else_or_and_in_first_cell(self):
        for data in (['ELSE', '1', '2'],
                     ['ELSE IF', '1', '2'],
                     ['AND', '1', '2']):
            for no_split in (data,
                             [''] + data,
                             ['', '', ''] + data,
                             ['...'] + data,
                             ['', '...'] + data,
                             ['', '', '', '...'] + data):
                self._test(no_split, [no_split], cols=100)

    def test_split_internal_else_lines(self):
        data = ['1', '2', '3', '4', '5', '6', '7', '8']
        self._test(data + ['ELSE IF'] + data + ['ELSE'] + data,
                   [['1', '2', '3', '4'],
                    ['...', '5', '6', '7'],
                    ['...', '8'],
                    ['...', 'ELSE IF', '1', '2'],
                    ['...', '3', '4', '5'],
                    ['...', '6', '7', '8'],
                    ['...', 'ELSE', '1', '2'],
                    ['...', '3', '4', '5'],
                    ['...', '6', '7', '8']],
                   cols=4)
        self._test([''] + data + ['ELSE IF'] + data + ['ELSE'] + data,
                   [['', '1', '2', '3', '4', '5', '6', '7'],
                    ['', '...', '8'],
                    ['', '...', 'ELSE IF', '1', '2', '3', '4', '5'],
                    ['', '...', '6', '7', '8'],
                    ['', '...', 'ELSE', '1', '2', '3', '4', '5'],
                    ['', '...', '6', '7', '8']],
                   cols=8)


if __name__ == '__main__':
    unittest.main()
