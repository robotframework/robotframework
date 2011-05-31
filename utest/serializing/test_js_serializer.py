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
        data_model = self._get_data_model('<msg timestamp="20110531 12:48:09.088" level="FAIL">AssertionError</msg>')
        assert_equals(data_model._basemillis, 1306835289088)
        assert_equals(data_model._robot_data, [0, 'F', 1])
        assert_equals(data_model._texts, ['*', '*AssertionError'])

    def test_status_xml_parsing(self):
        data_model = self._get_data_model('<status status="PASS" endtime="20110531 12:48:09.042" starttime="20110531 12:48:09.000"></status>')
        assert_equals(data_model._basemillis, 1306835289000)
        assert_equals(data_model._robot_data, ['P',0,42])
        assert_equals(data_model._texts, ['*'])

    def test_tags_xml_parsing(self):
        tags_xml = """
        <tags>
            <tag>someothertag</tag>
            <tag>sometag</tag>
        </tags>
        """
        data_model = self._get_data_model(tags_xml)
        assert_equals(data_model._robot_data, [1, 2])
        assert_equals(data_model._texts, ['*', '*someothertag', '*sometag'])

    def test_arguments_xml_parsing(self):
        arguments_xml = """
        <arguments>
        <arg>${arg}</arg>
        <arg>${level}</arg>
        </arguments>
        """
        data_model = self._get_data_model(arguments_xml)
        assert_equals(data_model._robot_data, 1)
        assert_equals(data_model._texts, ['*', '*${arg}, ${level}'])

    def test_keyword_xml_parsing(self):
        keyword_xml = """
        <kw type="teardown" name="BuiltIn.Log" timeout="">
        <doc>Logs the given message with the given level.</doc>
        <arguments>
        <arg>keyword teardown</arg>
        </arguments>
        <msg timestamp="20110531 12:48:09.070" level="INFO">keyword teardown</msg>
        <status status="PASS" endtime="20110531 12:48:09.071" starttime="20110531 12:48:09.069"></status>
        </kw>
        """
        data_model = self._get_data_model(keyword_xml)
        assert_equals(data_model._basemillis, 1306835289070)
        assert_equals(data_model._robot_data, ['teardown', 1, 0, 2, 3, [0, "I", 3], ["P", -1, 2]])
        assert_equals(data_model._texts, ['*', '*BuiltIn.Log', '*Logs the given message with the given level.', '*keyword teardown'])

    def _get_data_model(self, xml_string):
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
