import unittest
from robot.output.logger import Logger
from robot.output.readers import ExecutionErrors
import resources
from robot.common.model import BaseTestSuite
import robot.output
from robot.serializing.testoutput import Reporter
import robot.serializing.testoutput

def set_serialize_log_mock():
    results = {'log_path':None}
    def serialize_log(test_output_datamodel, log_path, title=None):
        results['log_path'] = log_path
        results['title'] = title
    robot.serializing.testoutput.serialize_log = serialize_log
    return results

def set_serialize_report_mock():
    results = {'report_path':None}
    def serialize_report(test_output_datamodel, report_path, title=None, logpath=None):
        results['report_path'] = report_path
        results['title'] = title
        results['logpath'] = logpath
    robot.serializing.testoutput.serialize_report = serialize_report
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
    robot.serializing.testoutput.process_outputs = process_outputs
    return results

class TestReporting(unittest.TestCase):

    def setUp(self):
        self._reporter = Reporter()
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
        self._original_logger = robot.serializing.testoutput.LOGGER
        robot.serializing.testoutput.LOGGER = Logger()
        robot.serializing.testoutput.LOGGER.disable_automatic_console_logger()
        self._log_results = set_serialize_log_mock()
        self._report_results = set_serialize_report_mock()
        #self._process_outputs_results = set_process_outputs_mock()

    def tearDown(self):
        robot.serializing.testoutput.LOGGER = self._original_logger

    def test_generate_report_and_log(self):
        self._settings['Log'] = 'log.html'
        self._settings['Report'] = 'report.html'
        self._reporter.execute(self._settings, resources.GOLDEN_OUTPUT)
        self._assert_expected_log('log.html')
        self._assert_expected_report('report.html')
        self._assert_log_link_in_report('log.html')

    def test_no_generation(self):
        self._reporter.execute(self._settings, resources.GOLDEN_OUTPUT)
        self._assert_no_log()
        self._assert_no_report()

    def test_only_log(self):
        self._settings['Log'] = 'only-log.html'
        self._reporter.execute(self._settings, resources.GOLDEN_OUTPUT)
        self._assert_expected_log('only-log.html')
        self._assert_no_report()

    def test_only_report(self):
        self._settings['Report'] = 'reports-only.html'
        self._reporter.execute(self._settings, resources.GOLDEN_OUTPUT)
        self._assert_no_log()
        self._assert_expected_report('reports-only.html')
        self._assert_no_log_links_in_report()

    def test_multiple_outputs(self):
        self._settings['Log'] = 'log.html'
        self._settings['Report'] = 'report.html'
        self._reporter.execute_rebot(self._settings, *[resources.GOLDEN_OUTPUT, resources.GOLDEN_OUTPUT2])
        self._assert_expected_log('log.html')
        self._assert_expected_report('report.html')

    def _assert_expected_log(self, expected_file_name):
        self.assertEquals(self._log_results['log_path'], expected_file_name)

    def _assert_expected_report(self, expected_file_name):
        self.assertEquals(self._report_results['report_path'], expected_file_name)

    def _assert_log_link_in_report(self, expected_log_link):
        self.assertEquals(self._report_results['logpath'], expected_log_link)

    def _assert_no_log_links_in_report(self):
        self._assert_log_link_in_report(None)

    def _assert_no_log(self):
        self._assert_expected_log(None)

    def _assert_no_report(self):
        self._assert_expected_report(None)


if __name__ == '__main__':
    unittest.main()
