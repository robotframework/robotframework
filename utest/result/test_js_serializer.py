from __future__ import with_statement
from StringIO import StringIO
import time
import os

import unittest
from mock import Mock
from robot.output.loggerhelper import Message
from robot.output.readers import Keyword
from robot.output.xmllogger import XmlLogger

from robot.result.outputparser import OutputParser, CombiningOutputParser
from robot.utils.abstractxmlwriter import AbstractXmlWriter
from robot.utils.asserts import assert_equals, assert_true
from robot.utils.xmlwriter import XmlWriter


def assert_model(data_model, basemillis=None, suite=None, strings=None, plain_suite=None):
    if basemillis is not None:
        basemillis += time.altzone*1000
        assert_equals(data_model._robot_data['baseMillis'], basemillis)
    if suite is not None:
        assert_equals(data_model._robot_data['suite'], suite)
    if strings is not None:
        assert_equals(data_model._robot_data['strings'], strings)
    if plain_suite is not None:
        _assert_plain_suite(data_model, plain_suite)


def _assert_plain_suite(data_model, plain_suite):
    _assert_plain_suite_item(plain_suite, data_model._robot_data['suite'], data_model._robot_data['strings'])

def _assert_plain_suite_item(expected, actual, strings):
    if isinstance(expected, (float, int)):
        assert_equals(expected, actual)
    elif isinstance(expected, list):
        assert_equals(len(expected), len(actual), 'len(%s) != len(%s)' % (expected, actual))
        for exp, act in zip(expected, actual):
            _assert_plain_suite_item(exp, act, strings)
    else:
        actual =_reverse_id(strings, actual)
        assert_equals(expected, actual)

def _reverse_id(strings, id):
    if id is None:
        return None
    return strings[id]


class _JsSerializerTestBase(unittest.TestCase):

    def _get_data_model(self, xml_string, parser=None):
        return self._parse(xml_string, parser)._get_data_model()

    def _parse(self, xml_string, parser=None):
        return self._parse_string('<robot generator="test">%s<statistics/><errors/></robot>' % xml_string,
                                  parser or self._parser)

    def _parse_string(self, xml_string, parser):
        outxml = StringIO(xml_string)
        parser._parse_fileobj(outxml)
        return parser

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


class _StreamXmlWriter(AbstractXmlWriter):

    def __init__(self, stream):
        self._stream = stream

    def _start(self, name, attrs):
        self._stream.write('<'+name)
        for attr in attrs:
            self._stream.write(' %s="%s"' % (attr, attrs[attr]))
        self._stream.write('>')

    def _content(self, content):
        self._stream.write(content)

    def _end(self, name):
        self._stream.write('</%s>' % name)

class StreamXmlLogger(XmlLogger):

    def _get_writer(self, stream, generator):
        return _StreamXmlWriter(stream)


class TestJsSerializer(_JsSerializerTestBase):

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
  <test name="setup" timeout="">
    <doc>docu</doc>
    <kw type="kw" name="Keyword.Example" timeout="1 second">
      <doc>*html* &lt;esc&gt; http://x.y http://x.y/z.jpg</doc>
      <arguments><arg>a1</arg><arg>a2</arg></arguments>
      <msg timestamp="20110601 12:01:51.353" level="INFO">sample</msg>
      <status status="PASS" endtime="20110601 12:01:51.453" starttime="20110601 12:01:51.453"></status>
    </kw>
    <tags></tags>
    <status status="PASS" endtime="20110601 12:01:51.454" critical="yes" starttime="20110601 12:01:51.453"></status>
  </test>
  <kw type="teardown" name="Suite Teardown" timeout="">
    <doc>std</doc>
    <arguments><arg>1</arg><arg>2</arg></arguments>
    <msg timestamp="20110601 12:01:51.453" level="INFO">STD</msg>
    <status status="PASS" endtime="20110601 12:01:51.454" starttime="20110601 12:01:51.453"></status>
  </kw>
  <status status="PASS" endtime="20110601 12:01:51.454" starttime="20110601 12:01:51.329"></status>
</suite>"""

    SUITE_XML_STATS = """
    <statistics>
    <total>
    <stat fail="0" pass="2">Critical Tests</stat>
    <stat fail="0" pass="2">All Tests</stat>
    </total>
    <tag>
    <stat info="" links="" doc="" combined="" pass="1" fail="0">t1</stat>
    <stat info="" links="" doc="" combined="" pass="1" fail="0">t2</stat>
    </tag>
    <suite>
    <stat fail="0" name="Verysimple" idx="s1" pass="2">Verysimple</stat>
    </suite>
    </statistics>
    <errors>
    </errors>
    """

    SUITE_XML_COMBINED = """<?xml version="1.0" encoding="UTF-8"?>
    <robot generated="20111004 10:45:37.778" generator="Rebot 2.6.1 (Python 2.6.5 on linux2)">
    <suite name="Verysimple &amp; Verysimple">
       <doc></doc>
       <metadata></metadata>"""+\
        SUITE_XML+\
        SUITE_XML+\
    """<status status="PASS" elapsedtime="250" endtime="N/A" starttime="N/A"></status>
    </suite>
    <statistics>
    <total>
    <stat fail="0" pass="4">Critical Tests</stat>
    <stat fail="0" pass="4">All Tests</stat>
    </total>
    <tag>
    <stat info="" links="" doc="" combined="" pass="2" fail="0">t1</stat>
    <stat info="" links="" doc="" combined="" pass="2" fail="0">t2</stat>
    </tag>
    <suite>
    <stat fail="0" name="Verysimple &amp; Verysimple" idx="s1" pass="4">Verysimple &amp; Verysimple</stat>
    <stat fail="0" name="Verysimple" idx="s1-s1" pass="2">Verysimple &amp; Verysimple.Verysimple</stat>
    <stat fail="0" name="Verysimple" idx="s1-s2" pass="2">Verysimple &amp; Verysimple.Verysimple</stat>
    </suite>
    </statistics>
    <errors>
    </errors>
    <errors>
    </errors>
    </robot>
    """

    FOR_LOOP_XML = """
        <kw type="for" name="${i} IN RANGE [ 2 ]" timeout="">
            <doc></doc>
            <arguments></arguments>
            <kw type="foritem" name="${i} = 0" timeout="">
                <doc></doc>
                <arguments></arguments>
                <kw type="kw" name="babba" timeout="">
                    <doc>Doc in for</doc>
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
                    <doc>Doc in for</doc>
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
        self._parser = OutputParser()
        self._context = self._parser._context

    def test_message_xml_parsing(self):
        xml = self._write_message_to_xml(Message('AssertionError', level='FAIL', timestamp='20110531 12:48:09.088'))
        data_model = self._get_data_model(xml)
        assert_model(data_model, 1306846089088, [0, 4, 1], ['*', '*AssertionError'])

    def _write_message_to_xml(self, message):
        stream = StringIO()
        StreamXmlLogger(stream).log_message(message)
        return stream.getvalue()

    def test_plain_message_xml_parsing(self):
        xml = self._write_message_to_xml(Message('AssertionError', level='FAIL', timestamp='20110531 12:48:09.088'))
        data_model = self._get_data_model(xml)
        assert_model(data_model, basemillis=1306846089088, plain_suite=[0, 4, '*AssertionError'])

    def assert_model_does_not_contain(self, data_model, items):
        suite = self._reverse_from_ids(data_model,
                                       data_model._robot_data['suite'])
        self._check_does_not_contain(suite, items)

    def _check_does_not_contain(self, suite, items):
        for item in suite:
            assert_true(item not in items)
            if isinstance(item, list):
                self._check_does_not_contain(item, items)

    def _reverse_from_ids(self, data, item):
        if item is None:
            return None
        if isinstance(item, (long, int)):
            return item
        return [self._reverse_from_ids(data, i) for i in item]

    def test_status_xml_parsing(self):
        xml = self._write_status_to_xml(status='PASS',
                                        starttime='20110531 12:48:09.000',
                                        endtime='20110531 12:48:09.042')
        data_model = self._get_data_model(xml)
        assert_model(data_model, plain_suite=[1, 0, 42])

    def _write_status_to_xml(self, status, starttime, endtime, message=None):
        stats = Mock()
        stats.status = status
        stats.starttime = starttime
        stats.endtime = endtime
        stream = StringIO()
        StreamXmlLogger(stream)._write_status(stats, message=message)
        return stream.getvalue()

    def test_status_with_message_xml_parsing(self):
        xml = self._write_status_to_xml(status='PASS',
                                        starttime='20110531 12:48:09.000',
                                        endtime='20110531 12:48:09.042',
                                        message='Message')
        data_model = self._get_data_model(xml)
        assert_model(data_model, plain_suite=[1, 0, 42, '*Message'])

    def test_times(self):
        self._context.start_suite()
        times = """
        <kw type="kw" name="KwName" timeout="">
        <msg timestamp="20110531 12:48:09.020" level="FAIL">AssertionError</msg>
        <msg timestamp="N/A" level="FAIL">AssertionError</msg>
        <msg timestamp="20110531 12:48:09.010" level="FAIL">AssertionError</msg>
        <status status="FAIL" endtime="20110531 12:48:09.010" starttime="20110531 12:48:09.020"></status>
        </kw>
        """
        data_model = self._get_data_model(times)
        assert_model(data_model,
            plain_suite=[0, '*KwName', '*',
                         [0, 0, -10],
                        [],
                         [[0, 4, '*AssertionError'],
                         [None, 4, '*AssertionError'],
                         [-10, 4, '*AssertionError']]
                        ])

    def test_generated_millis(self):
        self._context.timestamp('19790101 12:00:00.000')
        data_model = self._get_data_model(self.SUITE_XML)
        basetime = 284040000 + time.altzone
        data_model._set_generated(time.localtime(basetime))
        assert_equals(data_model._robot_data['baseMillis'], basetime*1000)
        assert_equals(data_model._robot_data['generatedMillis'], 0)

    def test_arguments_xml_parsing(self):
        arguments_xml = """
        <arguments>
            <arg>${arg}</arg>
            <arg>${level}</arg>
        </arguments>
        """
        data_model = self._get_data_model(arguments_xml)
        assert_model(data_model, plain_suite='*${arg}, ${level}')

    def test_suite_teardown_parsing(self):
        data_model = self._get_data_model("""
        <suite source="/tmp/supersimple.txt" name="Supersimple">
          <doc>sdoc</doc>
          <test name="Test" timeout="">
            <doc>tdoc</doc>
            <status status="PASS" endtime="20110601 12:01:51.354" critical="yes" starttime="20110601 12:01:51.353"></status>
          </test>
          <kw type="teardown" name="Fail" timeout="">
            <doc>kdoc</doc>
            <msg timestamp="20110601 12:01:51.353" level="WARN">msg</msg>
            <status status="FAIL" endtime="20110601 12:01:51.354" starttime="20110601 12:01:51.354"></status>
          </kw>
          <status status="FAIL" endtime="20110601 12:01:51.354" starttime="20110601 12:01:51.353"></status>
        </suite>""")
        assert_model(data_model,
                     plain_suite=
                     ['*Supersimple', '*/tmp/supersimple.txt', '*', '*sdoc',
                      [0, 0, 1],
                      [],
                      [['*Test', '*', 1, '*tdoc', [1, 0, 1], []]],
                      [[2, '*Fail', '*', '*kdoc',
                       [0, 1, 0], [], [[0, 3, '*msg']]]],
                      1, [1, 0, 1, 0]])
        assert_equals(self._context.link_to([0, 3, 'msg']), "s1-k1")

    def test_test_teardown_parsing(self):
        data_model = self._get_data_model("""
        <suite source="/tmp/supersimple.txt" name="Supersimple">
          <doc>sdoc</doc>
          <test name="T1" timeout="">
            <doc>t1doc</doc>
            <status status="PASS" endtime="20110601 12:01:51.353" critical="yes" starttime="20110601 12:01:51.353"></status>
          </test>
          <test name="T2" timeout="">
            <doc>t2doc</doc>
            <kw type="teardown" name="Fail" timeout="">
              <doc>kdoc</doc>
              <msg timestamp="20110601 12:01:51.353" level="WARN">msg</msg>
              <status status="FAIL" endtime="20110601 12:01:51.354" starttime="20110601 12:01:51.354"></status>
            </kw>
            <status status="FAIL" endtime="20110601 12:01:51.354" critical="yes" starttime="20110601 12:01:51.353"></status>
          </test>
          <status status="FAIL" endtime="20110601 12:01:51.354" starttime="20110601 12:01:51.353"></status>
        </suite>""")
        assert_model(data_model,
                     plain_suite=
                     ['*Supersimple', '*/tmp/supersimple.txt', '*', '*sdoc',
                      [0, 0, 1],
                      [],
                      [['*T1', '*', 1, '*t1doc', [1, 0, 0], []],
                       ['*T2', '*', 1, '*t2doc', [0, 0, 1],
                        [[2, '*Fail', '*', '*kdoc',
                         [0, 1, 0], [], [[0, 3, '*msg']]]]]],
                      [],
                      0, [2, 1, 2, 1]])
        assert_equals(self._context.link_to([0, 3, 'msg']), "s1-t2-k1")

    def test_for_loop_xml_parsing(self):
        self._context.start_suite()
        data_model = self._get_data_model(self.FOR_LOOP_XML)
        assert_model(data_model,
            plain_suite=[3, '*${i} IN RANGE [ 2 ]', '*', '*', '*',
                         [1, -1, 4],
                         [[4, '*${i} = 0', '*', '*', '*',
                           [1, 0, 0],
                          [[0, '*babba', '*', '*Doc in for', '*${i}',
                           [1, 0, 0], [], [[0, 2, '*0']]]],
                            []
                           ],
                         [4, '*${i} = 1', '*', '*', '*',
                          [1, 1, 1],
                          [[0, '*babba', '*', '*Doc in for', '*${i}',
                            [1, 1, 0],
                            [],
                           [[1, 2, '*1']]]],
                          [],
                          ],
                         ],
                         [],
                        ])

    def test_for_loop_remove_keywords(self):
        test_xml = '<suite><doc></doc><metadata></metadata>' + \
                   '<test name="Test" timeout=""><doc></doc>' + \
                   self.FOR_LOOP_XML + \
                   '<tags></tags><status status="PASS" endtime="20110601 12:01:51.354" critical="yes" starttime="20110601 12:01:51.353"></status></test>' + \
                   '<status status="PASS" endtime="20110601 12:01:51.354" critical="yes" starttime="20110601 12:01:51.353"></status></suite>'
        self._test_remove_keywords(self._get_data_model(test_xml),
                                   should_not_contain_strings=['${i} IN RANGE [ 2 ]', 'babba', 'Doc in for'])

    def test_remove_errors(self):
        data_model = self._get_data_model(self.SUITE_XML)
        data_model.remove_errors()
        if 'errors' in data_model._robot_data:
            raise AssertionError('Errors still in data')

    def _test_remove_keywords(self, data_model, should_not_contain_strings, should_contain_strings=None):
        strings_before = self._list_size(data_model._robot_data['strings'])
        data_model_json_before = StringIO()
        data_model.write_to(data_model_json_before)
        data_model.remove_keywords()
        self.assert_model_does_not_contain(data_model, should_not_contain_strings)
        if should_contain_strings:
            for string in should_contain_strings:
                assert_true(string in data_model._robot_data['strings'], msg='string "%s" not in strings' % string)
        data_model_json_after = StringIO()
        data_model.write_to(data_model_json_after)
        assert_true(len(data_model_json_before.getvalue()) > len(data_model_json_after.getvalue()))
        assert_true(strings_before > self._list_size(data_model._robot_data['strings']))
        self._suite_should_not_have_keywords(data_model._robot_data['suite'])

    def _suite_should_not_have_keywords(self, suite):
        assert_equals(suite[8], [])
        for subsuite in suite[6]:
            self._suite_should_not_have_keywords(subsuite)
        for test in suite[7]:
            assert_equals(test[-1], [])

    def _list_size(self, array):
        return len(''.join(str(val) for val in array))

    def test_suite_xml_parsing(self):
        # Tests parsing the whole suite structure
        data_model = self._get_data_model(self.SUITE_XML)
        doc = '*<b>html</b> &lt;esc&gt; <a href="http://x.y">http://x.y</a> <img src="http://x.y/z.jpg" title="http://x.y/z.jpg" style="border: 1px solid gray">'
        assert_model(data_model, basemillis=1306929711353,
                          plain_suite=['*Verysimple', '*/tmp/verysimple.txt', '*', doc,
                                       ['*key', '*val', '*esc', '*&lt;',
                                        '*html', '*<img src="http://x.y.x.jpg" title="http://x.y.x.jpg" style="border: 1px solid gray">'],
                                       [1, -24, 125],
                                       [],
                              [['*Test', '*', 1, doc,
                                  ['*t1', '*t2'], [1, 0, 1],
                                  [
                                      [0, '*Keyword.Example', '*1 second', doc,
                                        '*a1, a2', [1, 23, -23], [], [[0, 3, '*simple']]]
                                  ]
                              ],['*setup', '*', 1, "*docu",
                                  [], [1, 100, 1],
                                  [
                                      [0, '*Keyword.Example', '*1 second', doc,
                                        '*a1, a2', [1, 100, 0], [], [[0, 2, '*sample']]]
                                  ]
                              ]],
                              [[2, '*Suite Teardown', '*', '*std', '*1, 2', [1, 100, 1], [], [[100, 2, '*STD']]]],
                              0, [2, 2, 2, 2]])
        assert_equals(self._context.link_to([0, 3, 'simple']),'s1-t1-k1')

    def test_combining_two_xmls(self):
        actual = self._combine(self.SUITE_XML+self.SUITE_XML_STATS, self.SUITE_XML+self.SUITE_XML_STATS)
        expected = self._parse_string(self.SUITE_XML_COMBINED, OutputParser())._get_data_model()
        self._verify_robot_data(expected._robot_data, actual._robot_data)

    def test_combined_suite_name(self):
        parser = CombiningOutputParser(main_suite_name='MAIN')
        data = self._combine(self.SUITE_XML+self.SUITE_XML_STATS, self.SUITE_XML+self.SUITE_XML_STATS, parser)._robot_data
        assert_true('*MAIN' in data['strings'])
        assert_true('*Verysimple & Verysimple' not in data['strings'])

    def test_combining_two_different_xmls(self):
        test_xml = """<suite source="test.txt" name="Test">
        <doc></doc>
        <metadata>
        </metadata>
        <test name="testii" timeout="">
        <doc></doc>
        <kw type="kw" name="BuiltIn.Log" timeout="">
        <doc>Logs the given message with the given level.</doc>
        <arguments>
        <arg>moi</arg>
        </arguments>
        <msg timestamp="20111007 09:29:25.934" level="INFO">moi</msg>
        <status status="PASS" endtime="20111007 09:29:25.934" starttime="20111007 09:29:25.933"></status>
        </kw>
        <tags>
        </tags>
        <status status="PASS" endtime="20111007 09:29:25.934" critical="yes" starttime="20111007 09:29:25.933"></status>
        </test>
        <status status="PASS" endtime="20111007 09:29:25.934" starttime="20111007 09:29:25.909"></status>
        </suite>
        """
        test_xml_stats = """<statistics>
        <total>
        <stat fail="0" pass="1">Critical Tests</stat>
        <stat fail="0" pass="1">All Tests</stat>
        </total>
        <tag>
        </tag>
        <suite>
        <stat fail="0" name="Test" idx="s1" pass="1">Test</stat>
        </suite>
        </statistics>
        <errors>
        </errors>"""
        combined = """<?xml version="1.0" encoding="UTF-8"?>
        <robot generated="20111007 09:30:35.073" generator="Rebot 2.6.1 (Python 2.6.5 on linux2)">
        <suite name="Test &amp; Verysimple">
        <doc></doc>
        <metadata>
        </metadata>"""+\
        test_xml+self.SUITE_XML+\
        """<status status="PASS" elapsedtime="150" endtime="N/A" starttime="N/A"></status>
        </suite>
        <statistics>
        <total>
        <stat fail="0" pass="3">Critical Tests</stat>
        <stat fail="0" pass="3">All Tests</stat>
        </total>
        <tag>
        <stat info="" links="" doc="" combined="" pass="1" fail="0">t1</stat>
        <stat info="" links="" doc="" combined="" pass="1" fail="0">t2</stat>
        </tag>
        <suite>
        <stat fail="0" name="Test &amp; Verysimple" idx="s1" pass="3">Test &amp; Verysimple</stat>
        <stat fail="0" name="Test" idx="s1-s1" pass="1">Test &amp; Verysimple.Test</stat>
        <stat fail="0" name="Verysimple" idx="s1-s2" pass="2">Test &amp; Verysimple.Verysimple</stat>
        </suite>
        </statistics>
        <errors>
        </errors>
        </robot>
        """
        actual = self._combine(test_xml+test_xml_stats, self.SUITE_XML+self.SUITE_XML_STATS)
        expected = self._parse_string(combined, OutputParser())._get_data_model()
        self._verify_robot_data(expected._robot_data, actual._robot_data)

    def _combine(self, xml_string1, xml_string2, combining_parser=None):
        combining_parser = combining_parser or CombiningOutputParser()
        self._parse_string('<robot generator="test">%s</robot>' % xml_string1, combining_parser)
        self._parse_string('<robot generator="test">%s</robot>' % xml_string2, combining_parser)
        return combining_parser._get_data_model()

    def _verify_robot_data(self, expected, actual):
        for key in actual:
            if key in ['generatedMillis', 'generatedTimestamp']:
                continue
            assert_equals(actual[key], expected[key],
                          msg='Values "%s" are different:\nexpected= %r\nactual=   %r\n' %
                              (key, expected[key], actual[key]))
        assert_equals(len(actual), len(expected))

    def test_suite_data_model_keywords_clearing(self):
        self._test_remove_keywords(self._get_data_model(self.SUITE_XML),
                                   should_contain_strings=['*key', '*val', '*docu'],
                                   should_not_contain_strings=['**html* &lt;esc&gt; http://x.y http://x.y/z.jpg',
                                                               '*Keyword.Example', '*Suite Teardown', '*std', '*STD'])

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
                    [{'label': 'someothertag', 'pass': 0, 'fail': 1},
                     {'label': 'sometag', 'pass': 0, 'fail': 1,
                      'doc': '<b>bold</b>'}],
                    [{'label': 'Data', 'name': 'Data', 'pass': 0, 'fail': 4},
                     {'label': 'Data.All Settings', 'name': 'All Settings', 'pass': 0, 'fail': 1},
                     {'label': 'Data.Failing Suite', 'name': 'Failing Suite', 'pass': 0, 'fail': 3}]]
        assert_model(data_model, suite=expected, strings=['*'])

    def test_errors_xml_parsing(self):
        errors_xml = """
        <errors>
            <msg timestamp="20110531 12:48:09.078" level="ERROR">Error in file '/tmp/data/failing_suite.txt' in table 'Settings': Resource file 'nope' does not exist.</msg>
        </errors>
        """
        data_model = self._get_data_model(errors_xml)
        assert_model(data_model, basemillis=1306846089078,
                     plain_suite=[[0, 5, "*Error in file '/tmp/data/failing_suite.txt' in table 'Settings': Resource file 'nope' does not exist."]])


class TestTestSplittingJsSerializer(_JsSerializerTestBase):

    def setUp(self):
        self._parser = OutputParser(split_log=True)
        self._context = self._parser._context

    def test_split_tests(self):
        data_model = self._get_data_model("""
<suite source="/tmp/supersimple.txt" name="Supersimple">
  <doc>sdoc</doc>
  <test name="Test" timeout="">
    <doc>doc</doc>
    <kw type="kw" name="Keyword.Example" timeout="">
      <status status="PASS" endtime="20110601 12:01:51.353" starttime="20110601 12:01:51.376"></status>
    </kw>
    <kw type="kw" name="Second keyword" timeout="">
      <status status="PASS" endtime="20110601 12:01:51.353" starttime="20110601 12:01:51.376"></status>
    </kw>
    <status status="PASS" endtime="20110601 12:01:51.354" critical="yes" starttime="20110601 12:01:51.353"></status>
  </test>
  <status status="PASS" endtime="20110601 12:01:51.354" starttime="20110601 12:01:51.329"></status>
</suite>""")
        assert_model(data_model,
                     plain_suite=
                     ['*Supersimple', '*/tmp/supersimple.txt', '*', '*sdoc',
                      [1, -47, 25],
                      [],
                      [['*Test', '*', 1, '*doc', [1, -23, 1], 1]],
                      [],
                      0, [1, 1, 1, 1]])
        expected_data = [[0, '*Keyword.Example', '*', [1, 0, -23], [], []],
                         [0, '*Second keyword', '*', [1, 0, -23], [], []]]
        keywords, strings = self._context.split_results[0]
        _assert_plain_suite_item(expected_data, keywords, strings)

    def test_split_tests_and_suite_keywords(self):
        data_model = self._get_data_model("""
<suite source="/tmp/supersimple.txt" name="Supersimple">
  <doc>sdoc</doc>
  <kw type="setup" name="Suite Setup" timeout="1 year">
    <doc>setup doc</doc>
    <kw type="kw" name="First keyword" timeout="">
      <doc>1st doc</doc>
      <msg timestamp="20110601 12:01:51.353" level="WARN">setup msg</msg>
      <status status="PASS" endtime="20110601 12:01:51.353" starttime="20110601 12:01:51.353"></status>
      <kw type="kw" name="Sub keyword" timeout="">
        <doc>sub doc</doc>
        <status status="PASS" endtime="20110601 12:01:51.353" starttime="20110601 12:01:51.353"></status>
      </kw>
    </kw>
    <kw type="kw" name="Second keyword" timeout="">
      <doc>2nd doc</doc>
      <status status="PASS" endtime="20110601 12:01:51.353" starttime="20110601 12:01:51.353"></status>
    </kw>
    <status status="PASS" endtime="20110601 12:01:51.353" starttime="20110601 12:01:51.353"></status>
  </kw>
  <test name="Test" timeout="">
    <doc>doc</doc>
    <kw type="kw" name="Keyword.Example" timeout="">
      <doc>kd</doc>
      <status status="PASS" endtime="20110601 12:01:51.354" starttime="20110601 12:01:51.353"></status>
    </kw>
    <kw type="teardown" name="Pass" timeout="">
      <doc>ted</doc>
      <status status="PASS" endtime="20110601 12:01:51.354" starttime="20110601 12:01:51.354"></status>
    </kw>
    <status status="PASS" endtime="20110601 12:01:51.354" critical="yes" starttime="20110601 12:01:51.353"></status>
  </test>
  <kw type="teardown" name="Suite Teardown" timeout="">
    <doc>td doc</doc>
    <msg timestamp="20110601 12:01:51.354" level="WARN">td msg</msg>
    <kw type="kw" name="Td Sub keyword" timeout="">
      <doc>td sub doc</doc>
      <status status="PASS" endtime="20110601 12:01:51.354" starttime="20110601 12:01:51.354"></status>
    </kw>
    <status status="FAIL" endtime="20110601 12:01:51.354" starttime="20110601 12:01:51.354"></status>
  </kw>
  <status status="FAIL" endtime="20110601 12:01:51.354" starttime="20110601 12:01:51.353"></status>
</suite>""")
        assert_model(data_model,
                     plain_suite=
                     ['*Supersimple', '*/tmp/supersimple.txt', '*', '*sdoc',
                      [0, 0, 1],
                      [],
                      [['*Test', '*', 1, '*doc', [1, 0, 1], 2]],
                      [
                       [1, '*Suite Setup', '*1 year', '*setup doc',
                        [1, 0, 0], 1, []],
                       [2, '*Suite Teardown', '*', '*td doc',
                        [0, 1, 0], 3, [[1, 3, '*td msg']]],
                      ],
                      1, [1, 0, 1, 0]])
        split_test = [[0, '*Keyword.Example', '*', '*kd', [1, 0, 1], [], []],
                      [2, '*Pass', '*', '*ted', [1, 1, 0], [], []]]
        _assert_plain_suite_item(split_test, *self._context.split_results[1])
        split_setup = [[0, '*First keyword', '*', '*1st doc', [1, 0, 0],
                        [[0, '*Sub keyword', '*', '*sub doc', [1, 0, 0], [], []]],
                        [[0, 3, '*setup msg']]
                       ],
                       [0, '*Second keyword', '*', '*2nd doc', [1, 0, 0], [], []]]
        _assert_plain_suite_item(split_setup, *self._context.split_results[0])
        split_teardown = [[0, '*Td Sub keyword', '*', '*td sub doc', [1, 1, 0], [], []]]
        _assert_plain_suite_item(split_teardown, *self._context.split_results[2])
        assert_equals(self._context.link_to([0, 3, 'setup msg']), "s1-k1-k1")
        assert_equals(self._context.link_to([1, 3, 'td msg']), "s1-k2")

    def test_tests_and_suite_keywords_without_keywords_are_not_split(self):
        data_model = self._get_data_model("""
<suite source="/tmp/supersimple.txt" name="Supersimple">
  <doc>sdoc</doc>
  <kw type="setup" name="SSetup" timeout="">
    <doc>setup</doc>
    <status status="PASS" endtime="20110601 12:01:51.353" starttime="20110601 12:01:51.353"></status>
  </kw>
  <test name="Test" timeout="1s">
    <doc>doc</doc>
    <kw type="kw" name="Keyword" timeout="">
      <doc>kd</doc>
      <status status="PASS" endtime="20110601 12:01:51.354" starttime="20110601 12:01:51.353"></status>
    </kw>
    <status status="PASS" endtime="20110601 12:01:51.354" critical="yes" starttime="20110601 12:01:51.353"></status>
  </test>
  <test name="Empty" timeout="">
    <doc>empty</doc>
    <status status="FAIL" endtime="20110601 12:01:51.354" critical="no" starttime="20110601 12:01:51.354">Err</status>
  </test>
  <kw type="teardown" name="STeardown" timeout="">
    <doc>td</doc>
    <msg timestamp="20110601 12:01:51.354" level="WARN">msg</msg>
    <status status="PASS" endtime="20110601 12:01:51.354" starttime="20110601 12:01:51.354"></status>
  </kw>
  <status status="PASS" endtime="20110601 12:01:51.354" starttime="20110601 12:01:51.353"></status>
</suite>""")
        assert_model(data_model,
                     plain_suite=
                     ['*Supersimple', '*/tmp/supersimple.txt', '*', '*sdoc',
                      [1, 0, 1], [],
                      [['*Test', '*1s', 1, '*doc', [1, 0, 1], 1],
                       ['*Empty', '*', 0, '*empty', [0, 1, 0, '*Err'], []]],
                      [[1, '*SSetup', '*', '*setup',
                        [1, 0, 0], [], []],
                       [2, '*STeardown', '*', '*td',
                        [1, 1, 0], [], [[1, 3, '*msg']]]],
                      0, [2, 1, 1, 1]])
        split_test = [[0, '*Keyword', '*', '*kd', [1, 0, 1], [], []]]
        _assert_plain_suite_item(split_test, *self._context.split_results[0])


class TestRelativeSuiteSource(_JsSerializerTestBase):
    SUITE_XML = """
<suite source="/tmp/supersimple.txt" name="Supersimple">
  <test name="Test" timeout="">
    <doc>doc</doc>
    <kw type="kw" name="Keyword.Example" timeout="">
      <status status="PASS" endtime="20110601 12:01:51.353" starttime="20110601 12:01:51.376"></status>
    </kw>
    <status status="PASS" endtime="20110601 12:01:51.354" critical="yes" starttime="20110601 12:01:51.353"></status>
  </test>
  <status status="PASS" endtime="20110601 12:01:51.354" starttime="20110601 12:01:51.329"></status>
</suite>"""

    def setUp(self):
        self._original_exists = os.path.exists
        os.path.exists = lambda path: True

    def tearDown(self):
        os.path.exists = self._original_exists

    def test_no_log_path(self):
        self._test_rel_path(log='NONE', expected='')

    def test_log_path(self):
        self._test_rel_path(log='/tmp/non_existing_log.html', expected='supersimple.txt')
        self._test_rel_path(log='/tmp/kekko/non_existing_log.html', expected='../supersimple.txt')
        self._test_rel_path(log='/home/non_existing_log.html', expected='../tmp/supersimple.txt')

    def test_no_source(self):
        os.path.exists = lambda path: False
        self._test_rel_path(log='/tmp', expected='')

    def _test_rel_path(self, log, expected):
        parser = OutputParser(log_path=log)
        data_model = self._get_data_model(self.SUITE_XML, parser)
        relpath_id = data_model._robot_data['suite'][2]
        relpath = _reverse_id(data_model._robot_data['strings'], relpath_id)
        assert_equals(relpath, '*'+expected)


if __name__ == '__main__':
    unittest.main()
