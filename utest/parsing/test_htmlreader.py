import unittest
from StringIO import StringIO

from robot.parsing.htmlreader import HtmlReader
from robot.parsing.stdhtmlparser import RobotHtmlParser as StdHtmlParser
try:
    from robot.parsing.lxmlhtmlparser import RobotHtmlParser as LxmlHtmlParser
except ImportError:
    def LxmlHtmlParser(*args):
        raise RuntimeError('This test requires lxml module to be installed')

from robot.utils.asserts import assert_equals


VALID_TABLES = [ "Variable", "Setting", "Test Case", "Test Suite", "Keyword" ]
ROW_TEMPLATE = '<tr><td>%s</td><td>%s</td><td>%s</td></tr>'


class PopulatorMock:

    def __init__(self):
        self.tables = {}
        self.current = None

    def start_table(self, header):
        name = header[0]
        if name in VALID_TABLES:
            self.tables[name] = []
            self.current = name
            return True
        else:
            self.current = None
            return False

    def add(self, cells):
        self.tables[self.current].append(cells)

    def eof(self):
        pass


class TestHtmlReaderWithStdHtmlParser(unittest.TestCase):
    parser = StdHtmlParser

    def setUp(self):
        self.reader = HtmlReader(parser=self.parser)

    def _read(self, *data):
        self.reader.read(StringIO('\n'.join(data)), PopulatorMock())

    def test_empty_table(self):
        self._read('<table></table>')
        assert_equals(self.reader.state, self.reader.IGNORE)

    def test_start_valid_table(self):
        for name in VALID_TABLES:
            self._read('<table>', ROW_TEMPLATE % (name, 'Value 1', 'Value2'))
            assert_equals(self.reader.populator.current, name)

    def test_start_invalid_table(self):
        for name in ["Foo", "VariableTable"]:
            self._read('<table>', ROW_TEMPLATE % (name, 'Value 1', 'Value2'),
                       ROW_TEMPLATE % ('This', 'row', 'is ignored'))
            assert_equals(self.reader.state, self.reader.IGNORE)
            assert_equals(self.reader.populator.current, None)
            assert_equals(self.reader.populator.tables, {})

    def test_br(self):
        inp = ['x<br>y', '1<br />2', '<br><br>']
        exp = ['x\ny', '1\n2', '\n\n']
        for name in VALID_TABLES:
            self._read('<table>', ROW_TEMPLATE % (name, 'Value 1', 'Value2'),
                       ROW_TEMPLATE % tuple(inp), '</table>')
            assert_equals(self.reader.populator.tables[name], [exp])

    def test_comment(self):
        self._read('<table>', ROW_TEMPLATE % ('Setting', 'Value 1', 'Value2'),
                   '<!-- ignore me please -->', ROW_TEMPLATE % tuple('ABC'),
                   ROW_TEMPLATE % tuple('123'), '</table>')
        assert_equals(self.reader.populator.tables['Setting'],
                      [['A', 'B', 'C'], ['1', '2', '3']])

    def test_processing(self):
        self._row_processing(ROW_TEMPLATE)

    def test_missing_end_td(self):
        self._row_processing('<tr><td>%s<td>%s</td><td>%s</td></tr>')
        self._row_processing('<tr><td>%s<td>%s<td>%s</tr>')

    def test_missing_end_tr(self):
        self._row_processing('<tr><td>%s<td>%s</td><td>%s</td>')

    def test_extra_end_tr(self):
        self._row_processing('<tr><td>%s<td>%s</td><td>%s</td></tr></tr>')

    def test_missing_start_tr(self):
        self._row_processing('<td>%s<td>%s</td><td>%s</td></tr>')

    def _row_processing(self, row_template):
        row_data = [['Just', 'some', 'data'],
                    ['here', '', 'for'],
                    ['', 'these', 'rows']]
        for name in VALID_TABLES:
            rows = ['<table>', row_template % (name, 'Value 1', 'Value2')] + \
                [row_template % tuple(row) for row in row_data] + ['</table>']
            self._read(*rows)
            assert_equals(self.reader.populator.tables[name], row_data)
            assert_equals(self.reader.state, self.reader.IGNORE)


class TestHtmlReaderWithLxmlParser(TestHtmlReaderWithStdHtmlParser):
    parser=LxmlHtmlParser

    def test_missing_start_tr(self):
        # lxml doens't handle this: it ignores also </tr> if there's no <tr>
        pass



class TestEntityAndCharRefsWithStdHtmlParser(unittest.TestCase):
    parser = StdHtmlParser

    def test_entityrefs(self):
        for inp, exp in [('nbsp', ' '),
                         ('apos', "'"),
                         ('tilde', '~'),
                         ('lt', '<'),
                         ('gt', '>'),
                         ('amp', '&'),
                         ('quot', '"'),
                         ('auml', u'\u00E4'),
                         ('ouml', u'\u00F6'),
                         ('uuml', u'\u00FC'),
                         ('aring', u'\u00E5'),
                         ('ntilde', u'\u00F1'),
                         ('Auml', u'\u00C4'),
                         ('Ouml', u'\u00D6'),
                         ('Uuml', u'\u00DC'),
                         ('Aring', u'\u00C5'),
                         ('Ntilde', u'\u00D1'),
                         ('nabla', u'\u2207'),
                         ('ldquo', u'\u201c'),
                         ('invalid', '&invalid;')]:
            self._test('&%s;' % inp, exp)

    def test_charrefs(self):
        for inp, exp in [('82', 'R'), ('228', u'\u00E4')]:
            self._test('&#%s;' % inp, exp)

    def test_invalid_charref(self):
        self._test('&#invalid;', '&#invalid;')

    def _test(self, input, expected):
        result = []
        def collect_data(data):
            result.append(data)
        reader = HtmlReader(parser=self.parser)
        reader.data = collect_data
        reader.read(StringIO(input), PopulatorMock())
        msg = "'%s': %r != %r" % (input, ''.join(result), expected)
        assert_equals(''.join(result), expected, msg, values=False)


class TestEntityAndCharRefsWithLxmlParser(TestEntityAndCharRefsWithStdHtmlParser):
    parser = LxmlHtmlParser

    def test_invalid_charref(self):
        self._test('&#invalid;', 'invalid;')


class TestEncodingWithStdHtmlParser(unittest.TestCase):

    def test_default_encoding(self):
        assert_equals(StdHtmlParser(reader=None)._encoding, 'ISO-8859-1')

    def test_encoding_is_read_from_meta_tag(self):
        self._test_encoding('<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />', 'utf-8')
        self._test_encoding('<META HTTP-EQUIV="CONTENT-TYPE" CONTENT="TEXT/HTML; CHARSET=UTF-8">', 'UTF-8')

    def test_valid_http_equiv_is_required_in_meta(self):
        self._test_encoding('<meta content="text/html; charset=utf-8" />', 'ISO-8859-1')
        self._test_encoding('<meta http-equiv="Invalid" content="text/html; charset=utf-8" />', 'ISO-8859-1')

    def test_encoding_is_read_from_pi(self):
        self._test_encoding('<?xml version="1.0" encoding="UTF-8"?>', 'UTF-8')
        self._test_encoding('<?xml encoding=US-ASCII version="1.0"?>', 'US-ASCII')

    def _test_encoding(self, data, expected):
        parser = StdHtmlParser(reader=HtmlReader())
        parser.parse(StringIO(data))
        assert_equals(parser._encoding, expected)


if __name__ == '__main__':
    unittest.main()
