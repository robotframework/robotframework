import unittest

from robot.writer.formatters import Formatter, TxtFormatter, Cell
from robot.utils.asserts import assert_equals


class TestTxtFormatter(unittest.TestCase):

    def test_escaping_empty_cells_at_eol(self):
        formatter = Formatter(cols=3)
        assert_equals(formatter.format(['Some', 'text', '', 'with empty'], 0),
                                       [['Some', 'text', '${EMPTY}'],
                                        ['...', 'with empty']])

    def test_escaping(self):
        formatter = TxtFormatter()
        assert_equals(formatter.format(['so  me']), [['so \ me']])


class TestHtmlFormatter(unittest.TestCase):

    def test_add_br_to_newlines(self):
        original = """This is real new line:
        here we have a single backslash n: \\n and here backslash + newline: \\\n and here bslash blash n \\\\n and bslash x 3 n \\\\\\n """
        expected = 'This is real new line:\n        here we have a single backslash n: \\n<br>\nand here backslash + newline: \\\n and here bslash blash n \\\\n and bslash x 3 n \\\\\\n<br>\n'
        assert_equals(Cell(original).content, expected)

    def test_no_br_to_newlines_without_whitespace(self):
        original = r"Here there is no space after backslash-n: '\n'"
        assert_equals(Cell(original).content, original)

    def test_no_br_to_double_backslashes(self):
        original = r"Here there is double backslash-n: \\n "
        assert_equals(Cell(original).content, original)


if __name__ == "__main__":
    unittest.main()
