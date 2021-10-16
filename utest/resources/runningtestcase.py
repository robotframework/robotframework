import sys
import unittest
from glob import glob
from io import StringIO
from os import remove
from os.path import exists

from robot.utils import is_integer


class RunningTestCase(unittest.TestCase):
    remove_files = []

    def setUp(self):
        self.orig__stdout__ = sys.__stdout__
        self.orig__stderr__ = sys.__stderr__
        self.orig_stdout = sys.stdout
        self.orig_stderr = sys.stderr
        self._setup_output_streams()
        self._remove_files()

    def tearDown(self):
        sys.__stdout__ = self.orig__stdout__
        sys.__stderr__ = self.orig__stderr__
        sys.stdout = self.orig_stdout
        sys.stderr = self.orig_stderr
        self._remove_files()

    def _setup_output_streams(self):
        sys.__stdout__ = StringIO()
        sys.__stderr__ = StringIO()
        sys.stdout = StringIO()
        sys.stderr = StringIO()

    def _clear_outputs(self):
        self._setup_output_streams()

    def _assert_outputs(self, stdout=None, stderr=None):
        self._assert_output(sys.__stdout__, stdout)
        self._assert_output(sys.__stderr__, stderr)
        self._assert_output(sys.stdout, None)
        self._assert_output(sys.stderr, None)

    def _assert_output(self, stream, expected):
        output = stream.getvalue()
        if expected:
            for content, count in expected:
                self._assert_output_contains(output, content, count)
        else:
            self._assert_no_output(output)

    def _assert_no_output(self, output):
        if output:
            raise AssertionError('Expected output to be empty:\n%s' % output)

    def _assert_output_contains(self, output, content, count):
        if is_integer(count):
            if output.count(content) != count:
                raise AssertionError("'%s' not %d times in output:\n%s"
                                     % (content, count, output))
        else:
            min_count, max_count = count
            if not (min_count <= output.count(content) <= max_count):
                raise AssertionError("'%s' not %d-%d times in output:\n%s"
                                     % (content, min_count,max_count, output))

    def _remove_files(self):
        for pattern in self.remove_files:
            for path in glob(pattern):
                if exists(path):
                    remove(path)
