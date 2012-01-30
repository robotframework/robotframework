import unittest

from robot.parsing.model import TestCaseTable
from robot.utils.asserts import assert_equals
from robot.writer.aligners import ColumnAligner


class TestColumnAligner(unittest.TestCase):

    def test_counting_column_widths(self):
        table = TestCaseTable(None)
        table.set_header(['test cases', 'col header', 'short'])
        assert_equals(ColumnAligner(18, table)._widths, [18, 10, 5])
        test = table.add('A test')
        test.add_step(['Some kw', 'a longer arg', 'another']    )
        assert_equals(ColumnAligner(18, table)._widths, [18, 10, 12, 7])
