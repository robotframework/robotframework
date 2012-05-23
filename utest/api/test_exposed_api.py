import unittest

from os.path import abspath, join

from robot import api, parsing, result, running
from robot.conf import RobotSettings

from robot.utils.asserts import assert_equals


class TestExposedApi(unittest.TestCase):

    def test_test_case_file(self):
        assert_equals(api.TestCaseFile, parsing.TestCaseFile)

    def test_test_data_directory(self):
        assert_equals(api.TestDataDirectory, parsing.TestDataDirectory)

    def test_resource_file(self):
        assert_equals(api.ResourceFile, parsing.ResourceFile)

    def test_test_data(self):
        assert_equals(api.TestData, parsing.TestData)

    def test_execution_result(self):
        assert_equals(api.ExecutionResult, result.ExecutionResult)

    def test_test_suite(self):
        assert_equals(api.TestSuite, running.TestSuite)


class TestTestSuite(unittest.TestCase):
    misc = join(abspath(__file__), '..', '..', '..', 'atest', 'testdata', 'misc')
    sources = [join(misc, n) for n in 'pass_and_fail.html', 'normal.html']

    def test_create_with_datasources_as_list(self):
        suite = api.TestSuite(self.sources, RobotSettings())
        assert_equals(suite.name, 'Pass And Fail & Normal')

    def test_create_with_datasource_as_string(self):
        suite = api.TestSuite(self.sources[0], RobotSettings())
        assert_equals(suite.name, 'Pass And Fail')

if __name__ == '__main__':
    unittest.main()
