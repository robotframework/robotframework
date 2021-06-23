import os
import re
import shlex
from os.path import abspath, dirname, join
from subprocess import run, PIPE, STDOUT


from robot.utils.asserts import assert_equal, assert_true


ROBOT_SRC = join(dirname(abspath(__file__)), '..', '..', '..', 'src')
DATA_DIR = join(dirname(abspath(__file__)), '..', '..', 'testdata', 'tidy')
OUTFILE = join(os.getenv('TEMPDIR'), 'tidy-test-dir', 'tidy-test-file.robot')
DEPRECATION = ("The built-in Tidy tool (\'robot.tidy\') has been deprecated in "
               "favor of the new and enhanced external Robotidy tool. Learn "
               "more about the new tool at https://robotidy.readthedocs.io/.\n")


class TidyLib(object):

    def __init__(self, interpreter):
        self._tidy = interpreter.tidy
        self._interpreter = interpreter.interpreter

    def run_tidy(self, options=None, input=None, output=None, tidy=None, rc=0,
                 deprecation=True):
        """Runs tidy in the operating system and returns output."""
        command = (tidy or self._tidy)[:]
        if options:
            command.extend(shlex.split(options))
        if input:
            command.append(self._path(input))
        if output:
            command.append(output)
        print(' '.join(command))
        result = run(command,
                     cwd=ROBOT_SRC,
                     stdout=PIPE,
                     stderr=PIPE,
                     universal_newlines=True,
                     shell=os.sep == '\\')
        output = result.stdout.rstrip()
        print('\n' + output)
        if deprecation and result.stderr != DEPRECATION:
            raise RuntimeError(f'No deprecation warning in stderr:\n')
        if result.returncode != rc:
            raise RuntimeError(f'Expected Tidy to return {rc} but it returned '
                               f'{result.returncode}.')
        return output

    def run_tidy_and_check_result(self, options=None, input=None,
                                  output=OUTFILE, expected=None):
        """Runs tidy and checks that output matches content of file `expected`."""
        result = self.run_tidy(options, input, output)
        return self.compare_tidy_results(output or result, expected or input)

    def run_tidy_as_script_and_check_result(self, options=None, input=None,
                                            output=OUTFILE, expected=None):
        """Runs tidy and checks that output matches content of file `expected`."""
        tidy = self._interpreter + [join(ROBOT_SRC, 'robot', 'tidy.py')]
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
        assert_equal(len(result_lines), len(expected_lines), msg)
        for res, exp in zip(result_lines, expected_lines):
            filter = self._filter_matches(filters, exp)
            if not filter:
                assert_equal(repr(res), repr(exp), msg)
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
