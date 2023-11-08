import unittest
from io import StringIO

from robot.utils import HtmlWriter
from robot.utils.asserts import assert_equal


class TestHtmlWriter(unittest.TestCase):

    def setUp(self):
        self.output = StringIO()
        self.writer = HtmlWriter(self.output)

    def test_start(self):
        self.writer.start('r')
        self._verify('<r>\n')

    def test_start_without_newline(self):
        self.writer.start('robot', newline=False)
        self._verify('<robot>')

    def test_start_with_attribute(self):
        self.writer.start('robot', {'name': 'Suite1'}, False)
        self._verify('<robot name="Suite1">')

    def test_start_with_attributes(self):
        self.writer.start('test', {'class': '123', 'x': 'y', 'a': 'z'})
        self._verify('<test a="z" class="123" x="y">\n')

    def test_start_with_non_ascii_attributes(self):
        self.writer.start('test', {'name': '§', 'ä': '§'})
        self._verify('<test name="§" ä="§">\n')

    def test_start_with_quotes_in_attribute_value(self):
        self.writer.start('x', {'q':'"', 'qs': '""""', 'a': "'"}, False)
        self._verify('<x a="\'" q="&quot;" qs="&quot;&quot;&quot;&quot;">')

    def test_start_with_html_in_attribute_values(self):
        self.writer.start('x', {'1':'<', '2': '&', '3': '</html>'}, False)
        self._verify('<x 1="&lt;" 2="&amp;" 3="&lt;/html&gt;">')

    def test_start_with_newlines_and_tabs_in_attribute_values(self):
        self.writer.start('x', {'1':'\n', '3': 'A\nB\tC', '2': '\t', '4': '\r\n'}, False)
        self._verify('<x 1="&#10;" 2="&#09;" 3="A&#10;B&#09;C" 4="&#13;&#10;">')

    def test_end(self):
        self.writer.start('robot', newline=False)
        self.writer.end('robot')
        self._verify('<robot></robot>\n')

    def test_end_without_newline(self):
        self.writer.start('robot', newline=False)
        self.writer.end('robot', newline=False)
        self._verify('<robot></robot>')

    def test_end_alone(self):
        self.writer.end('suite', newline=False)
        self._verify('</suite>')

    def test_content(self):
        self.writer.start('robot')
        self.writer.content('Hello world!')
        self._verify('<robot>\nHello world!')

    def test_content_with_non_ascii_data(self):
        self.writer.start('robot', newline=False)
        self.writer.content('Circle is 360°. ')
        self.writer.content('Hyvää üötä!')
        self.writer.end('robot', newline=False)
        self._verify('<robot>Circle is 360°. Hyvää üötä!</robot>')

    def test_multiple_content(self):
        self.writer.start('robot')
        self.writer.content('Hello world!')
        self.writer.content('Hi again!')
        self._verify('<robot>\nHello world!Hi again!')

    def test_content_with_chars_needing_escaping(self):
        self.writer.content('Me, "Myself" & I > U')
        self._verify('Me, "Myself" &amp; I &gt; U')

    def test_content_alone(self):
        self.writer.content('hello')
        self._verify('hello')

    def test_none_content(self):
        self.writer.start('robot')
        self.writer.content(None)
        self.writer.content('')
        self._verify('<robot>\n')

    def test_element(self):
        self.writer.element('div', 'content', {'id': '1'})
        self.writer.element('i', newline=False)
        self._verify('<div id="1">content</div>\n<i></i>')

    def test_line_separator(self):
        output = StringIO()
        writer = HtmlWriter(output)
        writer.start('b')
        writer.end('b')
        writer.element('i')
        assert_equal(output.getvalue(), '<b>\n</b>\n<i></i>\n')

    def test_non_ascii(self):
        self.output = StringIO()
        writer = HtmlWriter(self.output)
        writer.start('p', attrs={'name': 'hyvää'}, newline=False)
        writer.content('yö')
        writer.element('i', 'tä', newline=False)
        writer.end('p', newline=False)
        self._verify('<p name="hyvää">yö<i>tä</i></p>')

    def _verify(self, expected):
        assert_equal(self.output.getvalue(), expected)


if __name__ == '__main__':
    unittest.main()
