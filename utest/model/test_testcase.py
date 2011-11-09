import unittest
from robot.utils.asserts import assert_equal

from robot.model import TestCase, TestSuite


class TestTestCase(unittest.TestCase):

    def setUp(self):
        self.test = TestCase(tags=['t1', 't2'], name='test')

    def test_id_without_parent(self):
        assert_equal(self.test.id, 't1')

    def test_id_with_parent(self):
        suite = TestSuite()
        suite.suites.create().tests = [TestCase(), TestCase()]
        suite.suites.create().tests = [TestCase()]
        assert_equal(suite.suites[0].tests[0].id, 's1-s1-t1')
        assert_equal(suite.suites[0].tests[1].id, 's1-s1-t2')
        assert_equal(suite.suites[1].tests[0].id, 's1-s2-t1')

    def test_modify_tags(self):
        self.test.tags.add(['t0', 't3'])
        self.test.tags.remove('T2')
        assert_equal(list(self.test.tags), ['t0', 't1', 't3'])

    def test_set_tags(self):
        self.test.tags = ['s2', 's1']
        self.test.tags.add('s3')
        assert_equal(list(self.test.tags), ['s1', 's2', 's3'])

    def test_longname(self):
        assert_equal(self.test.longname, 'test')
        self.test.parent = TestSuite(name='suite').suites.create(name='sub suite')
        assert_equal(self.test.longname, 'suite.sub suite.test')


if __name__ == '__main__':
    unittest.main()
