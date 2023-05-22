import unittest
import warnings
from pathlib import Path

from robot.model import TestSuite
from robot.running import TestSuite as RunningTestSuite
from robot.result import TestSuite as ResultTestSuite
from robot.utils.asserts import (assert_equal, assert_true, assert_raises,
                                 assert_raises_with_msg)


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

    def test_name_from_source(self):
        for inp, exp in [(None, ''), ('', ''), ('name', 'Name'), ('name.robot', 'Name'),
                         ('naMe', 'naMe'), ('na_me', 'Na Me'), ('na_M_e_', 'na M e'),
                         ('prefix__name', 'Name'), ('__n', 'N'), ('naMe__', 'naMe')]:
            assert_equal(TestSuite.name_from_source(inp), exp)
            suite = TestSuite(source=inp)
            assert_equal(suite.name, exp)
            suite.suites.create(name='xxx')
            assert_equal(suite.name, exp or 'xxx')
            suite.name = 'new name'
            assert_equal(suite.name, 'new name')
            if inp:
                assert_equal(TestSuite(source=Path(inp)).name, exp)
                assert_equal(TestSuite(source=Path(inp).resolve()).name, exp)

    def test_name_from_source_with_extensions(self):
        for ext, exp in [('z', 'X.Y'), ('.z', 'X.Y'), ('y.z', 'X'),
                         (['x', 'y', 'z'], 'X.Y')]:
            assert_equal(TestSuite.name_from_source('x.y.z', ext), exp)

    def test_name_from_source_with_bad_extensions(self):
        assert_raises_with_msg(
            ValueError,
            "File 'x.y' does not have extension 'z'.",
            TestSuite.name_from_source, 'x.y', extension='z'
        )
        assert_raises_with_msg(
            ValueError,
            "File 'x.y' does not have extension 'a', 'b' or 'c'.",
            TestSuite.name_from_source, 'x.y', ('a', 'b', 'c')
        )

    def test_suite_name_from_child_suites(self):
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

    def test_set_tags(self):
        suite = TestSuite()
        suite.tests.create()
        suite.tests.create(tags=['t1', 't2'])
        suite.set_tags(add='a', remove=['t2', 'nonex'])
        suite.tests.create()
        assert_equal(list(suite.tests[0].tags), ['a'])
        assert_equal(list(suite.tests[1].tags), ['a', 't1'])
        assert_equal(list(suite.tests[2].tags), [])

    def test_set_tags_also_to_new_child(self):
        suite = TestSuite()
        suite.tests.create()
        suite.set_tags(add='a', remove=['t2', 'nonex'], persist=True)
        suite.tests.create(tags=['t1', 't2'])
        suite.tests = list(suite.tests)
        suite.tests.create()
        suite.suites.create().tests.create()
        assert_equal(list(suite.tests[0].tags), ['a'])
        assert_equal(list(suite.tests[1].tags), ['a', 't1'])
        assert_equal(list(suite.tests[2].tags), ['a'])
        assert_equal(list(suite.suites[0].tests[0].tags), ['a'])

    def test_all_tests_and_test_count(self):
        root = TestSuite()
        assert_equal(root.test_count, 0)
        assert_equal(list(root.all_tests), [])
        for i in range(10):
            suite = root.suites.create()
            for j in range(100):
                suite.tests.create()
        assert_equal(root.test_count, 1000)
        assert_equal(len(list(root.all_tests)), 1000)
        assert_equal(list(root.suites[0].all_tests), list(root.suites[0].tests))

    def test_configure_only_works_with_root_suite(self):
        for Suite in TestSuite, RunningTestSuite, ResultTestSuite:
            root = Suite()
            child = root.suites.create()
            child.tests.create()
            root.configure(name='Configured')
            assert_equal(root.name, 'Configured')
            assert_raises_with_msg(
                ValueError, "'TestSuite.configure()' can only be used with "
                "the root test suite.", child.configure, name='Bang'
            )

    def test_slots(self):
        assert_raises(AttributeError, setattr, self.suite, 'attr', 'value')

    def test_keywords_deprecation(self):
        self.suite.setup.config(name='S')
        with warnings.catch_warnings(record=True) as w:
            kws = self.suite.keywords
            assert_equal(len(kws), 1)
            assert_true('deprecated' in str(w[0].message))
        assert_raises(AttributeError, kws.extend, ())
        assert_raises(AttributeError, setattr, self.suite, 'keywords', [])


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

    def test_str(self):
        for tc, expected in [(self.empty, ''),
                             (self.ascii, 'Kekkonen'),
                             (self.non_ascii, u'hyv\xe4 nimi')]:
            assert_equal(str(tc), expected)

    def test_repr(self):
        for tc, expected in [(self.empty, "TestSuite(name='')"),
                             (self.ascii, "TestSuite(name='Kekkonen')"),
                             (self.non_ascii, u"TestSuite(name=%r)" % u'hyv\xe4 nimi')]:
            assert_equal(repr(tc), 'robot.model.' + expected)


if __name__ == '__main__':
    unittest.main()
