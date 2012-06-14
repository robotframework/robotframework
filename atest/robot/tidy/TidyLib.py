from __future__ import with_statement

import os
from os.path import abspath, dirname, join
from subprocess import call, STDOUT
import tempfile

from robot.utils.asserts import assert_equals

ROBOT_SRC = join(dirname(abspath(__file__)), '..', '..', '..', 'src')


class TidyLib(object):

    def __init__(self, interpreter):
        self._cmd = [interpreter, '-m', 'robot.tidy']
        self._interpreter = interpreter

    def run_tidy(self, options, input, command=None):
        """Runs tidy in the operating system and returns output."""
        options = options.split(' ') if options else []
        with tempfile.TemporaryFile() as output:
            rc = call(self._cmd + options + [self._path(input)], stdout=output,
                      stderr=STDOUT, cwd=ROBOT_SRC, shell=os.sep=='\\')
            output.seek(0)
            content = output.read()
            if rc:
                raise RuntimeError(content)
            return content.decode('UTF-8')

    def run_tidy_and_check_result(self, options, input, expected=None):
        """Runs tidy and checks that output matches content of file `expected`."""
        result = self.run_tidy(options, input)
        self.compare_tidy_results(result, expected or input)

    def run_tidy_as_a_script_and_check_result(self, options, input, expected=None):
        """Runs tidy and checks that output matches content of file `expected`."""
        cmd = [self._interpreter, join(ROBOT_SRC, 'robot', 'tidy.py')]
        result = self.run_tidy(options, input, cmd)
        self.compare_tidy_results(result, expected or input)

    def compare_tidy_results(self, result, expected):
        if os.path.isfile(result):
            result = self._read(result)
        if os.path.isfile(expected):
            expected = self._read(expected)
        result_lines = result.splitlines()
        expected_lines = expected.splitlines()
        msg = "Actual:\n%s\n\nExpected:\n%s\n\n" % (repr(result), repr(expected))
        assert_equals(len(result_lines), len(expected_lines), msg)
        for line1, line2 in zip(result_lines, expected_lines):
            assert_equals(repr(unicode(line1)), repr(unicode(line2)), msg)

    def _path(self, path):
        return path.replace('/', os.sep)

    def _read(self, path):
        with open(self._path(path)) as f:
            return f.read().decode('UTF-8')
