import copy
import unittest

from robot import model
from robot.running.model import TestSuite, TestCase, Keyword
from robot.utils.asserts import assert_equal, assert_not_equal


class TestModelTypes(unittest.TestCase):

    def test_suite_keyword(self):
        kw = TestSuite().keywords.create()
        assert_equal(type(kw), Keyword)
        assert_not_equal(type(kw), model.Keyword)

    def test_suite_test_case(self):
        test = TestSuite().tests.create()
        assert_equal(type(test), TestCase)
        assert_not_equal(type(test), model.TestCase)

    def test_test_case_keyword(self):
        kw = TestCase().keywords.create()
        assert_equal(type(kw), Keyword)
        assert_not_equal(type(kw), model.Keyword)


class TestRunningCase(unittest.TestCase):
    def test_copy_testcase(self):
        case = TestCase()
        new_case = copy.copy(case)
        self.assertEqual(new_case.name, case.name)

        new_case.name = case.name + '_1'
        self.assertNotEqual(new_case.name, case.name)

        self.assertEqual(id(new_case.tags), id(case.tags))
        new_case.tags = "123"
        self.assertNotEqual(id(new_case.tags), id(case.tags))

    def test_deep_copy_testcase(self):
        case = TestCase()
        new_case = copy.deepcopy(case)
        self.assertEqual(new_case.name, case.name)
        self.assertNotEqual(id(new_case.tags), id(case.tags))


class TestRunningKeyword(unittest.TestCase):
    def test_copy_keyword(self):
        kw = Keyword()
        kw_new = copy.copy(kw)
        self.assertEqual(kw.name, kw_new.name)

        kw_new.name = kw.name + '1'
        self.assertNotEqual(kw.name, kw_new.name)

        self.assertEqual(id(kw.tags), id(kw_new.tags))

    def test_deepcopy_keyword(self):
        kw = Keyword()
        kw_new = copy.deepcopy(kw)
        self.assertEqual(kw.name, kw_new.name)
        self.assertNotEqual(id(kw.tags), id(kw_new.tags))


if __name__ == '__main__':
    unittest.main()
