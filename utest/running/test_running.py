import unittest
from StringIO import StringIO
from os.path import abspath, dirname, normpath, join

from robot.utils.asserts import assert_equals
from robot.running import TestSuite, TestSuiteBuilder


CURDIR = dirname(abspath(__file__))
DATADIR = normpath(join(CURDIR, '..', '..', 'atest', 'testdata', 'misc'))


def run(suite, **kwargs):
    result = suite.run(output='NONE', stdout=StringIO(), stderr=StringIO(),
                       **kwargs)
    return result.suite


def build(path):
    return TestSuiteBuilder().build(join(DATADIR, path))


def assert_suite(suite, name, status, message='', tests=1):
    assert_equals(suite.name, name)
    assert_equals(suite.status, status)
    assert_equals(suite.message, message)
    assert_equals(len(suite.tests), tests)


def assert_test(test, name, status, tags=(), msg=''):
    assert_equals(test.name, name)
    assert_equals(test.status, status)
    assert_equals(test.message, msg)
    assert_equals(tuple(test.tags), tags)


class TestRunning(unittest.TestCase):

    def test_one_library_keyword(self):
        suite = TestSuite(name='Suite')
        suite.tests.create(name='Test').keywords.create('Log',
                                                        args=['Hello, world!'])
        result = run(suite)
        assert_suite(result, 'Suite', 'PASS')
        assert_test(result.tests[0], 'Test', 'PASS')

    def test_failing_library_keyword(self):
        suite = TestSuite(name='Suite')
        test = suite.tests.create(name='Test')
        test.keywords.create('Log', args=['Dont fail yet.'])
        test.keywords.create('Fail', args=['Hello, world!'])
        result = run(suite)
        assert_suite(result, 'Suite', 'FAIL')
        assert_test(result.tests[0], 'Test', 'FAIL', msg='Hello, world!')

    def test_assign(self):
        suite = TestSuite(name='Suite')
        test = suite.tests.create(name='Test')
        test.keywords.create(assign=['${var}'], name='Set Variable', args=['value in variable'])
        test.keywords.create('Fail', args=['${var}'])
        result = run(suite)
        assert_suite(result, 'Suite', 'FAIL')
        assert_test(result.tests[0], 'Test', 'FAIL', msg='value in variable')

    def test_suites_in_suites(self):
        root = TestSuite(name='Root')
        root.suites.create(name='Child')\
            .tests.create(name='Test')\
            .keywords.create('Log', args=['Hello, world!'])
        result = run(root)
        assert_suite(result, 'Root', 'PASS', tests=0)
        assert_suite(result.suites[0], 'Child', 'PASS')
        assert_test(result.suites[0].tests[0], 'Test', 'PASS')

    def test_imports(self):
        suite = TestSuite(name='Suite')
        suite.imports.create('Library', 'OperatingSystem')
        suite.tests.create(name='Test').keywords.create('Directory Should Exist',
                                                        args=['.'])
        result = run(suite)
        assert_suite(result, 'Suite', 'PASS')
        assert_test(result.tests[0], 'Test', 'PASS')

    def test_user_keywords(self):
        suite = TestSuite(name='Suite')
        suite.tests.create(name='Test').keywords.create('User keyword', args=['From uk'])
        uk = suite.user_keywords.create(name='User keyword', args=['${msg}'])
        uk.keywords.create(name='Fail', args=['${msg}'])
        result = run(suite)
        assert_suite(result, 'Suite', 'FAIL')
        assert_test(result.tests[0], 'Test', 'FAIL', msg='From uk')

    def test_variables(self):
        suite = TestSuite(name='Suite')
        suite.variables.create('${ERROR}', 'Error message')
        suite.variables.create('@{LIST}', ['Error', 'added tag'])
        suite.tests.create(name='T1').keywords.create('Fail', args=['${ERROR}'])
        suite.tests.create(name='T2').keywords.create('Fail', args=['@{LIST}'])
        result = run(suite)
        assert_suite(result, 'Suite', 'FAIL', tests=2)
        assert_test(result.tests[0], 'T1', 'FAIL', msg='Error message')
        assert_test(result.tests[1], 'T2', 'FAIL', ('added tag',), 'Error')


class TestTestSetupAndTeardown(unittest.TestCase):

    def setUp(self):
        self.tests = run(build('setups_and_teardowns.txt')).tests

    def test_passing_setup_and_teardown(self):
        assert_test(self.tests[0], 'Test with setup and teardown', 'PASS')

    def test_failing_setup(self):
        assert_test(self.tests[1], 'Test with failing setup', 'FAIL',
                    msg='Setup failed:\nTest Setup')

    def test_failing_teardown(self):
        assert_test(self.tests[2], 'Test with failing teardown', 'FAIL',
                    msg='Teardown failed:\nTest Teardown')

    def test_failing_test_with_failing_teardown(self):
        assert_test(self.tests[3], 'Failing test with failing teardown', 'FAIL',
                    msg='Keyword\n\nAlso teardown failed:\nTest Teardown')


class TestSuiteSetupAndTeardown(unittest.TestCase):

    def setUp(self):
        self.suite = build('setups_and_teardowns.txt')

    def test_passing_setup_and_teardown(self):
        suite = run(self.suite)
        assert_suite(suite, 'Setups And Teardowns', 'FAIL', tests=4)
        assert_test(suite.tests[0], 'Test with setup and teardown', 'PASS')

    def test_failing_setup(self):
        suite = run(self.suite, variable='SUITE SETUP:Fail')
        assert_suite(suite, 'Setups And Teardowns', 'FAIL',
                     'Suite setup failed:\nAssertionError', 4)
        assert_test(suite.tests[0], 'Test with setup and teardown', 'FAIL',
                    msg='Parent suite setup failed:\nAssertionError')

    def test_failing_teardown(self):
        suite = run(self.suite, variable='SUITE TEARDOWN:Fail')
        assert_suite(suite, 'Setups And Teardowns', 'FAIL',
                     'Suite teardown failed:\nAssertionError', 4)
        assert_test(suite.tests[0], 'Test with setup and teardown', 'FAIL',
                    msg='Parent suite teardown failed:\nAssertionError')

    def test_failing_test_with_failing_teardown(self):
        suite = run(self.suite, variable=['SUITE SETUP:Fail', 'SUITE TEARDOWN:Fail'])
        assert_suite(suite, 'Setups And Teardowns', 'FAIL',
                     'Suite setup failed:\nAssertionError\n\n'
                     'Also suite teardown failed:\nAssertionError', 4)
        assert_test(suite.tests[0], 'Test with setup and teardown', 'FAIL',
                    msg='Parent suite setup failed:\nAssertionError\n\n'
                        'Also parent suite teardown failed:\nAssertionError')

    def test_nested_setups_and_teardowns(self):
        root = TestSuite(name='Root')
        root.keywords.create('Fail', ['Top level'], type='teardown')
        root.suites.append(self.suite)
        suite = run(root, variable=['SUITE SETUP:Fail', 'SUITE TEARDOWN:Fail'])
        assert_suite(suite, 'Root', 'FAIL',
                     'Suite teardown failed:\nTop level', 0)
        assert_suite(suite.suites[0], 'Setups And Teardowns', 'FAIL',
                     'Suite setup failed:\nAssertionError\n\n'
                     'Also suite teardown failed:\nAssertionError', 4)
        assert_test(suite.suites[0].tests[0], 'Test with setup and teardown', 'FAIL',
                    msg='Parent suite setup failed:\nAssertionError\n\n'
                        'Also parent suite teardown failed:\nAssertionError\n\n'
                        'Also parent suite teardown failed:\nTop level')


if __name__ == '__main__':
    unittest.main()
