import sys
import unittest
from types import UnicodeType

from robot.parsing.htmlreader import HtmlReader
from robot.utils.asserts import *


VALID_TABLES = [ "Variable", "Setting", "Test Case", "Test Suite", "Keyword" ]
ROW_TEMPLATE = '<tr><td>%s</td><td>%s</td><td>%s</td></tr>'


class TestDataMock:

    def __init__(self):
        self.tables = {}
        self.current = None

    def start_table(self, name):
        if name in VALID_TABLES:
            self.tables[name] = []
            self.current = name
            return True
        else:
            self.current = None
            return False

    def add_row(self, cells):
        self.tables[self.current].append(cells)


class TestHtmlReader(unittest.TestCase):

    def setUp(self):
        self.reader = HtmlReader()
        self.reader.data = TestDataMock()

    def test_initial_state(self):
        self.reader.state = self.reader.IGNORE
        self.reader.feed('<table>')
        assert_equals(self.reader.state, self.reader.INITIAL)
        self.reader.feed('</table>')
        assert_equals(self.reader.state, self.reader.IGNORE)

    def test_start_valid_table(self):
        for name in VALID_TABLES:
            self.reader.feed('<table>')
            self.reader.feed(ROW_TEMPLATE % (name, 'Value 1', 'Value2'))
            assert_equals(self.reader.state, self.reader.PROCESS)
            assert_equals(self.reader.data.current, name)
            self.reader.feed('</table>')
            assert_equals(self.reader.state, self.reader.IGNORE)

    def test_process_invalid_table(self):
        for name in [ "Foo", "VaribleTable" ]:
            self.reader.feed('<table>')
            self.reader.feed(ROW_TEMPLATE % (name, 'Value 1', 'Value2'))
            assert_equals(self.reader.state, self.reader.IGNORE)
            assert_none(self.reader.data.current)
            self.reader.feed(ROW_TEMPLATE % ('This', 'row', 'is ignored'))
            assert_equals(self.reader.state, self.reader.IGNORE)
            assert_equals(len(self.reader.data.tables.values()), 0)
            self.reader.feed('</table>')
            assert_equals(self.reader.state, self.reader.IGNORE)

    def test_br(self):
        inp = ('x<br>y', '1<br />2', '<br><br>')
        exp = ['x\ny', '1\n2', '\n\n']
        for name in VALID_TABLES:
            self.reader.feed('<table>')
            self.reader.feed(ROW_TEMPLATE % (name, 'Value 1', 'Value2'))
            self.reader.feed(ROW_TEMPLATE % inp)
            self.reader.feed('</table>')
            assert_equals(self.reader.data.tables[name], [ exp ])

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
        self._row_processing('<td>%s<td>%s</td><td>%s</td></tr></tr>')

    def _row_processing(self, row_template):
        for name in VALID_TABLES:
            self.reader.feed('<table>')
            self.reader.feed(row_template % (name, 'Value 1', 'Value2'))
            row_data = [ ['Just', 'some', 'data'],
                         ['here', '', 'for'],
                         ['', 'these', 'rows'] ]
            for data in row_data:
                self.reader.feed(row_template % tuple(data))
            assert_equals(self.reader.state, self.reader.PROCESS)
            self.reader.feed('</table>')
            assert_equals(self.reader.state, self.reader.IGNORE)
            assert_equals(self.reader.data.tables[name], row_data)


class TestEntityAndCharRefs(unittest.TestCase):

    def setUp(self):
        self.reader = HtmlReader()
        self.reader.handle_data = self._handle_response

    def _handle_response(self, value, decode):
        self.response = value

    def test_handle_entiryrefs(self):
        for inp, exp in [ ('nbsp', ' '),
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
                          ('invalid', '&invalid;') ]:
            self.reader.handle_entityref(inp)
            msg = '%s: %r != %r' % (inp,  self.response, exp)
            assert_equals(self.response, exp, msg, False)

    def test_handle_charefs(self):
        for inp, exp in [ ('82', 'R'),
                          ('228', u'\u00E4'),
                          ('invalid', '&#invalid;') ]:
            self.reader.handle_charref(inp)
            msg = '%s: %r != %r' % (inp,  self.response, exp)
            assert_equals(self.response, exp, msg, False)


class TestEncoding(unittest.TestCase):

    def test_default_encoding(self):
        assert_equals(HtmlReader()._encoding, 'ISO-8859-1')

    def test_encoding_is_read_from_meta_tag(self):
        reader = HtmlReader()
        reader.feed('<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />')
        assert_equals(reader._encoding, 'utf-8')
        reader.feed('<meta http-equiv="Content-Type" content="text/html; charset=UTF-8">')
        assert_equals(reader._encoding, 'UTF-8')

    def test_valid_http_equiv_is_required(self):
        reader = HtmlReader()
        reader.feed('<meta content="text/html; charset=utf-8" />')
        assert_equals(reader._encoding, 'ISO-8859-1')
        reader.feed('<meta http-equiv="Invalid" content="text/html; charset=utf-8" />')
        assert_equals(reader._encoding, 'ISO-8859-1')

    def test_encoding_is_set_from_xml_preamble(self):
        reader = HtmlReader()
        reader.feed('<?xml version="1.0" encoding="UTF-8"?>')
        assert_equals(reader._encoding, 'UTF-8')
        reader.feed('<?xml encoding=US-ASCII version="1.0"?>')
        assert_equals(reader._encoding, 'US-ASCII')

    def test_encoding_and_entityrefs(self):
        reader = HtmlReader()
        reader.data = TestDataMock()
        reader.feed('<meta content="text/html; charset=utf-8" />')
        reader.feed('<table><tr><td>Setting</td></tr>')
        reader.feed('<tr><td>&auml;iti')
        assert_equals(reader.current_cell, [u'\xe4', u'iti'])
        reader.feed('</tr>')
        assert_equals(reader.data.tables['Setting'][0], [u'\xe4iti'])


if __name__ == '__main__':
    unittest.main()
