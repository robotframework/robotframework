import unittest

from robot.writer.rowsplitter import RowSplitter
from robot.utils.asserts import assert_equals


class TestRowSplitter(unittest.TestCase):

    def setUp(self):
        self._cols = 3
        self._formatter = RowSplitter(cols=self._cols)

    def test_escaping_empty_cells_at_eol(self):
        assert_equals(self._formatter.split(['Some', 'text', '', 'with empty']),
            [['Some', 'text', '${EMPTY}'],
                ['...', 'with empty']])

    def test_splitting_inside_comment(self):
        assert_equals(self._formatter.split(['Kw', 'Arg', '#Comment in', 'many cells']),
            [['Kw', 'Arg', '#Comment in'], ['...', '#many cells']])

    def test_splitting_whitespace_rows(self):
        # Checking loop border case conditions in row splitting mechanism
        # Based on
        assert_equals(self._formatter.split(['']*(self._cols+1)+['foo', '#Some random comment']),
            [['', '', '${EMPTY}'],
             ['...', '', 'foo'],
             ['...', '#Some random comment']])
        assert_equals(self._formatter.split(['']*self._cols+['foo', '#Some random comment']),
            [['', '', '${EMPTY}'],
             ['...', 'foo', '#Some random comment']])
        assert_equals(self._formatter.split(['']*(self._cols-1)+['foo', '#Some random comment']),
            [['', '', 'foo'],
             ['...', '#Some random comment']])
