import unittest

from robot.model import TestSuite
from robot.model.filter import Filter
from robot.utils.asserts import assert_equal


class FilterBaseTest(unittest.TestCase):

    def _create_suite(self):
        self.s1 = TestSuite(name='s1')
        self.s21 = self.s1.suites.create(name='s21')
        self.s31 = self.s21.suites.create(name='s31')
        self.s31.tests.create(name='t1', tags=['t1', 's31'])
        self.s31.tests.create(name='t2', tags=['t2', 's31'])
        self.s31.tests.create(name='t3')
        self.s22 = self.s1.suites.create(name='s22')
        self.s22.tests.create(name='t1', tags=['t1', 's22', 'X'])

    def _test(self, filter, s31_tests, s22_tests):
        self._create_suite()
        self.s1.visit(filter)
        assert_equal([t.name for t in self.s31.tests], s31_tests)
        assert_equal([t.name for t in self.s22.tests], s22_tests)
        assert_equal(self.s1.test_count, len(s31_tests + s22_tests))


class TestFilterByIncludeTags(FilterBaseTest):

    def test_no_filtering(self):
        self._test(Filter(), ['t1', 't2', 't3'], ['t1'])
        self._test(Filter(include_tags=None), ['t1', 't2', 't3'], ['t1'])

    def test_empty_list_matches_none(self):
        self._test(Filter(include_tags=[]), [], [])

    def test_no_match(self):
        self._test(Filter(include_tags=['no', 'match']), [], [])

    def test_constant(self):
        self._test(Filter(include_tags=['t1']), ['t1'], ['t1'])

    def test_string(self):
        self._test(Filter(include_tags='t1'), ['t1'], ['t1'])

    def test_pattern(self):
        self._test(Filter(include_tags=['t*']), ['t1', 't2'], ['t1'])
        self._test(Filter(include_tags=['xxx', '?2', 's*2']), ['t2'], ['t1'])

    def test_normalization(self):
        self._test(Filter(include_tags=['T 1', '_T_2_']), ['t1', 't2'], ['t1'])

    def test_and_and_not(self):
        self._test(Filter(include_tags=['t1ANDs31']), ['t1'], [])
        self._test(Filter(include_tags=['?1ANDs*2ANDx']), [], ['t1'])
        self._test(Filter(include_tags=['t1ANDs*NOTx']), ['t1'], [])
        self._test(Filter(include_tags=['t1AND?1NOTs*ANDx']), ['t1'], [])


class TestFilterByExcludeTags(FilterBaseTest):

    def test_no_filtering(self):
        self._test(Filter(), ['t1', 't2', 't3'], ['t1'])
        self._test(Filter(exclude_tags=None), ['t1', 't2', 't3'], ['t1'])

    def test_empty_list_matches_none(self):
        self._test(Filter(exclude_tags=[]), ['t1', 't2', 't3'], ['t1'])

    def test_no_match(self):
        self._test(Filter(exclude_tags=['no', 'match']), ['t1', 't2', 't3'], ['t1'])

    def test_constant(self):
        self._test(Filter(exclude_tags=['t1']), ['t2', 't3'], [])

    def test_string(self):
        self._test(Filter(exclude_tags='t1'), ['t2', 't3'], [])

    def test_pattern(self):
        self._test(Filter(exclude_tags=['t*']), ['t3'], [])
        self._test(Filter(exclude_tags=['xxx', '?2', 's3*']), ['t3'], ['t1'])

    def test_normalization(self):
        self._test(Filter(exclude_tags=['T 1', '_T_2_']), ['t3'], [])

    def test_and_and_not(self):
        self._test(Filter(exclude_tags=['t1ANDs31']), ['t2', 't3'], ['t1'])
        self._test(Filter(exclude_tags=['?1ANDs*2ANDx']), ['t1', 't2', 't3'], [])
        self._test(Filter(exclude_tags=['t1ANDs*NOTx']), ['t2', 't3'], ['t1'])
        self._test(Filter(exclude_tags=['t1AND?1NOTs*ANDx']), ['t2', 't3'], ['t1'])


class TestFilterByTestName(FilterBaseTest):

    def test_no_filtering(self):
        self._test(Filter(), ['t1', 't2', 't3'], ['t1'])
        self._test(Filter(include_tests=None), ['t1', 't2', 't3'], ['t1'])

    def test_empty_list_matches_none(self):
        self._test(Filter(include_tests=[]), [], [])

    def test_no_match(self):
        self._test(Filter(include_tests=['no match']), [], [])

    def test_constant(self):
        self._test(Filter(include_tests=['t1']), ['t1'], ['t1'])
        self._test(Filter(include_tests=['t2', 'xxx']), ['t2'], [])

    def test_string(self):
        self._test(Filter(include_tests='t1'), ['t1'], ['t1'])

    def test_pattern(self):
        self._test(Filter(include_tests=['t*']), ['t1', 't2', 't3'], ['t1'])
        self._test(Filter(include_tests=['xxx', '*2', '?3']), ['t2', 't3'], [])

    def test_longname(self):
        self._test(Filter(include_tests=['s1.s21.s31.t3', 's1.s?2.*']), ['t3'], ['t1'])

    def test_normalization(self):
        self._test(Filter(include_tests=['T 1', '_T_2_']), ['t1', 't2'], ['t1'])


class TestFilterBySuiteName(FilterBaseTest):

    def test_no_filtering(self):
        self._test(Filter(), ['t1', 't2', 't3'], ['t1'])
        self._test(Filter(include_suites=None), ['t1', 't2', 't3'], ['t1'])

    def test_empty_list_matches_none(self):
        self._test(Filter(include_suites=[]), [], [])

    def test_no_match(self):
        self._test(Filter(include_suites=['no match']), [], [])

    def test_constant(self):
        self._test(Filter(include_suites=['s22']), [], ['t1'])
        self._test(Filter(include_suites=['s1', 'xxx']), ['t1', 't2', 't3'], ['t1'])

    def test_string(self):
        self._test(Filter(include_suites='s22'), [], ['t1'])

    def test_pattern(self):
        self._test(Filter(include_suites=['s3?']), ['t1', 't2', 't3'], [])

    def test_reuse_filter(self):
        filter = Filter(include_suites=['s22'])
        self._test(filter, [], ['t1'])
        self._test(filter, [], ['t1'])

    def test_longname(self):
        self._test(Filter(include_suites=['s1.s21.s31']), ['t1', 't2', 't3'], [])
        self._test(Filter(include_suites=['*.s2?.s31']), ['t1', 't2', 't3'], [])
        self._test(Filter(include_suites=['*.s22']), [], ['t1'])
        self._test(Filter(include_suites=['nonex.s22']), [], [])

    def test_normalization(self):
        self._test(Filter(include_suites=['_S 2 2_', 'xxx']), [], ['t1'])

    def test_with_other_filters(self):
        self._test(Filter(include_suites=['s21'], include_tests=['t1']), ['t1'], [])
        self._test(Filter(include_suites=['s22'], include_tags=['t*']), [], ['t1'])
        self._test(Filter(include_suites=['s21', 's22'], exclude_tags=['t?']), ['t3'], [])


class TestRemoveEmptySuitesDuringFilter(FilterBaseTest):

    def test_remove_empty_leaf_suite(self):
        self._test(Filter(include_tags='t2'), ['t2'], [])
        assert_equal(list(self.s1.suites), [self.s21])

    def test_remove_branch(self):
        self._test(Filter(include_suites='s22'), [], ['t1'])
        assert_equal(list(self.s1.suites), [self.s22])

    def test_remove_all(self):
        self._test(Filter(include_tests='none'), [], [])
        assert_equal(list(self.s1.suites), [])


if __name__ == '__main__':
    unittest.main()
