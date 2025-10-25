import sys
import unittest
from glob import glob
from io import StringIO
from os import remove
from os.path import exists


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
            raise AssertionError(f"Expected output to be empty:{output}")

    def _assert_output_contains(self, output, content, count):
        if isinstance(count, int):
            if output.count(content) != count:
                raise AssertionError(
                    f"'{content}' not {count} times in output:\n{output}"
                )
        else:
            minc, maxc = count
            if not (minc <= output.count(content) <= maxc):
                raise AssertionError(
                    f"'{content}' not {minc}-{maxc} times in output:\n{output}"
                )

    def _remove_files(self):
        for pattern in self.remove_files:
            for path in glob(pattern):
                if exists(path):
                    remove(path)
