from StringIO import StringIO
import os
import unittest
from robot.reporting.resultwriter import ResultWriter, Result
from robot.output import LOGGER

from robot.result.executionresult import ExecutionResult
from robot.result.testsuite import TestSuite
from robot.utils.asserts import assert_true, assert_equals


LOGGER.disable_automatic_console_logger()

class TestReporting(unittest.TestCase):

    EXPECTED_SUITE_NAME = 'My Suite Name'
    EXPECTED_TEST_NAME  = 'My Test Name'
    EXPECTED_KEYWORD_NAME = 'My Keyword Name'
    EXPECTED_FAILING_TEST = 'My Failing Test'
    EXPECTED_DEBUG_MESSAGE = '1111DEBUG777'

    def setUp(self):
        self._settings = lambda:0
        self._settings.log = None
        self._settings.log_config = None
        self._settings.split_log = False
        self._settings.report = None
        self._settings.report_config = None
        self._settings.output = None
        self._settings.xunit = None
        self._settings.status_rc = True
        self._settings.suite_config = {}
        self._settings.statistics_config = {}
        self._create_suite_and_writer()

    def _create_suite_and_writer(self):
        self._root_suite = TestSuite(name=self.EXPECTED_SUITE_NAME)
        self._root_suite.tests.create(name=self.EXPECTED_TEST_NAME).\
                    keywords.create(name=self.EXPECTED_KEYWORD_NAME,
                                    status='PASS')
        self._root_suite.tests.create(name=self.EXPECTED_FAILING_TEST).\
                    keywords.create(name=self.EXPECTED_KEYWORD_NAME).\
                        messages.create(message=self.EXPECTED_DEBUG_MESSAGE,
                                        level='DEBUG',
                                        timestamp='20201212 12:12:12.000')
        self._writer = ResultWriter(self._settings)
        self._writer._result._model = ExecutionResult(self._root_suite)

    def test_generate_report_and_log(self):
        self._settings.log = ClosableOutput('log.html')
        self._settings.report = ClosableOutput('report.html')
        self._write_results()
        self._verify_log()
        self._verify_report()

    def _write_results(self):
        self._writer.write_results()

    def _verify_log(self):
        log = self._settings.log.getvalue()
        assert_true(self.EXPECTED_KEYWORD_NAME in log)
        assert_true(self.EXPECTED_SUITE_NAME in log)
        assert_true(self.EXPECTED_TEST_NAME in log)
        assert_true(self.EXPECTED_FAILING_TEST in log)

    def _verify_report(self):
        report = self._settings.report.getvalue()
        assert_true(self.EXPECTED_KEYWORD_NAME not in report)
        assert_true(self.EXPECTED_SUITE_NAME in report)
        assert_true(self.EXPECTED_TEST_NAME in report)
        assert_true(self.EXPECTED_FAILING_TEST in report)

    def test_no_generation(self):
        self._writer._result._model = None
        self._write_results()
        assert_equals(self._writer._result._model, None)

    def test_only_log(self):
        self._settings.log = ClosableOutput('log.html')
        self._write_results()
        self._verify_log()

    def test_only_report(self):
        self._settings.report = ClosableOutput('report.html')
        self._write_results()
        self._verify_report()

    def test_only_xunit(self):
        self._settings.xunit = ClosableOutput('xunit.xml')
        self._write_results()
        self._verify_xunit()

    def test_only_output_generation(self):
        self._settings.output = ClosableOutput('output.xml')
        self._write_results()
        self._verify_output()

    def test_generate_all(self):
        self._settings.log = ClosableOutput('l.html')
        self._settings.report = ClosableOutput('r.html')
        self._settings.xunit = ClosableOutput('x.xml')
        self._settings.output = ClosableOutput('o.xml')
        self._write_results()
        self._verify_log()
        self._verify_report()
        self._verify_xunit()
        self._verify_output()

    def test_log_generation_removes_keywords_from_original_model(self):
        self._settings.log = ClosableOutput('log.html')
        self._write_results()
        for test in self._root_suite.tests:
            assert_equals(len(test.keywords), 0)

    def _verify_xunit(self):
        xunit = self._settings.xunit.getvalue()
        assert_true(self.EXPECTED_DEBUG_MESSAGE in xunit)

    def _verify_output(self):
        assert_true(self._settings.output.getvalue())


if os.name == 'java':
    import java.io.OutputStream
    import java.lang.String

    class ClosableOutput(java.io.OutputStream):
        def __init__(self, path):
            self._output = StringIO()
            self._path = path

        __enter__ = lambda *args: 0
        __exit__ = lambda self, *args: self.close()

        def write(self, *args):
            self._output.write(java.lang.String(args[0]))

        def close(self):
            self.value = self._output.getvalue()
            self._output.close()

        def getvalue(self):
            return self.value

        def __str__(self):
            return self._path

else:

    class ClosableOutput(object):

        def __init__(self, path):
            self._output = StringIO()
            self._path = path

        __enter__= lambda *args: 0
        __exit__ = lambda self, *args: self.close()

        def write(self, data):
            self._output.write(data)

        def close(self):
            self.value = self._output.getvalue()
            self._output.close()

        def getvalue(self):
            return self.value

        def __str__(self):
            return self._path


if __name__ == '__main__':
    unittest.main()
