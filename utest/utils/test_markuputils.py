import unittest

from robot.utils.asserts import assert_equals

from robot.utils.markuputils import html_escape, html_format, attribute_escape, xml_escape
from robot.utils.htmlformatters import TableFormatter

_format_table = TableFormatter()._format_table


def assert_escape_and_format(inp, exp_escape=None, exp_format=None):
    if exp_escape is None:
        exp_escape = str(inp)
    if exp_format is None:
        exp_format = exp_escape
    exp_format = '<p>%s</p>' % exp_format.replace('\n', ' ')
    escape = html_escape(inp)
    format = html_format(inp)
    assert_equals(escape, exp_escape,
                  'ESCAPE:\n%r   =!\n%r' % (escape, exp_escape), values=False)
    assert_equals(format, exp_format,
                  'FORMAT:\n%r   =!\n%r' % (format, exp_format), values=False)

def assert_format(inp, exp=None, p=False):
    exp = exp if exp is not None else inp
    if p:
        exp = '<p>%s</p>' % exp
    assert_equals(html_format(inp), exp)

def assert_escape(inp, exp=None):
    exp = exp if exp is not None else inp
    assert_equals(html_escape(inp), exp)


class TestHtmlEscape(unittest.TestCase):

    def test_no_changes(self):
        for inp in ['', 'nothing to change']:
            assert_escape(inp)

    def test_newlines_and_paragraphs(self):
        for inp in ['Text on first line.\nText on second line.',
                    '1 line\n2 line\n3 line\n4 line\n5 line\n',
                    'Para 1 line 1\nP1 L2\n\nP2 L1\nP2 L1\n\nP3 L1\nP3 L2',
                     'Multiple empty lines\n\n\n\n\nbetween these lines']:
            assert_escape(inp)


class TestEntities(unittest.TestCase):

    def test_entities(self):
        for char, entity in [('<','&lt;'), ('>','&gt;'), ('&','&amp;')]:
            for inp, exp in [(char, entity),
                             ('text %s' % char, 'text %s' % entity),
                             ('-%s-%s-' % (char, char),
                              '-%s-%s-' % (entity, entity)),
                             ('"%s&%s"' % (char, char),
                              '"%s&amp;%s"' % (entity, entity))]:
                assert_escape_and_format(inp, exp)


class TestUrlsToLinks(unittest.TestCase):

    def test_not_links(self):
        for nolink in ['http no link', 'http:/no', 'xx://no',
                       'tooolong10://no', 'http://', 'http:// no']:
            assert_escape_and_format(nolink)

    def test_simple_links(self):
        for link in ['http://robot.fi', 'https://r.fi/', 'FTP://x.y.z/p/f.txt',
                     '123456://link', 'file:///c:/temp/xxx.yyy']:
            exp = '<a href="%s">%s</a>' % (link, link)
            assert_escape_and_format(link, exp)
            for end in [',', '.', ';', ':', '!', '?', '...', '!?!', ' hello' ]:
                assert_escape_and_format(link+end, exp+end)
                assert_escape_and_format('xxx '+link+end, 'xxx '+exp+end)
            for start, end in [('(',')'), ('[',']'), ('"','"'), ("'","'")]:
                assert_escape_and_format(start+link+end, start+exp+end)

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
                 '"<a href="gopher://3.0">gopher://3.0</a>"')]:
            assert_escape_and_format(inp, exp)

    def test_image_links(self):
        link = '(<a href="%s">%s</a>)'
        img = '(<img src="%s" title="%s">)'
        for ext in ['jpg', 'jpeg', 'png', 'gif', 'bmp']:
            url = 'foo://bar/zap.%s' % ext
            uprl = url.upper()
            inp = '(%s)' % url
            assert_escape_and_format(inp, link % (url, url), img % (url, url))
            assert_escape_and_format(inp.upper(), link % (uprl, uprl),
                                    img % (uprl, uprl))

    def test_link_with_chars_needed_escaping(self):
        for items in [
            ('http://foo"bar',
             '<a href="http://foo&quot;bar">http://foo"bar</a>'),
            ('ftp://<&>/',
             '<a href="ftp://&lt;&amp;&gt;/">ftp://&lt;&amp;&gt;/</a>'),
            ('http://x&".png',
            '<a href="http://x&amp;&quot;.png">http://x&amp;".png</a>',
            '<img src="http://x&amp;&quot;.png" title="http://x&amp;&quot;.png">')
        ]:
            assert_escape_and_format(*items)


class TestFormatParagraph(unittest.TestCase):

    def test_empty(self):
        assert_format('', '')

    def test_single_line(self):
        assert_format('foo', '<p>foo</p>')

    def test_multi_line(self):
        assert_format('foo\nbar', '<p>foo bar</p>')

    def test_leading_and_trailing_spaces(self):
        assert_format('  foo  \n  bar', '<p>foo bar</p>')

    def test_multiple_paragraphs(self):
        assert_format('P\n1\n\nP 2', '<p>P 1</p>\n<p>P 2</p>')

    def test_leading_empty_line(self):
        assert_format('\nP', '<p>P</p>')

    def test_other_formatted_content_before_paragraph(self):
        assert_format('---\nP', '<hr>\n<p>P</p>')
        assert_format('| PRE \nP', '<pre>\nPRE\n</pre>\n<p>P</p>')

    def test_other_formatted_content_after_paragraph(self):
        assert_format('P\n---', '<p>P</p>\n<hr>')
        assert_format('P\n| PRE \n', '<p>P</p>\n<pre>\nPRE\n</pre>')


class TestHtmlFormatBoldAndItalic(unittest.TestCase):

    def test_one_word_bold(self):
        for inp, exp in [('*bold*', '<b>bold</b>'),
                         ('*b*', '<b>b</b>'),
                         ('*many bold words*', '<b>many bold words</b>'),
                         (' *bold*', '<b>bold</b>'),
                         ('*bold* ', '<b>bold</b>'),
                         ('xx *bold*', 'xx <b>bold</b>'),
                         ('*bold* xx', '<b>bold</b> xx'),
                         ('***', '<b>*</b>'),
                         ('****', '<b>**</b>'),
                         ('*****', '<b>***</b>')]:
            assert_format(inp, exp, p=True)

    def test_multiple_word_bold(self):
        for inp, exp in [('*bold* *b* not bold *b3* not',
                          '<b>bold</b> <b>b</b> not bold <b>b3</b> not'),
                         ('not b *this is b* *more b words here*',
                          'not b <b>this is b</b> <b>more b words here</b>'),
                         ('*** not *b* ***',
                          '<b>*</b> not <b>b</b> <b>*</b>')]:
            assert_format(inp, exp, p=True)

    def test_bold_on_multiple_lines(self):
        inp = 'this is *bold*\nand *this*\nand *that*'
        exp = 'this is <b>bold</b> and <b>this</b> and <b>that</b>'
        assert_format(inp, exp, p=True)
        assert_format('this *works\ntoo!*', 'this <b>works too!</b>', p=True)

    def test_not_bolded_if_no_content(self):
        assert_format('**', p=True)

    def test_asterisk_in_the_middle_of_word_is_ignored(self):
        for inp, exp in [('aa*notbold*bbb', None),
                         ('*bold*still bold*', '<b>bold*still bold</b>'),
                         ('a*not*b c*still not*d', None),
                         ('*b*b2* -*n*- *b3*', '<b>b*b2</b> -*n*- <b>b3</b>')]:
            assert_format(inp, exp, p=True)

    def test_asterisk_alone_does_not_start_bolding(self):
        for inp, exp in [('*', None),
                         (' * ', '*'),
                         ('* not *', None),
                         (' * not * ', '* not *'),
                         ('* not*', None),
                         ('*bold *', '<b>bold </b>'),
                         ('* *b* *', '* <b>b</b> *'),
                         ('*bold * not*', '<b>bold </b> not*'),
                         ('*bold * not*not* *b*',
                          '<b>bold </b> not*not* <b>b</b>')]:
            assert_format(inp, exp, p=True)

    def test_one_word_italic(self):
        for inp, exp in [('_italic_', '<i>italic</i>'),
                         ('_i_', '<i>i</i>'),
                         ('_many italic words_', '<i>many italic words</i>'),
                         (' _italic_', '<i>italic</i>'),
                         ('_italic_ ', '<i>italic</i>'),
                         ('xx _italic_', 'xx <i>italic</i>'),
                         ('_italic_ xx', '<i>italic</i> xx')]:
            assert_format(inp, exp, p=True)

    def test_multiple_word_italic(self):
        for inp, exp in [('_italic_ _i_ not italic _i3_ not',
                          '<i>italic</i> <i>i</i> not italic <i>i3</i> not'),
                         ('not i _this is i_ _more i words here_',
                          'not i <i>this is i</i> <i>more i words here</i>')]:
            assert_format(inp, exp, p=True)

    def test_not_italiced_if_no_content(self):
        assert_format('__', p=True)

    def test_not_italiced_many_underlines(self):
        for inp in ['___', '____', '_________', '__len__']:
            assert_format(inp, p=True)

    def test_underscore_in_the_middle_of_word_is_ignored(self):
        for inp, exp in [('aa_notitalic_bbb', None),
                         ('_ital_still ital_', '<i>ital_still ital</i>'),
                         ('a_not_b c_still not_d', None),
                         ('_b_b2_ -_n_- _b3_', '<i>b_b2</i> -_n_- <i>b3</i>')]:
            assert_format(inp, exp, p=True)

    def test_underscore_alone_does_not_start_italicing(self):
        for inp, exp in [('_', None),
                         (' _ ', '_'),
                         ('_ not _', None),
                         (' _ not _ ', '_ not _'),
                         ('_ not_', None),
                         ('_italic _', '<i>italic </i>'),
                         ('_ _b_ _', '_ <i>b</i> _'),
                         ('_italic _ not_', '<i>italic </i> not_'),
                         ('_italic _ not_not_ _b_',
                          '<i>italic </i> not_not_ <i>b</i>')]:
            assert_format(inp, exp, p=True)

    def test_bold_and_italic(self):
        for inp, exp in [('*b* _i_', '<b>b</b> <i>i</i>')]:
            assert_format(inp, exp, p=True)

    def test_bold_and_italic_works_with_punctuation_marks(self):
        for bef, aft in [('(',''), ('"',''), ("'",''), ('(\'"(',''),
                         ('',')'), ('','"'), ('',','), ('','"\').,!?!?:;'),
                         ('(',')'), ('"','"'), ('("\'','\'";)'), ('"','..."')]:
            for inp, exp in [('*bold*','<b>bold</b>'),
                             ('_ital_','<i>ital</i>'),
                             ('*b* _i_','<b>b</b> <i>i</i>')]:
                assert_format(bef + inp + aft, bef + exp + aft, p=True)

    def test_bold_italic(self):
        for inp, exp in [('_*bi*_', '<i><b>bi</b></i>'),
                         ('_*bold ital*_', '<i><b>bold ital</b></i>'),
                         ('_*bi* i_', '<i><b>bi</b> i</i>'),
                         ('_*bi_ b*', '<i><b>bi</i> b</b>'),
                         ('_i *bi*_', '<i>i <b>bi</b></i>'),
                         ('*b _bi*_', '<b>b <i>bi</b></i>')]:
            assert_format(inp, exp, p=True)


class TestHtmlFormatCustomLinks(unittest.TestCase):

    def test_text_with_text(self):
        assert_format('[link.html|title]', '<a href="link.html">title</a>', p=True)
        assert_format('[link|t|i|t|l|e]', '<a href="link">t|i|t|l|e</a>', p=True)

    def test_text_with_image(self):
        assert_format('[link|img.png]',
                      '<a href="link"><img src="img.png" title="link"></a>',
                      p=True)

    def test_image_with_text(self):
        assert_format('[img.png|title]', '<img src="img.png" title="title">', p=True)
        assert_format('[img.png|]', '<img src="img.png" title="img.png">', p=True)

    def test_image_with_image(self):
        assert_format('[x.png|thumb.png]',
                      '<a href="x.png"><img src="thumb.png" title="x.png"></a>',
                      p=True)

    def test_link_is_required(self):
        assert_format('[|]', '[|]', p=True)

    def test_whitespace_is_strip(self):
        assert_format('[ link.html  | title words  ]',
                      '<a href="link.html">title words</a>', p=True)

    def test_url_and_link(self):
        assert_format('http://url [link|title]',
                      '<a href="http://url">http://url</a> <a href="link">title</a>',
                      p=True)

    def test_link_as_url(self):
        assert_format('[http://url|title]', '<a href="http://url">title</a>', p=True)

    def test_multiple_links(self):
        assert_format('start [link|img.png] middle [link.html|title] end',
                      'start <a href="link"><img src="img.png" title="link"></a> '
                      'middle <a href="link.html">title</a> end', p=True)

    def test_multiple_links_and_urls(self):
        assert_format('[L|T]ftp://u[X|Y][http://u]',
                      '<a href="L">T</a><a href="ftp://u">ftp://u</a>'
                      '<a href="X">Y</a>[<a href="http://u">http://u</a>]', p=True)

    def test_escaping(self):
        assert_format('["|<&>]', '<a href="&quot;">&lt;&amp;&gt;</a>', p=True)
        assert_format('[<".jpg|">]', '<img src="&lt;&quot;.jpg" title="&quot;&gt;">', p=True)

    def test_formatted_link(self):
        assert_format('*[link.html|title]*', '<b><a href="link.html">title</a></b>', p=True)

    def test_link_in_table(self):
        assert_format('| [link.html|title] |', '''\
<table>
<tr>
<td><a href="link.html">title</a></td>
</tr>
</table>''')


class TestHtmlFormatTable(unittest.TestCase):

    def test_one_row_table(self):
        inp = '| one | two |'
        exp = _format_table([['one','two']])
        assert_format(inp, exp)

    def test_multi_row_table(self):
        inp = '| 1.1 | 1.2 | 1.3 |\n| 2.1 | 2.2 |\n| 3.1 | 3.2 | 3.3 |\n'
        exp = _format_table([['1.1','1.2','1.3'],
                             ['2.1','2.2'],
                             ['3.1','3.2','3.3']])
        assert_format(inp, exp)

    def test_table_with_extra_spaces(self):
        inp = '  |   1.1   |  1.2   |  \n   | 2.1 | 2.2 |    '
        exp = _format_table([['1.1','1.2',],['2.1','2.2']])
        assert_format(inp, exp)

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
        assert_format(inp, exp)

    def test_one_column_table(self):
        inp = '|  one column |\n| |\n  |  |  \n| 2 | col |\n|          |'
        exp = _format_table([['one column'],[''],[''],['2','col'],['']])
        assert_format(inp, exp)

    def test_table_with_other_content_around(self):
        inp = '''before table
| in | table |
| still | in |

 after table
'''
        exp = '<p>before table</p>\n' \
            + _format_table([['in','table'],['still','in']]) \
            + '\n<p>after table</p>'
        assert_format(inp, exp)

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
        exp = '<p>before tables</p>\n' \
            + _format_table([['table','1'],['still','1']]) \
            + '\n<p>between</p>\n' \
            + _format_table([['table','2']]) \
            + '\n<p>between</p>\n' \
            + _format_table([['3.1.1','3.1.2','3.1.3'],
                             ['3.2.1','3.2.2','3.2.3'],
                             ['3.3.1','3.3.2','3.3.3']]) \
            + '\n' \
            + _format_table([['t','4'],['','']]) \
            + '\n<p>after</p>'
        assert_format(inp, exp)

    def test_ragged_table(self):
        inp = '''
| 1.1 | 1.2 | 1.3 |
| 2.1 |
| 3.1 | 3.2 |
'''
        exp = _format_table([['1.1','1.2','1.3'],
                             ['2.1','',''],
                             ['3.1','3.2','']])
        assert_format(inp, exp)

    def test_bold_in_table_cells(self):
        inp = '''
| *a* | *b* | *c* |
| *b* |  x  |  y  |
| *c* |  z  |     |

| a   | x *b* y | *b* *c* |
| *a  | b*      |         |
'''
        exp = _format_table([['<b>a</b>','<b>b</b>','<b>c</b>'],
                             ['<b>b</b>','x','y'],
                             ['<b>c</b>','z','']]) + '\n' \
            + _format_table([['a','x <b>b</b> y','<b>b</b> <b>c</b>'],
                             ['*a','b*','']])
        assert_format(inp, exp)

    def test_italic_in_table_cells(self):
        inp = '''
| _a_ | _b_ | _c_ |
| _b_ |  x  |  y  |
| _c_ |  z  |     |

| a   | x _b_ y | _b_ _c_ |
| _a  | b_      |         |
'''
        exp = _format_table([['<i>a</i>','<i>b</i>','<i>c</i>'],
                             ['<i>b</i>','x','y'],
                             ['<i>c</i>','z','']]) + '\n' \
            +  _format_table([['a','x <i>b</i> y','<i>b</i> <i>c</i>'],
                              ['_a','b_','']])
        assert_format(inp, exp)

    def test_bold_and_italic_in_table_cells(self):
        inp = '''
| *a* | *b* | *c* |
| _b_ |  x  |  y  |
| _c_ |  z  | *b* _i_ |
'''
        exp = _format_table([['<b>a</b>','<b>b</b>','<b>c</b>'],
                             ['<i>b</i>','x','y'],
                             ['<i>c</i>','z','<b>b</b> <i>i</i>']])
        assert_format(inp, exp)

    def test_link_in_table_cell(self):
        inp = '''
| 1 | http://one |
| 2 | ftp://two/ |
'''
        exp = _format_table([['1','<a href="http://one">http://one</a>'],
                             ['2','<a href="ftp://two/">ftp://two/</a>']])
        assert_format(inp, exp)


class TestHtmlFormatHr(unittest.TestCase):

    def test_hr_is_three_or_more_hyphens(self):
        for i in range(3, 10):
            hr = '-' * i
            spaces = ' ' * i
            assert_format(hr, '<hr>')
            assert_format(spaces + hr + spaces, '<hr>')

    def test_hr_with_other_stuff_around(self):
        for inp, exp in [('---\n-', '<hr>\n<p>-</p>'),
                         ('xx\n---\nxx', '<p>xx</p>\n<hr>\n<p>xx</p>'),
                         ('xx\n\n------\n\nxx', '<p>xx</p>\n<hr>\n<p>xx</p>')]:
            assert_format(inp, exp)

    def test_multiple_hrs(self):
        assert_format('---\n---\n\n---', '<hr>\n<hr>\n<hr>')

    def test_not_hr(self):
        for inp in ['-', '--', '-- --', '...---...', '===']:
            assert_format(inp, p=True)

    def test_hr_before_and_after_table(self):
        inp = '''
---
| t | a | b | l | e |
---'''
        exp = '<hr>\n' + _format_table([['t','a','b','l','e']]) + '\n<hr>'
        assert_format(inp, exp)


class TestHtmlFormatList(unittest.TestCase):

    def test_not_a_list(self):
        for inp in ('-- item', '+ item', '* item', '-item'):
            assert_format(inp, inp, p=True)

    def test_one_item_list(self):
        assert_format('- item', '<ul>\n<li>item</li>\n</ul>')
        assert_format(' -   item', '<ul>\n<li>item</li>\n</ul>')

    def test_multi_item_list(self):
        assert_format('- 1\n  -  2\n- 3',
                      '<ul>\n<li>1</li>\n<li>2</li>\n<li>3</li>\n</ul>')

    def test_list_with_formatted_content(self):
        assert_format('- *bold* text\n- _italic_\n- [http://url|link]',
                      '<ul>\n<li><b>bold</b> text</li>\n<li><i>italic</i></li>\n'
                      '<li><a href="http://url">link</a></li>\n</ul>')

    def test_lists_with_other_content_around(self):
        assert_format('''
before
- a
- *b*
between

- c
- d

---
''',  '''\
<p>before</p>
<ul>
<li>a</li>
<li><b>b</b></li>
</ul>
<p>between</p>
<ul>
<li>c</li>
<li>d</li>
</ul>
<hr>''')


class TestHtmlFormatPreformatted(unittest.TestCase):

    def test_single_line_block(self):
        self._assert_preformatted('| some', 'some')

    def test_block_without_any_content(self):
        self._assert_preformatted('|', '')

    def test_first_char_after_pipe_must_be_space(self):
        assert_format('|x', p=True)

    def test_multi_line_block(self):
        self._assert_preformatted('| some\n|\n| quote', 'some\n\nquote')

    def test_internal_whitespace_is_preserved(self):
        self._assert_preformatted('|   so\t\tme  ', '  so\t\tme')

    def test_spaces_before_leading_pipe_are_ignored(self):
        self._assert_preformatted(' | some', 'some')

    def test_block_mixed_with_other_content(self):
        assert_format('before block:\n| some\n| quote\nafter block',
                      '<p>before block:</p>\n<pre>\nsome\nquote\n</pre>\n<p>after block</p>')

    def test_multiple_blocks(self):
        assert_format('| some\n| quote\nbetween\n| other block\n\nafter', '''\
<pre>
some
quote
</pre>
<p>between</p>
<pre>
other block
</pre>
<p>after</p>''')

    def test_block_line_with_other_formatting(self):
        self._assert_preformatted('| _some_ formatted\n| text *here*',
                                  '<i>some</i> formatted\ntext <b>here</b>')

    def _assert_preformatted(self, inp, exp):
        assert_format(inp, '<pre>\n' + exp + '\n</pre>')


class TestFormatTable(unittest.TestCase):
    _table_start = '<table>'

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


class TestAttributeEscape(unittest.TestCase):

    def test_nothing_to_escape(self):
        for inp in ['', 'whatever', 'nothing here, move along']:
            assert_equals(attribute_escape(inp), inp)

    def test_html_entities(self):
        for inp, exp in [('"', '&quot;'), ('<', '&lt;'), ('>', '&gt;'),
                         ('&', '&amp;'), ('&<">&', '&amp;&lt;&quot;&gt;&amp;'),
                         ('Sanity < "check"', 'Sanity &lt; &quot;check&quot;')]:
            assert_equals(attribute_escape(inp), exp)

    def test_newlines_and_tabs(self):
        for inp, exp in [('\n', ' '), ('\t', ' '), ('"\n\t"', '&quot;  &quot;'),
                         ('N1\nN2\n\nT1\tT3\t\t\t', 'N1 N2  T1 T3   ')]:
            assert_equals(attribute_escape(inp), exp)

    def test_illegal_chars_in_xml(self):
        for c in u'\x00\x08\x0B\x0C\x0E\x1F\uFFFE\uFFFF':
            assert_equals(attribute_escape(c), '')


class TestConvertingNonStringsToStrings(unittest.TestCase):

    def test_xml_escape(self):
        self._test_escape_method(xml_escape)

    def test_html_escape(self):
        self._test_escape_method(html_escape)

    def test_attribute_escape(self):
        self._test_escape_method(attribute_escape)

    def test_html_format(self):
        self._test_escape_method(html_format, '<p>', '</p>')

    def _test_escape_method(self, method, before='', after=''):
        self._verify_result(method(42), '42', before, after)
        self._verify_result(method('\xff'), '\\xff', before, after)
        self._verify_result(method(self.CustomStr('>\x00<')), '&gt;&lt;', before, after)
        self._verify_result(method(self.CustomStr('\xff')), '\\xff', before, after)

    def _verify_result(self, expected, actual, before, after):
        assert_equals(expected, before + actual + after)

    class CustomStr:
        def __init__(self, custom_str):
            self.custom_str = custom_str
        def __str__(self):
            return self.custom_str


if __name__ == '__main__':
    unittest.main()
