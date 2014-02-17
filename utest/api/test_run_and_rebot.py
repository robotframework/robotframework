import unittest
import sys
import tempfile
import signal
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
    kwargs.update(output='NONE', log='NoNe', report='none')
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
    data = join(ROOT, 'atest', 'testdata', 'misc', 'pass_and_fail.txt')
    warn = join(ROOT, 'atest', 'testdata', 'misc', 'warnings_and_errors.txt')
    nonex = join(TEMP, 'non-existing-file-this-is.txt')
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
        data = join(ROOT, 'atest', 'testdata', 'core', 'import_settings.txt')
        run(data, outputdir=TEMP, stdout=StringIO(), stderr=StringIO())
        lib = self._import_library()
        res = self._import_resource()
        run(data, outputdir=TEMP, stdout=StringIO(), stderr=StringIO())
        assert_true(lib is not self._import_library())
        assert_true(res is not self._import_resource())

    def _import_library(self):
        return namespace.IMPORTER.import_library('OperatingSystem',None, None, None)

    def _import_resource(self):
        resource = join(ROOT, 'atest', 'testdata', 'core', 'resources.html')
        return namespace.IMPORTER.import_resource(resource)

    def test_clear_namespace_between_runs(self):
        data = join(ROOT, 'atest', 'testdata', 'variables', 'commandline_variables.html')
        rc = run(data, outputdir=TEMP, stdout=StringIO(), stderr=StringIO(),
                 test=['NormalText'], variable=['NormalText:Hello'])
        assert_equals(rc, 0)
        rc = run(data, outputdir=TEMP, stdout=StringIO(), stderr=StringIO(),
                 test=['NormalText'])
        assert_equals(rc, 1)


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
        run(join(ROOT, 'atest', 'testdata', 'misc', 'pass_and_fail.txt'),
            stdout=StringIO(), output=None, log=None, report=None)
        assert_equals(signal.getsignal(signal.SIGINT), self.orig_sigint)
        assert_equals(signal.getsignal(signal.SIGTERM), my_sigterm)


class TestRelativeImportsFromPythonpath(RunningTestCase):
    _data = join(abspath(dirname(__file__)), 'import_test.txt')

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
