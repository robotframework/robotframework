import unittest
import sys
import tempfile
from os.path import abspath, dirname, join, exists
from os import remove
from StringIO import StringIO

from robot.utils.asserts import assert_equals
from robot import run, run_rebot

ROOT = dirname(dirname(dirname(abspath(__file__))))
TEMP = tempfile.gettempdir()
LOG_PATH = join(TEMP, 'log.html')
LOG = 'Log:     %s' % LOG_PATH


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

    def _assert_output_contains(self, output, expected_items):
        for expected in expected_items:
            content, count = expected
            if output.count(content) != count:
                raise AssertionError("'%s' not %d times in output:\n%s"
                                     % (content, count, output))


class TestRun(Base):
    data = join(ROOT, 'atest', 'testdata', 'misc', 'pass_and_fail.html')
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


class TestRebot(Base):
    data = join(ROOT, 'atest', 'testdata', 'rebot', 'created_normal.xml')
    nonex = join(TEMP, 'non-existing-file-this-is.xml')

    def test_run_once(self):
        assert_equals(run_rebot(self.data, outputdir=TEMP, report='NONE'), 1)
        self._assert_outputs([(LOG, 1), ('Report:', 0)])
        assert exists(LOG_PATH)

    def test_run_multiple_times(self):
        assert_equals(run_rebot(self.data, outputdir=TEMP, critical='nomatch'), 0)
        assert_equals(run_rebot(self.data, outputdir=TEMP, name='New Name'), 1)
        self._assert_outputs([(LOG, 2)])

    def test_run_fails(self):
        assert_equals(run_rebot(self.nonex), 252)
        assert_equals(run_rebot(self.data, outputdir=TEMP), 1)
        self._assert_outputs(stdout=[(LOG, 1)],
                             stderr=[('[ ERROR ]', 1), (self.nonex, 2), ('--help', 1)])


if __name__ == '__main__':
    unittest.main()
