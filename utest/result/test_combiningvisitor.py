import unittest
from robot.result.combiningvisitor import CombiningVisitor
from robot.result.testsuite import TestSuite
from robot.result.visitor import ResultVisitor
from robot.utils.asserts import assert_equals, assert_true


class MyTestCase(unittest.TestCase, ResultVisitor):

    def setUp(self):
        self._start_suite_calls = 0
        self._start_test_calls = 0
        self._start_keyword_calls = 0
        self._end_suite_calls = 0
        self._end_test_calls = 0
        self._end_keyword_calls = 0
        self._start_message_calls = 0
        self._end_message_calls = 0

    def start_suite(self, suite):
        self._start_suite_calls += 1

    def end_suite(self, suite):
        assert_true(self._end_test_calls > 0)
        self._end_suite_calls += 1

    def start_test(self, test):
        assert_true(self._start_suite_calls > 0)
        self._start_test_calls += 1

    def end_test(self, test):
        assert_true(self._end_keyword_calls > 0)
        self._end_test_calls += 1

    def start_keyword(self, keyword):
        assert_true(self._start_test_calls > 0)
        self._start_keyword_calls += 1

    def end_keyword(self, keyword):
        assert_true(self._end_message_calls > 0)
        self._end_keyword_calls += 1

    def start_message(self, msg):
        assert_true(self._start_keyword_calls > 0)
        self._start_message_calls += 1

    def end_message(self, msg):
        assert_true(self._start_message_calls > 0)
        self._end_message_calls += 1

    def test_combining_visitor(self):
        suite = TestSuite(name='hello')
        suite.tests.create(name='test').keywords.create(name='foo').messages.create(message='hello')
        suite.visit(CombiningVisitor(self, self))
        assert_equals(self._start_suite_calls, 2)
        assert_equals(self._start_test_calls, 2)
        assert_equals(self._start_keyword_calls, 2)
        assert_equals(self._start_message_calls, 2)
        assert_equals(self._end_suite_calls, 2)
        assert_equals(self._end_test_calls, 2)
        assert_equals(self._end_keyword_calls, 2)
        assert_equals(self._end_message_calls, 2)


if __name__ == '__main__':
    unittest.main()
