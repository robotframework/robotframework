import unittest
from robot.utils.asserts import (assert_equal, assert_false, assert_raises,
                                 assert_raises_with_msg, assert_true)

from robot.result import Message, Keyword, TestCase, TestSuite


class TestSuiteStats(unittest.TestCase):

    def test_stats(self):
        suite = self._create_suite_with_tests()
        assert_equal(suite.statistics.critical.passed, 2)
        assert_equal(suite.statistics.critical.failed, 1)
        assert_equal(suite.statistics.all.passed, 3)
        assert_equal(suite.statistics.all.failed, 2)

    def test_nested_suite_stats(self):
        suite = self._create_nested_suite_with_tests()
        assert_equal(suite.statistics.critical.passed, 4)
        assert_equal(suite.statistics.critical.failed, 2)
        assert_equal(suite.statistics.all.passed, 6)
        assert_equal(suite.statistics.all.failed, 4)

    def test_test_count(self):
        suite = self._create_nested_suite_with_tests()
        assert_equal(suite.test_count, 10)
        assert_equal(suite.suites[0].test_count, 5)
        suite.suites.append(self._create_suite_with_tests())
        assert_equal(suite.test_count, 15)
        suite.suites[-1].tests.create()
        assert_equal(suite.test_count, 16)
        assert_equal(suite.suites[-1].test_count, 6)

    def _create_nested_suite_with_tests(self):
        suite = TestSuite()
        suite.set_criticality([], ['nc'])
        suite.suites = [self._create_suite_with_tests(),
                        self._create_suite_with_tests()]
        return suite

    def _create_suite_with_tests(self):
        suite = TestSuite()
        suite.set_criticality([], ['nc'])
        suite.tests = [TestCase(status='PASS'),
                       TestCase(status='PASS', tags='nc'),
                       TestCase(status='PASS'),
                       TestCase(status='FAIL'),
                       TestCase(status='FAIL', tags='nc')]
        return suite


class TestSuiteStatus(unittest.TestCase):

    def test_suite_status_is_passed_by_default(self):
        assert_equal(TestSuite().status, 'PASS')

    def test_suite_status_is_failed_if_critical_failed_test(self):
        suite = TestSuite()
        suite.tests.create(status='PASS')
        assert_equal(suite.status, 'PASS')
        suite.tests.create(status='FAIL')
        assert_equal(suite.status, 'FAIL')
        suite.tests.create(status='PASS')
        assert_equal(suite.status, 'FAIL')

    def test_suite_status_is_passed_if_only_passed_tests(self):
        suite = TestSuite()
        for i in range(10):
            suite.tests.create(status='PASS')
        assert_equal(TestSuite().status, 'PASS')

    def test_suite_status_is_failed_if_failed_subsuite(self):
        suite = TestSuite()
        suite.suites.create().tests.create(status='FAIL')
        assert_equal(suite.status, 'FAIL')

    def test_passed(self):
        suite = TestSuite()
        assert_true(suite.passed)
        suite.tests.create(status='PASS')
        assert_true(suite.passed)
        suite.tests.create(status='FAIL', tags='tag')
        assert_false(suite.passed)
        suite.set_criticality(non_critical_tags='tag')
        assert_true(suite.passed)


class TestElapsedTime(unittest.TestCase):

    def test_suite_elapsed_time_when_start_and_end_given(self):
        suite = TestSuite()
        suite.starttime = '20010101 10:00:00.000'
        suite.endtime = '20010101 10:00:01.234'
        assert_equal(suite.elapsedtime, 1234)

    def test_suite_elapsed_time_is_zero_by_default(self):
        suite = TestSuite()
        assert_equal(suite.elapsedtime, 0)

    def _test_suite_elapsed_time_is_test_time(self):
        suite = TestSuite()
        suite.tests.create(starttime='19991212 12:00:00.010',
                           endtime='19991212 13:00:01.010')
        assert_equal(suite.elapsedtime, 3610000)


class TestSlots(unittest.TestCase):

    def test_testsuite(self):
        self._verify(TestSuite())

    def test_testcase(self):
        self._verify(TestCase())

    def test_keyword(self):
        self._verify(Keyword())

    def test_message(self):
        self._verify(Message())

    def _verify(self, item):
        assert_raises(AttributeError, setattr, item, 'attr', 'value')


class TestCriticality(unittest.TestCase):

    def setUp(self):
        self.suite = TestSuite()
        self.sub = self.suite.suites.create()

    def test_default_criticality(self):
        self._verify_criticality(self.suite, [], [])
        self._verify_criticality(self.sub, [], [])

    def test_set_criticality(self):
        self.suite.set_criticality(['c1', 'c2'], 'non')
        self._verify_criticality(self.suite, ['c1', 'c2'], ['non'])
        self._verify_criticality(self.sub, ['c1', 'c2'], ['non'])

    def test_cannot_set_criticality_for_child_suites(self):
        assert_raises_with_msg(
            ValueError, 'Criticality can only be set to the root suite.',
            self.sub.set_criticality
        )

    def test_criticality_set_for_child_suites_earlier_is_ignored(self):
        self.suite.set_criticality('use', 'us')
        sub2 = TestSuite()
        sub2.set_criticality('ignore', 'these')
        self.suite.suites.append(sub2)
        self._verify_criticality(self.suite, ['use'], ['us'])
        self._verify_criticality(self.sub, ['use'], ['us'])
        self._verify_criticality(sub2, ['use'], ['us'])

    def test_critical_with_parent(self):
        suite = TestSuite()
        assert_equal(suite.tests.create().critical, True)
        suite.set_criticality(critical_tags=['crit'])
        assert_equal(suite.tests.create().critical, False)
        assert_equal(suite.tests.create(tags=['crit']).critical, True)

    def test_critical_without_parent(self):
        assert_equal(TestCase().critical, True)

    def _verify_criticality(self, suite, crit, non_crit):
        assert_equal([str(t) for t in suite.criticality.critical_tags], crit)
        assert_equal([str(t) for t in suite.criticality.non_critical_tags], non_crit)


class TestModel(unittest.TestCase):

    def test_keyword_name(self):
        kw = Keyword('keyword')
        assert_equal(kw.name, 'keyword')
        kw = Keyword('keyword', 'lib')
        assert_equal(kw.name, 'lib.keyword')
        kw.kwname = 'Kekkonen'
        kw.libname = 'Urho'
        assert_equal(kw.name, 'Urho.Kekkonen')

    def test_keyword_name_cannot_be_set_directly(self):
        assert_raises(AttributeError, setattr, Keyword(), 'name', 'value')

    def test_test_passed(self):
        self._test_passed(TestCase())

    def test_keyword_passed(self):
        self._test_passed(Keyword())

    def test_keyword_passed_after_dry_run(self):
        self._test_passed(Keyword(status='NOT_RUN'),
                          initial_status='NOT_RUN')

    def _test_passed(self, item, initial_status='FAIL'):
        assert_equal(item.passed, False)
        assert_equal(item.status, initial_status)
        item.passed = True
        assert_equal(item.passed, True)
        assert_equal(item.status, 'PASS')
        item.passed = False
        assert_equal(item.passed, False)
        assert_equal(item.status, 'FAIL')

    def test_suite_passed(self):
        suite = TestSuite()
        assert_equal(suite.passed, True)
        suite.tests.create(status='FAIL')
        assert_equal(suite.passed, False)
        assert_raises(AttributeError, setattr, TestSuite(), 'passed', True)


if __name__ == '__main__':
    unittest.main()
