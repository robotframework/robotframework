import unittest

from robot import model
from robot.new_running import TestSuite, TestCase, Keyword
from robot.utils.asserts import assert_false, assert_equals, assert_not_equals


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


class TestRandomizing(unittest.TestCase):
    names = [str(i) for i in range(100)]

    def setUp(self):
        self.suite = TestSuite()
        self.suite.suites = self._generate_suites()
        self.suite.tests = self._generate_tests()

    def _generate_suites(self):
        return [TestSuite(name=n) for n in self.names]

    def _generate_tests(self):
        return [TestCase(name=n) for n in self.names]

    def _assert_randomized(self, items):
        assert_not_equals([i.name for i in items], self.names)

    def _assert_not_randomized(self, items):
        assert_equals([i.name for i in items], self.names)

    def test_randomize_nothing(self):
        self.suite.randomize(suites=False, tests=False)
        self._assert_not_randomized(self.suite.suites)
        self._assert_not_randomized(self.suite.tests)

    def test_randomize_only_suites(self):
        self.suite.randomize(suites=True, tests=False)
        self._assert_randomized(self.suite.suites)
        self._assert_not_randomized(self.suite.tests)

    def test_randomize_only_tests(self):
        self.suite.randomize(suites=False, tests=True)
        self._assert_not_randomized(self.suite.suites)
        self._assert_randomized(self.suite.tests)

    def test_randomize_both(self):
        self.suite.randomize(suites=True, tests=True)
        self._assert_randomized(self.suite.suites)
        self._assert_randomized(self.suite.tests)

    def test_randomize_recursively(self):
        self.suite.suites[0].suites = self._generate_suites()
        self.suite.suites[1].tests = self._generate_tests()
        self.suite.randomize(suites=True, tests=True)
        self._assert_randomized(self.suite.suites[0].suites)
        self._assert_randomized(self.suite.suites[1].tests)

    def test_randomizing_changes_ids(self):
        assert_equals([s.id for s in self.suite.suites],
                      ['s1-s%d' % i for i in range(1, 101)])
        assert_equals([t.id for t in self.suite.tests],
                      ['s1-t%d' % i for i in range(1, 101)])
        self.suite.randomize(suites=True, tests=True)
        assert_equals([s.id for s in self.suite.suites],
                      ['s1-s%d' % i for i in range(1, 101)])
        assert_equals([t.id for t in self.suite.tests],
                      ['s1-t%d' % i for i in range(1, 101)])


if __name__ == '__main__':
    unittest.main()
