import unittest

from robot.parsing.robotreader import RobotReader
from robot.parsing.txtreader import TxtReader
from robot.utils.asserts import assert_equal


class TestRobotReader(unittest.TestCase):
    Reader = RobotReader

    def test_split_row_with_pipe(self):
        raw_text = "| col0 | col1   | col2"
        expected = ["col0", "col1", "col2"]
        assert_equal(self.Reader.split_row(raw_text), expected)
        assert_equal(self.Reader().split_row(raw_text), expected)

    def test_split_row_with_trailing_pipe(self):
        raw_text = "| col0 | col1 | col2    |"
        expected = ["col0", "col1", "col2"]
        assert_equal(self.Reader.split_row(raw_text), expected)
        assert_equal(self.Reader().split_row(raw_text), expected)


class TestDeprecatedTxtReader(TestRobotReader):
    Reader = TxtReader


if __name__ == '__main__':
    unittest.main()
