import unittest
from os.path import abspath

from robot.conf import RebotSettings
from robot.reporting.builders import LogBuilder, ReportBuilder
from robot.reporting.resultwriter import ResultWriter
from robot.output import LOGGER

import resources
from robot.utils.asserts import assert_true


LOGGER.disable_automatic_console_logger()


def set_write_split_test_mock():
    results = []
    def _write_split_log(self, index, keywords, strings, name):
        results.append(name)
    LogBuilder._write_split_log = _write_split_log
    return results


class TestReporting(unittest.TestCase, ResultWriter):

    def setUp(self):
        self._settings = RebotSettings()
        self._settings._opts = {
            'Report': 'NONE',
            'Log': 'NONE',
            'XUnitFile': 'NONE',
            'Output': 'NONE',
            'LogTitle': None,
            'ReportTitle': None,
            'ReportBackground': ('green', 'pink', 'red'),
            'SuiteStatLevel': -1,
            'SplitLog': False,
            'TagStatInclude': None,
            'TagStatExclude': None,
            'TagStatCombine': None,
            'TagDoc': None,
            'TagStatLink': None,
            'SetTag': None,
            'SuiteNames': None,
            'TestNames': None,
            'Include': None,
            'Exclude': None,
            'StartTime': 0,
            'Name': None,
            'Doc': None,
            'Metadata': {},
            'Critical': None,
            'NonCritical': None,
            'NoStatusRC': None,
            'RunEmptySuite': False,
            'EndTime': 0,
            'LogLevel': 'INFO',
            'RemoveKeywords': None,
            'TimestampOutputs': None,
            'OutputDir': '.',
        }
        self._log_result = None
        self._report_result = None
        self._xunit_result = None
        self._split_test_names = set_write_split_test_mock()
        self._output_result = None
        self._logs_splitted = False

    def _write_xunit(self, result, xunit):
        self._xunit_result = xunit

    def _write_output(self, result, output):
        self._output_result = output

    def _write_report(self, result, report, config):
        self._report_result = report

    def _write_log(self, result, log, config):
        self._log_result = log
        if result.js_model.split_results:
            self._logs_splitted = True

    def test_generate_report_and_log(self):
        self._settings._opts['Log'] = 'log.html'
        self._settings._opts['Report'] = 'report.html'
        self.write_results(resources.GOLDEN_OUTPUT)
        self._assert_expected_log('log.html')
        self._assert_expected_report('report.html')

    def test_no_generation(self):
        self.write_results(resources.GOLDEN_OUTPUT)
        self._assert_no_log()
        self._assert_no_report()

    def test_only_log(self):
        self._settings._opts['Log'] = 'only-log.html'
        self.write_results(resources.GOLDEN_OUTPUT)
        self._assert_expected_log('only-log.html')
        self._assert_no_report()
        assert_true(not self._logs_splitted)

    def test_only_report(self):
        self._settings._opts['Report'] = 'reports-only.html'
        self.write_results(resources.GOLDEN_OUTPUT)
        self._assert_no_log()
        self._assert_expected_report('reports-only.html')

    def test_only_xunit(self):
        self._settings._opts['XUnitFile'] = 'xunitfile-only.xml'
        self.write_results(resources.GOLDEN_OUTPUT)
        self._assert_no_log()
        self._assert_no_report()
        self._assert_expected_xunit('xunitfile-only.xml')

    def test_split_tests(self):
        self._settings._opts['SplitLog'] = True
        self._settings._opts['Log'] = '/tmp/foo/log.bar.html'
        self.write_results(resources.GOLDEN_OUTPUT)
        assert_true(self._logs_splitted)

    def _assert_expected_log(self, expected_file_name):
        if expected_file_name:
            expected_file_name = abspath(expected_file_name)
        self.assertEquals(self._log_result, expected_file_name)

    def _assert_expected_report(self, expected_file_name):
        if expected_file_name:
            expected_file_name = abspath(expected_file_name)
        self.assertEquals(self._report_result, expected_file_name)

    def _assert_expected_xunit(self, expected_file_name):
        self.assertEquals(self._xunit_result, abspath(expected_file_name))

    def _assert_no_log(self):
        self._assert_expected_log(None)

    def _assert_no_report(self):
        self._assert_expected_report(None)

    def test_multiple_outputs(self):
        self._settings['Log'] = 'log.html'
        self._settings['Report'] = 'report.html'
        self.write_results(resources.GOLDEN_OUTPUT, resources.GOLDEN_OUTPUT2)
        self._assert_expected_log('log.html')
        self._assert_expected_report('report.html')

    def test_output_generation(self):
        self._settings['Output'] = 'ouz.xml'
        self.write_results(resources.GOLDEN_OUTPUT, resources.GOLDEN_OUTPUT2)
        self._assert_expected_output('ouz.xml')

    def _assert_expected_output(self, expected_file_name):
        self.assertEquals(self._output_result, abspath(expected_file_name))

if __name__ == '__main__':
    unittest.main()
