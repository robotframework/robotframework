from __future__ import with_statement

from os.path import join, dirname
import unittest
from StringIO import StringIO
from robot import DataError

from robot.result import ResultFromXml
from robot.utils.asserts import assert_equals, assert_true, assert_raises

def _read_file(name):
    with open(join(dirname(__file__), name)) as f:
        return f.read()

GOLDEN_XML = _read_file('golden.xml')
GOLDEN_XML_TWICE = _read_file('goldenTwice.xml')
SUITE_TEARDOWN_FAILED = _read_file('suite_teardown_failed.xml')


class TestBuildingSuiteExecutionResult(unittest.TestCase):

    def setUp(self):
        result = ResultFromXml(StringIO(GOLDEN_XML))
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
        assert_equals(self._suite.statistics.critical.passed, 1)
        assert_equals(self._suite.statistics.critical.failed, 0)
        assert_equals(self._suite.statistics.all.passed, 1)
        assert_equals(self._suite.statistics.all.failed, 0)

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

    def test_suite_setup_is_built(self):
        assert_equals(len(self._setup.keywords), 0)
        assert_equals(len(self._setup.messages), 0)

    def test_errors_are_built(self):
        assert_equals(len(self._errors.messages), 1)
        assert_equals(self._errors.messages[0].message,
                      "Error in file 'normal.html' in table 'Settings': Resource file 'nope' does not exist.")


class TestCombiningSuites(unittest.TestCase):

    def setUp(self):
        self.result = ResultFromXml(StringIO(GOLDEN_XML), StringIO(GOLDEN_XML))

    def test_name(self):
        assert_equals(self.result.suite.name, 'Normal & Normal')


class TestElements(unittest.TestCase):

    def test_nested_suites(self):
        xml = """
        <robot>
        <suite name="foo">
          <suite name="bar">
            <suite name="quux">
            </suite>
          </suite>
        </suite>
        </robot>
        """
        suite = ResultFromXml(StringIO(xml)).suite
        assert_equals(suite.name, 'foo')
        assert_equals(suite.suites[0].name, 'bar')
        assert_equals(suite.longname, 'foo')
        assert_equals(suite.suites[0].longname, 'foo.bar')
        assert_equals(suite.suites[0].suites[0].name, 'quux')
        assert_equals(suite.suites[0].suites[0].longname, 'foo.bar.quux')

    def test_test_message(self):
        xml = """
        <robot>
        <suite name="foo">
          <test name="test">
            <status status="FAIL">Failure message</status>
          </test>
        </suite>
        </robot>
        """
        test = ResultFromXml(StringIO(xml)).suite.tests[0]
        assert_equals(test.message, 'Failure message')
        assert_equals(test.status, 'FAIL')
        assert_equals(test.longname, 'foo.test')

    def test_suite_message(self):
        xml = """
        <robot>
        <suite name="foo">
          <status status="FAIL">Setup failed</status>
        </suite>
        </robot>
        """
        suite = ResultFromXml(StringIO(xml)).suite
        assert_equals(suite.message, 'Setup failed')

    def test_unknown_elements_cause_an_error(self):
        assert_raises(DataError, ResultFromXml, StringIO('<some_tag/>'))


class TestSuiteTeardownFailed(unittest.TestCase):

    def test_passed_test(self):
        tc = ResultFromXml(StringIO(SUITE_TEARDOWN_FAILED)).suite.tests[0]
        assert_equals(tc.status, 'FAIL')
        assert_equals(tc.message, 'Teardown of the parent suite failed.')

    def test_failed_test(self):
        tc = ResultFromXml(StringIO(SUITE_TEARDOWN_FAILED)).suite.tests[1]
        assert_equals(tc.status, 'FAIL')
        assert_equals(tc.message, 'Message\n\nAlso teardown of the parent suite failed.')

    def test_already_processed(self):
        inp = SUITE_TEARDOWN_FAILED.replace('generator="Robot', 'generator="Rebot')
        tc1, tc2 = ResultFromXml(StringIO(inp)).suite.tests
        assert_equals(tc1.status, 'PASS')
        assert_equals(tc1.message, '')
        assert_equals(tc2.status, 'FAIL')
        assert_equals(tc2.message, 'Message')


class TestBuildingFromXmlString(unittest.TestCase):

    def test_result_is_built(self):
        xml = """
<robot>
    <suite name="foo">
        <test name="some name">
            <status status="PASS"></status>
        </test>
    <status status="PASS"></status>
    </suite>
</robot>
""".strip()
        result = ResultFromXml(xml)

if __name__ == '__main__':
    unittest.main()

