import unittest

from robot.reporting.webcontentfile import WebContentFile
from robot.utils.asserts import assert_true, assert_raises, assert_equals


class TestWebContentFile(unittest.TestCase):

    def test_get_webcontent_file(self):
        log = list(WebContentFile('log.html'))
        assert_true(log[0].startswith('<!DOCTYPE'))
        assert_equals(log[-1], '</html>')

    def test_lines_do_not_have_line_breaks(self):
        for line in WebContentFile('report.html'):
            assert_true(not line.endswith('\n'))

    def test_non_existing(self):
        assert_raises(IOError, list, WebContentFile('nonex.html'))


if __name__ == "__main__":
    unittest.main()
