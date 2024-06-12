import unittest
from itertools import chain

from robot.errors import DataError
from robot.result import Keyword, TestCase, TestSuite
from robot.result.configurer import SuiteConfigurer
from robot.utils.asserts import assert_equal, assert_raises_with_msg, assert_true


SETUP = Keyword.SETUP
TEARDOWN = Keyword.TEARDOWN


class TestSuiteAttributes(unittest.TestCase):

    def setUp(self):
        self.suite = TestSuite(name='Suite', metadata={'A A': '1', 'bb': '1'})
        self.suite.tests.create(name='Make suite non-empty')

    def test_name_and_doc(self):
        self.suite.visit(SuiteConfigurer(name='New Name', doc='New Doc'))
        assert_equal(self.suite.name, 'New Name')
        assert_equal(self.suite.doc, 'New Doc')

    def test_metadata(self):
        self.suite.visit(SuiteConfigurer(metadata={'bb': '2', 'C': '2'}))
        assert_equal(self.suite.metadata, {'A A': '1', 'bb': '2', 'C': '2'})

    def test_metadata_is_normalized(self):
        self.suite.visit(SuiteConfigurer(metadata={'aa': '2', 'B_B': '2'}))
        assert_equal(self.suite.metadata, {'A A': '2', 'bb': '2'})


class TestTestAttributes(unittest.TestCase):

    def setUp(self):
        self.suite = TestSuite()
        self.suite.tests = [TestCase()]
        self.suite.suites = [TestSuite()]
        self.suite.suites[0].tests = [TestCase(tags=['tag'])]

    def test_set_tags(self):
        self.suite.visit(SuiteConfigurer(set_tags=['new']))
        assert_equal(list(self.suite.tests[0].tags), ['new'])
        assert_equal(list(self.suite.suites[0].tests[0].tags), ['new', 'tag'])

    def test_tags_are_normalized(self):
        self.suite.visit(SuiteConfigurer(set_tags=['TAG', '', 't a g', 'NONE']))
        assert_equal(list(self.suite.tests[0].tags), ['TAG'])
        assert_equal(list(self.suite.suites[0].tests[0].tags), ['tag'])

    def test_remove_negative_tags(self):
        self.suite.visit(SuiteConfigurer(set_tags=['n', '-TAG']))
        assert_equal(list(self.suite.tests[0].tags), ['n'])
        assert_equal(list(self.suite.suites[0].tests[0].tags), ['n'])

    def test_remove_negative_tags_using_pattern(self):
        self.suite.visit(SuiteConfigurer(set_tags=['-t*', '-nomatch']))
        assert_equal(list(self.suite.tests[0].tags), [])
        assert_equal(list(self.suite.suites[0].tests[0].tags), [])


class TestFiltering(unittest.TestCase):

    def setUp(self):
        self.suite = TestSuite(name='root')
        self.suite.tests = [TestCase(name='n0'), TestCase(name='n1', tags=['t1']),
                            TestCase(name='n2', tags=['t1', 't2'])]
        self.suite.suites.create(name='sub').tests.create(name='n1', tags=['t1'])

    def test_include(self):
        self.suite.visit(SuiteConfigurer(include_tags=['t1', 'none', '', '?2']))
        assert_equal([t.name for t in self.suite.tests], ['n1', 'n2'])
        assert_equal([t.name for t in self.suite.suites[0].tests], ['n1'])

    def test_exclude(self):
        self.suite.visit(SuiteConfigurer(exclude_tags=['t1', '?1ANDt2']))
        assert_equal([t.name for t in self.suite.tests], ['n0'])
        assert_equal(list(self.suite.suites), [])

    def test_include_by_names(self):
        self.suite.visit(SuiteConfigurer(include_suites=['s?b', 'xxx'],
                                         include_tests=['', '*1', 'xxx']))
        assert_equal(list(self.suite.tests), [])
        assert_equal([t.name for t in self.suite.suites[0].tests], ['n1'])

    def test_no_matching_tests_with_one_selector_each(self):
        configurer = SuiteConfigurer(include_tags='i', exclude_tags='e',
                                     include_suites='s', include_tests='t')
        assert_raises_with_msg(
            DataError,
            "Suite 'root' contains no tests matching name 't' "
            "and matching tag 'i' "
            "and not matching tag 'e' "
            "in suite 's'.",
            self.suite.visit, configurer
        )

    def test_no_matching_tests_with_multiple_selectors(self):
        configurer = SuiteConfigurer(include_tags=['i1', 'i2', 'i3'],
                                     exclude_tags=['e1', 'e2'],
                                     include_suites=['s1', 's2', 's3'],
                                     include_tests=['t1', 't2'])
        assert_raises_with_msg(
            DataError,
            "Suite 'root' contains no tests matching name 't1' or 't2' "
            "and matching tags 'i1', 'i2' or 'i3' "
            "and not matching tags 'e1' or 'e2' "
            "in suites 's1', 's2' or 's3'.",
            self.suite.visit, configurer
        )

    def test_empty_suite(self):
        suite = TestSuite(name='x')
        suite.visit(SuiteConfigurer(empty_suite_ok=True))
        assert_raises_with_msg(DataError,
                               "Suite 'x' contains no tests.",
                               suite.visit, SuiteConfigurer())


class TestRemoveKeywords(unittest.TestCase):

    def test_remove_all_removes_all(self):
        suite = self._suite_with_setup_and_teardown_and_test_with_keywords()
        self._remove('ALL', suite)
        for keyword in chain((suite.setup, suite.teardown), suite.tests[0].body):
            self._should_contain_no_messages_or_keywords(keyword)

    def test_remove_passed_removes_from_passed_test(self):
        suite = TestSuite()
        test = suite.tests.create(status='PASS')
        test.body.create_keyword(status='PASS').body.create_message(message='keyword message')
        test.body.create_keyword(status='PASS').body.create_keyword(status='PASS')
        self._remove_passed(suite)
        for keyword in test.body:
            self._should_contain_no_messages_or_keywords(keyword)

    def test_remove_passed_removes_setup_and_teardown_from_passed_suite(self):
        suite = TestSuite()
        suite.tests.create(status='PASS')
        suite.setup.config(name='S', status='PASS').body.create_keyword()
        suite.teardown.config(name='T', status='PASS').body.create_message(message='message')
        self._remove_passed(suite)
        for keyword in suite.setup, suite.teardown:
            self._should_contain_no_messages_or_keywords(keyword)

    def test_remove_passed_does_not_remove_when_test_failed(self):
        suite = TestSuite()
        test = suite.tests.create(status='FAIL')
        test.body.create_keyword(status='PASS').body.create_keyword()
        test.body.create_keyword(status='PASS').body.create_message(message='message')
        failed_keyword = test.body.create_keyword(status='FAIL')
        failed_keyword.body.create_message('mess')
        failed_keyword.body.create_keyword()
        self._remove_passed(suite)
        assert_equal(len(test.body[0].body), 1)
        assert_equal(len(test.body[0].messages), 0)
        assert_equal(len(test.body[1].body), 1)
        assert_equal(len(test.body[1].messages), 1)
        assert_equal(len(test.body[2].body), 2)
        assert_equal(len(test.body[2].messages), 1)

    def test_remove_passed_does_not_remove_when_test_contains_warning(self):
        suite = TestSuite()
        test = self._test_with_warning(suite)
        self._remove_passed(suite)
        assert_equal(len(test.body[0].body), 1)
        assert_equal(len(test.body[1].messages), 1)

    def _test_with_warning(self, suite):
        test = suite.tests.create(status='PASS')
        test.body.create_keyword(status='PASS').body.create_keyword()
        test.body.create_keyword(status='PASS').body.create_message(message='danger!',
                                                                    level='WARN')
        return test

    def test_remove_passed_does_not_remove_setup_and_teardown_from_failed_suite(self):
        suite = TestSuite()
        suite.setup.config(name='SETUP').body.create_message(message='some')
        suite.teardown.config(type='TEARDOWN').body.create_keyword()
        suite.tests.create(status='FAIL')
        self._remove_passed(suite)
        assert_equal(len(suite.setup.messages), 1)
        assert_equal(len(suite.teardown.body), 1)

    def test_remove_for_removes_passed_iterations_except_last(self):
        suite, loop = self.suite_with_for_loop()
        last = loop.body[-1]
        self._remove_for_loop(suite)
        assert_equal(len(loop.body), 1)
        assert_true(loop.body[-1] is last)

    def suite_with_for_loop(self):
        suite = TestSuite()
        test = suite.tests.create(status='PASS')
        loop = test.body.create_for(status='PASS')
        for i in range(100):
            loop.body.create_iteration({'${i}': i}, status='PASS')\
                .body.create_keyword(name='k%d' % i, status='PASS')\
                .body.create_message(message='something')
        return suite, loop

    def test_remove_for_does_not_remove_failed_iterations(self):
        suite, loop = self.suite_with_for_loop()
        fail1 = loop.body[42]
        fail2 = loop.body[75]
        last = loop.body[-1]
        fail1.failed = fail2.failed = True
        self._remove_for_loop(suite)
        assert_equal(len(loop.body), 3)
        assert_equal(list(loop.body), [fail1, fail2, last])

    def test_remove_for_does_not_remove_iterations_with_warnings(self):
        suite, loop = self.suite_with_for_loop()
        loop.body[2].body.create_message(message='danger!', level='WARN')
        warn = loop.body[2]
        last = loop.body[-1]
        self._remove_for_loop(suite)
        assert_equal(len(loop.body), 2)
        assert_equal(list(loop.body), [warn, last])

    def test_remove_based_on_multiple_condition(self):
        suite = TestSuite()
        t1 = suite.tests.create(status='PASS')
        t1.body.create_keyword().body.create_message()
        t2 = suite.tests.create(status='FAIL')
        t2.body.create_keyword().body.create_message()
        iteration = t2.body.create_for().body.create_iteration()
        for i in range(10):
            iteration.body.create_keyword(status='PASS')
        self._remove(['passed', 'for'], suite)
        assert_equal(len(t1.body[0].messages), 0)
        assert_equal(len(t2.body[0].messages), 1)
        assert_equal(len(t2.body[1].body), 1)

    def _suite_with_setup_and_teardown_and_test_with_keywords(self):
        suite = TestSuite()
        suite.setup.config(name='S', status='PASS').body.create_message('setup message')
        suite.teardown.config(name='T', status='PASS').body.create_message(message='message')
        test = suite.tests.create()
        test.body.create_keyword().body.create_keyword()
        test.body.create_keyword().body.create_message('kw with message')
        return suite

    def _should_contain_no_messages_or_keywords(self, keyword):
        assert_equal(len(keyword.messages), 0)
        assert_equal(len(keyword.body), 0)

    def _remove(self, option, item):
        item.visit(SuiteConfigurer(remove_keywords=option))

    def _remove_passed(self, item):
        self._remove('PASSED', item)

    def _remove_for_loop(self, item):
        self._remove('FOR', item)


if __name__ == '__main__':
    unittest.main()
