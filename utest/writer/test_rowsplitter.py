import unittest

from robot.writer.rowsplitter import RowSplitter
from robot.utils.asserts import assert_equals


class TestRowSplitter(unittest.TestCase):

    def _test(self, data, expected, cols=3, table_type='settings'):
        splitter = RowSplitter(cols=cols)
        actual = list(splitter.split(data, table_type))
        assert_equals(actual, expected)

    def test_escaping_empty_cells_at_eol(self):
        self._test(['Some', 'text', '', 'with empty'],
                   [['Some', 'text', '${EMPTY}'],
                    ['...', 'with empty']])

    def test_splitting_inside_comment(self):
        self._test(['Kw', 'Arg', '#Comment in', 'many cells'],
                   [['Kw', 'Arg', '#Comment in'],
                    ['...', '#many cells']])

    def test_splitting_whitespace_rows(self):
        self._test([''] * 4 + ['foo', '#Some random comment'],
                   [['', '', '${EMPTY}'],
                    ['...', '', 'foo'],
                    ['...', '#Some random comment']])
        self._test([''] * 3 + ['foo', '#Some random comment'],
                   [['', '', '${EMPTY}'],
                    ['...', 'foo', '#Some random comment']])
        self._test([''] * 2 + ['foo', '#Some random comment'],
                   [['', '', 'foo'],
                    ['...', '#Some random comment']])


if __name__ == '__main__':
    unittest.main()
