import unittest

from robot.result import ResultWriter
import robot.result.builders

import resources


def set_write_log_mock():
    results = {'log_path': None}
    def write_log(self):
        results['log_path'] = self._path
    robot.result.builders.LogBuilder._write_file = write_log
    return results

def set_write_report_mock():
    results = {'report_path': None}
    def write_report(self):
        results['report_path'] = self._path
    robot.result.builders.ReportBuilder._write_file = write_report
    return results


class TestReporting(unittest.TestCase):

    def setUp(self):
        self._settings = {
            'Report': 'NONE',
            'Log': 'NONE',
            'XUnitFile': 'NONE',
            'Output': 'NONE',
            'LogTitle': None,
            'ReportTitle': None,
            'ReportBackground': None,
            'SuiteStatLevel': None,
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
            'LogLevel': 'INFO'
        }
        self._reporter = ResultWriter(self._settings)
        robot.result.builders.LOGGER.disable_automatic_console_logger()
        self._log_results = set_write_log_mock()
        self._report_results = set_write_report_mock()

    def test_generate_report_and_log(self):
        self._settings['Log'] = 'log.html'
        self._settings['Report'] = 'report.html'
        self._reporter.write_robot_results(resources.GOLDEN_OUTPUT)
        self._assert_expected_log('log.html')
        self._assert_expected_report('report.html')

    def test_no_generation(self):
        self._reporter.write_robot_results(resources.GOLDEN_OUTPUT)
        self._assert_no_log()
        self._assert_no_report()

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

    def test_multiple_outputs(self):
        self._settings['Log'] = 'log.html'
        self._settings['Report'] = 'report.html'
        self._reporter.write_rebot_results(*[resources.GOLDEN_OUTPUT, resources.GOLDEN_OUTPUT2])
        self._assert_expected_log('log.html')
        self._assert_expected_report('report.html')

    def _assert_expected_log(self, expected_file_name):
        self.assertEquals(self._log_results['log_path'], expected_file_name)

    def _assert_expected_report(self, expected_file_name):
        self.assertEquals(self._report_results['report_path'], expected_file_name)

    def _assert_no_log(self):
        self._assert_expected_log(None)

    def _assert_no_report(self):
        self._assert_expected_report(None)


if __name__ == '__main__':
    unittest.main()
