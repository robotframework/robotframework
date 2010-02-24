import unittest
import sys

from robot.utils.asserts import assert_equals, assert_raises_with_msg,\
    assert_true, assert_false
from robot import utils
from robot.errors import DataError

from robot.common.model import BaseTestSuite, BaseTestCase, _Critical

def _get_suite():
    suite = BaseTestSuite('Root')
    suite.suites = [ BaseTestSuite('Sub1', parent=suite), BaseTestSuite('Sub2', parent=suite) ]
    suite.suites[0].suites = [ BaseTestSuite('Sub11', parent=suite.suites[0]), 
                              BaseTestSuite('Sub', parent=suite.suites[0])]
    suite.suites[0].suites[0].tests \
            = [ BaseTestCase('T11', suite.suites[0].suites[0]), 
               BaseTestCase('T12', suite.suites[0].suites[0]) ]
    suite.suites[0].suites[0].suites \
            = [ BaseTestSuite('Sub', parent=suite.suites[0].suites[0]) ]
    suite.suites[0].suites[0].suites[0].tests \
            = [ BaseTestCase('T', suite.suites[0].suites[0].suites[0]) ]
    suite.suites[0].suites[1].tests = [ BaseTestCase('T', parent=suite.suites[0].suites[1]) ]
    suite.suites[1].tests = [ BaseTestCase('T21', suite.suites[1]) ]
    return suite

class TestGetLongName(unittest.TestCase):
    
    def setUp(self):
        self.suite = _get_suite()
        
    def test_get_long_name_for_root_suite(self):
        assert_equals(self.suite.get_long_name(), 'Root')

    def test_get_long_name_for_sub_suite(self):
        assert_equals(self.suite.suites[0].get_long_name(), 'Root.Sub1')

    def test_get_long_name_for_sub_sub_suite(self):
        assert_equals(self.suite.suites[0].suites[1].get_long_name(), 
                      'Root.Sub1.Sub')

    def test_get_long_name_for_test(self):
        assert_equals(self.suite.suites[0].suites[0].tests[0].get_long_name(), 
                      'Root.Sub1.Sub11.T11')

    def test_get_long_name_for_test_with_non_default_separator(self):
        assert_equals(self.suite.suites[0].suites[0].tests[0].get_long_name(separator='|'), 
                      'Root|Sub1|Sub11|T11')

    def test_get_long_name_for_sub_suite_with_parts(self):
        assert_equals(self.suite.suites[0].get_long_name(separator=None), 
                      ['Root', 'Sub1'])

    def test_get_long_name_for_test_with_parts(self):
        assert_equals(self.suite.suites[0].suites[0].tests[0].get_long_name(separator=None), 
                      ['Root', 'Sub1', 'Sub11', 'T11'])

    def test_get_long_name_for_sub_suite_with_split_level_smaller(self):
        assert_equals(self.suite.suites[0].get_long_name(split_level=1), 
                      'Sub1')

    def test_get_long_name_for_sub_suite_with_split_level_same(self):
        assert_equals(self.suite.suites[0].get_long_name(split_level=2), 
                      'Root.Sub1')

    def test_get_long_name_for_sub_suite_with_split_level_larger(self):
        assert_equals(self.suite.suites[0].get_long_name(split_level=3), 
                      'Root.Sub1')

    def test_get_long_name_for_test_with_split_level_smaller(self):
        assert_equals(self.suite.suites[0].suites[0].tests[0].get_long_name(split_level=2), 
                      'Sub11.T11')

    def test_get_long_name_for_test_with_split_level_at_parent_suite_level(self):
        assert_equals(self.suite.suites[0].suites[0].tests[0].get_long_name(split_level=3), 
                      'Root.Sub1.Sub11.T11')

    def test_get_long_name_for_test_with_split_level_same(self):
        assert_equals(self.suite.suites[0].suites[0].tests[0].get_long_name(split_level=4), 
                      'Root.Sub1.Sub11.T11')

    def test_get_long_name_for_test_with_split_level_larger(self):
        assert_equals(self.suite.suites[0].suites[0].tests[0].get_long_name(split_level=5), 
                      'Root.Sub1.Sub11.T11')
    

class TestFilterByNames(unittest.TestCase):
    
    
    def test_with_suites(self):
        for names, count in [ (['Root'], 5),
                              (['Sub1'], 4),
                              (['Sub 11'], 3),
                              (['s u b 2'], 1), 
                              (['Sub?'], 5),
                              (['Sub 1*'], 4),
                              (['ROOT','Sub1'], 5),
                              (['Sub2','Nonex'], 1),
                              (['Sub11.Sub'], 1),
                              (['Root.Sub1.Sub'], 1)]:
            suite = _get_suite()
            suite.filter_by_names(names, [])
            assert_equals(suite.get_test_count(), count, names)

    def test_with_suites_no_matches(self):
        suite = _get_suite()
        err =  "Suite 'Root' contains no test suites named '%s'."
        assert_raises_with_msg(DataError, err % ('nonex'), 
                               suite.filter_by_names, ['nonex'], [])
        assert_raises_with_msg(DataError, err % ('b1.Sub'), 
                               suite.filter_by_names, ['b1.Sub'], [])

    def test_with_tests(self):
        for names, count in [ (['T11'], 1),
                              (['?12'], 1),
                              (['t 2  1'], 1), 
                              (['t*'], 5),
                              (['??1'], 2),
                              (['T11','T12'], 2),
                              (['Nonex','T21','Nonex2'], 1) ]:
            suite = _get_suite()
            suite.filter_by_names([], names)
            assert_equals(suite.get_test_count(), count)

    def test_with_tests_no_matches(self):
        suite = _get_suite()
        err =  "Suite 'Root' contains no test cases named 'x', 'y' or 'z'."
        assert_raises_with_msg(DataError, err, suite.filter_by_names, [], ['x','y','z'])

    def test_with_suites_and_tests(self):
        for suites, tests, count in [ (['Root'], ['T11'], 1),
                                      (['Sub1'], ['t 1  2'], 1), 
                                      (['sub11'], ['t11','nonex'], 1),
                                      (['sub1'], ['t11','t2.1'], 1),
                                      (['sub?'], ['t11','t21'], 2),
                                      (['ROOT','nonex'], ['t11','t21'], 2),
                                      (['*'], ['t*'], 5) ]:
            suite = _get_suite()
            suite.filter_by_names(suites, tests)
            assert_equals(suite.get_test_count(), count, '%s & %s'%(suites,tests))

    def test_with_suites_and_tests_no_matches(self):
        suite = _get_suite()
        for suites, tests in [ (['Root'], ['nonex']),
                               (['Nonex'], ['T1.1']),
                               (['Sub2'], ['T1.1']), ]:
            msg = ("Suite 'Root' contains no test cases %s in suites %s." 
                   % (utils.seq2str(tests, lastsep=' or '),
                      utils.seq2str(suites, lastsep=' or ')))
            assert_raises_with_msg(DataError, msg, suite.filter_by_names, suites, tests)


class TestSetCriticality(unittest.TestCase):
    
    def _test(self, crit, noncrit, exp):
        test = BaseTestCase('Name', parent=None)
        critical = _Critical()
        critical.set(crit, noncrit)
        test.tags = ['tag1', 'tag2', 'tag3']
        test.set_criticality(critical)
        assert_equals(test.critical, exp) 
    
    def test_no_crit_nor_noncrit(self):
        self._test([], [], 'yes')
        
    def test_non_matching_crit(self):
        self._test(['no','match'], [], 'no')
            
    def test_non_matching_noncrit(self):
        self._test([], ['nomatch'], 'yes')
        
    def test_non_matching_crit_and_noncrit(self):
        self._test(['no'], ['match','here'], 'no')
    
    def test_matching_crit(self):
        self._test(['tag1','match'], [], 'yes')
            
    def test_matching_noncrit(self):
        self._test([], ['tag1','tag2'], 'no')
        
    def test_matching_crit_and_noncrit(self):
        self._test(['tag1'], ['yyy','tag2','xxx'], 'no')
    
    def test_crit_is_pattern(self):
        self._test(['*1'], [], 'yes')
        self._test(['*1'], ['tag2'], 'no')
        
    def test_non_crit_is_pattern(self):
        self._test([], ['tag?'], 'no')
        self._test(['tag1','tagx'], ['????'], 'no')
        
    def test_crit_and_noncrit_are_patterns(self):
        self._test(['*1'], ['tag?'], 'no')
        self._test(['?a?3'], ['nomatch-*'], 'yes')
        self._test(['?a?3'], ['tag*'], 'no')


class TC(BaseTestCase):

    def __init__(self, tags=[]):
        self.tags = tags

class TestFilterByTags(unittest.TestCase):

    def setUp(self):
        self._tag1 = TC(['tag1'])
        self._tags12 = TC(['tag1', 'tag2'])
        self._tags123 = TC(['tag1', 'tag2', 'tag3'])

    def test_no_tags_no_incl_no_excl(self):
        assert_true(TC().is_included([], []))

    def test_tags_no_incl_no_excl(self):
        assert_true(self._tags12.is_included([], []))

    def test_simple_include(self):
        assert_true(self._tag1.is_included(['tag1'], []))
        assert_false(self._tag1.is_included(['tag2'], []))

    def test_simple_exclude(self):
        assert_false(self._tag1.is_included([], ['tag1']))
        assert_true(self._tag1.is_included([], ['tag2']))

    def test_include_and_exclude(self):
        assert_false(self._tags12.is_included(['tag1'], ['tag2']))

    def test_include_with_and(self):
        assert_true(self._tags12.is_included(['tag1&tag2'], []))
        assert_false(self._tags12.is_included(['tag1&tag3'], []))

    def test_exclude_with_and(self):
        assert_false(self._tags12.is_included([], ['tag1&tag2']))
        assert_true(self._tags12.is_included([], ['tag1&tag3']))

    def test_include_with_not(self):
        assert_false(self._tags12.is_included(['tag1NOTtag2'], []))
        assert_true(self._tags12.is_included(['tag1NOTtag3'], []))

    def test_exclude_with_not(self):
        assert_true(self._tags12.is_included([], ['tag1NOTtag2']))
        assert_false(self._tags12.is_included([], ['tag1NOTtag3']))

    def test_include_with_multiple_nots(self):
        assert_false(self._tags123.is_included(['tag1NOTtag2NOTtag3'], []))
        assert_false(self._tags123.is_included(['tag1NOTtag4NOTtag2'], []))
        assert_true(self._tags123.is_included(['tag1NOTtag4NOTtag5'], []))

    def test_exclude_with_multiple_nots(self):
        assert_true(self._tags123.is_included([], ['tag1NOTtag2NOTtag3']))
        assert_true(self._tags123.is_included([], ['tag1NOTtag4NOTtag2']))
        assert_false(self._tags123.is_included([], ['tag1NOTtag4NOTtag5']))

    def test_include_with_multiple_nots_and_ands(self):
        assert_true(self._tag1.is_included(['tag1NOTtag2&tag3NOTtag4&tag5'], []))
        assert_true(TC(['tag1', 'tag2', 'tag4']).is_included(['tag1NOTtag2&tag3NOTtag4&tag5'], []))
        assert_false(TC(['tag1', 'tag2', 'tag3']).is_included(['tag1NOTtag2&tag3NOTtag4&tag5'], []))
        assert_false(TC(['tag1', 'tag4', 'tag5']).is_included(['tag1NOTtag2&tag3NOTtag4&tag5'], []))
        assert_false(TC(['tag1', 'tag4']).is_included(['tag1NOTtag2NOTtag3NOTtag4NOTtag5'], []))

    def test_multiple_includes(self):
        assert_true(self._tags123.is_included(['incl', 'tag2'], []))
        assert_true(self._tags123.is_included(['tag1', 'tag2', 'tag3'], []))
        assert_false(self._tags123.is_included(['tag', 'incl', 'not', 'matching'], []))

    def test_multiple_excludes(self):
        assert_false(self._tags123.is_included([], ['incl', 'tag2']))
        assert_false(self._tags123.is_included([], ['tag1', 'tag2', 'tag3']))
        assert_true(self._tags123.is_included([], ['tag', 'excl', 'not', 'matching']))

    def test_invalid(self):
        for invalid in [ 'NOT', 'NOTNOT', 'xNOTNOTy', 'NOTa', 'bNOT', 
                         'NOTaNOTb', 'aNOTbNOT' ]:
            assert_false(self._tag1.is_included([invalid], []))
            assert_true(self._tag1.is_included(['tag1'], [invalid]))

if __name__ == "__main__":
    unittest.main()
