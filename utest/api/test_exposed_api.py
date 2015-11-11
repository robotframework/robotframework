import unittest

from os.path import abspath, join

from robot import api, model, parsing, reporting, result, running

from robot.utils.asserts import assert_equal


class TestExposedApi(unittest.TestCase):

    def test_test_case_file(self):
        assert_equal(api.TestCaseFile, parsing.TestCaseFile)

    def test_test_data_directory(self):
        assert_equal(api.TestDataDirectory, parsing.TestDataDirectory)

    def test_resource_file(self):
        assert_equal(api.ResourceFile, parsing.ResourceFile)

    def test_test_data(self):
        assert_equal(api.TestData, parsing.TestData)

    def test_execution_result(self):
        assert_equal(api.ExecutionResult, result.ExecutionResult)

    def test_test_suite(self):
        assert_equal(api.TestSuite, running.TestSuite)

    def test_result_writer(self):
        assert_equal(api.ResultWriter, reporting.ResultWriter)

    def test_visitors(self):
        assert_equal(api.SuiteVisitor, model.SuiteVisitor)
        assert_equal(api.ResultVisitor, result.ResultVisitor)


class TestTestSuiteBuilder(unittest.TestCase):
    sources = [join(abspath(__file__), '..', '..', '..', 'atest', 'testdata', 'misc', n)
               for n in ('pass_and_fail.robot', 'normal.robot')]

    def test_create_with_datasources_as_list(self):
        suite = api.TestSuiteBuilder().build(*self.sources)
        assert_equal(suite.name, 'Pass And Fail & Normal')

    def test_create_with_datasource_as_string(self):
        suite = api.TestSuiteBuilder().build(self.sources[0])
        assert_equal(suite.name, 'Pass And Fail')


if __name__ == '__main__':
    unittest.main()
