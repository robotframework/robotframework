import unittest
from os.path import dirname, join

from robot.result import ExecutionResult
from robot.result.visitor import SuiteVisitor


RESULT = ExecutionResult(join(dirname(__file__), 'golden.xml'))


class TestVisitingSuite(unittest.TestCase):

    def test_abstract_visitor(self):
        RESULT.suite.visit(SuiteVisitor())
        RESULT.suite.visit(SuiteVisitor())

    def test_start_suite_can_stop_visiting(self):
        RESULT.suite.visit(StartSuiteStopping())

    def test_start_test_can_stop_visiting(self):
        RESULT.suite.visit(StartTestStopping())

    def test_start_keyword_can_stop_visiting(self):
        RESULT.suite.visit(StartKeywordStopping())


class StartSuiteStopping(SuiteVisitor):

    def start_suite(self, suite):
        return False

    def end_suite(self, suite):
        raise AssertionError

    def start_test(self, test):
        raise AssertionError

    def start_keyword(self, keyword):
        raise AssertionError


class StartTestStopping(SuiteVisitor):

    def __init__(self):
        self.test_started = False

    def start_test(self, test):
        self.test_started = True
        return False

    def end_test(self, test):
        raise AssertionError

    def start_keyword(self, keyword):
        if self.test_started:
            raise AssertionError


class StartKeywordStopping(SuiteVisitor):

    def start_keyword(self, test):
        return False

    def end_keyword(self, test):
        raise AssertionError

    def log_message(self, msg):
        raise AssertionError


if __name__ == '__main__':
    unittest.main()
