import unittest

from robot.parsing.txtreader import TxtReader
from robot.utils.asserts import assert_equals


class TestTxtParser(unittest.TestCase):

    def test_split_row_with_pipe(self):
        raw_text = "| col0 | col1   | col2"
        expected = ["col0", "col1", "col2"]
        assert_equals(TxtReader.split_row(raw_text), expected)
        assert_equals(TxtReader().split_row(raw_text), expected)

    def test_split_row_with_trailing_pipe(self):
        raw_text = "| col0 | col1 | col2    |"
        expected = ["col0", "col1", "col2"]
        assert_equals(TxtReader.split_row(raw_text), expected)
        assert_equals(TxtReader().split_row(raw_text), expected)


if __name__ == '__main__':
    unittest.main()
