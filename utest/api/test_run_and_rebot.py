import unittest
import time
import glob
import sys
import threading
import tempfile
import signal
import logging
from io import StringIO
from os.path import abspath, curdir, dirname, exists, join
from os import chdir, getenv

from robot import run, run_cli, rebot, rebot_cli
from robot.model import SuiteVisitor
from robot.running import namespace
from robot.utils.asserts import assert_equal, assert_raises, assert_true

from resources.runningtestcase import RunningTestCase
from resources.Listener import Listener


ROOT = dirname(dirname(dirname(abspath(__file__))))
TEMP = getenv('TEMPDIR', tempfile.gettempdir())
OUTPUT_PATH = join(TEMP, 'output.xml')
REPORT_PATH = join(TEMP, 'report.html')
LOG_PATH = join(TEMP, 'log.html')
LOG = 'Log:     %s' % LOG_PATH


def run_without_outputs(*args, **kwargs):
    options = {'output': 'NONE', 'log': 'NoNe', 'report': None}
    options.update(kwargs)
    return run(*args, **options)


def assert_signal_handler_equal(signum, expected):
    sig = signal.getsignal(signum)
    assert_equal(sig, expected)


class StreamWithOnlyWriteAndFlush(object):

    def __init__(self):
        self._buffer = []

    def write(self, msg):
        self._buffer.append(msg)

    def flush(self):
        pass

    def getvalue(self):
        return ''.join(self._buffer)


class TestRun(RunningTestCase):
    data = join(ROOT, 'atest', 'testdata', 'misc', 'pass_and_fail.robot')
    warn = join(ROOT, 'atest', 'testdata', 'misc', 'warnings_and_errors.robot')
    nonex = join(TEMP, 'non-existing-file-this-is.robot')
    remove_files = [LOG_PATH, REPORT_PATH, OUTPUT_PATH]

    def test_run_once(self):
        assert_equal(run(self.data, outputdir=TEMP, report='none'), 1)
        self._assert_outputs([('Pass And Fail', 2), (LOG, 1), ('Report:', 0)])
        assert exists(LOG_PATH)

    def test_run_multiple_times(self):
        assert_equal(run_without_outputs(self.data), 1)
        assert_equal(run_without_outputs(self.data, name='New Name'), 1)
        self._assert_outputs([('Pass And Fail', 2), ('New Name', 2), (LOG, 0)])

    def test_run_fail(self):
        assert_equal(run(self.data, outputdir=TEMP), 1)
        self._assert_outputs(stdout=[('Pass And Fail', 2), (LOG, 1)])

    def test_run_error(self):
        assert_equal(run(self.nonex), 252)
        self._assert_outputs(stderr=[('[ ERROR ]', 1), (self.nonex, 1),
                                     ('--help', 1)])

    def test_custom_stdout(self):
        stdout = StringIO()
        assert_equal(run_without_outputs(self.data, stdout=stdout), 1)
        self._assert_output(stdout, [('Pass And Fail', 2), ('Output:', 1),
                                     ('Log:', 0), ('Report:', 0)])
        self._assert_outputs()

    def test_custom_stderr(self):
        stderr = StringIO()
        assert_equal(run_without_outputs(self.warn, stderr=stderr), 0)
        self._assert_output(stderr, [('[ WARN ]', 4), ('[ ERROR ]', 2)])
        self._assert_outputs([('Warnings And Errors', 2), ('Output:', 1),
                              ('Log:', 0), ('Report:', 0)])

    def test_custom_stdout_and_stderr_with_minimal_implementation(self):
        output = StreamWithOnlyWriteAndFlush()
        assert_equal(run_without_outputs(self.warn, stdout=output, stderr=output), 0)
        self._assert_output(output, [('[ WARN ]', 4), ('[ ERROR ]', 2),
                                     ('Warnings And Errors', 3), ('Output:', 1),
                                     ('Log:', 0), ('Report:', 0)])
        self._assert_outputs()

    def test_multi_options_as_single_string(self):
        assert_equal(run_without_outputs(self.data, exclude='fail', skip='pass',
                                         skiponfailure='xxx'), 0)
        self._assert_outputs([('FAIL', 0)])
        self._assert_outputs([('1 test, 0 passed, 0 failed, 1 skipped', 1)])

    def test_multi_options_as_tuples(self):
        assert_equal(run_without_outputs(self.data, exclude=('fail',), skip=('pass',),
                                         skiponfailure=('xxx', 'yyy')), 0)
        self._assert_outputs([('FAIL', 0)])
        self._assert_outputs([('1 test, 0 passed, 0 failed, 1 skipped', 1)])

    def test_listener_gets_notification_about_log_report_and_output(self):
        listener = join(ROOT, 'utest', 'resources', 'Listener.py')
        assert_equal(run(self.data, output=OUTPUT_PATH, report=REPORT_PATH,
                          log=LOG_PATH, listener=listener), 1)
        self._assert_outputs(stdout=[('[output {0}]'.format(OUTPUT_PATH), 1),
                                     ('[report {0}]'.format(REPORT_PATH), 1),
                                     ('[log {0}]'.format(LOG_PATH), 1),
                                     ('[listener close]', 1)])

    def test_pass_listener_as_instance(self):
        assert_equal(run_without_outputs(self.data, listener=Listener(1)), 1)
        self._assert_outputs([("[from listener 1]", 1)])

    def test_pass_listener_as_string(self):
        module_file = join(ROOT, 'utest', 'resources', 'Listener.py')
        assert_equal(run_without_outputs(self.data, listener=module_file+":1"), 1)
        self._assert_outputs([("[from listener 1]", 1)])

    def test_pass_listener_as_list(self):
        module_file = join(ROOT, 'utest', 'resources', 'Listener.py')
        assert_equal(run_without_outputs(self.data, listener=[module_file+":1", Listener(2)]), 1)
        self._assert_outputs([("[from listener 1]", 1), ("[from listener 2]", 1)])

    def test_pre_run_modifier_as_instance(self):
        class Modifier(SuiteVisitor):
            def start_suite(self, suite):
                suite.tests = [t for t in suite.tests if t.tags.match('pass')]
        assert_equal(run_without_outputs(self.data, prerunmodifier=Modifier()), 0)
        self._assert_outputs([('Pass       ', 1), ('Fail :: FAIL', 0)])

    def test_pre_rebot_modifier_as_instance(self):
        class Modifier(SuiteVisitor):
            def __init__(self):
                self.tests = []
            def visit_test(self, test):
                self.tests.append(test.name)
        modifier = Modifier()
        assert_equal(run(self.data, outputdir=TEMP, log=LOG_PATH, prerebotmodifier=modifier), 1)
        assert_equal(modifier.tests, ['Pass', 'Fail'])
        self._assert_outputs([('Pass       ', 1), ('Fail :: FAIL', 1)])

    def test_invalid_modifier(self):
        assert_equal(run_without_outputs(self.data, prerunmodifier=42), 1)
        self._assert_outputs([('Pass       ', 1), ('Fail :: FAIL', 1)],
                             [("[ ERROR ] Executing model modifier 'integer' "
                               "failed: AttributeError: ", 1)])

    def test_run_cli_system_exits_by_default(self):
        exit = assert_raises(SystemExit, run_cli, ['-d', TEMP, self.data])
        assert_equal(exit.code, 1)

    def test_run_cli_optionally_returns_rc(self):
        rc = run_cli(['-d', TEMP, self.data], exit=False)
        assert_equal(rc, 1)


class TestRebot(RunningTestCase):
    data = join(ROOT, 'atest', 'testdata', 'rebot', 'created_normal.xml')
    nonex = join(TEMP, 'non-existing-file-this-is.xml')
    remove_files = [LOG_PATH, REPORT_PATH]

    def test_run_once(self):
        assert_equal(rebot(self.data, outputdir=TEMP, report='NONE'), 1)
        self._assert_outputs([(LOG, 1), ('Report:', 0)])
        assert exists(LOG_PATH)

    def test_run_multiple_times(self):
        assert_equal(rebot(self.data, outputdir=TEMP), 1)
        assert_equal(rebot(self.data, outputdir=TEMP, name='New Name'), 1)
        self._assert_outputs([(LOG, 2)])

    def test_run_fails(self):
        assert_equal(rebot(self.nonex), 252)
        assert_equal(rebot(self.data, outputdir=TEMP), 1)
        self._assert_outputs(stdout=[(LOG, 1)],
                             stderr=[('[ ERROR ]', 1), (self.nonex, (1, 2)),
                                     ('--help', 1)])

    def test_custom_stdout(self):
        stdout = StringIO()
        assert_equal(rebot(self.data, report='None', stdout=stdout,
                           outputdir=TEMP), 1)
        self._assert_output(stdout, [('Log:', 1), ('Report:', 0)])
        self._assert_outputs()

    def test_custom_stdout_and_stderr_with_minimal_implementation(self):
        output = StreamWithOnlyWriteAndFlush()
        assert_equal(rebot(self.data, log='NONE', report='NONE', stdout=output,
                           stderr=output), 252)
        assert_equal(rebot(self.data, report='NONE', stdout=output,
                           stderr=output, outputdir=TEMP), 1)
        self._assert_output(output, [('[ ERROR ] No outputs created', 1),
                                     ('--help', 1), ('Log:', 1), ('Report:', 0)])
        self._assert_outputs()

    def test_pre_rebot_modifier_as_instance(self):
        class Modifier(SuiteVisitor):
            def __init__(self):
                self.tests = []
            def visit_test(self, test):
                self.tests.append(test.name)
                test.status = 'FAIL'
        modifier = Modifier()
        assert_equal(rebot(self.data, outputdir=TEMP,
                           prerebotmodifier=modifier), 3)
        assert_equal(modifier.tests, ['Test 1.1', 'Test 1.2', 'Test 2.1'])

    def test_rebot_cli_system_exits_by_default(self):
        exit = assert_raises(SystemExit, rebot_cli, ['-d', TEMP, self.data])
        assert_equal(exit.code, 1)

    def test_rebot_cli_optionally_returns_rc(self):
        rc = rebot_cli(['-d', TEMP, self.data], exit=False)
        assert_equal(rc, 1)


class TestStateBetweenTestRuns(RunningTestCase):
    data = join(ROOT, 'atest', 'testdata', 'misc', 'normal.robot')

    def test_importer_caches_are_cleared_between_runs(self):
        self._run(self.data)
        lib = self._import_library()
        res = self._import_resource()
        self._run(self.data)
        assert_true(lib is not self._import_library())
        assert_true(res is not self._import_resource())

    def _run(self, data, rc=None, **config):
        self._clear_outputs()
        returned_rc = run_without_outputs(data, outputdir=TEMP, **config)
        if rc is not None:
            assert_equal(returned_rc, rc)

    def _import_library(self):
        return namespace.IMPORTER.import_library('BuiltIn', None, None, None)

    def _import_resource(self):
        resource = join(ROOT, 'atest', 'testdata', 'core', 'resources.robot')
        return namespace.IMPORTER.import_resource(resource)

    def test_clear_namespace_between_runs(self):
        data = join(ROOT, 'atest', 'testdata', 'variables', 'commandline_variables.robot')
        self._run(data, test=['NormalText'], variable=['NormalText:Hello'], rc=0)
        self._run(data, test=['NormalText'], rc=1)

    def test_reset_logging_conf(self):
        assert_equal(logging.getLogger().handlers, [])
        assert_equal(logging.raiseExceptions, 1)
        self._run(join(ROOT, 'atest', 'testdata', 'misc', 'normal.robot'))
        assert_equal(logging.getLogger().handlers, [])
        assert_equal(logging.raiseExceptions, 1)

    def test_listener_unregistration(self):
        listener = join(ROOT, 'utest', 'resources', 'Listener.py')
        self._run(self.data, listener=listener+':1', rc=0)
        self._assert_outputs([("[from listener 1]", 1), ("[listener close]", 1)])
        self._run(self.data, rc=0)
        self._assert_outputs([("[from listener 1]", 0), ("[listener close]", 0)])

    def test_rerunfailed_is_not_persistent(self):
        # https://github.com/robotframework/robotframework/issues/2437
        data = join(ROOT, 'atest', 'testdata', 'misc', 'pass_and_fail.robot')
        self._run(data, output=OUTPUT_PATH, rc=1)
        self._run(data, rerunfailed=OUTPUT_PATH, rc=1)
        self._run(self.data, output=OUTPUT_PATH, rc=0)
        assert_equal(rebot(OUTPUT_PATH, log=LOG_PATH, report=None), 0)


class TestTimestampOutputs(RunningTestCase):
    output = join(TEMP, 'output-ts-*.xml')
    report = join(TEMP, 'report-ts-*.html')
    log = join(TEMP, 'log-ts-*.html')
    remove_files = [output, report, log]

    def test_different_timestamps_when_run_multiple_times(self):
        self.run_tests()
        output1, = self.find_results(self.output, 1)
        report1, = self.find_results(self.report, 1)
        log1, = self.find_results(self.log, 1)
        self.wait_until_next_second()
        self.run_tests()
        output21, output22 = self.find_results(self.output, 2)
        report21, report22 = self.find_results(self.report, 2)
        log21, log22 = self.find_results(self.log, 2)
        assert_equal(output1, output21)
        assert_equal(report1, report21)
        assert_equal(log1, log21)

    def run_tests(self):
        data = join(ROOT, 'atest', 'testdata', 'misc', 'pass_and_fail.robot')
        assert_equal(run(data, timestampoutputs=True, outputdir=TEMP,
                         output='output-ts.xml', report='report-ts.html',
                         log='log-ts'), 1)

    def find_results(self, pattern, expected):
        matches = glob.glob(pattern)
        assert_equal(len(matches), expected)
        return sorted(matches)

    def wait_until_next_second(self):
        start = time.localtime()[5]
        while time.localtime()[5] == start:
            time.sleep(0.01)


class TestSignalHandlers(unittest.TestCase):
    data = join(ROOT, 'atest', 'testdata', 'misc', 'pass_and_fail.robot')

    def test_original_signal_handlers_are_restored(self):
        orig_sigint = signal.getsignal(signal.SIGINT)
        orig_sigterm = signal.getsignal(signal.SIGTERM)
        my_sigterm = lambda signum, frame: None
        signal.signal(signal.SIGTERM, my_sigterm)
        try:
            run_without_outputs(self.data, stdout=StringIO())
            assert_signal_handler_equal(signal.SIGINT, orig_sigint)
            assert_signal_handler_equal(signal.SIGTERM, my_sigterm)
        finally:
            signal.signal(signal.SIGINT, orig_sigint)
            signal.signal(signal.SIGTERM, orig_sigterm)

    def test_dont_register_signal_handlers_when_run_on_thread(self):
        stream = StringIO()
        thread = threading.Thread(target=run_without_outputs, args=(self.data,),
                                  kwargs=dict(stdout=stream, stderr=stream))
        thread.start()
        thread.join()
        output = stream.getvalue()
        assert_true('ERROR' not in output.upper(), 'Errors:\n%s' % output)


class TestRelativeImportsFromPythonpath(RunningTestCase):
    data = join(abspath(dirname(__file__)), 'import_test.robot')

    def setUp(self):
        self._orig_path = abspath(curdir)
        chdir(ROOT)
        sys.path.append(join('atest', 'testresources'))

    def tearDown(self):
        chdir(self._orig_path)
        sys.path.pop()

    def test_importing_library_from_pythonpath(self):
        errors = StringIO()
        run(self.data, outputdir=TEMP, stdout=StringIO(), stderr=errors)
        self._assert_output(errors, '')


if __name__ == '__main__':
    unittest.main()
