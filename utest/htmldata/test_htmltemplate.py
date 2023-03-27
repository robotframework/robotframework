import unittest

from robot.htmldata.template import HtmlTemplate
from robot.htmldata import LOG, REPORT
from robot.utils.asserts import assert_true, assert_equal, assert_raises


class TestHtmlTemplate(unittest.TestCase):

    def test_creating(self):
        log = list(HtmlTemplate(LOG))
        assert_true(log[0].startswith('<!DOCTYPE'))
        assert_equal(log[-1], '</html>')

    def test_lines_do_not_have_line_breaks(self):
        for line in HtmlTemplate(REPORT):
            assert_true(not line.endswith('\n'))

    def test_bad_path(self):
        assert_raises(ValueError, HtmlTemplate, 'one_part.html')
        assert_raises(ValueError, HtmlTemplate, 'more_than/two/parts.html')

    def test_non_existing(self):
        assert_raises((ImportError, IOError), list, HtmlTemplate('non/ex.html'))


if __name__ == "__main__":
    unittest.main()
