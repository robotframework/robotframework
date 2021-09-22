import logging
import signal
import sys
import unittest
from io import StringIO
from os.path import abspath, dirname, join

from robot.running import TestSuite, TestSuiteBuilder
from robot.utils.asserts import assert_equal

from resources.runningtestcase import RunningTestCase
from resources.Listener import Listener


CURDIR = dirname(abspath(__file__))
ROOTDIR = dirname(dirname(CURDIR))
DATADIR = join(ROOTDIR, 'atest', 'testdata', 'misc')


def run(suite, **kwargs):
    config = dict(output=None, log=None, report=None,
                  stdout=StringIO(), stderr=StringIO())
    config.update(kwargs)
    result = suite.run(**config)
    return result.suite


def build(path):
    return TestSuiteBuilder().build(join(DATADIR, path))


def assert_suite(suite, name, status, message='', tests=1):
    assert_equal(suite.name, name)
    assert_equal(suite.status, status)
    assert_equal(suite.message, message)
    assert_equal(len(suite.tests), tests)


def assert_test(test, name, status, tags=(), msg=''):
    assert_equal(test.name, name)
    assert_equal(test.status, status)
    assert_equal(test.message, msg)
    assert_equal(tuple(test.tags), tags)


def assert_signal_handler_equal(signum, expected):
    sig = signal.getsignal(signum)
    assert_equal(sig, expected)


class TestRunning(unittest.TestCase):

    def test_one_library_keyword(self):
        suite = TestSuite(name='Suite')
        suite.tests.create(name='Test').body.create_keyword('Log', args=['Hello!'])
        result = run(suite)
        assert_suite(result, 'Suite', 'PASS')
        assert_test(result.tests[0], 'Test', 'PASS')

    def test_failing_library_keyword(self):
        suite = TestSuite(name='Suite')
        test = suite.tests.create(name='Test')
        test.body.create_keyword('Log', args=['Dont fail yet.'])
        test.body.create_keyword('Fail', args=['Hello, world!'])
        result = run(suite)
        assert_suite(result, 'Suite', 'FAIL')
        assert_test(result.tests[0], 'Test', 'FAIL', msg='Hello, world!')

    def test_assign(self):
        suite = TestSuite(name='Suite')
        test = suite.tests.create(name='Test')
        test.body.create_keyword(assign=['${var}'], name='Set Variable',
                                 args=['value in variable'])
        test.body.create_keyword('Fail', args=['${var}'])
        result = run(suite)
        assert_suite(result, 'Suite', 'FAIL')
        assert_test(result.tests[0], 'Test', 'FAIL', msg='value in variable')

    def test_suites_in_suites(self):
        root = TestSuite(name='Root')
        root.suites.create(name='Child')\
            .tests.create(name='Test')\
            .body.create_keyword('Log', args=['Hello, world!'])
        result = run(root)
        assert_suite(result, 'Root', 'PASS', tests=0)
        assert_suite(result.suites[0], 'Child', 'PASS')
        assert_test(result.suites[0].tests[0], 'Test', 'PASS')

    def test_user_keywords(self):
        suite = TestSuite(name='Suite')
        suite.tests.create(name='Test')\
            .body.create_keyword('User keyword', args=['From uk'])
        uk = suite.resource.keywords.create(name='User keyword', args=['${msg}'])
        uk.body.create_keyword(name='Fail', args=['${msg}'])
        result = run(suite)
        assert_suite(result, 'Suite', 'FAIL')
        assert_test(result.tests[0], 'Test', 'FAIL', msg='From uk')

    def test_variables(self):
        suite = TestSuite(name='Suite')
        suite.resource.variables.create('${ERROR}', 'Error message')
        suite.resource.variables.create('@{LIST}', ['Error', 'added tag'])
        suite.tests.create(name='T1').body.create_keyword('Fail', args=['${ERROR}'])
        suite.tests.create(name='T2').body.create_keyword('Fail', args=['@{LIST}'])
        result = run(suite)
        assert_suite(result, 'Suite', 'FAIL', tests=2)
        assert_test(result.tests[0], 'T1', 'FAIL', msg='Error message')
        assert_test(result.tests[1], 'T2', 'FAIL', ('added tag',), 'Error')

    def test_modifiers_are_not_used(self):
        # These options are valid but not used. Modifiers can be passed to
        # suite.visit() explicitly if needed.
        suite = TestSuite(name='Suite')
        suite.tests.create(name='Test').body.create_keyword('No Operation')
        result = run(suite, prerunmodifier='not used', prerebotmodifier=42)
        assert_suite(result, 'Suite', 'PASS', tests=1)


class TestTestSetupAndTeardown(unittest.TestCase):

    def setUp(self):
        self.tests = run(build('setups_and_teardowns.robot')).tests

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
        self.suite = build('setups_and_teardowns.robot')

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
        root.teardown.config(name='Fail', args=['Top level'], type='teardown')
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


class TestCustomStreams(RunningTestCase):

    def test_stdout_and_stderr(self):
        self._run()
        self._assert_output(sys.__stdout__,
                            [('My Suite', 2), ('My Test', 1),
                             ('1 test, 1 passed, 0 failed', 1)])
        self._assert_output(sys.__stderr__, [('Hello, world!', 1)])

    def test_custom_stdout_and_stderr(self):
        stdout, stderr = StringIO(), StringIO()
        self._run(stdout, stderr)
        self._assert_normal_stdout_stderr_are_empty()
        self._assert_output(stdout, [('My Suite', 2), ('My Test', 1)])
        self._assert_output(stderr, [('Hello, world!', 1)])

    def test_same_custom_stdout_and_stderr(self):
        output = StringIO()
        self._run(output, output)
        self._assert_normal_stdout_stderr_are_empty()
        self._assert_output(output, [('My Suite', 2), ('My Test', 1),
                                     ('Hello, world!', 1)])

    def test_run_multiple_times_with_different_stdout_and_stderr(self):
        stdout, stderr = StringIO(), StringIO()
        self._run(stdout, stderr)
        self._assert_normal_stdout_stderr_are_empty()
        self._assert_output(stdout, [('My Suite', 2), ('My Test', 1)])
        self._assert_output(stderr, [('Hello, world!', 1)])
        stdout.close(); stderr.close()
        output = StringIO()
        self._run(output, output, variable='MESSAGE:Hi, again!')
        self._assert_normal_stdout_stderr_are_empty()
        self._assert_output(output, [('My Suite', 2), ('My Test', 1),
                                     ('Hi, again!', 1), ('Hello, world!', 0)])
        output.close()
        self._run(variable='MESSAGE:Last hi!')
        self._assert_output(sys.__stdout__, [('My Suite', 2), ('My Test', 1)])
        self._assert_output(sys.__stderr__, [('Last hi!', 1), ('Hello, world!', 0)])

    def _run(self, stdout=None, stderr=None, **options):
        suite = TestSuite(name='My Suite')
        suite.resource.variables.create('${MESSAGE}', 'Hello, world!')
        suite.tests.create(name='My Test')\
            .body.create_keyword('Log', args=['${MESSAGE}', 'WARN'])
        run(suite, stdout=stdout, stderr=stderr, **options)

    def _assert_normal_stdout_stderr_are_empty(self):
        self._assert_outputs()


class TestPreservingSignalHandlers(unittest.TestCase):

    def setUp(self):
        self.orig_sigint = signal.getsignal(signal.SIGINT)
        self.orig_sigterm = signal.getsignal(signal.SIGTERM)

    def tearDown(self):
        signal.signal(signal.SIGINT, self.orig_sigint)
        signal.signal(signal.SIGTERM, self.orig_sigterm)

    def test_original_signal_handlers_are_restored(self):
        my_sigterm = lambda signum, frame: None
        signal.signal(signal.SIGTERM, my_sigterm)
        suite = TestSuite(name='My Suite')
        suite.tests.create(name='My Test').body.create_keyword('Log', args=['Hi!'])
        run(suite)
        assert_signal_handler_equal(signal.SIGINT, self.orig_sigint)
        assert_signal_handler_equal(signal.SIGTERM, my_sigterm)


class TestStateBetweenTestRuns(unittest.TestCase):

    def test_reset_logging_conf(self):
        assert_equal(logging.getLogger().handlers, [])
        assert_equal(logging.raiseExceptions, 1)
        suite = TestSuite(name='My Suite')
        suite.tests.create(name='My Test').body.create_keyword('Log', args=['Hi!'])
        run(suite)
        assert_equal(logging.getLogger().handlers, [])
        assert_equal(logging.raiseExceptions, 1)


class TestListeners(RunningTestCase):

    def test_listeners(self):
        module_file = join(ROOTDIR, 'utest', 'resources', 'Listener.py')
        suite = build('setups_and_teardowns.robot')
        suite.run(output=None, log=None, report=None, listener=[module_file+":1", Listener(2)])
        self._assert_outputs([("[from listener 1]", 1), ("[from listener 2]", 1)])

    def test_listeners_unregistration(self):
        module_file = join(ROOTDIR, 'utest', 'resources', 'Listener.py')
        suite = build('setups_and_teardowns.robot')
        suite.run(output=None, log=None, report=None, listener=module_file+":1")
        self._assert_outputs([("[from listener 1]", 1), ("[listener close]", 1)])
        self._clear_outputs()
        suite.run(output=None, log=None, report=None)
        self._assert_outputs([("[from listener 1]", 0), ("[listener close]", 0)])


if __name__ == '__main__':
    unittest.main()
