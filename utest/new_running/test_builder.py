import unittest
from os.path import abspath, dirname, normpath, join

from robot.utils.asserts import assert_equals, assert_true
from robot.new_running import TestSuite, TestSuiteBuilder


CURDIR = dirname(abspath(__file__))
DATADIR = normpath(join(CURDIR, '..', '..', 'atest', 'testdata', 'misc'))


class TestBuilding(unittest.TestCase):

    def _build(self, *paths):
        paths = [join(DATADIR, p) for p in paths]
        suite = TestSuiteBuilder().build(*paths)
        assert_true(isinstance(suite, TestSuite))
        assert_equals(suite.source, paths[0] if len(paths) == 1 else '')
        return suite

    def test_suite_data(self):
        suite = self._build('pass_and_fail.txt')
        assert_equals(suite.name, 'Pass And Fail')
        assert_equals(suite.doc, 'Some tests here')
        assert_equals(suite.metadata, {})

    def test_imports(self):
        imp = self._build('dummy_lib_test.txt').imports[0]
        assert_equals(imp.type, 'Library')
        assert_equals(imp.name, 'DummyLib')
        assert_equals(imp.args, ())

    def test_variables(self):
        variables = self._build('pass_and_fail.txt').variables
        assert_equals(variables[0].name, '${LEVEL1}')
        assert_equals(variables[0].value, 'INFO')
        assert_equals(variables[1].name, '${LEVEL2}')
        assert_equals(variables[1].value, 'DEBUG')

    def test_user_keywords(self):
        uk = self._build('pass_and_fail.txt').user_keywords[0]
        assert_equals(uk.name, 'My Keyword')
        assert_equals(uk.args, ('${who}',))

    def test_test_data(self):
        test = self._build('pass_and_fail.txt').tests[1]
        assert_equals(test.name, 'Fail')
        assert_equals(test.doc, 'FAIL Expected failure')
        assert_equals(list(test.tags), ['fail', 'force'])

    def test_test_keywords(self):
        kw = self._build('pass_and_fail.txt').tests[0].keywords[0]
        assert_equals(kw.name, 'My Keyword')
        assert_equals(kw.args, ('Pass',))
        assert_equals(kw.assign, ())
        assert_equals(kw.type, kw.KEYWORD_TYPE)

    def test_directory_suite(self):
        suite = self._build('suites')
        assert_equals(suite.name, 'Suites')
        assert_equals(suite.suites[1].name, 'Subsuites')
        assert_equals(suite.suites[-1].name, 'Tsuite3')
        assert_equals(suite.suites[1].suites[1].name, 'Sub2')
        assert_equals(len(suite.suites[1].suites[1].tests), 1)
        assert_equals(suite.suites[1].suites[1].tests[0].id, 's1-s2-s2-t1')

    def test_multiple_inputs(self):
        suite = self._build('pass_and_fail.txt', 'normal.txt')
        assert_equals(suite.name, 'Pass And Fail & Normal')
        assert_equals(suite.suites[0].name, 'Pass And Fail')
        assert_equals(suite.suites[1].name, 'Normal')
        assert_equals(suite.suites[1].tests[1].id, 's1-s2-t2')
