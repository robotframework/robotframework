import os
import re
from os.path import abspath, dirname, join
from subprocess import call, STDOUT
from shlex import split
import tempfile


from robot.utils.asserts import assert_equals, assert_true
from robot.utils import decode_output


ROBOT_SRC = join(dirname(abspath(__file__)), '..', '..', '..', 'src')
DATA_DIR = join(dirname(abspath(__file__)), '..', '..', 'testdata', 'tidy')
TEMP_FILE = join(os.getenv('TEMPDIR'), 'tidy-test-dir', 'tidy-test-file.txt')


class TidyLib(object):

    def __init__(self, *command):
        self._tidy = list(command)

    def run_tidy(self, options, input, output=None, tidy=None):
        """Runs tidy in the operating system and returns output."""
        command = (tidy or self._tidy)[:]
        if options:
            command.extend([e.decode('utf8') for e in split(options.encode('utf8'))])
        command.append(self._path(input))
        if output:
            command.append(output)
        print ' '.join(command)
        with tempfile.TemporaryFile() as stdout:
            rc = call(command, stdout=stdout, stderr=STDOUT,
                      cwd=ROBOT_SRC, shell=os.sep=='\\')
            stdout.seek(0)
            content = decode_output(stdout.read().strip())
            if rc:
                raise RuntimeError(content)
            return content

    def run_tidy_and_check_result(self, options, input, output=TEMP_FILE,
                                  expected=None):
        """Runs tidy and checks that output matches content of file `expected`."""
        result = self.run_tidy(options, input, output)
        return self.compare_tidy_results(output or result, expected or input)

    def run_tidy_as_a_script_and_check_result(self, interpreter, options, input,
                                              output=TEMP_FILE, expected=None):
        """Runs tidy and checks that output matches content of file `expected`."""
        tidy = [interpreter, join(ROBOT_SRC, 'robot', 'tidy.py')]
        result = self.run_tidy(options, input, output, tidy)
        return self.compare_tidy_results(output or result, expected or input)

    def compare_tidy_results(self, result, expected, *filters):
        if os.path.isfile(result):
            result = self._read(result)
        filters = [re.compile('^%s$' % f) for f in filters]
        expected = self._read(expected)
        result_lines = result.splitlines()
        expected_lines = expected.splitlines()
        msg = "Actual:\n%s\n\nExpected:\n%s\n\n" \
              % (repr(result).replace('\\n', '\\n\n'),
                 repr(expected).replace('\\n', '\\n\n'))
        assert_equals(len(result_lines), len(expected_lines), msg)
        for res, exp in zip(result_lines, expected_lines):
            filter = self._filter_matches(filters, exp)
            if not filter:
                assert_equals(repr(unicode(res)), repr(unicode(exp)), msg)
            else:
                assert_true(filter.match(res),
                            '%s: %r does not match %r' % (msg, res, filter.pattern))
        return result

    def _filter_matches(self, filters, expected):
        for filter in filters:
            if filter.match(expected):
                return filter
        return None

    def _path(self, path):
        return abspath(join(DATA_DIR, path.replace('/', os.sep)))

    def _read(self, path):
        with open(self._path(path), 'rb') as f:
            return f.read().decode('UTF-8')
