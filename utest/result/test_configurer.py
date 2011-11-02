from itertools import chain
import unittest
from robot.utils.asserts import assert_equal, assert_true

from robot.result.model import TestSuite, TestCase
from robot.result.configurer import SuiteConfigurer


class TestSuiteAttributes(unittest.TestCase):

    def setUp(self):
        self.suite = TestSuite(name='Suite', metadata={'A A': '1', 'bb': '1'})

    def test_name_and_doc(self):
        SuiteConfigurer(name='New Name', doc='New Doc').configure(self.suite)
        assert_equal(self.suite.name, 'New Name')
        assert_equal(self.suite.doc, 'New Doc')

    def test_metadata(self):
        SuiteConfigurer(metadata={'bb': '2', 'C': '2'}).configure(self.suite)
        assert_equal(self.suite.metadata, {'A A': '1', 'bb': '2', 'C': '2'})

    def test_metadata_is_normalized(self):
        SuiteConfigurer(metadata={'aa': '2', 'B_B': '2'}).configure(self.suite)
        assert_equal(self.suite.metadata, {'A A': '2', 'bb': '2'})


class TestTestAttributes(unittest.TestCase):

    def setUp(self):
        self.suite = TestSuite()
        self.suite.tests = [TestCase()]
        self.suite.suites = [TestSuite()]
        self.suite.suites[0].tests = [TestCase(tags=['tag'])]

    def test_set_tags(self):
        SuiteConfigurer(set_tags=['new']).configure(self.suite)
        assert_equal(list(self.suite.tests[0].tags), ['new'])
        assert_equal(list(self.suite.suites[0].tests[0].tags), ['new', 'tag'])

    def test_tags_are_normalized(self):
        SuiteConfigurer(set_tags=['TAG', '', 't a g', 'NONE']).configure(self.suite)
        assert_equal(list(self.suite.tests[0].tags), ['TAG'])
        assert_equal(list(self.suite.suites[0].tests[0].tags), ['tag'])

    def test_remove_negative_tags(self):
        SuiteConfigurer(set_tags=['n', '-TAG']).configure(self.suite)
        assert_equal(list(self.suite.tests[0].tags), ['n'])
        assert_equal(list(self.suite.suites[0].tests[0].tags), ['n'])

    def test_remove_negative_tags_using_pattern(self):
        SuiteConfigurer(set_tags=['-t*', '-nomatch']).configure(self.suite)
        assert_equal(list(self.suite.tests[0].tags), [])
        assert_equal(list(self.suite.suites[0].tests[0].tags), [])


class TestFilteringByTags(unittest.TestCase):

    def setUp(self):
        self.suite = TestSuite(name='root')
        self.suite.tests = [TestCase(name='n0'), TestCase(name='n1', tags=['t1']),
                            TestCase(name='n2', tags=['t1', 't2'])]
        self.suite.suites.create(name='sub').tests.create(name='n1', tags=['t1'])

    def test_include(self):
        SuiteConfigurer(include_tags=['t1', 'none', '', '?2']).configure(self.suite)
        assert_equal([t.name for t in self.suite.tests], ['n1', 'n2'])
        assert_equal([t.name for t in self.suite.suites[0].tests], ['n1'])

    def test_exclude(self):
        SuiteConfigurer(exclude_tags=['t1', '?1ANDt2']).configure(self.suite)
        assert_equal([t.name for t in self.suite.tests], ['n0'])
        assert_equal(list(self.suite.suites), [])

    def test_include_by_names(self):
        SuiteConfigurer(include_suites=['s?b', 'xxx'],
                        include_tests=['', '*1', 'xxx']).configure(self.suite)
        assert_equal(list(self.suite.tests), [])
        assert_equal([t.name for t in self.suite.suites[0].tests], ['n1'])


class TestRemoveKeywords(unittest.TestCase):

    def test_remove_all_removes_all(self):
        suite = self._suite_with_setup_and_teardown_and_test_with_keywords()
        self._remove('ALL', suite)
        for keyword in chain(suite.keywords, suite.tests[0].keywords):
            self._should_contain_no_messages_or_keywords(keyword)

    def test_remove_passed_removes_from_passed_test(self):
        suite = TestSuite()
        test = suite.tests.create(status='PASS')
        test.keywords.create(status='PASS').messages.create(message='keyword message')
        test.keywords.create(status='PASS').keywords.create(status='PASS')
        self._remove_passed(suite)
        for keyword in test.keywords:
            self._should_contain_no_messages_or_keywords(keyword)

    def test_remove_passed_removes_setup_and_teardown_from_passed_suite(self):
        suite = TestSuite()
        suite.tests.create(status='PASS')
        suite.keywords.create(status='PASS', type='setup').keywords.create()
        suite.keywords.create(status='PASS', type='teardown').messages.create(message='message')
        self._remove_passed(suite)
        for keyword in suite.keywords:
            self._should_contain_no_messages_or_keywords(keyword)

    def test_remove_passed_does_not_remove_when_test_failed(self):
        suite = TestSuite()
        test = suite.tests.create(status='FAIL')
        test.keywords.create(status='PASS').keywords.create()
        test.keywords.create(status='PASS').messages.create(message='message')
        failed_keyword = test.keywords.create(status='FAIL')
        failed_keyword.messages.create('mess')
        failed_keyword.keywords.create()
        self._remove_passed(suite)
        assert_equal(len(test.keywords[0].keywords), 1)
        assert_equal(len(test.keywords[1].messages), 1)
        assert_equal(len(test.keywords[2].messages), 1)
        assert_equal(len(test.keywords[2].keywords), 1)

    def test_remove_passed_does_not_remove_when_test_contains_warning(self):
        suite = TestSuite()
        test = self._test_with_warning(suite)
        self._remove_passed(suite)
        assert_equal(len(test.keywords[0].keywords), 1)
        assert_equal(len(test.keywords[1].messages), 1)

    def _test_with_warning(self, suite):
        test = suite.tests.create(status='PASS')
        test.keywords.create(status='PASS').keywords.create()
        test.keywords.create(status='PASS').messages.create(message='danger!',
                                                            level='WARN')
        return test

    def test_remove_passed_does_not_remove_setup_and_teardown_from_failed_suite(self):
        suite = TestSuite()
        suite.keywords.create(type='setup').messages.create(message='some')
        suite.keywords.create(type='teardown').keywords.create()
        suite.tests.create(status='FAIL')
        self._remove_passed(suite)
        assert_equal(len(suite.keywords.setup.messages), 1)
        assert_equal(len(suite.keywords.teardown.keywords), 1)

    def test_remove_passed_does_now_remove_setup_and_teardown_from_suite_with_noncritical_failure(self):
        suite = TestSuite()
        suite.keywords.create(type='setup').messages.create(message='some')
        suite.keywords.create(type='teardown').keywords.create()
        #FIXME!: Possible bug in test as critical='no' does not work .. and default value is 'yes'
        suite.tests.create(status='FAIL', critical=False)
        assert_equal(suite.status, 'PASS')
        self._remove_passed(suite)
        assert_equal(len(suite.keywords.setup.messages), 1)
        assert_equal(len(suite.keywords.teardown.keywords), 1)

    def test_remove_for_removes_for_loop_items_when_item_is_passed(self):
        suite, forloop = self.suite_with_forloop()
        self._remove('FOR', suite)
        assert_equal(len(forloop.keywords), 0)

    def suite_with_forloop(self):
        suite = TestSuite()
        test = suite.tests.create(status='PASS')
        forloop = test.keywords.create(status='PASS', type='for')
        for i in range(100):
            forloop.keywords.create(status='PASS',
                                    type='foritem').messages.create(
                message='something')
        return suite, forloop

    def test_remove_for_does_not_remove_for_loop_items_when_item_fails(self):
        suite, forloop = self.suite_with_forloop()
        suite.tests[0].keywords.create(status='FAIL')
        suite.tests[0].status = 'FAIL'
        self._remove('FOR', suite)
        assert_equal(len(forloop.keywords), 100)

    def test_remove_for_does_not_remove_for_loop_items_when_warning_message_in_test(self):
        suite, forloop = self.suite_with_forloop()
        forloop.keywords[2].messages.create(message='danger!', level='WARN')
        self._remove('FOR', suite)
        assert_equal(len(forloop.keywords), 100)

    def _suite_with_setup_and_teardown_and_test_with_keywords(self):
        suite = TestSuite()
        suite.keywords.create(type='setup').messages.create('setup message')
        suite.keywords.create(type='teardown').messages.create(
            'teardown message')
        test = suite.tests.create()
        test.keywords.create().keywords.create()
        test.keywords.create().messages.create('kw with message')
        return suite

    def _should_contain_no_messages_or_keywords(self, keyword):
        assert_equal(len(keyword.messages), 0)
        assert_equal(len(keyword.keywords), 0)

    def _remove(self, option, item):
        SuiteConfigurer(remove_keywords=option).configure(item)

    def _remove_passed(self, item):
        self._remove('PASSED', item)


if __name__ == '__main__':
    unittest.main()
