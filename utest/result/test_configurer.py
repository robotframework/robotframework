import unittest
from robot.utils.asserts import assert_equal

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


if __name__ == '__main__':
    unittest.main()
