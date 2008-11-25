import unittest
import sys

from robot.utils.asserts import assert_equals, assert_raises_with_msg
from robot import utils
from robot.errors import DataError

from robot.common.model import BaseTestSuite, BaseTestCase, _Critical


class TestFilterByNames(unittest.TestCase):
    
    def _get_suite(selff):
        suite = BaseTestSuite('Root')
        suite.suites = [ BaseTestSuite('Sub1'), BaseTestSuite('Sub2') ]
        suite.suites[0].suites = [ BaseTestSuite('Sub11') , BaseTestSuite('Sub')]
        suite.suites[0].suites[0].tests \
                = [ BaseTestCase('T11'), BaseTestCase('T12') ]
        suite.suites[0].suites[0].suites = [ BaseTestSuite('Sub') ]
        suite.suites[0].suites[0].suites[0].tests = [ BaseTestCase('T') ]

        suite.suites[0].suites[1].tests = [ BaseTestCase('T') ]
        suite.suites[1].tests = [ BaseTestCase('T21') ]
        suite.set_names()
        return suite
    
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
            suite = self._get_suite()
            suite.filter_by_names(names, [])
            assert_equals(suite.get_test_count(), count, names)
            filtered = [ n.lower().replace(' ','') for n in names ]
            filtered.sort()
            assert_equals(suite.filtered.suites, filtered)
            assert_equals(suite.filtered.tests, [])

    def test_with_suites_no_matches(self):
        suite = self._get_suite()
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
            suite = self._get_suite()
            suite.filter_by_names([], names)
            assert_equals(suite.get_test_count(), count)
            filtered = [ n.lower().replace(' ','') for n in names ]
            filtered.sort()
            assert_equals(suite.filtered.tests, filtered)
            assert_equals(suite.filtered.suites, [])

    def test_with_tests_no_matches(self):
        suite = self._get_suite()
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
            suite = self._get_suite()
            suite.filter_by_names(suites, tests)
            assert_equals(suite.get_test_count(), count, '%s & %s'%(suites,tests))
            filt_suites = [ n.lower().replace(' ','') for n in suites ]
            filt_tests = [ n.lower().replace(' ','') for n in tests ]
            filt_suites.sort(); filt_tests.sort()
            assert_equals(suite.filtered.suites, filt_suites)
            assert_equals(suite.filtered.tests, filt_tests)

    def test_with_suites_and_tests_no_matches(self):
        suite = self._get_suite()
        for suites, tests in [ (['Root'], ['nonex']),
                               (['Nonex'], ['T1.1']),
                               (['Sub2'], ['T1.1']), ]:
            msg = ("Suite 'Root' contains no test cases %s in suites %s." 
                   % (utils.seq2str(tests, lastsep=' or '),
                      utils.seq2str(suites, lastsep=' or ')))
            assert_raises_with_msg(DataError, msg, suite.filter_by_names, suites, tests)


class TestSetCriticality(unittest.TestCase):
    
    def _test(self, crit, noncrit, exp):
        test = BaseTestCase()
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


if __name__ == "__main__":
    unittest.main()