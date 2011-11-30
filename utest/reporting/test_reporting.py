import unittest
from os.path import abspath

from robot.conf import RebotSettings
from robot.reporting.builders import LogBuilder, ReportBuilder, XUnitBuilder, OutputBuilder
from robot.reporting.resultwriter import ResultWriter

import resources


def set_write_log_mock():
    results = {'log_path': None}
    def write_log(self, path, template):
        results['log_path'] = path
    LogBuilder._write_file = write_log
    return results

def set_write_report_mock():
    results = {'report_path': None}
    def write_report(self, path, template):
        results['report_path'] = path
    ReportBuilder._write_file = write_report
    return results

def set_write_xunit_mock():
    results = {'xunit_path': None}
    def build_xunit(self, path):
        results['xunit_path'] = path
    XUnitBuilder.build = build_xunit
    return results

def set_write_output_mock():
    results = {'output_path': None}
    def build_output(self, path):
        results['output_path'] = path
    OutputBuilder.build = build_output
    return results

def set_write_split_test_mock():
    results = []
    def _write_split_log(self, index, keywords, strings, name):
        results.append(name)
    LogBuilder._write_split_log = _write_split_log
    return results


class TestReporting(unittest.TestCase):

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
        self._log_results = set_write_log_mock()
        self._report_results = set_write_report_mock()
        self._xunit_results = set_write_xunit_mock()
        self._split_test_names = set_write_split_test_mock()
        self._output_results = set_write_output_mock()
        self._reporter = ResultWriter(self._settings)

    def test_generate_report_and_log(self):
        self._settings._opts['Log'] = 'log.html'
        self._settings._opts['Report'] = 'report.html'
        self._reporter.write_results(resources.GOLDEN_OUTPUT)
        self._assert_expected_log('log.html')
        self._assert_expected_report('report.html')

    def test_no_generation(self):
        self._reporter.write_results(resources.GOLDEN_OUTPUT)
        self._assert_no_log()
        self._assert_no_report()

    def test_only_log(self):
        self._settings._opts['Log'] = 'only-log.html'
        self._reporter.write_results(resources.GOLDEN_OUTPUT)
        self._assert_expected_log('only-log.html')
        self._assert_no_report()

    def test_only_report(self):
        self._settings._opts['Report'] = 'reports-only.html'
        self._reporter.write_results(resources.GOLDEN_OUTPUT)
        self._assert_no_log()
        self._assert_expected_report('reports-only.html')

    def test_only_xunit(self):
        self._settings._opts['XUnitFile'] = 'xunitfile-only.xml'
        self._reporter.write_results(resources.GOLDEN_OUTPUT)
        self._assert_no_log()
        self._assert_no_report()
        self._assert_expected_xunit('xunitfile-only.xml')

    def test_split_tests(self):
        self._settings._opts['SplitLog'] = True
        self._settings._opts['Log'] = '/tmp/foo/log.bar.html'
        self._write_results(resources.GOLDEN_OUTPUT)
        expected = ['/tmp/foo/log.bar-%d.js' % i for i in range(1, 5)]
        self.assertEquals(self._split_test_names, expected)

    def _assert_expected_log(self, expected_file_name):
        if expected_file_name:
            expected_file_name = abspath(expected_file_name)
        self.assertEquals(self._log_results['log_path'], expected_file_name)

    def _assert_expected_report(self, expected_file_name):
        if expected_file_name:
            expected_file_name = abspath(expected_file_name)
        self.assertEquals(self._report_results['report_path'], expected_file_name)

    def _assert_expected_xunit(self, expected_file_name):
        self.assertEquals(self._xunit_results['xunit_path'],
                          abspath(expected_file_name))

    def _assert_no_log(self):
        self._assert_expected_log(None)

    def _assert_no_report(self):
        self._assert_expected_report(None)

    def _assert_no_data_model_generation(self):
        self.assertEquals(len(self._datamodel_generations), 0)

    def _assert_data_model_generated_once(self):
        self.assertEquals(len(self._datamodel_generations), 1)

    def _write_results(self, *sources):
        self._reporter.write_results(*sources)

    def test_multiple_outputs(self):
        self._settings['Log'] = 'log.html'
        self._settings['Report'] = 'report.html'
        self._write_results(resources.GOLDEN_OUTPUT, resources.GOLDEN_OUTPUT2)
        self._assert_expected_log('log.html')
        self._assert_expected_report('report.html')

    def test_output_generation(self):
        self._settings['Output'] = 'ouz.xml'
        self._write_results(resources.GOLDEN_OUTPUT, resources.GOLDEN_OUTPUT2)
        self._assert_expected_output('ouz.xml')

    def _assert_expected_output(self, expected_file_name):
        self.assertEquals(self._output_results['output_path'],
                          abspath(expected_file_name))

if __name__ == '__main__':
    unittest.main()
