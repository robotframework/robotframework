import unittest

from robot.utils.asserts import assert_equal
from robot.result.model import TestSuite
from robot.result.visitors import *


class FilterBaseTest(unittest.TestCase):

    def _create_suite(self):
        self.s1 = TestSuite(name='s1')
        self.s21 = self.s1.suites.create(name='s21')
        self.s31 = self.s21.suites.create(name='s31')
        self.s31.tests.create(name='t1', tags=['t1', 's31'])
        self.s31.tests.create(name='t2', tags=['t2', 's31'])
        self.s31.tests.create(name='t3')
        self.s22 = self.s1.suites.create(name='s22')
        self.s22.tests.create(name='t1', tags=['t1', 's22'])
        return self.s1

    def _test(self, filter, s31_tests, s22_tests):
        suite = self._create_suite()
        suite.visit(filter)
        assert_equal([t.name for t in suite.suites[0].suites[0].tests], s31_tests)
        assert_equal([t.name for t in suite.suites[1].tests], s22_tests)
        assert_equal(suite.test_count, len(s31_tests + s22_tests))


class TestFilterByTestName(FilterBaseTest):

    def test_no_filtering(self):
        self._test(Filter(), ['t1', 't2', 't3'], ['t1'])
        self._test(Filter(include_tests=[]), ['t1', 't2', 't3'], ['t1'])

    def test_no_match(self):
        self._test(Filter(include_tests=['no match']), [], [])

    def test_constant(self):
        self._test(Filter(include_tests=['t1']), ['t1'], ['t1'])
        self._test(Filter(include_tests=['t2', 'xxx']), ['t2'], [])

    def test_pattern(self):
        self._test(Filter(include_tests=['t*']), ['t1', 't2', 't3'], ['t1'])
        self._test(Filter(include_tests=['xxx', '*2', '?3']), ['t2', 't3'], [])

    def test_longname(self):
        self._test(Filter(include_tests=['s1.s21.s31.t3', 's1.s?2.*']), ['t3'], ['t1'])

    def test_normalization(self):
        self._test(Filter(include_tests=['T 1', '_T_2_']), ['t1', 't2'], ['t1'])


class TestFilterByIncludeTags(FilterBaseTest):

    def test_no_filtering(self):
        self._test(Filter(), ['t1', 't2', 't3'], ['t1'])
        self._test(Filter(include_tags=[]), ['t1', 't2', 't3'], ['t1'])

    def test_no_match(self):
        self._test(Filter(include_tags=['no', 'match']), [], [])

    def test_constant(self):
        self._test(Filter(include_tags=['t1']), ['t1'], ['t1'])

    def test_pattern(self):
        self._test(Filter(include_tags=['t*']), ['t1', 't2'], ['t1'])
        self._test(Filter(include_tags=['xxx', '?2', 's*2']), ['t2'], ['t1'])

    def test_normalization(self):
        self._test(Filter(include_tags=['T 1', '_T_2_']), ['t1', 't2'], ['t1'])

    # TODO:
    # - AND and NOT patterns
    # - exclude
    # - suite
