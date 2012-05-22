import unittest
import sys
import tempfile
from os.path import abspath, dirname, join, exists
from os import remove
from StringIO import StringIO

from robot.utils.asserts import assert_equals, assert_true
from robot.running import namespace
from robot import run, rebot

ROOT = dirname(dirname(dirname(abspath(__file__))))
TEMP = tempfile.gettempdir()
LOG_PATH = join(TEMP, 'log.html')
LOG = 'Log:     %s' % LOG_PATH


class StreamWithOnlyWriteAndFlush(object):

    def __init__(self):
        self._buffer = []

    def write(self, msg):
        self._buffer.append(msg)

    def flush(self):
        pass

    def getvalue(self):
        return ''.join(self._buffer)


class Base(unittest.TestCase):

    def setUp(self):
        self.orig__stdout__ = sys.__stdout__
        self.orig__stderr__ = sys.__stderr__
        self.orig_stdout = sys.stdout
        self.orig_stderr = sys.stderr
        sys.__stdout__ = StringIO()
        sys.__stderr__ = StringIO()
        sys.stdout = StringIO()
        sys.stderr = StringIO()
        if exists(LOG_PATH):
            remove(LOG_PATH)

    def tearDown(self):
        sys.__stdout__ = self.orig__stdout__
        sys.__stderr__ = self.orig__stderr__
        sys.stdout = self.orig_stdout
        sys.stderr = self.orig_stderr

    def _assert_outputs(self, stdout=None, stderr=None):
        self._assert_output(sys.__stdout__, stdout)
        self._assert_output(sys.__stderr__, stderr)
        self._assert_output(sys.stdout, None)
        self._assert_output(sys.stderr, None)

    def _assert_output(self, stream, expected):
        output = stream.getvalue()
        if expected:
            self._assert_output_contains(output, expected)
        else:
            self._assert_no_output(output)

    def _assert_no_output(self, output):
        if output:
            raise AssertionError('Expected output to be empty:\n%s' % output)

    def _assert_output_contains(self, output, expected):
        for content, count in expected:
            if output.count(content) != count:
                raise AssertionError("'%s' not %d times in output:\n%s"
                                     % (content, count, output))


class TestRun(Base):
    data = join(ROOT, 'atest', 'testdata', 'misc', 'pass_and_fail.html')
    warn = join(ROOT, 'atest', 'testdata', 'misc', 'warnings_and_errors.txt')
    nonex = join(TEMP, 'non-existing-file-this-is.txt')

    def test_run_once(self):
        assert_equals(run(self.data, outputdir=TEMP, report='none'), 1)
        self._assert_outputs([('Pass And Fail', 2), (LOG, 1), ('Report:', 0)])
        assert exists(LOG_PATH)

    def test_run_multiple_times(self):
        assert_equals(run(self.data, output='NONE', critical='nomatch'), 0)
        assert_equals(run(self.data, output='NONE', name='New Name'), 1)
        self._assert_outputs([('Pass And Fail', 2), ('New Name', 2), (LOG, 0)])

    def test_run_fails(self):
        assert_equals(run(self.nonex), 252)
        assert_equals(run(self.data, outputdir=TEMP), 1)
        self._assert_outputs(stdout=[('Pass And Fail', 2), (LOG, 1)],
                             stderr=[('[ ERROR ]', 1), (self.nonex, 1), ('--help', 1)])

    def test_custom_stdout(self):
        stdout = StringIO()
        assert_equals(run(self.data, output='NONE', stdout=stdout), 1)
        self._assert_output(stdout, [('Pass And Fail', 2), ('Output:', 1),
                                     ('Log:', 0), ('Report:', 0)])
        self._assert_outputs()

    def test_custom_stderr(self):
        stderr = StringIO()
        assert_equals(run(self.warn, output='NONE', stderr=stderr), 0)
        self._assert_output(stderr, [('[ WARN ]', 4), ('[ ERROR ]', 1)])
        self._assert_outputs([('Warnings And Errors', 2), ('Output:', 1),
                              ('Log:', 0), ('Report:', 0)])

    def test_custom_stdout_and_stderr_with_minimal_implementation(self):
        output = StreamWithOnlyWriteAndFlush()
        assert_equals(run(self.warn, output='NONE', stdout=output, stderr=output), 0)
        self._assert_output(output, [('[ WARN ]', 4), ('[ ERROR ]', 1),
                                     ('Warnings And Errors', 3), ('Output:', 1),
                                     ('Log:', 0), ('Report:', 0)])
        self._assert_outputs()

    def test_multi_options_as_single_string(self):
        assert_equals(run(self.data, output='NONE', exclude='fail'), 0)
        self._assert_outputs([('FAIL', 0)])


class TestRebot(Base):
    data = join(ROOT, 'atest', 'testdata', 'rebot', 'created_normal.xml')
    nonex = join(TEMP, 'non-existing-file-this-is.xml')

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
                             stderr=[('[ ERROR ]', 1), (self.nonex, 2), ('--help', 1)])

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
        run(data, stdout=StringIO(), stderr=StringIO())
        lib = self._import_library()
        res = self._import_resource()
        run(data, stdout=StringIO(), stderr=StringIO())
        assert_true(lib is not self._import_library())
        assert_true(res is not self._import_resource())

    def _import_library(self):
        return namespace.IMPORTER.import_library('OperatingSystem')

    def _import_resource(self):
        resource = join(ROOT, 'atest', 'testdata', 'core', 'resources.html')
        return namespace.IMPORTER.import_resource(resource)

    def test_clear_namespace_between_runs(self):
        data = join(ROOT, 'atest', 'testdata', 'variables', 'commandline_variables.html')
        rc = run(data, stdout=StringIO(), stderr=StringIO(), test=['NormalText'], variable=['NormalText:Hello'])
        assert_equals(rc, 0)
        rc = run(data, stdout=StringIO(), stderr=StringIO(), test=['NormalText'])
        assert_equals(rc, 1)


if __name__ == '__main__':
    unittest.main()
