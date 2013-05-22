import unittest
from StringIO import StringIO

from robot.utils.asserts import assert_equals
from robot.new_running import TestSuite


class TestRunning(unittest.TestCase):

    def test_one_library_keyword(self):
        suite = TestSuite(name='Suite')
        suite.tests.create(name='Test').keywords.create('Log',
                                                        args=['Hello, world!'])
        result = self._run(suite)
        self._check_suite(result, 'Suite', 'PASS')
        self._check_test(result.tests[0], 'Test', 'PASS')

    def test_failing_library_keyword(self):
        suite = TestSuite(name='Suite')
        test = suite.tests.create(name='Test')
        test.keywords.create('Log', args=['Dont fail yet.'])
        test.keywords.create('Fail', args=['Hello, world!'])
        result = self._run(suite)
        self._check_suite(result, 'Suite', 'FAIL')
        self._check_test(result.tests[0], 'Test', 'FAIL', msg='Hello, world!')

    def test_assign(self):
        suite = TestSuite(name='Suite')
        test = suite.tests.create(name='Test')
        test.keywords.create(assign=['${var}'], name='Set Variable', args=['value in variable'])
        test.keywords.create('Fail', args=['${var}'])
        result = self._run(suite)
        self._check_suite(result, 'Suite', 'FAIL')
        self._check_test(result.tests[0], 'Test', 'FAIL', msg='value in variable')

    def test_suites_in_suites(self):
        root = TestSuite(name='Root')
        root.suites.create(name='Child')\
            .tests.create(name='Test')\
            .keywords.create('Log', args=['Hello, world!'])
        result = self._run(root)
        self._check_suite(result, 'Root', 'PASS', tests=0)
        self._check_suite(result.suites[0], 'Child', 'PASS')
        self._check_test(result.suites[0].tests[0], 'Test', 'PASS')

    def test_imports(self):
        suite = TestSuite(name='Suite')
        suite.imports.create('Library', 'OperatingSystem')
        suite.tests.create(name='Test').keywords.create('Directory Should Exist',
                                                        args=['.'])
        result = self._run(suite)
        self._check_suite(result, 'Suite', 'PASS')
        self._check_test(result.tests[0], 'Test', 'PASS')

    def test_user_keywords(self):
        suite = TestSuite(name='Suite')
        suite.tests.create(name='Test').keywords.create('User keyword', args=['From uk'])
        uk = suite.user_keywords.create(name='User keyword', args=['${msg}'])
        uk.keywords.create(name='Fail', args=['${msg}'])
        result = self._run(suite)
        self._check_suite(result, 'Suite', 'FAIL')
        self._check_test(result.tests[0], 'Test', 'FAIL', msg='From uk')

    def test_variables(self):
        suite = TestSuite(name='Suite')
        suite.variables.create('${ERROR}', 'Error message')
        suite.variables.create('@{LIST}', ['Error', 'added tag'])
        suite.tests.create(name='T1').keywords.create('Fail', args=['${ERROR}'])
        suite.tests.create(name='T2').keywords.create('Fail', args=['@{LIST}'])
        result = self._run(suite)
        self._check_suite(result, 'Suite', 'FAIL', tests=2)
        self._check_test(result.tests[0], 'T1', 'FAIL', msg='Error message')
        self._check_test(result.tests[1], 'T2', 'FAIL', ('added tag',), 'Error')

    def _run(self, suite):
        result = suite.run(output='NONE', stdout=StringIO(), stderr=StringIO())
        return result.suite

    def _check_suite(self, suite, name, status, tests=1):
        assert_equals(suite.name, name)
        assert_equals(suite.status, status)
        assert_equals(len(suite.tests), tests)

    def _check_test(self, test, name, status, tags=(), msg=''):
        assert_equals(test.name, name)
        assert_equals(test.status, status)
        assert_equals(test.message, msg)
        assert_equals(tuple(test.tags), tags)
