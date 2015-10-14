import unittest
from os.path import join, dirname

from robot.errors import DataError
from robot.result import ExecutionResult
from robot.utils import StringIO
from robot.utils.asserts import assert_equals, assert_true, assert_raises


def _read_file(name):
    with open(join(dirname(__file__), name)) as f:
        return f.read()


GOLDEN_XML = _read_file('golden.xml')
GOLDEN_XML_TWICE = _read_file('goldenTwice.xml')
SUITE_TEARDOWN_FAILED = _read_file('suite_teardown_failed.xml')


class TestBuildingSuiteExecutionResult(unittest.TestCase):

    def setUp(self):
        result = ExecutionResult(StringIO(GOLDEN_XML))
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
        assert_equals(self._test.timeout, None)
        assert_equals(list(self._test.tags), ['t1'])
        assert_equals(len(self._test.keywords), 2)
        assert_equals(self._test.status, 'PASS')
        assert_equals(self._test.starttime, '20111024 13:41:20.925')
        assert_equals(self._test.endtime, '20111024 13:41:20.934')
        assert_true(self._test.critical)

    def test_keyword_is_built(self):
        assert_equals(self._keyword.name, 'BuiltIn.Log')
        assert_equals(self._keyword.doc, 'Logs the given message with the given level.')
        assert_equals(self._keyword.args, ('Test 1',))
        assert_equals(self._keyword.assign, ())
        assert_equals(self._keyword.status, 'PASS')
        assert_equals(self._keyword.starttime, '20111024 13:41:20.926')
        assert_equals(self._keyword.endtime, '20111024 13:41:20.928')
        assert_equals(self._keyword.timeout, None)
        assert_equals(len(self._keyword.keywords), 0)
        assert_equals(len(self._keyword.messages), 1)

    def test_user_keyword_is_built(self):
        assert_equals(self._user_keyword.name, 'logs on trace')
        assert_equals(self._user_keyword.doc, '')
        assert_equals(self._user_keyword.args, ())
        assert_equals(self._user_keyword.assign, ('${not really in source}',))
        assert_equals(self._user_keyword.status, 'PASS')
        assert_equals(self._user_keyword.starttime, '20111024 13:41:20.930')
        assert_equals(self._user_keyword.endtime, '20111024 13:41:20.933')
        assert_equals(self._user_keyword.timeout, None)
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
        self.result = ExecutionResult(StringIO(GOLDEN_XML), StringIO(GOLDEN_XML))

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
        suite = ExecutionResult(StringIO(xml)).suite
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
        test = ExecutionResult(StringIO(xml)).suite.tests[0]
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
        suite = ExecutionResult(StringIO(xml)).suite
        assert_equals(suite.message, 'Setup failed')

    def test_unknown_elements_cause_an_error(self):
        assert_raises(DataError, ExecutionResult, StringIO('<some_tag/>'))


class TestSuiteTeardownFailed(unittest.TestCase):

    def test_passed_test(self):
        tc = ExecutionResult(StringIO(SUITE_TEARDOWN_FAILED)).suite.tests[0]
        assert_equals(tc.status, 'FAIL')
        assert_equals(tc.message, 'Parent suite teardown failed:\nXXX')

    def test_failed_test(self):
        tc = ExecutionResult(StringIO(SUITE_TEARDOWN_FAILED)).suite.tests[1]
        assert_equals(tc.status, 'FAIL')
        assert_equals(tc.message, 'Message\n\n'
                                  'Also parent suite teardown failed:\nXXX')

    def test_already_processed(self):
        inp = SUITE_TEARDOWN_FAILED.replace('generator="Robot', 'generator="Rebot')
        passed, failed, teardowns = ExecutionResult(StringIO(inp)).suite.tests
        assert_equals(passed.status, 'PASS')
        assert_equals(passed.message, '')
        assert_equals(failed.status, 'FAIL')
        assert_equals(failed.message, 'Message')
        assert_equals(teardowns.status, 'PASS')
        assert_equals(teardowns.message, '')

    def test_excluding_keywords(self):
        suite = ExecutionResult(StringIO(SUITE_TEARDOWN_FAILED),
                                include_keywords=False).suite
        passed, failed, teardowns = suite.tests
        assert_equals(passed.status, 'FAIL')
        assert_equals(passed.message, 'Parent suite teardown failed:\nXXX')
        assert_equals(failed.status, 'FAIL')
        assert_equals(failed.message, 'Message\n\n'
                                      'Also parent suite teardown failed:\nXXX')
        assert_equals(teardowns.status, 'FAIL')
        assert_equals(teardowns.message, 'Parent suite teardown failed:\nXXX')
        for item in suite, passed, failed, teardowns:
            assert_equals(list(item.keywords), [])

    def test_excluding_keywords_and_already_processed(self):
        inp = SUITE_TEARDOWN_FAILED.replace('generator="Robot', 'generator="Rebot')
        suite = ExecutionResult(StringIO(inp), include_keywords=False).suite
        passed, failed, teardowns = suite.tests
        assert_equals(passed.status, 'PASS')
        assert_equals(passed.message, '')
        assert_equals(failed.status, 'FAIL')
        assert_equals(failed.message, 'Message')
        assert_equals(teardowns.status, 'PASS')
        assert_equals(teardowns.message, '')
        for item in suite, passed, failed, teardowns:
            assert_equals(list(item.keywords), [])


class TestBuildingFromXmlStringAndHandlingMissingInformation(unittest.TestCase):

    def setUp(self):
        self.result = ExecutionResult("""
<robot>
    <suite name="foo">
        <test name="some name">
            <status status="PASS"></status>
        </test>
    <status status="PASS"></status>
    </suite>
</robot>
""")

    def test_suite(self):
        suite = self.result.suite
        assert_equals(suite.id, 's1')
        assert_equals(suite.name, 'foo')
        assert_equals(suite.doc, '')
        assert_equals(suite.source, None)
        assert_equals(suite.metadata, {})
        assert_equals(list(suite.keywords), [])
        assert_equals(suite.starttime, None)
        assert_equals(suite.endtime, None)
        assert_equals(suite.elapsedtime, 0)

    def test_test(self):
        test = self.result.suite.tests[0]
        assert_equals(test.id, 's1-t1')
        assert_equals(test.name, 'some name')
        assert_equals(test.doc, '')
        assert_equals(test.timeout, None)
        assert_equals(test.critical, True)
        assert_equals(list(test.tags), [])
        assert_equals(list(test.keywords), [])
        assert_equals(test.starttime, None)
        assert_equals(test.endtime, None)
        assert_equals(test.elapsedtime, 0)


if __name__ == '__main__':
    unittest.main()

