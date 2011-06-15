from __future__ import with_statement
import StringIO
import time

try:
    import json
except ImportError:
    try:
        import simplejson as json
    except ImportError:
        json = None
import unittest
import xml.sax as sax

from robot.serializing.jsparser import _RobotOutputHandler
from robot.serializing.json import json_dump
from robot.serializing.elementhandlers import Context
from robot.utils.asserts import assert_equals, assert_true

class TestJsSerializer(unittest.TestCase):

    SUITE_XML = """<suite source="/tmp/verysimple.txt" name="Verysimple">
                    <doc></doc>
                    <metadata>
                        <item name="key">val</item>
                    </metadata>
                    <test name="Test" timeout="">
                        <doc></doc>
                        <kw type="kw" name="BuiltIn.Log" timeout="">
                            <doc>Logs the given message with the given level.</doc>
                            <arguments><arg>simple</arg></arguments>
                            <msg timestamp="20110601 12:01:51.353" level="WARN">simple</msg>
                            <status status="PASS" endtime="20110601 12:01:51.353" starttime="20110601 12:01:51.353"></status>
                        </kw>
                        <tags></tags>
                        <status status="PASS" endtime="20110601 12:01:51.354" critical="yes" starttime="20110601 12:01:51.353"></status>
                    </test>
                    <status status="PASS" endtime="20110601 12:01:51.354" starttime="20110601 12:01:51.329"></status>
                    </suite>"""

    def setUp(self):
        self._context = Context()
        self._handler = _RobotOutputHandler(self._context)

    def test_message_xml_parsing(self):
        data_model = self._get_data_model('<msg timestamp="20110531 12:48:09.088" level="FAIL">AssertionError</msg>')
        self.assert_model(data_model, 1306835289088, [0, 'F', 1], ['*', '*AssertionError'])

    def assert_model(self, data_model, basemillis, suite, texts):
        assert_equals(data_model._robot_data['baseMillis'], basemillis)
        assert_equals(data_model._robot_data['suite'], suite)
        assert_equals(data_model._robot_data['strings'], texts)

    def test_status_xml_parsing(self):
        data_model = self._get_data_model('<status status="PASS" endtime="20110531 12:48:09.042" starttime="20110531 12:48:09.000"></status>')
        self.assert_model(data_model, 1306835289000, ['P',0,42], ['*'])

    def test_status_with_message_xml_parsing(self):
        data_model = self._get_data_model('<status status="PASS" endtime="20110531 12:48:09.042" starttime="20110531 12:48:09.000">Message</status>')
        self.assert_model(data_model, 1306835289000, ['P',0,42,1], ['*', '*Message'])

    def test_times(self):
        self._context.start_suite('suite')
        times = """
        <kw type="kw" name="KwName" timeout="">
        <msg timestamp="20110531 12:48:09.020" level="FAIL">AssertionError</msg>
        <msg timestamp="N/A" level="FAIL">AssertionError</msg>
        <msg timestamp="20110531 12:48:09.010" level="FAIL">AssertionError</msg>
        <status status="FAIL" endtime="20110531 12:48:09.010" starttime="20110531 12:48:09.020"></status>
        </kw>
        """
        data_model = self._get_data_model(times)
        self.assert_model(data_model, 1306835289020, ['kw', 1, 0,
            [0, 'F', 2],
            [None, 'F', 2],
            [-10, 'F', 2],
            ['F', 0, -10]], ['*', '*KwName', '*AssertionError'])

    def test_generated_millis(self):
        self._context.timestamp('19790101 12:00:00.000')
        data_model = self._get_data_model(self.SUITE_XML)
        data_model.set_generated(time.localtime(284029200))
        assert_equals(data_model._robot_data['generatedMillis'], 0)

    def test_tags_xml_parsing(self):
        tags_xml = """
        <tags>
            <tag>someothertag</tag>
            <tag>sometag</tag>
        </tags>
        """
        data_model = self._get_data_model(tags_xml)
        self.assert_model(data_model, None, [1, 2], ['*', '*someothertag', '*sometag'])

    def test_arguments_xml_parsing(self):
        arguments_xml = """
        <arguments>
            <arg>${arg}</arg>
            <arg>${level}</arg>
        </arguments>
        """
        data_model = self._get_data_model(arguments_xml)
        self.assert_model(data_model, None, 1, ['*', '*${arg}, ${level}'])

    def test_keyword_xml_parsing(self):
        keyword_xml = """
        <kw type="teardown" name="BuiltIn.Log" timeout="">
            <doc>Logs the given message with the given level.</doc>
            <arguments>
                <arg>keyword teardown</arg>
            </arguments>
            <msg timestamp="20110531 12:48:09.070" level="WARN">keyword teardown</msg>
            <status status="PASS" endtime="20110531 12:48:09.071" starttime="20110531 12:48:09.069"></status>
        </kw>
        """
        self._context.start_suite('suite')
        data_model = self._get_data_model(keyword_xml)
        self.assert_model(data_model, 1306835289070, ['teardown', 1, 0, 2, 3, [0, "W", 3], ["P", -1, 2]], ['*', '*BuiltIn.Log', '*Logs the given message with the given level.', '*keyword teardown'])
        assert_equals(self._context.link_to([0, "W", 3]), "keyword_suite.0")

    def test_test_xml_parsing(self):
        test_xml = """
        <test name="Test" timeout="">
            <doc></doc>
            <kw type="kw" name="Log" timeout="">
                <doc>Logging</doc>
                <arguments>
                    <arg>simple</arg>
                </arguments>
                <msg timestamp="20110601 12:01:51.353" level="INFO">simple</msg>
                <status status="PASS" endtime="20110601 12:01:51.353" starttime="20110601 12:01:51.353"></status>
            </kw>
            <tags>
            </tags>
            <status status="PASS" endtime="20110601 12:01:51.354" critical="yes" starttime="20110601 12:01:51.353"></status>
        </test>
        """
        self._context.start_suite('SuiteName')
        data_model = self._get_data_model(test_xml)
        self.assert_model(data_model, 1306918911353, ['test', 1, 0, 'Y', 0, ['kw', 2, 0, 3, 4, [0, 'I', 4], ['P', 0, 0]], [], ['P', 0, 1]], ['*', '*Test', '*Log', '*Logging', '*simple'])

    def test_suite_xml_parsing(self):
        data_model = self._get_data_model(self.SUITE_XML)
        self.assert_model(data_model, 1306918911353, ['suite', '/tmp/verysimple.txt', 'Verysimple',
                                               0, {'key': 1},
                                                ['test', 2, 0, 'Y', 0,
                                                    ['kw', 3, 0, 4, 5, [0, 'W', 5], ['P', 0, 0]], [],
                                                    ['P', 0, 1]], ['P', -24, 25], [1, 1, 1, 1]],
            ['*', '*val', '*Test', '*BuiltIn.Log', '*Logs the given message with the given level.', '*simple'])
        assert_equals(self._context.link_to([0, 'W', 5]), 'keyword_Verysimple.Test.0')

    def test_suite_data_model_keywords_clearing(self):
        data_model = self._get_data_model(self.SUITE_XML)
        data_model.remove_keywords()
        self.assert_model(data_model, 1306918911353, ['suite', '/tmp/verysimple.txt', 'Verysimple',
                                               0, {'key': 1},
                                                ['test', 2, 0, 'Y', 0, [],
                                                    ['P', 0, 1]], ['P', -24, 25], [1, 1, 1, 1]], ['*', '*val', '*Test', '', '', ''])

    def test_metadata_xml_parsing(self):
        meta_xml = """<metadata>
                        <item name="meta">&lt;b&gt;escaped&lt;/b&gt;</item>
                        <item name="version">alpha</item>
                      </metadata>"""
        data_model = self._get_data_model(meta_xml)
        self.assert_model(data_model, None, {'meta':1, 'version':2}, ['*', '*<b>escaped</b>', '*alpha'])

    def test_statistics_xml_parsing(self):
        statistics_xml = """
        <statistics>
            <total>
                <stat fail="4" doc="" pass="0">Critical Tests</stat>
                <stat fail="4" doc="" pass="0">All Tests</stat>
            </total>
            <tag>
                <stat info="" fail="1" pass="0" links="" doc="">someothertag</stat>
                <stat info="" fail="1" pass="0" links="" doc="">sometag</stat>
            </tag>
            <suite>
                <stat fail="4" doc="Data" pass="0">Data</stat>
                <stat fail="1" doc="Data.All Settings" pass="0">Data.All Settings</stat>
                <stat fail="3" doc="Data.Failing Suite" pass="0">Data.Failing Suite</stat>
            </suite>
        </statistics>
        """
        data_model = self._get_data_model(statistics_xml)
        self.assert_model(data_model, None,
            [[['Critical Tests', 0, 4, '', '', ''],
            ['All Tests', 0, 4, '', '', '']],
            [['someothertag', 0, 1, '', '', ''],
                ['sometag', 0, 1, '', '', '']],
            [['Data', 0, 4, 'Data', '', ''],
                ['Data.All Settings', 0, 1, 'Data.All Settings', '', ''],
                ['Data.Failing Suite', 0, 3, 'Data.Failing Suite', '', '']]], ['*'])

    def test_errors_xml_parsing(self):
        errors_xml = """
        <errors>
            <msg timestamp="20110531 12:48:09.078" level="ERROR">Invalid syntax in file '/tmp/data/failing_suite.txt' in table 'Settings': Resource file 'nope' does not exist.</msg>
        </errors>
        """
        data_model = self._get_data_model(errors_xml)
        self.assert_model(data_model,
                          1306835289078,
                          [[0, 'E', 1]],
                          ['*', "*Invalid syntax in file '/tmp/data/failing_suite.txt' in table 'Settings': Resource file 'nope' does not exist."])

    if json:
        def test_json_dump_string(self):
            string = u'string\u00A9\v\\\'\"\r\b\t\0\n\fjee'
            for i in range(1024):
                string += unichr(i)
            buffer = StringIO.StringIO()
            json_dump(string, buffer)
            expected = StringIO.StringIO()
            json.dump(string, expected)
            self._assert_long_equals(buffer.getvalue(), expected.getvalue())

    def test_json_dump_integer(self):
        buffer = StringIO.StringIO()
        json_dump(12, buffer)
        assert_equals('12', buffer.getvalue())

    def test_json_dump_list(self):
        buffer = StringIO.StringIO()
        json_dump([1,2,3, 'hello', 'world'], buffer)
        assert_equals('[1,2,3,"hello","world"]', buffer.getvalue())

    def test_json_dump_dictionary(self):
        buffer = StringIO.StringIO()
        json_dump({'key':1, 'hello':'world'}, buffer)
        assert_true(buffer.getvalue() in ('{"hello":"world","key":1}',
                                          '{"key":1,"hello":"world"}'))

    def test_json_dump_None(self):
        buffer = StringIO.StringIO()
        json_dump(None, buffer)
        assert_equals('null', buffer.getvalue())

    def _get_data_model(self, xml_string):
        sax.parseString('<robot generator="test">%s<statistics/><errors/></robot>' % xml_string, self._handler)
        return self._handler.datamodel

    def _assert_long_equals(self, given, expected):
        if given != expected:
            for index, char in enumerate(given):
                if index >= len(expected):
                    raise AssertionError('Expected is shorter than given string. Ending that was missing %s' % given[index:])
                if char != expected[index]:
                    raise AssertionError("Given and expected not equal ('%s' != '%s') at index %s.\n'%s' !=\n'%s'" %
                                         (char, expected[index], index, self._snippet(index, given), self._snippet(index, expected)))
            if len(expected) > len(given):
                raise AssertionError('Expected is longer than given string. Ending that was missing %s' % expected[len(given)-1:])

    def _snippet(self, index, string):
        start = max(0, index-20)
        start_padding = '' if start==0 else '...'
        end = min(len(string), index+20)
        end_padding = '' if end==0 else '...'
        return start_padding+string[start:end]+end_padding
