import unittest
from StringIO import StringIO
from robot.result.builders import ExecutionResultBuilder
from robot.utils.asserts import assert_equals, assert_true


XML = """<?xml version="1.0" encoding="UTF-8"?>
<robot generated="20111024 13:41:20.873" generator="Robot trunk 20111007 (Python 2.7.2 on linux2)">
<suite source="normal.html" name="Normal">
<doc>Normal test cases</doc>
<metadata>
<item name="Something">My Value</item>
</metadata>
<kw type="setup" name="my setup" timeout="1 year">
<doc></doc>
<arguments>
</arguments>
<status status="PASS" endtime="20111024 13:41:20.888" starttime="20111024 13:41:20.886"></status>
</kw>
<test name="First One" timeout="">
<doc>Test case documentation</doc>
<kw type="kw" name="BuiltIn.Log" timeout="">
<doc>Logs the given message with the given level.</doc>
<arguments>
<arg>Test 1</arg>
</arguments>
<msg timestamp="20111024 13:41:20.927" level="INFO">Test 1</msg>
<status status="PASS" endtime="20111024 13:41:20.928" starttime="20111024 13:41:20.926"></status>
</kw>
<kw type="kw" name="logs on trace" timeout="">
<doc></doc>
<arguments>
</arguments>
<kw type="kw" name="BuiltIn.Log" timeout="">
<doc>Logs the given message with the given level.</doc>
<arguments>
<arg>Log on ${TEST NAME}</arg>
<arg>TRACE</arg>
</arguments>
<status status="PASS" endtime="20111024 13:41:20.932" starttime="20111024 13:41:20.931"></status>
</kw>
<status status="PASS" endtime="20111024 13:41:20.933" starttime="20111024 13:41:20.930"></status>
</kw>
<tags>
<tag>t1</tag>
</tags>
<status status="PASS" endtime="20111024 13:41:20.934" critical="yes" starttime="20111024 13:41:20.925"></status>
</test>
<status status="PASS" endtime="20111024 13:41:20.952" starttime="20111024 13:41:20.873"></status>
</suite>
<statistics>
<total>
<stat fail="0" pass="1">Critical Tests</stat>
<stat fail="0" pass="1">All Tests</stat>
</total>
<tag>
<stat info="" links="" doc="" combined="" pass="1" fail="0">t1</stat>
</tag>
<suite>
<stat fail="0" name="Normal" idx="s1" pass="1">Normal</stat>
</suite>
</statistics>
<errors>
  <msg timestamp="20111024 13:41:20.873" level="ERROR">Error in file 'normal.html' in table 'Settings': Resource file 'nope' does not exist.</msg>
</errors>
</robot>
"""

class TestBuildingSuiteExecutionResult(unittest.TestCase):

    def setUp(self):
        result = ExecutionResultBuilder(StringIO(XML)).build()
        self._suite = result.suite
        self._test = self._suite.tests[0]
        self._keyword = self._test.keywords[0]
        self._user_keyword = self._test.keywords[1]
        self._message = self._keyword.messages[0]
        self._setup = self._suite.keywords[0]
        self._errors = result.errors

    def test_suite_is_built(self):
        assert_equals(self._suite.source, 'normal.html')
        assert_equals(self._suite.name, 'Normal')
        assert_equals(self._suite.doc, 'Normal test cases')
        assert_equals(self._suite.metadata, {'Something': 'My Value'})
        assert_equals(self._suite.status, 'PASS')
        assert_equals(self._suite.starttime, '20111024 13:41:20.873')
        assert_equals(self._suite.endtime, '20111024 13:41:20.952')
        assert_equals(self._suite.critical_stats.passed, 1)
        assert_equals(self._suite.critical_stats.failed, 0)
        assert_equals(self._suite.all_stats.passed, 1)
        assert_equals(self._suite.all_stats.failed, 0)

    def test_testcase_is_built(self):
        assert_equals(self._test.name, 'First One')
        assert_equals(self._test.doc, 'Test case documentation')
        assert_equals(self._test.timeout, '')
        assert_equals(list(self._test.tags), ['t1'])
        assert_equals(len(self._test.keywords), 2)
        assert_equals(self._test.status, 'PASS')
        assert_equals(self._test.starttime, '20111024 13:41:20.925')
        assert_equals(self._test.endtime, '20111024 13:41:20.934')
        assert_true(self._test.critical)

    def test_keyword_is_built(self):
        assert_equals(self._keyword.name, 'BuiltIn.Log')
        assert_equals(self._keyword.doc, 'Logs the given message with the given level.')
        assert_equals(self._keyword.args, ['Test 1'])
        assert_equals(self._keyword.status, 'PASS')
        assert_equals(self._keyword.starttime, '20111024 13:41:20.926')
        assert_equals(self._keyword.endtime, '20111024 13:41:20.928')
        assert_equals(len(self._keyword.keywords), 0)
        assert_equals(len(self._keyword.messages), 1)

    def test_user_keyword_is_built(self):
        assert_equals(self._user_keyword.name, 'logs on trace')
        assert_equals(self._user_keyword.doc, '')
        assert_equals(self._user_keyword.args, [])
        assert_equals(self._user_keyword.status, 'PASS')
        assert_equals(self._user_keyword.starttime, '20111024 13:41:20.930')
        assert_equals(self._user_keyword.endtime, '20111024 13:41:20.933')
        assert_equals(len(self._user_keyword.messages), 0)
        assert_equals(len(self._user_keyword.keywords), 1)

    def test_message_is_built(self):
        assert_equals(self._message.message, 'Test 1')
        assert_equals(self._message.level, 'INFO')
        assert_equals(self._message.timestamp, '20111024 13:41:20.927')

    def test_suite_setup_is_build(self):
        assert_equals(len(self._setup.keywords), 0)
        assert_equals(len(self._setup.messages), 0)


class TestElements(unittest.TestCase):

    def test_nested_suites(self):
        xml = """
        <robot>
        <suite name="foo">
          <suite name="bar">
          </suite>
        </suite>
        </robot>
        """
        result = ExecutionResultBuilder(StringIO(xml)).build()
        assert_equals(result.suite.name, 'foo')
        assert_equals(result.suite.suites[0].name, 'bar')


if __name__ == '__main__':
    unittest.main()

