import unittest
from robot.utils.asserts import (assert_equal, assert_false, assert_raises,
                                 assert_raises_with_msg, assert_true)

from robot.result import Message, Keyword, TestCase, TestSuite


class TestSuiteStats(unittest.TestCase):

    def test_stats(self):
        suite = self._create_suite_with_tests()
        assert_equal(suite.statistics.passed, 3)
        assert_equal(suite.statistics.failed, 2)

    def test_nested_suite_stats(self):
        suite = self._create_nested_suite_with_tests()
        assert_equal(suite.statistics.passed, 6)
        assert_equal(suite.statistics.failed, 4)

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
        suite.suites = [self._create_suite_with_tests(),
                        self._create_suite_with_tests()]
        return suite

    def _create_suite_with_tests(self):
        suite = TestSuite()
        suite.tests = [TestCase(status='PASS'),
                       TestCase(status='PASS', tags='nc'),
                       TestCase(status='PASS'),
                       TestCase(status='FAIL'),
                       TestCase(status='FAIL', tags='nc')]
        return suite


class TestSuiteStatus(unittest.TestCase):

    def test_suite_status_is_skip_if_there_are_no_tests(self):
        assert_equal(TestSuite().status, 'SKIP')

    def test_suite_status_is_fail_if_failed_test(self):
        suite = TestSuite()
        suite.tests.create(status='PASS')
        assert_equal(suite.status, 'PASS')
        suite.tests.create(status='FAIL')
        assert_equal(suite.status, 'FAIL')
        suite.tests.create(status='PASS')
        assert_equal(suite.status, 'FAIL')

    def test_suite_status_is_pass_if_only_passed_tests(self):
        suite = TestSuite()
        for i in range(10):
            suite.tests.create(status='PASS')
        assert_equal(suite.status, 'PASS')

    def test_suite_status_is_pass_if_passed_and_skipped(self):
        suite = TestSuite()
        for i in range(5):
            suite.tests.create(status='PASS')
            suite.tests.create(status='SKIP')
        assert_equal(suite.status, 'PASS')

    def test_suite_status_is_skip_if_only_skipped_tests(self):
        suite = TestSuite()
        for i in range(10):
            suite.tests.create(status='SKIP')
        assert_equal(suite.status, 'SKIP')
        assert_true(suite.skipped)

    def test_suite_status_is_fail_if_failed_subsuite(self):
        suite = TestSuite()
        suite.suites.create().tests.create(status='FAIL')
        assert_equal(suite.status, 'FAIL')
        suite.tests.create(status='PASS')
        assert_equal(suite.status, 'FAIL')

    def test_passed_failed_skipped_propertys(self):
        suite = TestSuite()
        assert_false(suite.passed)
        assert_false(suite.failed)
        assert_true(suite.skipped)
        suite.tests.create(status='SKIP')
        assert_false(suite.passed)
        assert_false(suite.failed)
        assert_true(suite.skipped)
        suite.tests.create(status='PASS')
        assert_true(suite.passed)
        assert_false(suite.failed)
        assert_false(suite.skipped)
        suite.tests.create(status='FAIL')
        assert_false(suite.passed)
        assert_true(suite.failed)
        assert_false(suite.skipped)

    def test_suite_status_cannot_be_set_directly(self):
        suite = TestSuite()
        for attr in 'status', 'passed', 'failed', 'skipped':
            assert_true(hasattr(suite, attr))
            assert_raises(AttributeError, setattr, suite, attr, True)


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

    def test_test_passed_failed_skipped_propertys(self):
        self._verify_passed_failed_skipped(TestCase())

    def test_keyword_passed_failed_skipped_propertys(self):
        self._verify_passed_failed_skipped(Keyword())

    def test_keyword_passed_after_dry_run(self):
        self._verify_passed_failed_skipped(Keyword(status='NOT_RUN'),
                                           initial_status='NOT_RUN')

    def _verify_passed_failed_skipped(self, item, initial_status='FAIL'):
        assert_equal(item.status, initial_status)
        assert_equal(item.passed, False)
        assert_equal(item.failed, initial_status == 'FAIL')
        assert_equal(item.skipped, False)
        item.passed = True
        assert_equal(item.passed, True)
        assert_equal(item.failed, False)
        assert_equal(item.skipped, False)
        assert_equal(item.status, 'PASS')
        item.passed = False
        assert_equal(item.passed, False)
        assert_equal(item.failed, True)
        assert_equal(item.skipped, False)
        assert_equal(item.status, 'FAIL')
        item.failed = True
        assert_equal(item.passed, False)
        assert_equal(item.failed, True)
        assert_equal(item.skipped, False)
        assert_equal(item.status, 'FAIL')
        item.failed = False
        assert_equal(item.passed, True)
        assert_equal(item.failed, False)
        assert_equal(item.skipped, False)
        assert_equal(item.status, 'PASS')
        item.skipped = True
        assert_equal(item.passed, False)
        assert_equal(item.failed, False)
        assert_equal(item.skipped, True)
        assert_equal(item.status, 'SKIP')
        assert_raises(ValueError, setattr, item, 'skipped', False)


class TestKeywordChildren(unittest.TestCase):

    def test_only_keywords(self):
        kw = Keyword()
        for i in range(10):
            kw.keywords.create(str(i))
        assert_equal(kw.children, list(kw.keywords))

    def test_only_messages(self):
        kw = Keyword()
        for i in range(10):
            kw.messages.create(str(i))
        assert_equal(kw.children, list(kw.messages))

    def test_order(self):
        kw = Keyword('parent')
        m1 = kw.messages.create('m1')
        k1 = kw.keywords.create('k1')
        k2 = kw.keywords.create('k2')
        m2 = kw.messages.create('m2')
        k3 = kw.keywords.create('k3')
        assert_equal(kw.children, [m1, k1, k2, m2, k3])

    def test_order_after_modifications(self):
        kw = Keyword('parent')
        kw.keywords.create('k1')
        kw.messages.create('m1')
        k2 = kw.keywords.create('k2')
        m2 = kw.messages.create('m2')
        k1 = kw.keywords[0] = Keyword('k1-new')
        m1 = kw.messages[0] = Message('m1-new')
        m3 = Message('m3')
        kw.messages.append(m3)
        k3 = Keyword('k3')
        kw.keywords.extend([k3])
        assert_equal(kw.children, [k1, m1, k2, m2, m3, k3])
        kw.keywords = [k1, k3]
        kw.messages = [m1]
        assert_equal(kw.children, [k1, m1, k3])

    def test_id_with_keyword_parents(self):
        kw = TestSuite().tests.create().keywords.create('parent')
        kw.keywords = [Keyword('child1'), Keyword('child2')]
        kw.keywords[-1].keywords.create()
        assert_equal(kw.keywords[0].id, 's1-t1-k1-k1')
        assert_equal(kw.keywords[1].id, 's1-t1-k1-k2')
        assert_equal(kw.keywords[1].keywords[0].id, 's1-t1-k1-k2-k1')


if __name__ == '__main__':
    unittest.main()
