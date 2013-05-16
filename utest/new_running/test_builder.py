import unittest
from os.path import abspath, dirname, normpath, join

from robot.utils.asserts import assert_equals, assert_true
from robot.new_running import TestSuite, TestSuiteBuilder


CURDIR = dirname(abspath(__file__))
DATADIR = normpath(join(CURDIR, '..', '..', 'atest', 'testdata', 'misc'))


class TestBuilding(unittest.TestCase):

    def _build(self, path):
        path = join(DATADIR, path)
        suite = TestSuiteBuilder().build(path)
        assert_true(isinstance(suite, TestSuite))
        assert_equals(suite.source, path)
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
