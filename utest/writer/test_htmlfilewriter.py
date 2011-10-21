import unittest

from robot.utils.asserts import assert_equals
from robot.writer.writer import HtmlFileWriter


class TestHtmlFileWriter(unittest.TestCase):

    def setUp(self):
        self._writer = HtmlFileWriter(None)

    def test_add_br_to_newlines(self):
        original = """This is real new line:
        here we have a single backslash n: \\n and here backslash + newline: \\\n and here bslash blash n \\\\n and bslash x 3 n \\\\\\n """
        expected = 'This is real new line:\n        here we have a single backslash n: \\n<br>\nand here backslash + newline: \\\n and here bslash blash n \\\\n and bslash x 3 n \\\\\\n<br>\n'
        assert_equals(self._writer._add_br_to_newlines(original), expected)

    def test_no_br_to_newlines_without_whitespace(self):
        original = r"Here there is no space after backslash-n: '\n'"
        assert_equals(self._writer._add_br_to_newlines(original), original)

    def test_no_br_to_double_backslashes(self):
        original = r"Here there is double backslash-n: \\n "
        assert_equals(self._writer._add_br_to_newlines(original), original)


if __name__ == "__main__":
    unittest.main()
