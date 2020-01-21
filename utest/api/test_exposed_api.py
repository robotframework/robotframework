import unittest

from os.path import join

from robot import api, model, parsing, reporting, result, running

from robot.utils.asserts import assert_equal, assert_true


class TestExposedApi(unittest.TestCase):

    def test_execution_result(self):
        assert_equal(api.ExecutionResult, result.ExecutionResult)

    def test_test_suite(self):
        assert_equal(api.TestSuite, running.TestSuite)

    def test_result_writer(self):
        assert_equal(api.ResultWriter, reporting.ResultWriter)

    def test_visitors(self):
        assert_equal(api.SuiteVisitor, model.SuiteVisitor)
        assert_equal(api.ResultVisitor, result.ResultVisitor)

    def test_parsing(self):
        assert_equal(api.get_model, parsing.get_model)
        assert_equal(api.get_resource_model, parsing.get_resource_model)
        assert_equal(api.get_tokens, parsing.get_tokens)
        assert_equal(api.get_resource_tokens, parsing.get_resource_tokens)
        assert_equal(api.ModelTransformer, parsing.ModelTransformer)
        assert_equal(api.ModelVisitor, parsing.ModelVisitor)
        assert_equal(api.Token, parsing.Token)


class TestModelObjects(unittest.TestCase):
    """These model objects are part of the public API.

    They are only seldom needed directly and thus not exposed via the robot.api
    package. Tests just validate they are not removed accidentally.
    """

    def test_running_objects(self):
        assert_true(running.TestSuite)
        assert_true(running.TestCase)
        assert_true(running.Keyword)

    def test_result_objects(self):
        assert_true(result.TestSuite)
        assert_true(result.TestCase)
        assert_true(result.Keyword)
        assert_true(result.Message)


class TestTestSuiteBuilder(unittest.TestCase):
    # This list has paths like `/path/file.py/../file.robot` on purpose.
    # They don't work unless normalized.
    sources = [join(__file__, '../../../atest/testdata/misc', name)
               for name in ('pass_and_fail.robot', 'normal.robot')]

    def test_create_with_datasources_as_list(self):
        suite = api.TestSuiteBuilder().build(*self.sources)
        assert_equal(suite.name, 'Pass And Fail & Normal')

    def test_create_with_datasource_as_string(self):
        suite = api.TestSuiteBuilder().build(self.sources[0])
        assert_equal(suite.name, 'Pass And Fail')


if __name__ == '__main__':
    unittest.main()
