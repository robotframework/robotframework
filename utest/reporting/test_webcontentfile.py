import unittest

from robot.reporting.webcontentfile import WebContentFile
from robot.utils.asserts import assert_true, assert_raises, assert_equals


class TestRobotFileReading(unittest.TestCase):

    def test_get_webcontent_file(self):
        log = WebContentFile('log.html')
        assert_true(list(log))

    def test_lines_have_line_breaks(self):
        for line in WebContentFile('report.html'):
            assert_equals(line[-1], '\n')

    def test_non_existing(self):
        assert_raises(IOError, list, WebContentFile('nonex.html'))


if __name__ == "__main__":
    unittest.main()
