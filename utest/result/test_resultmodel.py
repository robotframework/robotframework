import unittest
from robot.utils.asserts import assert_equals

from robot.reporting.results import SuiteExecutionResult

class TestSuiteExecutionResult(unittest.TestCase):

    def test_creation(self):
        somename = 'name'
        somesource = 'source'
        result = SuiteExecutionResult(somename, somesource)
        assert_equals(result.name, somename)
        assert_equals(result.source, somesource)


if __name__ == '__main__':
    unittest.main()

