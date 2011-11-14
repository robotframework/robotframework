import unittest
from robot.utils.asserts import assert_equal, assert_true, assert_raises

from robot.model import TestSuite


class TestTestSuite(unittest.TestCase):

    def setUp(self):
        self.suite = TestSuite(metadata={'M': 'V'})

    def test_modify_medatata(self):
        self.suite.metadata['m'] = 'v'
        self.suite.metadata['n'] = 'w'
        assert_equal(dict(self.suite.metadata), {'M': 'v', 'n': 'w'})

    def test_set_metadata(self):
        self.suite.metadata = {'a': '1', 'b': '1'}
        self.suite.metadata['A'] = '2'
        assert_equal(dict(self.suite.metadata), {'a': '2', 'b': '1'})

    def test_create_and_add_suite(self):
        s1 = self.suite.suites.create(name='s1')
        s2 = TestSuite(name='s2')
        self.suite.suites.append(s2)
        assert_true(s1.parent is self.suite)
        assert_true(s2.parent is self.suite)
        assert_equal(list(self.suite.suites), [s1, s2])

    def test_reset_suites(self):
        s1 = TestSuite(name='s1')
        self.suite.suites = [s1]
        s2 = self.suite.suites.create(name='s2')
        assert_true(s1.parent is self.suite)
        assert_true(s2.parent is self.suite)
        assert_equal(list(self.suite.suites), [s1, s2])

    def test_suite_name(self):
        suite = TestSuite()
        assert_equal(suite.name, '')
        assert_equal(suite.suites.create(name='foo').name, 'foo')
        assert_equal(suite.suites.create(name='bar').name, 'bar')
        assert_equal(suite.name, 'foo & bar')
        assert_equal(suite.suites.create(name='zap').name, 'zap')
        assert_equal(suite.name, 'foo & bar & zap')
        suite.name = 'new name'
        assert_equal(suite.name, 'new name')

    def test_nested_subsuites(self):
        suite = TestSuite(name='top')
        sub1 = suite.suites.create(name='sub1')
        sub2 = sub1.suites.create(name='sub2')
        assert_equal(list(suite.suites), [sub1])
        assert_equal(list(sub1.suites), [sub2])


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
        assert_raises(TypeError, self.sub.set_criticality)

    def test_criticality_set_for_child_suites_earlier_is_ignored(self):
        self.suite.set_criticality('use', 'us')
        sub2 = TestSuite()
        sub2.set_criticality('ignore', 'these')
        self.suite.suites.append(sub2)
        self._verify_criticality(self.suite, ['use'], ['us'])
        self._verify_criticality(self.sub, ['use'], ['us'])
        self._verify_criticality(sub2, ['use'], ['us'])

    def _verify_criticality(self, suite, crit, non_crit):
        assert_equal([unicode(t) for t in suite.criticality.critical_tags], crit)
        assert_equal([unicode(t) for t in suite.criticality.non_critical_tags], non_crit)


class TestSuiteId(unittest.TestCase):

    def test_one_suite(self):
        assert_equal(TestSuite().id, 's1')

    def test_sub_suites(self):
        parent = TestSuite()
        for i in range(10):
            assert_equal(parent.suites.create().id, 's1-s%s' % (i+1))
        assert_equal(parent.suites[-1].suites.create().id, 's1-s10-s1')

    def test_id_is_dynamic(self):
        suite = TestSuite()
        sub = suite.suites.create().suites.create()
        assert_equal(sub.id, 's1-s1-s1')
        suite.suites = [sub]
        assert_equal(sub.id, 's1-s1')


class TestStringRepresentation(unittest.TestCase):

    def setUp(self):
        self.empty = TestSuite()
        self.ascii = TestSuite(name='Kekkonen')
        self.non_ascii = TestSuite(name=u'hyv\xe4 nimi')

    def test_unicode(self):
        assert_equal(unicode(self.empty), '')
        assert_equal(unicode(self.ascii), 'Kekkonen')
        assert_equal(unicode(self.non_ascii), u'hyv\xe4 nimi')

    def test_str(self):
        assert_equal(str(self.empty), '')
        assert_equal(str(self.ascii), 'Kekkonen')
        assert_equal(str(self.non_ascii), 'hyv? nimi')

    def test_repr(self):
        assert_equal(repr(self.empty), "''")
        assert_equal(repr(self.ascii), "'Kekkonen'")
        assert_equal(repr(self.non_ascii), "'hyv? nimi'")


if __name__ == '__main__':
    unittest.main()
