from StringIO import StringIO
import os
import unittest
from robot.reporting.resultwriter import ResultWriter, Results
from robot.output import LOGGER

from robot.result.executionresult import ExecutionResult
from robot.result.executionerrors import ExecutionErrors
from robot.result.testsuite import TestSuite
from robot.utils.asserts import assert_true, assert_equals


LOGGER.disable_automatic_console_logger()


class TestReporting(unittest.TestCase):
    EXPECTED_SUITE_NAME = 'My Suite Name'
    EXPECTED_TEST_NAME  = 'My Test Name'
    EXPECTED_KEYWORD_NAME = 'My Keyword Name'
    EXPECTED_FAILING_TEST = 'My Failing Test'
    EXPECTED_DEBUG_MESSAGE = '1111DEBUG777'
    EXPECTED_ERROR_MESSAGE = 'ERROR M355463'

    def test_no_generation(self):
        settings = StubSettings()
        results = StubResults(None, settings)
        rc = ResultWriter().write_results(settings, results)
        assert_equals(rc, -1)

    def test_only_output(self):
        output = ClosableOutput('output.xml')
        self._write_results(output=output)
        self._verify_output(output.value)

    def test_only_xunit(self):
        xunit = ClosableOutput('xunit.xml')
        self._write_results(xunit=xunit)
        self._verify_xunit(xunit.value)

    def test_only_log(self):
        log = ClosableOutput('log.html')
        self._write_results(log=log)
        self._verify_log(log.value)

    def test_only_report(self):
        report = ClosableOutput('report.html')
        self._write_results(report=report)
        self._verify_report(report.value)

    def test_log_and_report(self):
        log = ClosableOutput('log.html')
        report = ClosableOutput('report.html')
        self._write_results(log=log, report=report)
        self._verify_log(log.value)
        self._verify_report(report.value)

    def test_generate_all(self):
        output = ClosableOutput('o.xml')
        xunit = ClosableOutput('x.xml')
        log = ClosableOutput('l.html')
        report = ClosableOutput('r.html')
        self._write_results(output=output, xunit=xunit, log=log, report=report)
        self._verify_output(output.value)
        self._verify_xunit(xunit.value)
        self._verify_log(log.value)
        self._verify_report(report.value)

    def test_log_generation_removes_keywords_from_execution_result(self):
        execution_result = self._write_results(log=ClosableOutput('log.html'))
        for test in execution_result.suite.tests:
            assert_equals(len(test.keywords), 0)

    def _write_results(self, **settings):
        execution_result = self._get_execution_result()
        settings = StubSettings(**settings)
        results = StubResults(execution_result, settings)
        rc = ResultWriter().write_results(settings, results)
        assert_equals(rc, 1)
        return execution_result

    def _get_execution_result(self):
        suite = TestSuite(name=self.EXPECTED_SUITE_NAME)
        tc = suite.tests.create(name=self.EXPECTED_TEST_NAME, status='PASS')
        tc.keywords.create(name=self.EXPECTED_KEYWORD_NAME, status='PASS')
        tc = suite.tests.create(name=self.EXPECTED_FAILING_TEST)
        kw = tc.keywords.create(name=self.EXPECTED_KEYWORD_NAME)
        kw.messages.create(message=self.EXPECTED_DEBUG_MESSAGE,
                           level='DEBUG', timestamp='20201212 12:12:12.000')
        errors = ExecutionErrors()
        errors.messages.create(message=self.EXPECTED_ERROR_MESSAGE,
                               level='ERROR', timestamp='20201212 12:12:12.000')
        return ExecutionResult(suite, errors)

    def _verify_output(self, content):
        assert_true(self.EXPECTED_SUITE_NAME in content)
        assert_true(self.EXPECTED_TEST_NAME in content)
        assert_true(self.EXPECTED_FAILING_TEST in content)
        assert_true(self.EXPECTED_KEYWORD_NAME in content)
        assert_true(self.EXPECTED_DEBUG_MESSAGE in content)
        assert_true(self.EXPECTED_ERROR_MESSAGE in content)

    def _verify_xunit(self, content):
        assert_true(self.EXPECTED_SUITE_NAME in content)
        assert_true(self.EXPECTED_TEST_NAME in content)
        assert_true(self.EXPECTED_FAILING_TEST in content)
        assert_true(self.EXPECTED_KEYWORD_NAME not in content)
        assert_true(self.EXPECTED_DEBUG_MESSAGE in content)
        assert_true(self.EXPECTED_ERROR_MESSAGE not in content)

    def _verify_log(self, content):
        self._verify_output(content)

    def _verify_report(self, content):
        assert_true(self.EXPECTED_SUITE_NAME in content)
        assert_true(self.EXPECTED_TEST_NAME in content)
        assert_true(self.EXPECTED_FAILING_TEST in content)
        assert_true(self.EXPECTED_KEYWORD_NAME not in content)
        assert_true(self.EXPECTED_DEBUG_MESSAGE not in content)
        assert_true(self.EXPECTED_ERROR_MESSAGE not in content)


class StubSettings(object):
    log = None
    log_config = None
    split_log = False
    report = None
    report_config = None
    output = None
    xunit = None
    status_rc = True
    suite_config = {}
    statistics_config = {}

    def __init__(self, **settings):
        self.__dict__.update(settings)


class StubResults(Results):

    def __init__(self, result, settings):
        Results.__init__(self, None, settings)
        self._result = result
        if result:
            self.return_code = result.return_code


class ClosableOutput(object):

    def __init__(self, path):
        self._output = StringIO()
        self._path = path

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()

    def write(self, data):
        self._output.write(data)

    def close(self):
        self.value = self._output.getvalue()
        self._output.close()

    def __str__(self):
        return self._path


if os.name == 'java':
    from java.io import OutputStream
    from java.lang import String

    class ClosableOutput(ClosableOutput, OutputStream):

        def write(self, *args):
            self._output.write(String(args[0]))


if __name__ == '__main__':
    unittest.main()
