from io import StringIO
import unittest

from robot.output import LOGGER
from robot.reporting.resultwriter import ResultWriter, Results
from robot.result.executionerrors import ExecutionErrors
from robot.result import TestSuite, Result
from robot.utils.asserts import assert_true, assert_equal


LOGGER.unregister_console_logger()


class TestReporting(unittest.TestCase):
    EXPECTED_SUITE_NAME = 'My Suite Name'
    EXPECTED_TEST_NAME = 'My Test Name'
    EXPECTED_KEYWORD_NAME = 'My Keyword Name'
    EXPECTED_FAILING_TEST = 'My Failing Test'
    EXPECTED_DEBUG_MESSAGE = '1111DEBUG777'
    EXPECTED_ERROR_MESSAGE = 'ERROR M355463'

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

    def test_js_generation_does_not_prune_given_result(self):
        result = self._get_execution_result()
        results = Results(StubSettings(), result)
        _ = results.js_result
        for test in results.result.suite.tests:
            assert_true(len(test.body) > 0)

    def test_js_generation_prunes_read_result(self):
        result = self._get_execution_result()
        results = Results(StubSettings(), 'output.xml')
        assert_equal(results._result, None)
        results._result = result  # Fake reading results
        _ = results.js_result
        for test in result.suite.tests:
            assert_equal(len(test.body), 0)

    def _write_results(self, **settings):
        result = self._get_execution_result()
        settings = StubSettings(**settings)
        rc = ResultWriter(result).write_results(settings)
        assert_equal(rc, 1)

    def _get_execution_result(self):
        suite = TestSuite(name=self.EXPECTED_SUITE_NAME)
        tc = suite.tests.create(name=self.EXPECTED_TEST_NAME, status='PASS')
        tc.body.create_keyword(name=self.EXPECTED_KEYWORD_NAME, status='PASS')
        tc = suite.tests.create(name=self.EXPECTED_FAILING_TEST)
        kw = tc.body.create_keyword(name=self.EXPECTED_KEYWORD_NAME)
        kw.body.create_message(message=self.EXPECTED_DEBUG_MESSAGE,
                               level='DEBUG', timestamp='2020-12-12 12:12:12.000')
        errors = ExecutionErrors()
        errors.messages.create(message=self.EXPECTED_ERROR_MESSAGE,
                               level='ERROR', timestamp='2020-12-12 12:12:12.000')
        return Result(root_suite=suite, errors=errors)

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
        assert_true(self.EXPECTED_DEBUG_MESSAGE not in content)
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


class StubSettings:
    log = None
    log_config = {}
    split_log = False
    report = None
    report_config = None
    output = None
    xunit = None
    status_rc = True
    suite_config = {}
    statistics_config = {}
    xunit_skip_noncritical = False
    expand_keywords = None
    legacy_output = False

    def __init__(self, **settings):
        self.__dict__.update(settings)


class ClosableOutput:

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


if __name__ == '__main__':
    unittest.main()
