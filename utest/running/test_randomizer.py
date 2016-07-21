import unittest

from robot.running import TestSuite, TestCase
from robot.utils.asserts import assert_equal, assert_not_equal

class TestRandomizing(unittest.TestCase):
    names = [str(i) for i in range(100)]

    def setUp(self):
        self.suite = self._generate_suite()

    def _generate_suite(self):
        s = TestSuite()
        s.suites = self._generate_suites()
        s.tests  = self._generate_tests()
        return s

    def _generate_suites(self):
        return [TestSuite(name=n) for n in self.names]

    def _generate_tests(self):
        return [TestCase(name=n) for n in self.names]

    def _assert_randomized(self, items):
        assert_not_equal([i.name for i in items], self.names)

    def _assert_not_randomized(self, items):
        assert_equal([i.name for i in items], self.names)

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
        assert_equal([s.id for s in self.suite.suites],
                      ['s1-s%d' % i for i in range(1, 101)])
        assert_equal([t.id for t in self.suite.tests],
                      ['s1-t%d' % i for i in range(1, 101)])
        self.suite.randomize(suites=True, tests=True)
        assert_equal([s.id for s in self.suite.suites],
                      ['s1-s%d' % i for i in range(1, 101)])
        assert_equal([t.id for t in self.suite.tests],
                      ['s1-t%d' % i for i in range(1, 101)])

    def _gen_random_suite(self, seed):
        suite = self._generate_suite()
        suite.randomize(suites=True, tests=True, seed=seed)
        random_order_suites = [i.name for i in suite.suites]
        random_order_tests  = [i.name for i in suite.tests]
        return (random_order_suites, random_order_tests)

    def test_randomize_seed(self):
        """
        GIVEN a test suite
        WHEN it's randomized with a given seed
        THEN it's always sorted in the same order
        """
        (random_order_suites1, random_order_tests1) = self._gen_random_suite(1234)
        (random_order_suites2, random_order_tests2) = self._gen_random_suite(1234)
        assert_equal( random_order_suites1, random_order_suites2 )
        assert_equal( random_order_tests1, random_order_tests2 )

if __name__ == '__main__':
    unittest.main()
