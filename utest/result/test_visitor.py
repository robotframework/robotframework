import unittest
from os.path import dirname, join

from robot.result import ExecutionResult
from robot.result.visitor import SuiteVisitor
from robot.utils.asserts import assert_equal


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

    def test_start_and_end_methods_can_add_items(self):
        suite = RESULT.suite.deepcopy()
        suite.visit(ItemAdder())
        assert_equal(len(suite.tests), len(RESULT.suite.tests) + 2)
        assert_equal(suite.tests[-2].name, 'Added by start_test')
        assert_equal(suite.tests[-1].name, 'Added by end_test')
        assert_equal(len(suite.tests[0].keywords),
                     len(RESULT.suite.tests[0].keywords) + 2)
        assert_equal(suite.tests[0].keywords[-2].name, 'Added by start_keyword')
        assert_equal(suite.tests[0].keywords[-1].name, 'Added by end_keyword')


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


class ItemAdder(SuiteVisitor):
    test_to_add = 2
    test_started = False
    kw_added = False

    def start_test(self, test):
        if self.test_to_add > 0:
            test.parent.tests.create(name='Added by start_test')
            self.test_to_add -= 1
        self.test_started = True

    def end_test(self, test):
        if self.test_to_add > 0:
            test.parent.tests.create(name='Added by end_test')
            self.test_to_add -= 1
        self.test_started = False

    def start_keyword(self, keyword):
        if self.test_started and not self.kw_added:
            keyword.parent.keywords.create(kwname='Added by start_keyword')
            self.kw_added = True

    def end_keyword(self, keyword):
        if keyword.name == 'Added by start_keyword':
            keyword.parent.keywords.create(kwname='Added by end_keyword')


if __name__ == '__main__':
    unittest.main()
