import unittest
from robot.output.logger import Logger
from robot.output.readers import ExecutionErrors
import resources
from robot.common.model import BaseTestSuite
import robot.output
from robot.result import ResultWriter
import robot.result.resultwriter

def set_serialize_log_mock():
    results = {'log_path':None}
    def serialize_log(test_output_datamodel, log_path, title=None):
        results['log_path'] = log_path
        results['title'] = title
    robot.result.resultwriter.serialize_log = serialize_log
    return results

def set_serialize_report_mock():
    results = {'report_path':None}
    def serialize_report(test_output_datamodel, report_path, title=None, logpath=None):
        results['report_path'] = report_path
        results['title'] = title
        results['logpath'] = logpath
    robot.result.resultwriter.serialize_report = serialize_report
    return results

def set_process_outputs_mock():
    results = {'paths':None}
    def process_outputs(paths, settings):
        results['paths'] = paths
        results['settings'] = settings
        suite = BaseTestSuite('Suite')
        suite.starttime = 7
        suite.endtime = 42
        return suite, ExecutionErrors(None)
    robot.serializing.resultwriter.process_outputs = process_outputs
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
        self._original_logger = robot.result.resultwriter.LOGGER
        robot.result.resultwriter.LOGGER = Logger()
        robot.result.resultwriter.LOGGER.disable_automatic_console_logger()
        self._log_results = set_serialize_log_mock()
        self._report_results = set_serialize_report_mock()

    def tearDown(self):
        robot.result.resultwriter.LOGGER = self._original_logger

    def test_generate_report_and_log(self):
        self._settings['Log'] = 'log.html'
        self._settings['Report'] = 'report.html'
        self._reporter.execute(resources.GOLDEN_OUTPUT)
        self._assert_expected_log('log.html')
        self._assert_expected_report('report.html')

    def test_no_generation(self):
        self._reporter.execute(resources.GOLDEN_OUTPUT)
        self._assert_no_log()
        self._assert_no_report()

    def test_only_log(self):
        self._settings['Log'] = 'only-log.html'
        self._reporter.execute(resources.GOLDEN_OUTPUT)
        self._assert_expected_log('only-log.html')
        self._assert_no_report()

    def test_only_report(self):
        self._settings['Report'] = 'reports-only.html'
        self._reporter.execute(resources.GOLDEN_OUTPUT)
        self._assert_no_log()
        self._assert_expected_report('reports-only.html')

    def test_multiple_outputs(self):
        self._settings['Log'] = 'log.html'
        self._settings['Report'] = 'report.html'
        self._reporter.execute_rebot(*[resources.GOLDEN_OUTPUT, resources.GOLDEN_OUTPUT2])
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
