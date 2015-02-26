import unittest
import time
import glob
import sys
import threading
import tempfile
import signal
import logging
from os.path import abspath, dirname, join, exists, curdir
from os import chdir
from six.moves import StringIO

from robot.utils.asserts import assert_equals, assert_true
from robot.running import namespace
from robot import run, rebot
from resources.runningtestcase import RunningTestCase

ROOT = dirname(dirname(dirname(abspath(__file__))))
TEMP = tempfile.gettempdir()
LOG_PATH = join(TEMP, 'log.html')
LOG = 'Log:     %s' % LOG_PATH


def run_without_outputs(*args, **kwargs):
    kwargs.update(output='NONE', log='NoNe', report=None)
    return run(*args, **kwargs)


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
    remove_files = [LOG_PATH]

    def test_run_once(self):
        assert_equals(run(self.data, outputdir=TEMP, report='none'), 1)
        self._assert_outputs([('Pass And Fail', 2), (LOG, 1), ('Report:', 0)])
        assert exists(LOG_PATH)

    def test_run_multiple_times(self):
        assert_equals(run_without_outputs(self.data, critical='nomatch'), 0)
        assert_equals(run_without_outputs(self.data, name='New Name'), 1)
        self._assert_outputs([('Pass And Fail', 2), ('New Name', 2), (LOG, 0)])

    def test_run_fails(self):
        assert_equals(run(self.nonex), 252)
        assert_equals(run(self.data, outputdir=TEMP), 1)
        self._assert_outputs(stdout=[('Pass And Fail', 2), (LOG, 1)],
                             stderr=[('[ ERROR ]', 1), (self.nonex, 1),
                                     ('--help', 1)])

    def test_custom_stdout(self):
        stdout = StringIO()
        assert_equals(run_without_outputs(self.data, stdout=stdout), 1)
        self._assert_output(stdout, [('Pass And Fail', 2), ('Output:', 1),
                                     ('Log:', 0), ('Report:', 0)])
        self._assert_outputs()

    def test_custom_stderr(self):
        stderr = StringIO()
        assert_equals(run_without_outputs(self.warn, stderr=stderr), 0)
        self._assert_output(stderr, [('[ WARN ]', 4), ('[ ERROR ]', 1)])
        self._assert_outputs([('Warnings And Errors', 2), ('Output:', 1),
                              ('Log:', 0), ('Report:', 0)])

    def test_custom_stdout_and_stderr_with_minimal_implementation(self):
        output = StreamWithOnlyWriteAndFlush()
        assert_equals(run_without_outputs(self.warn, stdout=output, stderr=output), 0)
        self._assert_output(output, [('[ WARN ]', 4), ('[ ERROR ]', 1),
                                     ('Warnings And Errors', 3), ('Output:', 1),
                                     ('Log:', 0), ('Report:', 0)])
        self._assert_outputs()

    def test_multi_options_as_single_string(self):
        assert_equals(run_without_outputs(self.data, exclude='fail'), 0)
        self._assert_outputs([('FAIL', 0)])


class TestRebot(RunningTestCase):
    data = join(ROOT, 'atest', 'testdata', 'rebot', 'created_normal.xml')
    nonex = join(TEMP, 'non-existing-file-this-is.xml')
    remove_files = [LOG_PATH]

    def test_run_once(self):
        assert_equals(rebot(self.data, outputdir=TEMP, report='NONE'), 1)
        self._assert_outputs([(LOG, 1), ('Report:', 0)])
        assert exists(LOG_PATH)

    def test_run_multiple_times(self):
        assert_equals(rebot(self.data, outputdir=TEMP, critical='nomatch'), 0)
        assert_equals(rebot(self.data, outputdir=TEMP, name='New Name'), 1)
        self._assert_outputs([(LOG, 2)])

    def test_run_fails(self):
        assert_equals(rebot(self.nonex), 252)
        assert_equals(rebot(self.data, outputdir=TEMP), 1)
        self._assert_outputs(stdout=[(LOG, 1)],
                             stderr=[('[ ERROR ]', 1), (self.nonex, 1),
                                     ('--help', 1)])

    def test_custom_stdout(self):
        stdout = StringIO()
        assert_equals(rebot(self.data, report='None', stdout=stdout,
                            outputdir=TEMP), 1)
        self._assert_output(stdout, [('Log:', 1), ('Report:', 0)])
        self._assert_outputs()

    def test_custom_stdout_and_stderr_with_minumal_implementation(self):
        output = StreamWithOnlyWriteAndFlush()
        assert_equals(rebot(self.data, log='NONE', report='NONE', stdout=output,
                            stderr=output), 252)
        assert_equals(rebot(self.data, report='NONE', stdout=output,
                            stderr=output, outputdir=TEMP), 1)
        self._assert_output(output, [('[ ERROR ] No outputs created', 1),
                                     ('--help', 1), ('Log:', 1), ('Report:', 0)])
        self._assert_outputs()


class TestStateBetweenTestRuns(unittest.TestCase):

    def test_importer_caches_are_cleared_between_runs(self):
        data = join(ROOT, 'atest', 'testdata', 'misc', 'normal.robot')
        self._run(data)
        lib = self._import_library()
        res = self._import_resource()
        self._run(data)
        assert_true(lib is not self._import_library())
        assert_true(res is not self._import_resource())

    def _run(self, data, **config):
        return run_without_outputs(data, stdout=StringIO(), stderr=StringIO(),
                                   outputdir=TEMP, **config)

    def _import_library(self):
        return namespace.IMPORTER.import_library('BuiltIn', None, None, None)

    def _import_resource(self):
        resource = join(ROOT, 'atest', 'testdata', 'core', 'resources.robot')
        return namespace.IMPORTER.import_resource(resource)

    def test_clear_namespace_between_runs(self):
        data = join(ROOT, 'atest', 'testdata', 'variables', 'commandline_variables.robot')
        rc = self._run(data, test=['NormalText'], variable=['NormalText:Hello'])
        assert_equals(rc, 0)
        rc = self._run(data, test=['NormalText'])
        assert_equals(rc, 1)

    def test_reset_logging_conf(self):
        assert_equals(logging.getLogger().handlers, [])
        assert_equals(logging.raiseExceptions, 1)
        self._run(join(ROOT, 'atest', 'testdata', 'misc', 'normal.robot'))
        assert_equals(logging.getLogger().handlers, [])
        assert_equals(logging.raiseExceptions, 1)


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
        assert_equals(output1, output21)
        assert_equals(report1, report21)
        assert_equals(log1, log21)

    def run_tests(self):
        data = join(ROOT, 'atest', 'testdata', 'misc', 'pass_and_fail.robot')
        assert_equals(run(data, timestampoutputs=True, outputdir=TEMP,
                          output='output-ts.xml', report='report-ts.html',
                          log='log-ts'), 1)

    def find_results(self, pattern, expected):
        matches = glob.glob(pattern)
        assert_equals(len(matches), expected)
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
            assert_equals(signal.getsignal(signal.SIGINT), orig_sigint)
            assert_equals(signal.getsignal(signal.SIGTERM), my_sigterm)
        finally:
            signal.signal(signal.SIGINT, orig_sigint)
            signal.signal(signal.SIGTERM, orig_sigterm)

    def test_dont_register_signal_handlers_then_run_on_thread(self):
        stream = StringIO()
        thread = threading.Thread(target=run_without_outputs, args=(self.data,),
                                  kwargs=dict(stdout=stream, stderr=stream))
        thread.start()
        thread.join()
        output = stream.getvalue()
        assert_true('ERROR' not in output.upper(), 'Errors:\n%s' % output)


class TestRelativeImportsFromPythonpath(RunningTestCase):
    _data = join(abspath(dirname(__file__)), 'import_test.robot')

    def setUp(self):
        self._orig_path = abspath(curdir)
        chdir(ROOT)
        sys.path.append(join('atest', 'testresources'))

    def tearDown(self):
        chdir(self._orig_path)
        sys.path.pop()

    def test_importing_library_from_pythonpath(self):
        errors = StringIO()
        run(self._data, outputdir=TEMP, stdout=StringIO(), stderr=errors)
        self._assert_output(errors, '')


if __name__ == '__main__':
    unittest.main()
