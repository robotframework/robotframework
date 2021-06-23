import unittest
import warnings

from robot.model import Tags
from robot.result import For, If, IfBranch, Keyword, Message, TestCase, TestSuite
from robot.utils.asserts import (assert_equal, assert_false, assert_raises,
                                 assert_raises_with_msg, assert_true)


class TestSuiteStats(unittest.TestCase):

    def test_stats(self):
        suite = self._create_suite_with_tests()
        assert_equal(suite.statistics.passed, 3)
        assert_equal(suite.statistics.failed, 2)
        assert_equal(suite.statistics.skipped, 1)

    def test_nested_suite_stats(self):
        suite = self._create_nested_suite_with_tests()
        assert_equal(suite.statistics.passed, 6)
        assert_equal(suite.statistics.failed, 4)
        assert_equal(suite.statistics.skipped, 2)

    def test_test_count(self):
        suite = self._create_nested_suite_with_tests()
        assert_equal(suite.test_count, 12)
        assert_equal(suite.suites[0].test_count, 6)
        suite.suites.append(self._create_suite_with_tests())
        assert_equal(suite.test_count, 18)
        assert_equal(suite.suites[-1].test_count, 6)
        suite.suites[-1].tests.create()
        assert_equal(suite.test_count, 19)
        assert_equal(suite.suites[-1].test_count, 7)

    def _create_nested_suite_with_tests(self):
        suite = TestSuite()
        suite.suites = [self._create_suite_with_tests(),
                        self._create_suite_with_tests()]
        return suite

    def _create_suite_with_tests(self):
        suite = TestSuite()
        suite.tests = [TestCase(status='PASS'),
                       TestCase(status='PASS'),
                       TestCase(status='PASS'),
                       TestCase(status='FAIL'),
                       TestCase(status='FAIL'),
                       TestCase(status='SKIP')]
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

    def test_status_propertys(self):
        suite = TestSuite()
        assert_false(suite.passed)
        assert_false(suite.failed)
        assert_true(suite.skipped)
        assert_false(suite.not_run)
        suite.tests.create(status='SKIP')
        assert_false(suite.passed)
        assert_false(suite.failed)
        assert_true(suite.skipped)
        assert_false(suite.not_run)
        suite.tests.create(status='PASS')
        assert_true(suite.passed)
        assert_false(suite.failed)
        assert_false(suite.skipped)
        assert_false(suite.not_run)
        suite.tests.create(status='FAIL')
        assert_false(suite.passed)
        assert_true(suite.failed)
        assert_false(suite.skipped)
        assert_false(suite.not_run)

    def test_suite_status_cannot_be_set_directly(self):
        suite = TestSuite()
        for attr in 'status', 'passed', 'failed', 'skipped', 'not_run':
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

    def test_if(self):
        self._verify(If())

    def test_for(self):
        self._verify(For())

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

    def test_status_propertys_with_test(self):
        self._verify_status_propertys(TestCase())

    def test_status_propertys_with_keyword(self):
        self._verify_status_propertys(Keyword())

    def test_status_propertys_with_if(self):
        self._verify_status_propertys(If())

    def test_keyword_passed_after_dry_run(self):
        self._verify_status_propertys(Keyword(status=Keyword.NOT_RUN),
                                      initial_status=Keyword.NOT_RUN)

    def _verify_status_propertys(self, item, initial_status='FAIL'):
        item.starttime = '20210121 17:04:00.000'
        item.endtime = '20210121 17:04:01.002'
        assert_equal(item.elapsedtime, 1002)
        assert_equal(item.passed, initial_status == item.PASS)
        assert_equal(item.failed, initial_status == item.FAIL)
        assert_equal(item.skipped, initial_status == item.SKIP)
        assert_equal(item.not_run, initial_status == item.NOT_RUN)
        assert_equal(item.status, initial_status)
        item.passed = True
        assert_equal(item.passed, True)
        assert_equal(item.failed, False)
        assert_equal(item.skipped, False)
        assert_equal(item.not_run, False)
        assert_equal(item.status, 'PASS')
        item.passed = False
        assert_equal(item.passed, False)
        assert_equal(item.failed, True)
        assert_equal(item.skipped, False)
        assert_equal(item.not_run, False)
        assert_equal(item.status, 'FAIL')
        item.failed = True
        assert_equal(item.passed, False)
        assert_equal(item.failed, True)
        assert_equal(item.skipped, False)
        assert_equal(item.not_run, False)
        assert_equal(item.status, 'FAIL')
        item.failed = False
        assert_equal(item.passed, True)
        assert_equal(item.failed, False)
        assert_equal(item.skipped, False)
        assert_equal(item.not_run, False)
        assert_equal(item.status, 'PASS')
        item.skipped = True
        assert_equal(item.passed, False)
        assert_equal(item.failed, False)
        assert_equal(item.skipped, True)
        assert_equal(item.not_run, False)
        assert_equal(item.status, 'SKIP')
        assert_raises(ValueError, setattr, item, 'skipped', False)
        if isinstance(item, TestCase):
            assert_raises(AttributeError, setattr, item, 'not_run', True)
            assert_raises(AttributeError, setattr, item, 'not_run', False)
        else:
            item.not_run = True
            assert_equal(item.passed, False)
            assert_equal(item.failed, False)
            assert_equal(item.skipped, False)
            assert_equal(item.not_run, True)
            assert_equal(item.status, 'NOT RUN')
            assert_raises(ValueError, setattr, item, 'not_run', False)

    def test_keywords_deprecation(self):
        kw = Keyword()
        kw.body = [Keyword(), Message(), Keyword(), Keyword(), Message()]
        kw.teardown.config(kwname='T')
        with warnings.catch_warnings(record=True) as w:
            kws = kw.keywords
            assert_equal(list(kws), [kw.body[0], kw.body[2], kw.body[3], kw.teardown])
            assert_true('deprecated' in str(w[0].message))
        assert_raises(AttributeError, kws.append, Keyword())
        assert_raises(AttributeError, setattr, kw, 'keywords', [])

    def test_for_parents(self):
        test = TestCase()
        for_ = test.body.create_for()
        assert_equal(for_.parent, test)
        iter1 = for_.body.create_iteration()
        assert_equal(iter1.parent, for_)
        kw = iter1.body.create_keyword()
        assert_equal(kw.parent, iter1)
        iter2 = for_.body.create_iteration()
        assert_equal(iter2.parent, for_)
        kw = iter2.body.create_keyword()
        assert_equal(kw.parent, iter2)

    def test_if_parents(self):
        test = TestCase()
        if_ = test.body.create_if()
        assert_equal(if_.parent, test)
        branch = if_.body.create_branch(if_.IF, '$x > 0')
        assert_equal(branch.parent, if_)
        kw = branch.body.create_keyword()
        assert_equal(kw.parent, branch)
        branch = if_.body.create_branch(if_.ELSE_IF, '$x < 0')
        assert_equal(branch.parent, if_)
        kw = branch.body.create_keyword()
        assert_equal(kw.parent, branch)
        branch = if_.body.create_branch(if_.ELSE)
        assert_equal(branch.parent, if_)
        kw = branch.body.create_keyword()
        assert_equal(kw.parent, branch)


class TestBody(unittest.TestCase):

    def test_only_keywords(self):
        kw = Keyword()
        for i in range(10):
            kw.body.create_keyword(str(i))
        assert_equal([k.name for k in kw.body], [str(i) for i in range(10)])

    def test_only_messages(self):
        kw = Keyword()
        for i in range(10):
            kw.body.create_message(str(i))
        assert_equal([m.message for m in kw.body], [str(i) for i in range(10)])

    def test_order(self):
        kw = Keyword()
        m1 = kw.body.create_message('m1')
        k1 = kw.body.create_keyword('k1')
        k2 = kw.body.create_keyword('k2')
        m2 = kw.body.create_message('m2')
        k3 = kw.body.create_keyword('k3')
        assert_equal(list(kw.body), [m1, k1, k2, m2, k3])

    def test_order_after_modifications(self):
        kw = Keyword('parent')
        kw.body.create_keyword('k1')
        kw.body.create_message('m1')
        k2 = kw.body.create_keyword('k2')
        m2 = kw.body.create_message('m2')
        k1 = kw.body[0] = Keyword('k1-new')
        m1 = kw.body[1] = Message('m1-new')
        m3 = Message('m3')
        kw.body.append(m3)
        k3 = Keyword('k3')
        kw.body.extend([k3])
        assert_equal(list(kw.body), [k1, m1, k2, m2, m3, k3])
        kw.body = [k3, m2, k1]
        assert_equal(list(kw.body), [k3, m2, k1])

    def test_id(self):
        kw = TestSuite().tests.create().body.create_keyword()
        kw.body = [Keyword(), Message(), Keyword()]
        kw.body[-1].body = [Message(), Keyword(), Message()]
        assert_equal(kw.body[0].id, 's1-t1-k1-k1')
        assert_equal(kw.body[1].id, 's1-t1-k1-m1')
        assert_equal(kw.body[2].id, 's1-t1-k1-k2')
        assert_equal(kw.body[2].body[0].id, 's1-t1-k1-k2-m1')
        assert_equal(kw.body[2].body[1].id, 's1-t1-k1-k2-k1')
        assert_equal(kw.body[2].body[2].id, 's1-t1-k1-k2-m2')


class TestForIterations(unittest.TestCase):

    def test_create_iteration_message_supported(self):
        for_ = For()
        iterations = for_.body
        for creator in (iterations.create_iteration,
                        iterations.create_message):
            item = creator()
            assert_equal(item.parent, for_)

    def test_create_keyword_for_if_not_supported(self):
        iterations = For().body
        for creator in (iterations.create_keyword,
                        iterations.create_for,
                        iterations.create_if):
            msg = "'ForIterations' object does not support '%s'." % creator.__name__
            assert_raises_with_msg(TypeError, msg, creator)


class TestDeprecatedKeywordSpecificAttributes(unittest.TestCase):

    def test_deprecated_keyword_specific_properties(self):
        for_ = For(['${x}', '${y}'], 'IN', ['a', 'b', 'c', 'd'])
        for name, expected in [('name', '${x} | ${y} IN [ a | b | c | d ]'),
                               ('args', ()),
                               ('assign', ()),
                               ('tags', Tags()),
                               ('timeout', None)]:
            assert_equal(getattr(for_, name), expected)

    def test_if(self):
        for name, expected in [('name', ''),
                               ('args', ()),
                               ('assign', ()),
                               ('tags', Tags()),
                               ('timeout', None)]:
            assert_equal(getattr(If(), name), expected)

    def test_if_branch(self):
        branch = IfBranch(IfBranch.IF, '$x > 0')
        for name, expected in [('name', '$x > 0'),
                               ('args', ()),
                               ('assign', ()),
                               ('tags', Tags()),
                               ('timeout', None)]:
            assert_equal(getattr(branch, name), expected)


if __name__ == '__main__':
    unittest.main()
