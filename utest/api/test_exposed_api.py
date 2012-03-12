import unittest

from robot import parsing
from robot import result
from robot import running

from robot.utils.asserts import assert_equals

class TestExposedApi(unittest.TestCase):

    def test_test_case_file(self):
        from robot.api import TestCaseFile
        assert_equals(TestCaseFile, parsing.TestCaseFile)

    def test_test_data_directory(self):
        from robot.api import TestDataDirectory
        assert_equals(TestDataDirectory, parsing.TestDataDirectory)

    def test_resource_file(self):
        from robot.api import ResourceFile
        assert_equals(ResourceFile, parsing.ResourceFile)

    def test_test_data(self):
        from robot.api import TestData
        assert_equals(TestData, parsing.TestData)

    def test_execution_result(self):
        from robot.api import ExecutionResult
        assert_equals(ExecutionResult, result.ExecutionResult)

    def test_test_suite(self):
        from robot.api import TestSuite
        assert_equals(TestSuite, running.TestSuite)
