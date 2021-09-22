import unittest
import warnings

from robot.utils.asserts import (assert_equal, assert_false, assert_not_equal, assert_raises,
                                 assert_raises_with_msg, assert_true)
from robot.model import TestSuite, TestCase, Keyword
from robot.model.testcase import TestCases


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

    def test_source(self):
        test = TestCase()
        assert_equal(test.source, None)
        suite = TestSuite()
        suite.tests.append(test)
        assert_equal(test.source, None)
        suite.tests.append(test)
        suite.source = '/unit/tests'
        assert_equal(test.source, '/unit/tests')

    def test_setup(self):
        assert_equal(self.test.setup.__class__, Keyword)
        assert_equal(self.test.setup.name, None)
        assert_false(self.test.setup)
        self.test.setup.config(name='setup kw')
        assert_equal(self.test.setup.name, 'setup kw')
        assert_true(self.test.setup)
        self.test.setup = None
        assert_equal(self.test.setup.name, None)
        assert_false(self.test.setup)

    def test_teardown(self):
        assert_equal(self.test.teardown.__class__, Keyword)
        assert_equal(self.test.teardown.name, None)
        assert_false(self.test.teardown)
        self.test.teardown.config(name='teardown kw')
        assert_equal(self.test.teardown.name, 'teardown kw')
        assert_true(self.test.teardown)
        self.test.teardown = None
        assert_equal(self.test.teardown.name, None)
        assert_false(self.test.teardown)

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

    def test_copy(self):
        test = self.test
        copy = test.copy()
        assert_equal(test.name, copy.name)
        copy.name += 'copy'
        assert_not_equal(test.name, copy.name)
        assert_equal(id(test.tags), id(copy.tags))

    def test_copy_with_attributes(self):
        test = TestCase(name='Orig', doc='Orig', tags=['orig'])
        copy = test.copy(name='New', doc='New', tags=['new'])
        assert_equal(copy.name, 'New')
        assert_equal(copy.doc, 'New')
        assert_equal(list(copy.tags), ['new'])

    def test_deepcopy_(self):
        test = self.test
        copy = test.deepcopy()
        assert_equal(test.name, copy.name)
        assert_not_equal(id(test.tags), id(copy.tags))

    def test_deepcopy_with_attributes(self):
        copy = TestCase(name='Orig').deepcopy(name='New', doc='New')
        assert_equal(copy.name, 'New')
        assert_equal(copy.doc, 'New')

    def test_keywords_deprecation(self):
        self.test.body = [Keyword(), Keyword(), Keyword()]
        with warnings.catch_warnings(record=True) as w:
            kws = self.test.keywords
            assert_equal(len(kws), 3)
            assert_true('deprecated' in str(w[0].message))
        assert_raises(AttributeError, kws.append, Keyword())
        assert_raises(AttributeError, setattr, self.test, 'keywords', [])


class TestStringRepresentation(unittest.TestCase):

    def setUp(self):
        self.empty = TestCase()
        self.ascii = TestCase(name='Kekkonen')
        self.non_ascii = TestCase(name=u'hyv\xe4 nimi')

    def test_str(self):
        for tc, expected in [(self.empty, ''),
                             (self.ascii, 'Kekkonen'),
                             (self.non_ascii, u'hyv\xe4 nimi')]:
            assert_equal(str(tc), expected)

    def test_repr(self):
        for tc, expected in [(self.empty, "TestCase(name='')"),
                             (self.ascii, "TestCase(name='Kekkonen')"),
                             (self.non_ascii, u"TestCase(name=%r)" % u'hyv\xe4 nimi')]:
            assert_equal(repr(tc), 'robot.model.' + expected)


class TestTestCases(unittest.TestCase):

    def setUp(self):
        self.suite = TestSuite()
        self.tests = TestCases(parent=self.suite,
                               tests=[TestCase(name=c) for c in 'abc'])

    def test_getitem_slice(self):
        tests = self.tests[:]
        assert_true(isinstance(tests, TestCases))
        assert_equal([t.name for t in tests], ['a', 'b', 'c'])
        tests.append(TestCase(name='d'))
        assert_equal([t.name for t in tests], ['a', 'b', 'c', 'd'])
        assert_true(all(t.parent is self.suite for t in tests))
        assert_equal([t.name for t in self.tests], ['a', 'b', 'c'])
        backwards = tests[::-1]
        assert_true(isinstance(tests, TestCases))
        assert_equal(list(backwards), list(reversed(tests)))

    def test_setitem_slice(self):
        tests = self.tests[:]
        tests[-1:] = [TestCase(name='b'), TestCase(name='a')]
        assert_equal([t.name for t in tests], ['a', 'b', 'b', 'a'])
        assert_true(all(t.parent is self.suite for t in tests))
        assert_raises_with_msg(TypeError,
                               'Only TestCase objects accepted, got TestSuite.',
                               tests.__setitem__, slice(0), [self.suite])


if __name__ == '__main__':
    unittest.main()
