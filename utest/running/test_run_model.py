import unittest

from robot import model
from robot.running.model import TestSuite, TestCase, Keyword
from robot.utils.asserts import assert_equals, assert_not_equals


class TestModelTypes(unittest.TestCase):

    def test_suite_keyword(self):
        kw = TestSuite().keywords.create()
        assert_equals(type(kw), Keyword)
        assert_not_equals(type(kw), model.Keyword)

    def test_suite_test_case(self):
        test = TestSuite().tests.create()
        assert_equals(type(test), TestCase)
        assert_not_equals(type(test), model.TestCase)

    def test_test_case_keyword(self):
        kw = TestCase().keywords.create()
        assert_equals(type(kw), Keyword)
        assert_not_equals(type(kw), model.Keyword)


if __name__ == '__main__':
    unittest.main()
