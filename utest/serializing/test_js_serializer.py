from __future__ import with_statement
import StringIO
import unittest
import xml.sax as sax

from resources import GOLDEN_OUTPUT, GOLDEN_JS
from robot.serializing.jsparser import _RobotOutputHandler, Context, parse_js
from robot.utils.asserts import assert_equals

class TestJsSerializer(unittest.TestCase):

    def setUp(self):
        self._handler = _RobotOutputHandler(Context())

    def test_message_xml_parsing(self):
        datamodel = self._get_datamodel('<msg timestamp="20110531 12:48:09.088" level="FAIL">AssertionError</msg>')
        assert_equals(datamodel._basemillis, 1306835289088)
        assert_equals(datamodel._robot_data, [0, 'F', 1])
        assert_equals(datamodel._texts, ['*', '*AssertionError'])

    def test_status_xml_parsing(self):
        datamodel = self._get_datamodel('<status status="PASS" endtime="20110531 12:48:09.042" starttime="20110531 12:48:09.000"></status>')
        assert_equals(datamodel._robot_data, ['P',0,42])


    def _get_datamodel(self, xml_string):
        sax.parseString(xml_string, self._handler)
        return self._handler.datamodel


    def test_golden_js_generation(self):
        buffer = StringIO.StringIO()
        parse_js(GOLDEN_OUTPUT, buffer)
        with open(GOLDEN_JS, 'r') as expected:
            self._assert_long_equals(buffer.getvalue(), expected.read())

    def _assert_long_equals(self, given, expected):
        if (given!=expected):
            for index, char in enumerate(given):
                if index >= len(expected):
                    raise AssertionError('Expected is shorter than given string. Ending that was missing %s' % given[index:])
                if char != expected[index]:
                    raise AssertionError("Given and expected not equal ('%s' != '%s') at index %s. '%s' != '%s'" %
                                         (char, expected[index], index, self._snippet(index, given), self._snippet(index, expected)))
            if len(expected) > len(given):
                raise AssertionError('Expected is longer than given string. Ending that was missing %s' % expected[len(given)-1:])

    def _snippet(self, index, string):
        start = max(0, index-10)
        startpadding = '' if start==0 else '...'
        end = min(len(string), index+10)
        endpadding = '' if end==0 else '...'
        return startpadding+string[start:end]+endpadding
