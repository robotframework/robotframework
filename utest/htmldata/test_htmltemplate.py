import unittest

from robot.htmldata.template import HtmlTemplate
from robot.htmldata import LOG, REPORT
from robot.utils.asserts import assert_true, assert_raises, assert_equal


class TestHtmlTemplate(unittest.TestCase):

    def test_creating(self):
        log = list(HtmlTemplate(LOG))
        assert_true(log[0].startswith('<!DOCTYPE'))
        assert_equal(log[-1], '</html>')

    def test_lines_do_not_have_line_breaks(self):
        for line in HtmlTemplate(REPORT):
            assert_true(not line.endswith('\n'))

    def test_non_existing(self):
        assert_raises(IOError, list, HtmlTemplate('nonex.html'))


if __name__ == "__main__":
    unittest.main()
