from six import text_type as unicode

import sys
import unittest
from robot.utils.asserts import assert_equal, assert_raises

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

    def test_slots(self):
        assert_raises(AttributeError, setattr, self.test, 'attr', 'value')


class TestStringRepresentation(unittest.TestCase):

    def setUp(self):
        self.empty = TestCase()
        self.ascii = TestCase(name='Kekkonen')
        self.non_ascii = TestCase(name=u'hyv\xe4 nimi')

    def test_unicode(self):
        assert_equal(unicode(self.empty), '')
        assert_equal(unicode(self.ascii), 'Kekkonen')
        assert_equal(unicode(self.non_ascii), u'hyv\xe4 nimi')

    if sys.version_info[0] < 3:
        def test_str(self):
            assert_equal(str(self.empty), '')
            assert_equal(str(self.ascii), 'Kekkonen')
            assert_equal(str(self.non_ascii), 'hyv? nimi')

    else:
        def test_bytes(self):
            assert_equal(bytes(self.empty), ''.encode())
            assert_equal(bytes(self.ascii), 'Kekkonen'.encode())
            assert_equal(bytes(self.non_ascii), 'hyv? nimi'.encode())


if __name__ == '__main__':
    unittest.main()
