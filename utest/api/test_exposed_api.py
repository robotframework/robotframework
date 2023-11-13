import unittest

from os.path import join

from robot import api, model, parsing, reporting, result, running
from robot.api import parsing as api_parsing

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

    def test_typeinfo(self):
        assert_equal(api.TypeInfo, running.TypeInfo)

    def test_deprecated_parsing(self):
        assert_equal(api.get_model, parsing.get_model)
        assert_equal(api.get_resource_model, parsing.get_resource_model)
        assert_equal(api.get_tokens, parsing.get_tokens)
        assert_equal(api.get_resource_tokens, parsing.get_resource_tokens)
        assert_equal(api.Token, parsing.Token)

    def test_parsing_getters(self):
        assert_equal(api_parsing.get_model, parsing.get_model)
        assert_equal(api_parsing.get_resource_model, parsing.get_resource_model)
        assert_equal(api_parsing.get_tokens, parsing.get_tokens)
        assert_equal(api_parsing.get_resource_tokens, parsing.get_resource_tokens)

    def test_parsing_token(self):
        assert_equal(api_parsing.Token, parsing.Token)

    def test_parsing_model_statements(self):
        for cls in parsing.model.Statement.statement_handlers.values():
            assert_equal(getattr(api_parsing, cls.__name__), cls)
        assert_true(not hasattr(api_parsing, 'Statement'))

    def test_parsing_model_blocks(self):
        for name in ('File', 'SettingSection', 'VariableSection', 'TestCaseSection',
                     'KeywordSection', 'CommentSection', 'TestCase', 'Keyword', 'For',
                     'If', 'Try', 'While'):
            assert_equal(getattr(api_parsing, name), getattr(parsing.model, name))
        assert_true(not hasattr(api_parsing, 'Block'))

    def test_parsing_visitors(self):
        assert_equal(api_parsing.ModelVisitor, parsing.ModelVisitor)
        assert_equal(api_parsing.ModelTransformer, parsing.ModelTransformer)


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
