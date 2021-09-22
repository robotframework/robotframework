import os
import unittest
import tempfile
from io import StringIO
from os.path import join, dirname
from pathlib import Path

from robot.errors import DataError
from robot.result import ExecutionResult, ExecutionResultBuilder, Result, TestSuite
from robot.utils.asserts import assert_equal, assert_false, assert_true, assert_raises


def _read_file(name):
    with open(join(dirname(__file__), name)) as f:
        return f.read()


GOLDEN_XML = _read_file('golden.xml')
GOLDEN_XML_TWICE = _read_file('goldenTwice.xml')
SUITE_TEARDOWN_FAILED = _read_file('suite_teardown_failed.xml')


class TestBuildingSuiteExecutionResult(unittest.TestCase):

    def setUp(self):
        self.result = ExecutionResult(StringIO(GOLDEN_XML))
        self.suite = self.result.suite
        self.test = self.suite.tests[0]

    def test_suite_is_built(self):
        assert_equal(self.suite.source, 'normal.html')
        assert_equal(self.suite.name, 'Normal')
        assert_equal(self.suite.doc, 'Normal test cases')
        assert_equal(self.suite.metadata, {'Something': 'My Value'})
        assert_equal(self.suite.status, 'PASS')
        assert_equal(self.suite.starttime, '20111024 13:41:20.873')
        assert_equal(self.suite.endtime, '20111024 13:41:20.952')
        assert_equal(self.suite.statistics.passed, 1)
        assert_equal(self.suite.statistics.failed, 0)

    def test_testcase_is_built(self):
        assert_equal(self.test.name, 'First One')
        assert_equal(self.test.doc, 'Test case documentation')
        assert_equal(self.test.timeout, None)
        assert_equal(list(self.test.tags), ['t1'])
        assert_equal(len(self.test.body), 4)
        assert_equal(self.test.status, 'PASS')
        assert_equal(self.test.starttime, '20111024 13:41:20.925')
        assert_equal(self.test.endtime, '20111024 13:41:20.934')

    def test_keyword_is_built(self):
        keyword = self.test.body[0]
        assert_equal(keyword.name, 'BuiltIn.Log')
        assert_equal(keyword.doc, 'Logs the given message with the given level.')
        assert_equal(keyword.args, ('Test 1',))
        assert_equal(keyword.assign, ())
        assert_equal(keyword.status, 'PASS')
        assert_equal(keyword.starttime, '20111024 13:41:20.926')
        assert_equal(keyword.endtime, '20111024 13:41:20.928')
        assert_equal(keyword.timeout, None)
        assert_equal(len(keyword.body), 1)
        assert_equal(keyword.body[0].type, keyword.body[0].MESSAGE)

    def test_user_keyword_is_built(self):
        user_keyword = self.test.body[1]
        assert_equal(user_keyword.name, 'logs on trace')
        assert_equal(user_keyword.doc, '')
        assert_equal(user_keyword.args, ())
        assert_equal(user_keyword.assign, ('${not really in source}',))
        assert_equal(user_keyword.status, 'PASS')
        assert_equal(user_keyword.starttime, '20111024 13:41:20.930')
        assert_equal(user_keyword.endtime, '20111024 13:41:20.933')
        assert_equal(user_keyword.timeout, None)
        assert_equal(len(user_keyword.messages), 0)
        assert_equal(len(user_keyword.body), 1)

    def test_message_is_built(self):
        message = self.test.body[0].messages[0]
        assert_equal(message.message, 'Test 1')
        assert_equal(message.level, 'INFO')
        assert_equal(message.timestamp, '20111024 13:41:20.927')

    def test_for_is_built(self):
        for_ = self.test.body[2]
        assert_equal(for_.flavor, 'IN')
        assert_equal(for_.variables, ('${x}',))
        assert_equal(for_.values, ('not in source',))
        assert_equal(len(for_.body), 1)
        assert_equal(for_.body[0].variables, {'${x}': 'not in source'})
        assert_equal(len(for_.body[0].body), 1)
        kw = for_.body[0].body[0]
        assert_equal(kw.name, 'BuiltIn.Log')
        assert_equal(kw.args, ('${x}',))
        assert_equal(len(kw.body), 1)
        assert_equal(kw.body[0].message, 'not in source')

    def test_if_is_built(self):
        root = self.test.body[3]
        if_, else_ = root.body
        assert_equal(if_.condition, "'IF' == 'WRONG'")
        assert_equal(if_.status, if_.NOT_RUN)
        assert_equal(len(if_.body), 1)
        kw = if_.body[0]
        assert_equal(kw.name, 'BuiltIn.Fail')
        assert_equal(kw.status, kw.NOT_RUN)
        assert_equal(else_.condition, None)
        assert_equal(else_.status, else_.PASS)
        assert_equal(len(else_.body), 1)
        kw = else_.body[0]
        assert_equal(kw.name, 'BuiltIn.No Operation')
        assert_equal(kw.status, kw.PASS)

    def test_suite_setup_is_built(self):
        assert_equal(len(self.suite.setup.body), 0)
        assert_equal(len(self.suite.setup.messages), 0)

    def test_errors_are_built(self):
        assert_equal(len(self.result.errors.messages), 1)
        assert_equal(self.result.errors.messages[0].message,
                     "Error in file 'normal.html' in table 'Settings': "
                     "Resource file 'nope' does not exist.")

    def test_omit_keywords(self):
        result = ExecutionResult(StringIO(GOLDEN_XML), include_keywords=False)
        assert_equal(len(result.suite.tests[0].body), 0)

    def test_omit_keywords_during_xml_parsing(self):
        class NonVisitingSuite(TestSuite):
            def visit(self, visitor):
                pass
        result = Result(root_suite=NonVisitingSuite())
        builder = ExecutionResultBuilder(StringIO(GOLDEN_XML), include_keywords=False)
        builder.build(result)
        assert_equal(len(result.suite.tests[0].body), 0)

    def test_rpa(self):
        rpa_false = GOLDEN_XML
        self._validate_rpa(ExecutionResult(StringIO(rpa_false)), False)
        self._validate_rpa(ExecutionResult(StringIO(rpa_false), rpa=True), True)
        rpa_true = GOLDEN_XML.replace('rpa="false"', 'rpa="true"')
        self._validate_rpa(ExecutionResult(StringIO(rpa_true)), True)
        self._validate_rpa(ExecutionResult(StringIO(rpa_true), rpa=False), False)

    def _validate_rpa(self, result, expected):
        assert_equal(result.rpa, expected)
        if isinstance(result, Result):
            children = [result.suite]
        else:
            children = result.suites
        for child in children:
            self._validate_rpa(child, expected)


class TestCombiningSuites(unittest.TestCase):

    def setUp(self):
        self.result = ExecutionResult(StringIO(GOLDEN_XML), StringIO(GOLDEN_XML))

    def test_name(self):
        assert_equal(self.result.suite.name, 'Normal & Normal')


class TestMergingSuites(unittest.TestCase):

    def setUp(self):
        result = ExecutionResult(StringIO(GOLDEN_XML), StringIO(GOLDEN_XML),
                                 StringIO(GOLDEN_XML), merge=True)
        self.suite = result.suite
        self.test = self.suite.tests[0]

    def test_name(self):
        assert_equal(self.suite.name, 'Normal')
        assert_equal(self.test.name, 'First One')

    def test_message(self):
        message = self.test.message
        assert_true(message.startswith('*HTML* <span class="merge">Test has been re-executed and results merged.</span><hr>'))
        assert_true('<span class="new-status">New status:</span> <span class="pass">PASS</span>' in message)
        assert_equal(message.count('<span class="new-status">'), 1)
        assert_true('<span class="new-message">New message:</span>' not in message)
        assert_true('<span class="old-status">Old status:</span> <span class="pass">PASS</span>' in message)
        assert_equal(message.count('<span class="old-status">'), 2)
        assert_true('<span class="old-message">Old message:</span>' not in message)


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
        assert_equal(suite.name, 'foo')
        assert_equal(suite.suites[0].name, 'bar')
        assert_equal(suite.longname, 'foo')
        assert_equal(suite.suites[0].longname, 'foo.bar')
        assert_equal(suite.suites[0].suites[0].name, 'quux')
        assert_equal(suite.suites[0].suites[0].longname, 'foo.bar.quux')

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
        assert_equal(test.message, 'Failure message')
        assert_equal(test.status, 'FAIL')
        assert_equal(test.longname, 'foo.test')

    def test_suite_message(self):
        xml = """
        <robot>
        <suite name="foo">
          <status status="FAIL">Setup failed</status>
        </suite>
        </robot>
        """
        suite = ExecutionResult(StringIO(xml)).suite
        assert_equal(suite.message, 'Setup failed')

    def test_unknown_elements_cause_an_error(self):
        assert_raises(DataError, ExecutionResult, StringIO('<some_tag/>'))


class TestSuiteTeardownFailed(unittest.TestCase):

    def test_passed_test(self):
        tc = ExecutionResult(StringIO(SUITE_TEARDOWN_FAILED)).suite.tests[0]
        assert_equal(tc.status, 'FAIL')
        assert_equal(tc.message, 'Parent suite teardown failed:\nXXX')

    def test_failed_test(self):
        tc = ExecutionResult(StringIO(SUITE_TEARDOWN_FAILED)).suite.tests[1]
        assert_equal(tc.status, 'FAIL')
        assert_equal(tc.message, 'Message\n\n'
                                  'Also parent suite teardown failed:\nXXX')

    def test_already_processed(self):
        inp = SUITE_TEARDOWN_FAILED.replace('generator="Robot', 'generator="Rebot')
        passed, failed, teardowns = ExecutionResult(StringIO(inp)).suite.tests
        assert_equal(passed.status, 'PASS')
        assert_equal(passed.message, '')
        assert_equal(failed.status, 'FAIL')
        assert_equal(failed.message, 'Message')
        assert_equal(teardowns.status, 'PASS')
        assert_equal(teardowns.message, '')

    def test_excluding_keywords(self):
        suite = ExecutionResult(StringIO(SUITE_TEARDOWN_FAILED),
                                include_keywords=False).suite
        passed, failed, teardowns = suite.tests
        assert_equal(passed.status, 'FAIL')
        assert_equal(passed.message, 'Parent suite teardown failed:\nXXX')
        assert_equal(failed.status, 'FAIL')
        assert_equal(failed.message, 'Message\n\n'
                                     'Also parent suite teardown failed:\nXXX')
        assert_equal(teardowns.status, 'FAIL')
        assert_equal(teardowns.message, 'Parent suite teardown failed:\nXXX')
        for item in suite.setup, suite.teardown:
            assert_false(item)
        for item in passed, failed, teardowns:
            assert_equal(list(item.body), [])

    def test_excluding_keywords_and_already_processed(self):
        inp = SUITE_TEARDOWN_FAILED.replace('generator="Robot', 'generator="Rebot')
        suite = ExecutionResult(StringIO(inp), include_keywords=False).suite
        passed, failed, teardowns = suite.tests
        assert_equal(passed.status, 'PASS')
        assert_equal(passed.message, '')
        assert_equal(failed.status, 'FAIL')
        assert_equal(failed.message, 'Message')
        assert_equal(teardowns.status, 'PASS')
        assert_equal(teardowns.message, '')
        for item in suite.setup, suite.teardown:
            assert_false(item)
        for item in passed, failed, teardowns:
            assert_equal(list(item.body), [])


class TestBuildingFromXmlStringAndHandlingMissingInformation(unittest.TestCase):

    def setUp(self):
        self.result = """
        <robot>
            <suite name="foo">
                <test name="some name">
                    <status status="PASS"></status>
                </test>
            <status status="PASS"></status>
            </suite>
        </robot>
        """
        self.string_result = ExecutionResult(self.result)
        self.byte_string_result = ExecutionResult(self.result.encode('UTF-8'))

    def test_suite_from_string(self):
        suite = self.string_result.suite
        self._test_suite(suite)

    def test_test_from_string(self):
        test = self.string_result.suite.tests[0]
        self._test_test(test)

    def test_suite_from_byte_string(self):
        suite = self.byte_string_result.suite
        self._test_suite(suite)

    def test_test_from_byte_string(self):
        test = self.byte_string_result.suite.tests[0]
        self._test_test(test)

    @staticmethod
    def _test_suite(suite):
        assert_equal(suite.id, 's1')
        assert_equal(suite.name, 'foo')
        assert_equal(suite.doc, '')
        assert_equal(suite.source, None)
        assert_equal(suite.metadata, {})
        assert_equal(suite.starttime, None)
        assert_equal(suite.endtime, None)
        assert_equal(suite.elapsedtime, 0)

    @staticmethod
    def _test_test(test):
        assert_equal(test.id, 's1-t1')
        assert_equal(test.name, 'some name')
        assert_equal(test.doc, '')
        assert_equal(test.timeout, None)
        assert_equal(list(test.tags), [])
        assert_equal(list(test.body), [])
        assert_equal(test.starttime, None)
        assert_equal(test.endtime, None)
        assert_equal(test.elapsedtime, 0)


class TestUsingPathlibPath(unittest.TestCase):

    def setUp(self):
        self.result = ExecutionResult(Path(__file__).parent / 'golden.xml')

    def test_suite_is_built(self, suite=None):
        suite = suite or self.result.suite
        assert_equal(suite.source, 'normal.html')
        assert_equal(suite.name, 'Normal')
        assert_equal(suite.doc, 'Normal test cases')
        assert_equal(suite.metadata, {'Something': 'My Value'})
        assert_equal(suite.status, 'PASS')
        assert_equal(suite.starttime, '20111024 13:41:20.873')
        assert_equal(suite.endtime, '20111024 13:41:20.952')
        assert_equal(suite.statistics.passed, 1)
        assert_equal(suite.statistics.failed, 0)

    def test_test_is_built(self, suite=None):
        test = (suite or self.result.suite).tests[0]
        assert_equal(test.name, 'First One')
        assert_equal(test.doc, 'Test case documentation')
        assert_equal(test.timeout, None)
        assert_equal(list(test.tags), ['t1'])
        assert_equal(len(test.body), 4)
        assert_equal(test.status, 'PASS')
        assert_equal(test.starttime, '20111024 13:41:20.925')
        assert_equal(test.endtime, '20111024 13:41:20.934')

    def test_save(self):
        temp = os.getenv('TEMPDIR', tempfile.gettempdir())
        path = Path(temp) / 'pathlib.xml'
        self.result.save(path)
        try:
            result = ExecutionResult(path)
        finally:
            path.unlink()
        self.test_suite_is_built(result.suite)
        self.test_test_is_built(result.suite)


if __name__ == '__main__':
    unittest.main()
