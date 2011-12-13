import os, sys, unittest
from StringIO import StringIO

from robot.errors import *
from robot import utils
from robot.utils import HtmlWriter
from robot.utils.asserts import *


class IOMock:

    def __init__(self):
        self.texts = []

    def write(self, text):
        self.texts.append(text)

    def close(self):
        pass

    def getvalue(self):
        return ''.join(self.texts)


class TestHtmlWriter(unittest.TestCase):

    def setUp(self):
        self.out = IOMock()
        self.writer = HtmlWriter(self.out)

    def test_start(self):
        self.writer.start('r')
        self._verify('<r>\n')

    def test_start_without_newline(self):
        self.writer.start('robot', newline=False)
        self._verify('<robot>')

    def test_start_with_attribute(self):
        self.writer.start('robot', newline=False)
        self.writer.start('suite', {'name': 'Suite1'}, False)
        self._verify('<robot><suite name="Suite1">')

    def test_start_with_attribute2(self):
        self.writer.start('test case', {'class': '123'})
        self._verify('<test case class="123">\n')

    def test_start_with_attributes(self):
        self.writer.start('test case', {'class': '123', 'x': 'y'})
        self._verify('<test case class="123" x="y">\n')

    def test_start_with_non_ascii_attributes(self):
        self.writer.start('test', {'name': u'\u00A7', u'\u00E4': u'\u00A7'})
        self._verify(u'<test name="\u00A7" \u00E4="\u00A7">\n')

    def test_start_with_quotes_in_attribute_value(self):
        self.writer.start('x', {'q':'"', 'qs': '""""', 'a': "'"}, False)
        self._verify('<x a="\'" q="&quot;" qs="&quot;&quot;&quot;&quot;">')

    def test_start_with_html_in_attribute_values(self):
        self.writer.start('x', {'1':'<', '2': '&', '3': '</html>'}, False)
        self._verify('<x 1="&lt;" 2="&amp;" 3="&lt;/html&gt;">')

    def test_start_with_newlines_and_tabs_in_attribute_values(self):
        self.writer.start('x', {'1':'\n', '3': 'A\nB\tC', '2': '\t'}, False)
        self._verify('<x 1=" " 2=" " 3="A B C">')

    def test_end(self):
        self.writer.start('robot', newline=False)
        self.writer.end('robot')
        self._verify('<robot></robot>\n')

    def test_end_without_newline(self):
        self.writer.start('robot', newline=False)
        self.writer.end('robot', newline=False)
        self._verify('<robot></robot>')

    def test_content(self):
        self.writer.start('robot')
        self.writer.content('Hello world!')
        self._verify('<robot>\nHello world!')

    def test_content_with_non_ascii_data(self):
        self.writer.start('robot', newline=False)
        self.writer.content(u'Circle is 360\u00B0. ')
        self.writer.content(u'Hyv\u00E4\u00E4 \u00FC\u00F6t\u00E4!')
        self.writer.end('robot', newline=False)
        expected = u'Circle is 360\u00B0. Hyv\u00E4\u00E4 \u00FC\u00F6t\u00E4!'
        self._verify('<robot>%s</robot>' % expected)

    def test_multiple_content(self):
        self.writer.start('robot')
        self.writer.content('Hello world!')
        self.writer.content('Hi again!')
        self._verify('<robot>\nHello world!Hi again!')

    def test_content_with_chars_needing_escaping(self):
        self.writer.content('Me, "Myself" & I > U')
        self._verify('Me, "Myself" &amp; I &gt; U')

    def test_none_content(self):
        self.writer.start('robot')
        self.writer.content(None)
        self._verify('<robot>\n')

    def test_close_empty(self):
        self.writer.end('suite', False)
        self._verify('</suite>')

    def _verify(self, expected):
        assert_equals(self.out.getvalue(), expected.replace('\n', os.linesep))


if __name__ == '__main__':
    unittest.main()
