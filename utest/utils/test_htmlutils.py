import unittest

from robot.utils.asserts import *

from robot.utils.htmlutils import html_escape, html_format, html_attr_escape
from robot.utils.htmlformatters import _TableFormatter

_format_table = _TableFormatter()._format_table


def _test_escape_and_format(inp, exp_escape=None, exp_format=None):
    if exp_escape is None:
        exp_escape = str(inp)
    if exp_format is None:
        exp_format = exp_escape
    escape = html_escape(inp)
    format = html_format(inp)
    assert_equals(escape, exp_escape,
                  'ESCAPE:\n%r   =!\n%r' % (escape, exp_escape), values=False)
    assert_equals(format, exp_format,
                  'FORMAT:\n%r   =!\n%r' % (format, exp_format), values=False)


class TestHtmlEscapeAndFormat(unittest.TestCase):

    def test_no_changes(self):
        for inp in ['', 'nothing to change']:
            _test_escape_and_format(inp)

    def test_newlines_and_paragraphs(self):
        for inp in ['Text on first line.\nText on second line.',
                    '1 line\n2 line\n3 line\n4 line\n5 line\n',
                    'Para 1 line 1\nP1 L2\n\nP2 L1\nP2 L1\n\nP3 L1\nP3 L2',
                     'Multiple empty lines\n\n\n\n\nbetween these lines']:
            _test_escape_and_format(inp, inp, inp.rstrip())

    def test_entities(self):
        for char, entity in [('<','&lt;'), ('>','&gt;'), ('&','&amp;')]:
            for inp, exp in [(char, entity),
                             ('text %s' % char, 'text %s' % entity),
                             ('-%s-%s-' % (char, char),
                              '-%s-%s-' % (entity, entity)),
                             ('"%s&%s"' % (char, char),
                              '"%s&amp;%s"' % (entity, entity))]:
                _test_escape_and_format(inp, exp)


class TestLinks(unittest.TestCase):

    def test_not_links(self):
        for nolink in ['http no link', 'http:/no', 'xx://no',
                       'tooolong10://no', 'http://', 'http:// no']:
            _test_escape_and_format(nolink)

    def test_simple_links(self):
        for link in ['http://robot.fi', 'https://r.fi/', 'FTP://x.y.z/p/f.txt',
                     '123456://link', 'file:///c:/temp/xxx.yyy']:
            exp = '<a href="%s">%s</a>' % (link, link)
            _test_escape_and_format(link, exp)
            for end in [',', '.', ';', ':', '!', '?', '...', '!?!', ' hello' ]:
                _test_escape_and_format(link+end, exp+end)
                _test_escape_and_format('xxx '+link+end, 'xxx '+exp+end)
            for start, end in [ ('(',')'), ('[',']'), ('"','"'), ("'","'") ]:
                _test_escape_and_format(start+link+end, start+exp+end)

    def test_complex_links(self):
        for inp, exp in [
                ('hello http://link world',
                 'hello <a href="http://link">http://link</a> world'),
                ('multi\nhttp://link\nline',
                 'multi\n<a href="http://link">http://link</a>\n'
                 'line'),
                ('http://link, ftp://link2.',
                 '<a href="http://link">http://link</a>, '
                 '<a href="ftp://link2">ftp://link2</a>.'),
                ('x (http://y, z)',
                 'x (<a href="http://y">http://y</a>, z)'),
                ('Hello http://one, ftp://kaksi/; "gopher://3.0"',
                 'Hello <a href="http://one">http://one</a>, '
                 '<a href="ftp://kaksi/">ftp://kaksi/</a>; '
                 '"<a href="gopher://3.0">gopher://3.0</a>"') ]:
            _test_escape_and_format(inp, exp)

    def test_image_links(self):
        link = '(<a href="%s">%s</a>)'
        img = '(<img src="%s" title="%s" class="robotdoc">)'
        for ext in ['jpg', 'jpeg', 'png', 'gif', 'bmp']:
            url = 'foo://bar/zap.%s' % ext
            uprl = url.upper()
            inp = '(%s)' % url
            _test_escape_and_format(inp, link % (url, url), img % (url, url))
            _test_escape_and_format(inp.upper(), link % (uprl, uprl),
                                    img % (uprl, uprl))

    def test_link_with_chars_needed_escaping(self):
        assert_equals(html_escape('http://foo"bar'),
                      '<a href="http://foo&quot;bar">http://foo&quot;bar</a>')
        assert_equals(html_escape('ftp://<&>/'),
                      '<a href="ftp://&lt;&amp;&gt;/">ftp://&lt;&amp;&gt;/</a>')


class TestHtmlFormat(unittest.TestCase):

    def test_one_word_bold(self):
        for inp, exp in [('*bold*', '<b>bold</b>'),
                         ('*b*', '<b>b</b>'),
                         ('*many bold words*', '<b>many bold words</b>'),
                         (' *bold*', ' <b>bold</b>'),
                         ('*bold* ', '<b>bold</b> '),
                         ('xx *bold*', 'xx <b>bold</b>'),
                         ('*bold* xx', '<b>bold</b> xx'),
                         ('***', '<b>*</b>'),
                         ('****', '<b>**</b>'),
                         ('*****', '<b>***</b>')]:
            assert_equals(html_format(inp), exp, "'%s'" % inp)

    def test_multiple_word_bold(self):
        for inp, exp in [('*bold* *b* not bold *b3* not',
                          '<b>bold</b> <b>b</b> not bold <b>b3</b> not'),
                         ('not b *this is b* *more b words here*',
                          'not b <b>this is b</b> <b>more b words here</b>'),
                         ('*** not *b* ***',
                          '<b>*</b> not <b>b</b> <b>*</b>')]:
            assert_equals(html_format(inp), exp, "'%s'" % inp)

    def test_bold_on_multiple_lines(self):
        inp = 'this is *bold*\nand *this*\nand *that*'
        exp = 'this is <b>bold</b>\nand <b>this</b>\nand <b>that</b>'
        assert_equals(html_format(inp), exp)
        inp2 = 'this *does not\nwork*'
        assert_equals(html_format(inp2), inp2.replace('\n','\n'))

    def test_not_bolded_if_no_content(self):
        assert_equals(html_format('**'), '**')

    def test_asterisk_in_the_middle_of_word_is_ignored(self):
        for inp, exp in [('aa*notbold*bbb', None),
                         ('*bold*still bold*', '<b>bold*still bold</b>'),
                         ('a*not*b c*still not*d', None),
                         ('*b*b2* -*n*- *b3*', '<b>b*b2</b> -*n*- <b>b3</b>')]:
            if exp is None: exp = inp
            assert_equals(html_format(inp), exp)

    def test_asterisk_alone_does_not_start_bolding(self):
        for inp, exp in [('*', None),
                         (' * ', None),
                         ('* not *', None),
                         (' * not * ', None),
                         ('* not*', None),
                         ('*bold *', '<b>bold </b>'),
                         ('* *b* *', '* <b>b</b> *'),
                         ('*bold * not*', '<b>bold </b> not*'),
                         ('*bold * not*not* *b*',
                          '<b>bold </b> not*not* <b>b</b>')]:
            if exp is None: exp = inp
            assert_equals(html_format(inp), exp)

    def test_one_word_italic(self):
        for inp, exp in [('_italic_', '<i>italic</i>'),
                         ('_i_', '<i>i</i>'),
                         ('_many italic words_', '<i>many italic words</i>'),
                         (' _italic_', ' <i>italic</i>'),
                         ('_italic_ ', '<i>italic</i> '),
                         ('xx _italic_', 'xx <i>italic</i>'),
                         ('_italic_ xx', '<i>italic</i> xx')]:
            assert_equals(repr(html_format(inp)), repr(exp), "'%s'" % inp)

    def test_multiple_word_italic(self):
        for inp, exp in [('_italic_ _i_ not italic _i3_ not',
                          '<i>italic</i> <i>i</i> not italic <i>i3</i> not'),
                         ('not i _this is i_ _more i words here_',
                          'not i <i>this is i</i> <i>more i words here</i>')]:
            assert_equals(html_format(inp), exp, "'%s'" % inp)

    def test_not_italiced_if_no_content(self):
        assert_equals(html_format('__'), '__')

    def test_not_italiced_many_underlines(self):
        for text in ['___', '____', '_________', '__len__']:
            assert_equals(html_format(text), text)

    def test_underscore_in_the_middle_of_word_is_ignored(self):
        for inp, exp in [('aa_notitalic_bbb', None),
                         ('_ital_still ital_', '<i>ital_still ital</i>'),
                         ('a_not_b c_still not_d', None),
                         ('_b_b2_ -_n_- _b3_', '<i>b_b2</i> -_n_- <i>b3</i>')]:
            if exp is None: exp = inp
            assert_equals(html_format(inp), exp)

    def test_underscore_alone_does_not_start_italicing(self):
        for inp, exp in [('_', None),
                         (' _ ', None),
                         ('_ not _', None),
                         (' _ not _ ', None),
                         ('_ not_', None),
                         ('_italic _', '<i>italic </i>'),
                         ('_ _b_ _', '_ <i>b</i> _'),
                         ('_italic _ not_', '<i>italic </i> not_'),
                         ('_italic _ not_not_ _b_',
                          '<i>italic </i> not_not_ <i>b</i>')]:
            if exp is None: exp = inp
            assert_equals(html_format(inp), exp)

    def test_bold_and_italic(self):
        for inp, exp in [ ('*b* _i_', '<b>b</b> <i>i</i>') ]:
            assert_equals(html_format(inp), exp)

    def test_bold_and_italic_works_with_punctuation_marks(self):
        for bef, aft in [('(',''), ('"',''), ("'",''), ('(\'"(',''),
                         ('',')'), ('','"'), ('',','), ('','"\').,!?!?:;'),
                         ('(',')'), ('"','"'), ('("\'','\'";)'), ('"','..."')]:
            for inp, exp in [('*bold*','<b>bold</b>'),
                             ('_ital_','<i>ital</i>'),
                             ('*b* _i_','<b>b</b> <i>i</i>')]:
                inp = bef + inp + aft
                exp = bef + exp + aft
                assert_equals(html_format(inp), exp)

    def test_bold_italic(self):
        for inp, exp in [('_*bi*_', '<i><b>bi</b></i>'),
                         ('_*bold ital*_', '<i><b>bold ital</b></i>'),
                         ('_*bi* i_', '<i><b>bi</b> i</i>'),
                         ('_*bi_ b*', '<i><b>bi</i> b</b>'),
                         ('_i *bi*_', '<i>i <b>bi</b></i>'),
                         ('*b _bi*_', '<b>b <i>bi</b></i>')]:
            assert_equals(html_format(inp), exp)

    def test_one_row_table(self):
        inp = '| one | two |'
        exp = _format_table([['one','two']])
        assert_equals(html_format(inp), exp)

    def test_multi_row_table(self):
        inp = '| 1.1 | 1.2 | 1.3 |\n| 2.1 | 2.2 |\n| 3.1 | 3.2 | 3.3 |\n'
        exp = _format_table([['1.1','1.2','1.3'],
                             ['2.1','2.2'],
                             ['3.1','3.2','3.3']])
        assert_equals(html_format(inp), exp)

    def test_table_with_extra_spaces(self):
        inp = '  |   1.1   |  1.2   |  \n   | 2.1 | 2.2 |    '
        exp = _format_table([['1.1','1.2',],['2.1','2.2']])
        assert_equals(html_format(inp), exp)

    def test_table_with_one_space_empty_cells(self):
        inp = '''
| 1.1 | 1.2 | |
| 2.1 | | 2.3 |
| | 3.2 | 3.3 |
| 4.1 | | |
| | 5.2 | |
| | | 6.3 |
| | | |
'''[1:-1]
        exp = _format_table([['1.1','1.2',''],
                             ['2.1','','2.3'],
                             ['','3.2','3.3'],
                             ['4.1','',''],
                             ['','5.2',''],
                             ['','','6.3'],
                             ['','','']])
        assert_equals(html_format(inp), exp)

    def test_one_column_table(self):
        inp = '|  one column |\n| |\n  |  |  \n| 2 | col |\n|          |'
        exp = _format_table([['one column'],[''],[''],['2','col'],['']])
        assert_equals(html_format(inp), exp)

    def test_table_with_other_content_around(self):
        inp = '''before table
| in | table |
| still | in |

 after table
'''
        exp = 'before table\n' \
            + _format_table([['in','table'],['still','in']]) \
            + '\n after table'
        assert_equals(html_format(inp), exp)

    def test_multiple_tables(self):
        inp = '''before tables
| table | 1 |
| still | 1 |

between

| table | 2 |
between
| 3.1.1 | 3.1.2 | 3.1.3 |
| 3.2.1 | 3.2.2 | 3.2.3 |
| 3.3.1 | 3.3.2 | 3.3.3 |

| t | 4 |
|   |   |

after
'''
        exp = 'before tables\n' \
            + _format_table([['table','1'],['still','1']]) \
            + '\nbetween\n\n' \
            + _format_table([['table','2']]) \
            + 'between\n' \
            + _format_table([['3.1.1','3.1.2','3.1.3'],
                             ['3.2.1','3.2.2','3.2.3'],
                             ['3.3.1','3.3.2','3.3.3']]) \
            + '\n' \
            + _format_table([['t','4'],['','']]) \
            + '\nafter'
        assert_equals(html_format(inp), exp)

    def test_ragged_table(self):
        inp = '''
| 1.1 | 1.2 | 1.3 |
| 2.1 |
| 3.1 | 3.2 |
'''
        exp = '\n' \
            + _format_table([['1.1','1.2','1.3'],
                             ['2.1','',''],
                             ['3.1','3.2','']])
        assert_equals(html_format(inp), exp)

    def test_bold_in_table_cells(self):
        inp = '''
| *a* | *b* | *c* |
| *b* |  x  |  y  |
| *c* |  z  |     |

| a   | x *b* y | *b* *c* |
| *a  | b*      |         |
'''
        exp = '\n' \
            + _format_table([['<b>a</b>','<b>b</b>','<b>c</b>'],
                             ['<b>b</b>','x','y'],
                             ['<b>c</b>','z','']]) \
            + '\n' \
            + _format_table([['a','x <b>b</b> y','<b>b</b> <b>c</b>'],
                             ['*a','b*','']])
        assert_equals(html_format(inp), exp)

    def test_italic_in_table_cells(self):
        inp = '''
| _a_ | _b_ | _c_ |
| _b_ |  x  |  y  |
| _c_ |  z  |     |

| a   | x _b_ y | _b_ _c_ |
| _a  | b_      |         |
'''
        exp = '\n' \
            + _format_table([['<i>a</i>','<i>b</i>','<i>c</i>'],
                             ['<i>b</i>','x','y'],
                             ['<i>c</i>','z','']]) \
            + '\n' \
            +  _format_table([['a','x <i>b</i> y','<i>b</i> <i>c</i>'],
                              ['_a','b_','']])
        assert_equals(html_format(inp), exp)

    def test_bold_and_italic_in_table_cells(self):
        inp = '''
| *a* | *b* | *c* |
| _b_ |  x  |  y  |
| _c_ |  z  | *b* _i_ |
'''
        exp = '\n' \
            + _format_table([['<b>a</b>','<b>b</b>','<b>c</b>'],
                             ['<i>b</i>','x','y'],
                             ['<i>c</i>','z','<b>b</b> <i>i</i>']])
        assert_equals(html_format(inp), exp)

    def test_link_in_table_cell(self):
        inp = '''
| 1 | http://one |
| 2 | ftp://two/ |
'''
        exp = '\n' \
            + _format_table([['1','<a href="http://one">http://one</a>'],
                             ['2','<a href="ftp://two/">ftp://two/</a>']])
        assert_equals(html_format(inp), exp)

    def test_hr_is_three_or_more_hyphens(self):
        for i in range(3, 100):
            hr = '-' * i
            assert_equals(html_format(hr), '<hr>')
            assert_equals(html_format(hr + '  '), '<hr>')

    def test_hr_with_other_stuff_around(self):
        for inp, exp in [('---\n-', '<hr>-'),
                         ('xx\n---\nxx', 'xx\n<hr>xx'),
                         ('xx\n\n------\n\nxx', 'xx\n\n<hr>\nxx')]:
            assert_equals(html_format(inp), exp)

    def test_not_hr(self):
        for inp in ['-', '--', ' ---', ' --- ', '...---...', '===']:
            assert_equals(html_format(inp), inp)

    def test_hr_before_and_after_table(self):
        inp = '''
---
| t | a | b | l | e |
---
'''[1:-1]
        exp = '<hr>' \
            + _format_table([['t','a','b','l','e']]) \
            + '<hr>'
        assert_equals(html_format(inp), exp)


class TestPreformattedBlock(unittest.TestCase):

    def test_single_line_block(self):
        self._assert_preformatted('| some', 'some')

    def test_multi_line_block(self):
        self._assert_preformatted('| some\n| quote', 'some\nquote')

    def test_additional_whitespace_is_preserved(self):
        self._assert_preformatted('|   some\t ', '  some\t ')

    def test_spaces_before_leading_pipe_cause_no_formatting(self):
        assert_equals(html_format(' | some'), ' | some')

    def test_block_mixed_with_other_content(self):
        assert_equals(html_format('before block:\n| some\n| quote\nafter block'),
                'before block:\n<pre class="robotdoc">\nsome\nquote\n</pre>\nafter block')

    def test_block_line_with_other_formatting(self):
        self._assert_preformatted('| _some_', '<i>some</i>')

    def _assert_preformatted(self, input, expected):
        expected = '<pre class="robotdoc">\n' + expected + '\n</pre>'
        assert_equals(html_format(input), expected)


class TestFormatTable(unittest.TestCase):
    _table_start = '<table class="robotdoc">'

    def test_one_row_table(self):
        inp = [['1','2','3']]
        exp = self._table_start + '''
<tr>
<td>1</td>
<td>2</td>
<td>3</td>
</tr>
</table>'''
        assert_equals(_format_table(inp), exp)

    def test_multi_row_table(self):
        inp = [['1.1','1.2'], ['2.1','2.2'], ['3.1','3.2']]
        exp = self._table_start + '''
<tr>
<td>1.1</td>
<td>1.2</td>
</tr>
<tr>
<td>2.1</td>
<td>2.2</td>
</tr>
<tr>
<td>3.1</td>
<td>3.2</td>
</tr>
</table>'''
        assert_equals(_format_table(inp), exp)

    def test_fix_ragged_table(self):
        inp = [['1.1','1.2','1.3'], ['2.1'], ['3.1','3.2']]
        exp = self._table_start + '''
<tr>
<td>1.1</td>
<td>1.2</td>
<td>1.3</td>
</tr>
<tr>
<td>2.1</td>
<td></td>
<td></td>
</tr>
<tr>
<td>3.1</td>
<td>3.2</td>
<td></td>
</tr>
</table>'''
        assert_equals(_format_table(inp), exp)


class TestHtmlAttrEscape(unittest.TestCase):

    def test_nothing_to_escape(self):
        for inp in ['', 'whatever', 'nothing here, move along']:
            assert_equals(html_attr_escape(inp), inp)

    def test_html_entities(self):
        for inp, exp in [('"', '&quot;'), ('<', '&lt;'), ('>', '&gt;'),
                         ('&', '&amp;'), ('&<">&', '&amp;&lt;&quot;&gt;&amp;'),
                         ('Sanity < "check"', 'Sanity &lt; &quot;check&quot;')]:
            assert_equals(html_attr_escape(inp), exp)

    def test_newlines_and_tabs(self):
        for inp, exp in [('\n', ' '), ('\t', ' '), ('"\n\t"', '&quot;  &quot;'),
                         ('N1\nN2\n\nT1\tT3\t\t\t', 'N1 N2  T1 T3   ')]:
            assert_equals(html_attr_escape(inp), exp)


if __name__ == '__main__':
    unittest.main()

