from __future__ import with_statement
import StringIO
import time

import unittest
import xml.sax as sax

from robot.result.jsparser import _RobotOutputHandler
from robot.result.elementhandlers import Context
from robot.utils.asserts import assert_equals, assert_true


# TODO: Split this monster test suite.

class TestJsSerializer(unittest.TestCase):

    SUITE_XML = """
<suite source="/tmp/verysimple.txt" name="Verysimple">
  <doc>*html* &lt;esc&gt; http://x.y http://x.y/z.jpg</doc>
  <metadata>
    <item name="key">val</item>
    <item name="esc">&lt;</item>
    <item name="html">http://x.y.x.jpg</item>
  </metadata>
  <test name="Test" timeout="">
    <doc>*html* &lt;esc&gt; http://x.y http://x.y/z.jpg</doc>
    <kw type="kw" name="Keyword.Example" timeout="1 second">
      <doc>*html* &lt;esc&gt; http://x.y http://x.y/z.jpg</doc>
      <arguments><arg>a1</arg><arg>a2</arg></arguments>
      <msg timestamp="20110601 12:01:51.353" level="WARN">simple</msg>
      <status status="PASS" endtime="20110601 12:01:51.353" starttime="20110601 12:01:51.376"></status>
    </kw>
    <tags><tag>t1</tag><tag>t2</tag></tags>
    <status status="PASS" endtime="20110601 12:01:51.354" critical="yes" starttime="20110601 12:01:51.353"></status>
  </test>
  <status status="PASS" endtime="20110601 12:01:51.354" starttime="20110601 12:01:51.329"></status>
</suite>"""

    FOR_LOOP_XML = """
        <kw type="for" name="${i} IN RANGE [ 2 ]" timeout="">
            <doc></doc>
            <arguments></arguments>
            <kw type="foritem" name="${i} = 0" timeout="">
                <doc></doc>
                <arguments></arguments>
                <kw type="kw" name="babba" timeout="">
                    <doc>Foo bar.</doc>
                    <arguments>
                        <arg>${i}</arg>
                    </arguments>
                    <msg timestamp="20110617 09:56:04.365" level="INFO">0</msg>
                    <status status="PASS" endtime="20110617 09:56:04.365" starttime="20110617 09:56:04.365"></status>
                </kw>
                <status status="PASS" endtime="20110617 09:56:04.365" starttime="20110617 09:56:04.365"></status>
            </kw>
            <kw type="foritem" name="${i} = 1" timeout="">
                <doc></doc>
                <arguments></arguments>
                <kw type="kw" name="babba" timeout="">
                    <doc>Foo bar.</doc>
                    <arguments>
                        <arg>${i}</arg>
                    </arguments>
                    <msg timestamp="20110617 09:56:04.366" level="INFO">1</msg>
                    <status status="PASS" endtime="20110617 09:56:04.366" starttime="20110617 09:56:04.366"></status>
                </kw>
                <status status="PASS" endtime="20110617 09:56:04.367" starttime="20110617 09:56:04.366"></status>
            </kw>
            <status status="PASS" endtime="20110617 09:56:04.368" starttime="20110617 09:56:04.364"></status>
        </kw>
        """

    def setUp(self):
        self._context = Context()
        self._handler = _RobotOutputHandler(self._context)

    def test_message_xml_parsing(self):
        data_model = self._get_data_model('<msg timestamp="20110531 12:48:09.088" level="FAIL">AssertionError</msg>')
        self.assert_model(data_model,
                          1306835289088,
                          [-1, 1, 2],
                          ['*', '*F', '*AssertionError'],
                          [0])

    def test_plain_message_xml_parsing(self):
        data_model = self._get_data_model('<msg timestamp="20110531 12:48:09.088" level="FAIL">AssertionError</msg>')
        self.assert_model(data_model, basemillis=1306835289088, plain_suite=[0, '*F', '*AssertionError'])

    def assert_model(self, data_model, basemillis=None, suite=None, strings=None, integers=None, plain_suite=None):
        if basemillis is not None:
            assert_equals(data_model._robot_data['baseMillis'], basemillis)
        if suite is not None:
            assert_equals(data_model._robot_data['suite'], suite)
        if strings is not None:
            assert_equals(data_model._robot_data['strings'], strings)
        if integers is not None:
            assert_equals(data_model._robot_data['integers'], integers)
        if plain_suite is not None:
            self._assert_plain_suite(data_model, plain_suite)

    def assert_model_does_not_contain(self, data_model, items):
        suite = self._reverse_from_ids(data_model,
                                       data_model._robot_data['suite'])
        self._check_does_not_contain(suite, ['*'+i for i in items])

    def _check_does_not_contain(self, suite, items):
        for item in suite:
            assert_true(item not in items)
            if isinstance(item, list):
                self._check_does_not_contain(item, items)

    def _assert_plain_suite(self, data_model, plain_suite):
        reversed = self._reverse_from_ids(data_model, data_model._robot_data['suite'])
        assert_equals(reversed, plain_suite)

    def _reverse_from_ids(self, data, item):
        if item is None:
            return None
        if isinstance(item, (int, long)):
            return self._reverse_id(data, item)
        recurse = self._reverse_from_ids
        if isinstance(item, list):
            return [recurse(data, i) for i in item]
        if isinstance(item, dict):
            return dict((recurse(data, k),
                         recurse(data, item[k])) for k in item)
        raise AssertionError('Unexpected item %r' % item)

    def _reverse_id(self, data_model, id):
        if id is None:
            return None
        elif id < 0:
            return data_model._robot_data['integers'][abs(id)-1]
        return data_model._robot_data['strings'][id]

    def test_status_xml_parsing(self):
        data_model = self._get_data_model('<status status="PASS" endtime="20110531 12:48:09.042" starttime="20110531 12:48:09.000"></status>')
        self.assert_model(data_model, plain_suite=['*P',0,42])

    def test_status_with_message_xml_parsing(self):
        data_model = self._get_data_model('<status status="PASS" endtime="20110531 12:48:09.042" starttime="20110531 12:48:09.000">Message</status>')
        self.assert_model(data_model, plain_suite=['*P', 0, 42, '*Message'])

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
        self.assert_model(data_model,
            plain_suite=['*kw', '*KwName', '*',
                         ['*F', 0, -10],
                        [],
                         [[0, '*F', '*AssertionError'],
                         [None, '*F', '*AssertionError'],
                         [-10, '*F', '*AssertionError']]
                        ])

    def test_generated_millis(self):
        self._context.timestamp('19790101 12:00:00.000')
        data_model = self._get_data_model(self.SUITE_XML)
        data_model._set_generated(time.localtime(284029200))
        assert_equals(data_model._robot_data['generatedMillis'], 0)

    def test_arguments_xml_parsing(self):
        arguments_xml = """
        <arguments>
            <arg>${arg}</arg>
            <arg>${level}</arg>
        </arguments>
        """
        data_model = self._get_data_model(arguments_xml)
        self.assert_model(data_model,
                          plain_suite='*${arg}, ${level}')

    def test_teardown_xml_parsing(self):
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
        self.assert_model(data_model,
                          plain_suite=['*teardown', '*BuiltIn.Log', '*', '*Logs the given message with the given level.', '*keyword teardown',
                                       ['*P', -1, 2], [],
                                        [[0, '*W', '*keyword teardown']]])
        assert_equals(self._context.link_to([0, 'W', 'keyword teardown']), "keyword_suite.0")

    def test_for_loop_xml_parsing(self):
        self._context.start_suite('suite')
        data_model = self._get_data_model(self.FOR_LOOP_XML)
        self.assert_model(data_model,
            plain_suite=['*forloop', '*${i} IN RANGE [ 2 ]', '*', '*', '*',
                         ['*P', -1, 4],
                         [['*foritem', '*${i} = 0', '*', '*', '*',
                           ['*P', 0, 0],
                          [['*kw', '*babba', '*', '*Foo bar.', '*${i}',
                           ['*P', 0, 0], [], [[0, '*I', '*0']]]],
                            []
                           ],
                         ['*foritem', '*${i} = 1', '*', '*', '*',
                          ['*P', 1, 1],
                          [['*kw', '*babba', '*', '*Foo bar.', '*${i}',
                            ['*P', 1, 0],
                            [],
                           [[1, '*I', '*1']]]],
                          [],
                          ],
                         ],
                         [],
                        ])

    def test_for_loop_remove_keywords(self):
        self._context.start_suite('suite')
        test_xml = '<test name="Test" timeout=""><doc></doc>' + \
                   self.FOR_LOOP_XML + \
                   '<tags></tags><status status="PASS" endtime="20110601 12:01:51.354" critical="yes" starttime="20110601 12:01:51.353"></status></test>'
        self._test_remove_keywords(self._get_data_model(test_xml))

    def test_remove_errors(self):
        data_model = self._get_data_model(self.SUITE_XML)
        data_model.remove_errors()
        if 'errors' in data_model._robot_data:
            raise AssertionError('Errors still in data')

    def _test_remove_keywords(self, data_model, should_contain_strings=None):
        strings_before = self._list_size(data_model._robot_data['strings'])
        integers_before = self._list_size(data_model._robot_data['integers'])
        data_model_json_before = StringIO.StringIO()
        data_model.write_to(data_model_json_before)
        data_model.remove_keywords()
        self.assert_model_does_not_contain(data_model, ['kw', 'setup', 'forloop', 'foritem'])
        if should_contain_strings:
            for string in should_contain_strings:
                assert_true(string in data_model._robot_data['strings'], msg='string "%s" not in strings' % string)
        data_model_json_after = StringIO.StringIO()
        data_model.write_to(data_model_json_after)
        assert_true(len(data_model_json_before.getvalue()) > len(data_model_json_after.getvalue()))
        assert_true(strings_before > self._list_size(data_model._robot_data['strings']))
        assert_true(integers_before > self._list_size(data_model._robot_data['integers']))

    def _list_size(self, array):
        return len(''.join(str(val) for val in array))

    def test_suite_xml_parsing(self):
        # Tests parsing the whole suite structure
        data_model = self._get_data_model(self.SUITE_XML)
        doc = '*<b>html</b> &lt;esc&gt; <a href="http://x.y">http://x.y</a> <img src="http://x.y/z.jpg" title="http://x.y/z.jpg" style="border: 1px solid gray" />'
        self.assert_model(data_model, basemillis=1306918911353,
                          plain_suite=['*/tmp/verysimple.txt', '*Verysimple', doc,
                                       ['*key', '*val', '*esc', '*&lt;',
                                        '*html', '*<img src="http://x.y.x.jpg" title="http://x.y.x.jpg" style="border: 1px solid gray" />'],
                                       ['*P', -24, 25],
                                       [],
                              [['*Test', '*', '*Y', doc,
                                  ['*t1', '*t2'], ['*P', 0, 1],
                                  [
                                      ['*kw', '*Keyword.Example', '*1 second', doc,
                                        '*a1, a2', ['*P', 23, -23], [], [[0, '*W', '*simple']]]
                                  ]
                              ]],
                                       [],
                              [1, 1, 1, 1]])
        assert_equals(self._context.link_to([0, 'W', 'simple']),
                      'keyword_Verysimple.Test.0')

    def test_suite_data_model_keywords_clearing(self):
        self._test_remove_keywords(self._get_data_model(self.SUITE_XML), should_contain_strings=['*key', '*val'])

    def test_statistics_xml_parsing(self):
        statistics_xml = """
        <statistics>
            <total>
                <stat fail="4" pass="0">Critical Tests</stat>
                <stat fail="4" pass="0">All Tests</stat>
            </total>
            <tag>
                <stat info="" fail="1" pass="0" links="" doc="">someothertag</stat>
                <stat info="" fail="1" pass="0" links="" doc="*bold*">sometag</stat>
            </tag>
            <suite>
                <stat fail="4" name="Data" pass="0">Data</stat>
                <stat fail="1" name="All Settings" pass="0">Data.All Settings</stat>
                <stat fail="3" name="Failing Suite" pass="0">Data.Failing Suite</stat>
            </suite>
        </statistics>
        """
        data_model = self._get_data_model(statistics_xml)
        expected = [[{'label': 'Critical Tests', 'pass': 0, 'fail': 4},
                     {'label': 'All Tests', 'pass': 0, 'fail': 4}],
                    [{'label': 'someothertag', 'pass': 0, 'fail': 1,
                      'info': '', 'links': '', 'doc': ''},
                     {'label': 'sometag', 'pass': 0, 'fail': 1,
                      'info': '', 'links': '', 'doc': '<b>bold</b>'}],
                    [{'label': 'Data', 'name': 'Data', 'pass': 0, 'fail': 4},
                     {'label': 'Data.All Settings', 'name': 'All Settings', 'pass': 0, 'fail': 1},
                     {'label': 'Data.Failing Suite', 'name': 'Failing Suite', 'pass': 0, 'fail': 3}]]
        self.assert_model(data_model, 0, expected, ['*'])

    def test_errors_xml_parsing(self):
        errors_xml = """
        <errors>
            <msg timestamp="20110531 12:48:09.078" level="ERROR">Invalid syntax in file '/tmp/data/failing_suite.txt' in table 'Settings': Resource file 'nope' does not exist.</msg>
        </errors>
        """
        data_model = self._get_data_model(errors_xml)
        self.assert_model(data_model, basemillis=1306835289078,
                          plain_suite=[[0, '*E', "*Invalid syntax in file '/tmp/data/failing_suite.txt' in table 'Settings': Resource file 'nope' does not exist."]])

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


if __name__ == '__main__':
    unittest.main()
