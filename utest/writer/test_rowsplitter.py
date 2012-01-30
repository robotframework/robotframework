import unittest

from robot.writer.rowsplitter import RowSplitter
from robot.utils.asserts import assert_equals


class TestRowSplitter(unittest.TestCase):

    def test_escaping_empty_cells_at_eol(self):
        formatter = RowSplitter(cols=3)
        assert_equals(formatter.split(['Some', 'text', '', 'with empty'], 0),
            [['Some', 'text', '${EMPTY}'],
                ['...', 'with empty']])

    def test_splitting_inside_comment(self):
        formatter = RowSplitter(cols=3)
        assert_equals(formatter.split(['Kw', 'Arg', '#Comment in', 'many cells'], 0),
            [['Kw', 'Arg', '#Comment in'], ['...', '#many cells']])
