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

    def setUp(self):
        self._main_suite = TestSuite()
        self._create_pass_and_fail()
        self._create_setup_fail()
        self._create_teardown_fail()

    def _create_pass_and_fail(self):
        self._pass_and_fail = self._main_suite.suites.create()
        self._keyword(self._pass_and_fail.tests.create(status='PASS'))
        failing_test = self._pass_and_fail.tests.create(status='FAIL')
        self._keyword(failing_test, status='PASS')
        self._keyword(failing_test, status='FAIL')

    def _keyword(self, parent, status=None):
        kw = parent.keywords.create(status=status or parent.status)
        kw.keywords.create(status=status or parent.status)
        kw.messages.create('something')
        return kw

    def _create_setup_fail(self):
        self._setup_fail = self._main_suite.suites.create()
        self._keyword(self._setup_fail, status='FAIL').type = 'setup'
        self._setup_fail.tests.create(status='FAIL')

    def _create_teardown_fail(self):
        self._teardown_fail = self._main_suite.suites.create()
        self._keyword(self._teardown_fail.tests.create(status='PASS'))
        self._keyword(self._teardown_fail, status='FAIL').type = 'teardown'

    def test_remove_all_keywords_removes_all_keywords(self):
        self._remove_all()
        for keyword in [self._pass_and_fail.tests[0].keywords[0],
                        self._pass_and_fail.tests[1].keywords[0],
                        self._pass_and_fail.tests[1].keywords[1],
                        self._setup_fail.keywords.setup,
                        self._teardown_fail.tests[0].keywords[0],
                        self._teardown_fail.keywords.teardown]:
            self._should_have_no_messages_or_keywords(keyword)


    def _should_have_no_messages_or_keywords(self, keyword):
        assert_equal(list(keyword.messages), [])
        assert_equal(list(keyword.keywords), [])

    def _remove_all(self):
        SuiteConfigurer(remove_keywords='ALL').configure(self._main_suite)

    def test_remove_passed_keywords_removes_messages_and_keywords_from_passed(self):
        self._remove_passed()
        for keyword in [self._pass_and_fail.tests[0].keywords[0],
                        self._teardown_fail.tests[0].keywords[0]]:
            self._should_have_no_messages_or_keywords(keyword)
        for keyword in [self._pass_and_fail.tests[1].keywords[0],
                        self._pass_and_fail.tests[1].keywords[1],
                        self._setup_fail.keywords.setup,
                        self._teardown_fail.keywords.teardown]:
            self._should_have_message_and_keyword(keyword)


    def _remove_passed(self):
        SuiteConfigurer(remove_keywords='PASSED').configure(self._main_suite)

    def _should_have_message_and_keyword(self, keyword):
        assert_equal(len(keyword.messages), 1)
        assert_equal(len(keyword.keywords), 1)

    def test_remove_nothing_removes_nothing(self):
        self._remove_nothing()
        for item in chain(self._pass_and_fail.tests, self._teardown_fail.tests,
                          [self._setup_fail, self._teardown_fail]):
            for keyword in item.keywords:
                self._should_have_message_and_keyword(keyword)

    def _remove_nothing(self):
        SuiteConfigurer(remove_keywords=None).configure(self._main_suite)



if __name__ == '__main__':
    unittest.main()
