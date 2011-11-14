import unittest

from robot.reporting import ResultWriter
from robot.reporting.outputparser import OutputParser
from robot.reporting.builders import LogBuilder, ReportBuilder, XUnitBuilder

import resources


def set_write_log_mock():
    results = {'log_path': None}
    def write_log(self):
        results['log_path'] = self._path
    LogBuilder._write_file = write_log
    return results

def set_write_report_mock():
    results = {'report_path': None}
    def write_report(self):
        results['report_path'] = self._path
    ReportBuilder._write_file = write_report
    return results

def set_write_xunit_mock():
    results = {'xunit_path': None}
    def build_xunit(self):
        results['xunit_path'] = self._path
    XUnitBuilder.build = build_xunit
    return results

def set_write_split_test_mock():
    results = []
    def _write_test(self, index, keywords, strings, name):
        results.append(name)
    LogBuilder._write_test = _write_test
    return results

def set_datamodel_generation_spy():
    generated = []
    original = OutputParser.parse
    def parse(*args):
        generated.append(True)
        return original(*args)
    OutputParser.parse = parse
    return generated


class TestReporting(unittest.TestCase):

    def setUp(self):
        self._settings = {
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
            'RemoveKeywords': None
        }
        self._reporter = ResultWriter(self._settings)
        self._log_results = set_write_log_mock()
        self._report_results = set_write_report_mock()
        self._xunit_results = set_write_xunit_mock()
        self._split_test_names = set_write_split_test_mock()
        self._datamodel_generations = set_datamodel_generation_spy()

    def test_generate_report_and_log(self):
        self._settings['Log'] = 'log.html'
        self._settings['Report'] = 'report.html'
        self._reporter.write_robot_results(resources.GOLDEN_OUTPUT)
        self._assert_expected_log('log.html')
        self._assert_expected_report('report.html')
        self._assert_data_model_generated_once()

    def test_no_generation(self):
        self._reporter.write_robot_results(resources.GOLDEN_OUTPUT)
        self._assert_no_log()
        self._assert_no_report()
        self._assert_no_data_model_generation()

    def test_only_log(self):
        self._settings['Log'] = 'only-log.html'
        self._reporter.write_robot_results(resources.GOLDEN_OUTPUT)
        self._assert_expected_log('only-log.html')
        self._assert_no_report()

    def test_only_report(self):
        self._settings['Report'] = 'reports-only.html'
        self._reporter.write_robot_results(resources.GOLDEN_OUTPUT)
        self._assert_no_log()
        self._assert_expected_report('reports-only.html')

    def test_only_xunit(self):
        self._settings['XUnitFile'] = 'xunitfile-only.xml'
        self._reporter.write_robot_results(resources.GOLDEN_OUTPUT)
        self._assert_no_log()
        self._assert_no_report()
        self._assert_expected_xunit('xunitfile-only.xml')

    def test_multiple_outputs(self):
        self._settings['Log'] = 'log.html'
        self._settings['Report'] = 'report.html'
        self._reporter.write_rebot_results(*[resources.GOLDEN_OUTPUT, resources.GOLDEN_OUTPUT2])
        self._assert_expected_log('log.html')
        self._assert_expected_report('report.html')

    def test_split_tests(self):
        self._settings['SplitLog'] = True
        self._settings['Log'] = '/tmp/foo/log.bar.html'
        self._reporter.write_robot_results(resources.GOLDEN_OUTPUT)
        expected = ('/tmp/foo/log.bar-%d.js' % i for i in range(1, 5))
        self._assert_expected_split_tests(*expected)

    def _assert_expected_log(self, expected_file_name):
        self.assertEquals(self._log_results['log_path'], expected_file_name)

    def _assert_expected_split_tests(self, *expected_names):
        self.assertEquals(self._split_test_names, list(expected_names))

    def _assert_expected_report(self, expected_file_name):
        self.assertEquals(self._report_results['report_path'], expected_file_name)

    def _assert_expected_xunit(self, expected_file_name):
        self.assertEquals(self._xunit_results['xunit_path'], expected_file_name)

    def _assert_no_log(self):
        self._assert_expected_log(None)

    def _assert_no_report(self):
        self._assert_expected_report(None)

    def _assert_no_data_model_generation(self):
        self.assertEquals(len(self._datamodel_generations), 0)

    def _assert_data_model_generated_once(self):
        self.assertEquals(len(self._datamodel_generations), 1)


if __name__ == '__main__':
    unittest.main()
