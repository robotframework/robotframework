import unittest
from robot.utils.asserts import assert_equal, assert_true

from robot.result.model import *


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
        self.suite.suites.add(s2)
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

    def test_stats(self):
        suite = self._create_suite_with_tests()
        assert_equal(suite.critical_stats.passed, 2)
        assert_equal(suite.critical_stats.failed, 1)
        assert_equal(suite.all_stats.passed, 3)
        assert_equal(suite.all_stats.failed, 2)

    def test_nested_suite_stats(self):
        suite = TestSuite()
        suite.suites = [self._create_suite_with_tests(),
                        self._create_suite_with_tests()]
        assert_equal(suite.critical_stats.passed, 4)
        assert_equal(suite.critical_stats.failed, 2)
        assert_equal(suite.all_stats.passed, 6)
        assert_equal(suite.all_stats.failed, 4)

    def _create_suite_with_tests(self):
        suite = TestSuite()
        suite.tests = [TestCase(status='PASS'),
                       TestCase(status='PASS'),
                       TestCase(status='PASS', critical=False),
                       TestCase(status='FAIL'),
                       TestCase(status='FAIL', critical=False)]
        return suite


class TestTestCase(unittest.TestCase):

    def setUp(self):
        self.test = TestCase(tags=['t1', 't2'])

    def test_modify_tags(self):
        self.test.tags.add(['t0', 't3'])
        self.test.tags.remove('T2')
        assert_equal(list(self.test.tags), ['t0', 't1', 't3'])

    def test_set_tags(self):
        self.test.tags = ['s2', 's1']
        self.test.tags.add('s3')
        assert_equal(list(self.test.tags), ['s1', 's2', 's3'])


class TestItemLists(unittest.TestCase):

    def test_create_suite(self):
        parent = object()
        suites = TestSuites(parent)
        suite = suites.create(name='New')
        assert_true(isinstance(suite, TestSuite))
        assert_true(suite.parent is parent)
        assert_equal(suite.name, 'New')
        assert_equal(list(suites), [suite])

    def test_create_test(self):
        parent = object()
        tests = TestCases(parent)
        test = tests.create(tags=['tag'])
        assert_true(isinstance(test, TestCase))
        assert_true(test.parent is parent)
        assert_equal(list(test.tags), ['tag'])
        assert_equal(list(tests), [test])

    def test_create_keyword(self):
        parent = object()
        kws = Keywords(parent)
        kw = kws.create(name='KW')
        assert_true(isinstance(kw, Keyword))
        assert_true(kw.parent is parent)
        assert_equal(kw.name, 'KW')
        assert_equal(list(kws), [kw])

    def test_add(self):
        kw = Keyword()
        parent = object()
        kws = Keywords(parent)
        kws.add(kw)
        assert_true(kw.parent is parent)
        assert_equal(list(kws), [kw])

    def test_initial_values(self):
        kw1 = Keyword()
        kw2 = Keyword()
        parent = object()
        kws = Keywords(parent, [kw1, kw2])
        assert_true(kw1.parent is parent)
        assert_true(kw2.parent is parent)
        assert_equal(list(kws), [kw1, kw2])

    def test_getitem(self):
        kw1 = Keyword()
        kw2 = Keyword()
        kws = Keywords(None, [kw1, kw2])
        assert_true(kws[0] is kw1)
        assert_true(kws[1] is kw2)
        assert_true(kws[-1] is kw2)

    def test_len(self):
        kws = Keywords(None)
        assert_equal(len(kws), 0)
        kws.create()
        assert_equal(len(kws), 1)


class TestMetadata(unittest.TestCase):

    def test_normalizetion(self):
        md = Metadata([('m1', 1), ('M2', 1), ('m_3', 1), ('M1', 2), ('M 3', 2)])
        assert_equal(dict(md), {'m1': 2, 'M2': 1, 'm_3': 2})

    def test_unicode(self):
        assert_equal(unicode(Metadata()), '{}')
        d = {'a': 1, 'B': 'two', u'\xe4': u'nelj\xe4'}
        assert_equal(unicode(Metadata(d)), u'{a: 1, B: two, \xe4: nelj\xe4}')


class TestTags(unittest.TestCase):

    def test_empty_init(self):
        assert_equal(list(Tags()), [])

    def test_init_with_string(self):
        assert_equal(list(Tags('string')), ['string'])

    def test_init_with_iterable_and_normalization_and_sorting(self):
        for inp in [['T 1', 't2', 't_3'],
                    ('t2', 'T 1', 't_3'),
                    ('t2', 'T 2', '__T__2__', 'T 1', 't1', 't_1', 't_3', 't3'),
                    ('', 'T 1', '', 't2', 't_3', 'NONE')]:
            assert_equal(list(Tags(inp)), ['T 1', 't2', 't_3'])

    def test_add_string(self):
        tags = Tags(['Y'])
        tags.add('x')
        assert_equal(list(tags), ['x', 'Y'])

    def test_add_iterable(self):
        tags = Tags(['A'])
        tags.add(('b b', '', 'a', 'NONE'))
        tags.add(Tags(['BB', 'C']))
        assert_equal(list(tags), ['A', 'b b', 'C'])

    def test_remove_string(self):
        tags = Tags(['a', 'B B'])
        tags.remove('a')
        assert_equal(list(tags), ['B B'])
        tags.remove('bb')
        assert_equal(list(tags), [])

    def test_remove_non_existing(self):
        tags = Tags(['a'])
        tags.remove('nonex')
        assert_equal(list(tags), ['a'])

    def test_remove_iterable(self):
        tags = Tags(['a', 'B B'])
        tags.remove(['nonex', '', 'A'])
        tags.remove(Tags('__B_B__'))
        assert_equal(list(tags), [])

    def test_remove_using_pattern(self):
        tags = Tags(['t1', 't2', '1', '1more'])
        tags.remove('?2')
        assert_equal(list(tags), ['1', '1more', 't1'])
        tags.remove('*1*')
        assert_equal(list(tags), [])

    def test_add_and_remove_none(self):
        tags = Tags(['t'])
        tags.add(None)
        tags.remove(None)
        assert_equal(list(tags), ['t'])

    def test_contains(self):
        assert_true('a' in Tags(['a', 'b']))
        assert_true('c' not in Tags(['a', 'b']))
        assert_true('AA' in Tags(['a_a', 'b']))

    def test_contains_pattern(self):
        assert_true('a*' in Tags(['a', 'b']))
        assert_true('a*' in Tags(['u2', 'abba']))
        assert_true('a?' not in Tags(['a', 'abba']))

    def test_length(self):
        assert_equal(len(Tags()), 0)
        assert_equal(len(Tags(['a', 'b'])), 2)

    def test_truth(self):
        assert_true(not Tags())
        assert_true(Tags(['a']))

    def test_unicode(self):
        assert_equal(unicode(Tags()), '[]')
        assert_equal(unicode(Tags(['y', "X'X"])), "[X'X, y]")
        assert_equal(unicode(Tags([u'\xe4', 'a'])), u'[a, \xe4]')

    def test_str(self):
        assert_equal(str(Tags()), '[]')
        assert_equal(str(Tags(['y', "X'X"])), "[X'X, y]")
        assert_equal(str(Tags([u'\xe4', 'a'])), '[a, \xc3\xa4]')


if __name__ == '__main__':
    unittest.main()
