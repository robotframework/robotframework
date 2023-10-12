import unittest

from robot.utils.asserts import assert_equal

from robot.utils.markuputils import html_escape, html_format, attribute_escape
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
    assert_equal(escape, exp_escape,
                 'ESCAPE:\n%r   =!\n%r' % (escape, exp_escape), values=False)
    assert_equal(format, exp_format,
                 'FORMAT:\n%r   =!\n%r' % (format, exp_format), values=False)


def assert_format(inp, exp=None, p=False):
    exp = exp if exp is not None else inp
    if p:
        exp = '<p>%s</p>' % exp
    assert_equal(html_format(inp), exp)


def assert_escape(inp, exp=None):
    exp = exp if exp is not None else inp
    assert_equal(html_escape(inp), exp)


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

    def test_not_urls(self):
        for no_url in ['http no link', 'http:/no', '123://no',
                       '1a://no', 'http://', 'http:// no']:
            assert_escape_and_format(no_url)

    def test_simple_urls(self):
        for link in ['http://robot.fi', 'https://r.fi/', 'FTP://x.y.z/p/f.txt',
                     'a23456://link', 'file:///c:/temp/xxx.yyy']:
            exp = '<a href="%s">%s</a>' % (link, link)
            assert_escape_and_format(link, exp)
            for end in [',', '.', ';', ':', '!', '?', '...', '!?!', ' hello' ]:
                assert_escape_and_format(link+end, exp+end)
                assert_escape_and_format('xxx '+link+end, 'xxx '+exp+end)
            for start, end in [('(',')'), ('[',']'), ('"','"'), ("'","'")]:
                assert_escape_and_format(start+link+end, start+exp+end)

    def test_complex_urls_and_surrounding_content(self):
        for inp, exp in [
                ('hello http://link world',
                 'hello <a href="http://link">http://link</a> world'),
                ('multi\nhttp://link\nline',
                 'multi\n<a href="http://link">http://link</a>\nline'),
                ('http://link, ftp://link2.',
                 '<a href="http://link">http://link</a>, '
                 '<a href="ftp://link2">ftp://link2</a>.'),
                ('x (git+ssh://yy, z)',
                 'x (<a href="git+ssh://yy">git+ssh://yy</a>, z)'),
                ('(http://x.com/blah_(wikipedia)#cite-1)',
                 '(<a href="http://x.com/blah_(wikipedia)#cite-1">http://x.com/blah_(wikipedia)#cite-1</a>)'),
                ('x-yojimbo-item://6303,E4C1,6A6E, FOO',
                 '<a href="x-yojimbo-item://6303,E4C1,6A6E">x-yojimbo-item://6303,E4C1,6A6E</a>, FOO'),
                ('Hello http://one, ftp://kaksi/; "gopher://3.0"',
                 'Hello <a href="http://one">http://one</a>, '
                 '<a href="ftp://kaksi/">ftp://kaksi/</a>; '
                 '"<a href="gopher://3.0">gopher://3.0</a>"'),
                ("'{https://issues/3231}'",
                 "'{<a href=\"https://issues/3231\">https://issues/3231</a>}'")]:
            assert_escape_and_format(inp, exp)

    def test_image_urls(self):
        link = '(<a href="%s">%s</a>)'
        img = '(<img src="%s" title="%s">)'
        for ext in ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'svg']:
            url = 'foo://bar/zap.%s' % ext
            uprl = url.upper()
            inp = '(%s)' % url
            assert_escape_and_format(inp, link % (url, url), img % (url, url))
            assert_escape_and_format(inp.upper(), link % (uprl, uprl),
                                    img % (uprl, uprl))

    def test_url_with_chars_needing_escaping(self):
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


class TestHtmlFormatInlineStyles(unittest.TestCase):

    def test_bold_once(self):
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

    def test_bold_multiple_times(self):
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

    def test_italic_once(self):
        for inp, exp in [('_italic_', '<i>italic</i>'),
                         ('_i_', '<i>i</i>'),
                         ('_many italic words_', '<i>many italic words</i>'),
                         (' _italic_', '<i>italic</i>'),
                         ('_italic_ ', '<i>italic</i>'),
                         ('xx _italic_', 'xx <i>italic</i>'),
                         ('_italic_ xx', '<i>italic</i> xx')]:
            assert_format(inp, exp, p=True)

    def test_italic_multiple_times(self):
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
                         ('_i_i2_ -_n_- _i3_', '<i>i_i2</i> -_n_- <i>i3</i>')]:
            assert_format(inp, exp, p=True)

    def test_underscore_alone_does_not_start_italicing(self):
        for inp, exp in [('_', None),
                         (' _ ', '_'),
                         ('_ not _', None),
                         (' _ not _ ', '_ not _'),
                         ('_ not_', None),
                         ('_italic _', '<i>italic </i>'),
                         ('_ _i_ _', '_ <i>i</i> _'),
                         ('_italic _ not_', '<i>italic </i> not_'),
                         ('_italic _ not_not_ _i_',
                          '<i>italic </i> not_not_ <i>i</i>')]:
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

    def test_code_once(self):
        for inp, exp in [('``code``', '<code>code</code>'),
                         ('``c``', '<code>c</code>'),
                         ('``many code words``', '<code>many code words</code>'),
                         (' ``leading space``', '<code>leading space</code>'),
                         ('``trailing space`` ', '<code>trailing space</code>'),
                         ('xx ``code``', 'xx <code>code</code>'),
                         ('``code`` xx', '<code>code</code> xx')]:
            assert_format(inp, exp, p=True)

    def test_code_multiple_times(self):
        for inp, exp in [('``code`` ``c`` not ``c3`` not',
                          '<code>code</code> <code>c</code> not <code>c3</code> not'),
                         ('not c ``this is c`` ``more c words here``',
                          'not c <code>this is c</code> <code>more c words here</code>')]:
            assert_format(inp, exp, p=True)

    def test_not_coded_if_no_content(self):
        assert_format('````', p=True)

    def test_not_codeed_many_underlines(self):
        for inp in ['``````', '````````', '``````````````````', '````len````']:
            assert_format(inp, p=True)

    def test_backtics_in_the_middle_of_word_are_ignored(self):
        for inp, exp in [('aa``notcode``bbb', None),
                         ('``code``still code``', '<code>code``still code</code>'),
                         ('a``not``b c``still not``d', None),
                         ('``c``c2`` -``n``- ``c3``', '<code>c``c2</code> -``n``- <code>c3</code>')]:
            assert_format(inp, exp, p=True)

    def test_backtics_alone_do_not_start_codeing(self):
        for inp, exp in [('``', None),
                         (' `` ', '``'),
                         ('`` not ``', None),
                         (' `` not `` ', '`` not ``'),
                         ('`` not``', None),
                         ('``code ``', '<code>code </code>'),
                         ('`` ``b`` ``', '`` <code>b</code> ``'),
                         ('``code `` not``', '<code>code </code> not``'),
                         ('``code `` not``not`` ``c``',
                          '<code>code </code> not``not`` <code>c</code>')]:
            assert_format(inp, exp, p=True)


class TestHtmlFormatCustomLinks(unittest.TestCase):
    image_extensions = ('jpg', 'jpeg', 'PNG', 'Gif', 'bMp', 'svg')

    def test_text_with_text(self):
        assert_format('[link.html|title]', '<a href="link.html">title</a>', p=True)
        assert_format('[link|t|i|t|l|e]', '<a href="link">t|i|t|l|e</a>', p=True)

    def test_text_with_image(self):
        for ext in self.image_extensions:
            assert_format(
                '[link|img.%s]' % ext,
                '<a href="link"><img src="img.%s" title="link"></a>' % ext,
                p=True
            )

    def test_image_with_text(self):
        for ext in self.image_extensions:
            img = 'doc/images/robot.%s' % ext
            assert_format(
                'Robot [%s|robot]!' % img,
                'Robot <img src="%s" title="robot">!' % img,
                p=True
            )
            assert_format(
                'Robot [%s|]!' % img,
                'Robot <img src="%s" title="%s">!' % (img, img),
                p=True
            )

    def test_image_with_image(self):
        for ext in self.image_extensions:
            assert_format(
                '[X.%s|Y.%s]' % (ext, ext),
                '<a href="X.%s"><img src="Y.%s" title="X.%s"></a>' % ((ext,)*3),
                p=True
            )

    def test_text_with_data_uri_image(self):
        uri = 'data:image/png;base64,oooxxx='
        assert_format(
            '[robot.html|%s]' % uri,
            '<a href="robot.html"><img src="%s" title="robot.html"></a>' % uri,
            p=True
        )

    def test_data_uri_image_with_text(self):
        uri = 'data:image/png;base64,oooxxx='
        assert_format(
            '[%s|Robot rocks!]' % uri,
            '<img src="%s" title="Robot rocks!">' % uri,
            p=True
        )

    def test_image_with_data_uri_image(self):
        uri = 'data:image/png;base64,oooxxx='
        assert_format(
            '[image.jpg|%s]' % uri,
            '<a href="image.jpg"><img src="%s" title="image.jpg"></a>' % uri,
            p=True
        )

    def test_data_uri_image_with_data_uri_image(self):
        uri = 'data:image/png;base64,oooxxx='
        assert_format(
            '[%s|%s]' % (uri, uri),
            '<a href="%s"><img src="%s" title="%s"></a>' % (uri, uri, uri),
            p=True
        )

    def test_link_is_required(self):
        assert_format('[|]', '[|]', p=True)

    def test_spaces_are_stripped(self):
        assert_format('[ link.html  | title words  ]',
                      '<a href="link.html">title words</a>', p=True)

    def test_newlines_inside_text(self):
        assert_format('[http://url|text\non\nmany\nlines]',
                      '<a href="http://url">text on many lines</a>', p=True)

    def test_newline_after_pipe(self):
        assert_format('[http://url|\nwrapping was needed]',
                      '<a href="http://url">wrapping was needed</a>', p=True)

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
        assert_format('[L|T]ftp://url[X|Y][http://u2]',
                      '<a href="L">T</a><a href="ftp://url">ftp://url</a>'
                      '<a href="X">Y</a>[<a href="http://u2">http://u2</a>]', p=True)

    def test_escaping(self):
        assert_format('["|<&>]', '<a href="&quot;">&lt;&amp;&gt;</a>', p=True)
        assert_format('[<".jpg|">]', '<img src="&lt;&quot;.jpg" title="&quot;&gt;">', p=True)

    def test_formatted_link(self):
        assert_format('*[link.html|title]*', '<b><a href="link.html">title</a></b>', p=True)

    def test_link_in_table(self):
        assert_format('| [link.html|title] |', '''\
<table border="1">
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

    def test_th(self):
        inp = '''
| =a= |   =   b   =   | = = c = = |
| = = |    = _e_ =    |  =_*f*_=  |
'''
        exp = '''
<table border="1">
<tr>
<th>a</th>
<th>b</th>
<th>= c =</th>
</tr>
<tr>
<th></th>
<th><i>e</i></th>
<th><i><b>f</b></i></th>
</tr>
</table>
'''
        assert_format(inp, exp.strip())

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
        exp = _format_table([['1','FIRST'],
                             ['2','SECOND']]) \
            .replace('FIRST', '<a href="http://one">http://one</a>') \
            .replace('SECOND', '<a href="ftp://two/">ftp://two/</a>')
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

    def test_indentation_can_be_used_to_continue_list_item(self):
        assert_format('''
  outside list
- this item
  continues
  - 2nd item
    continues
 twice
''', '''\
<p>outside list</p>
<ul>
<li>this item continues</li>
<li>2nd item continues twice</li>
</ul>''')

    def test_lists_with_other_content_around(self):
        assert_format('''
before
- a
- *b*
between

- c
- d
  e
  f

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
<li>d e f</li>
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


class TestHtmlFormatHeaders(unittest.TestCase):

    def test_no_header(self):
        for line in ['', 'hello', '=', '==', '====', '= =', '=  =', '==     ==',
                     '= inconsistent levels ==', '==== 4 is too many ====',
                     '=no spaces=', '=no spaces =', '= no spaces=']:
            assert_format(line, p=bool(line))

    def test_header(self):
        for line, expected in [('= My Header =', '<h2>My Header</h2>'),
                               ('== my == header ==', '<h3>my == header</h3>'),
                               ('  === ===    ===  ', '<h4>===</h4>')]:
            assert_format(line, expected)


class TestFormatTable(unittest.TestCase):
    # RIDE needs border="1" because its HTML view doesn't support CSS
    _table_start = '<table border="1">'

    def test_one_row_table(self):
        inp = [['1','2','3']]
        exp = self._table_start + '''
<tr>
<td>1</td>
<td>2</td>
<td>3</td>
</tr>
</table>'''
        assert_equal(_format_table(inp), exp)

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
        assert_equal(_format_table(inp), exp)

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
        assert_equal(_format_table(inp), exp)

    def test_th(self):
        inp = [['=h1.1=', '=  h  1.2   ='], ['== _h2.1_ =', '= not h 2.2']]
        exp = self._table_start + '''
<tr>
<th>h1.1</th>
<th>h  1.2</th>
</tr>
<tr>
<th>= <i>h2.1</i></th>
<td>= not h 2.2</td>
</tr>
</table>'''
        assert_equal(_format_table(inp), exp)


class TestAttributeEscape(unittest.TestCase):

    def test_nothing_to_escape(self):
        for inp in ['', 'whatever', 'nothing here, move along']:
            assert_equal(attribute_escape(inp), inp)

    def test_html_entities(self):
        for inp, exp in [('"', '&quot;'), ('<', '&lt;'), ('>', '&gt;'),
                         ('&', '&amp;'), ('&<">&', '&amp;&lt;&quot;&gt;&amp;'),
                         ('Sanity < "check"', 'Sanity &lt; &quot;check&quot;')]:
            assert_equal(attribute_escape(inp), exp)

    def test_newlines_and_tabs(self):
        for inp, exp in [('\n', '&#10;'), ('\t', '&#09;'), ('"\n\t"', '&quot;&#10;&#09;&quot;'),
                         ('N1\nN2\n\nT1\tT3\t\t\t', 'N1&#10;N2&#10;&#10;T1&#09;T3&#09;&#09;&#09;')]:
            assert_equal(attribute_escape(inp), exp)

    def test_illegal_chars_in_xml(self):
        for c in '\x00\x08\x0B\x0C\x0E\x1F\uFFFE\uFFFF':
            assert_equal(attribute_escape(c), '')


if __name__ == '__main__':
    unittest.main()
