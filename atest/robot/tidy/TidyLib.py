from __future__ import with_statement

import os
from os.path import abspath, dirname, join
from subprocess import call, STDOUT
import tempfile

from robot import DataError
from robot.utils.asserts import assert_equals
from robot.tidy import TidyCommandLine
import robot.tidy

ROBOT_SRC = join(dirname(abspath(__file__)), '..', '..', '..', 'src')


class TidyLib(object):

    def __init__(self, interpreter):
        self._cmd = [interpreter, '-m', 'robot.tidy']
        path_var = 'PYTHONPATH' if 'python' in interpreter else 'JYTHONPATH'
        self._env = os.environ
        self._env.update({path_var: ROBOT_SRC})

    def run_tidy_and_return_output(self, options, input):
        """Runs tidy in the operating system and returns output."""
        options = options.split(' ') if options else []
        with tempfile.TemporaryFile() as output:
            rc = call(self._cmd + options + [self._path(input)],
                      stdout=output, stderr=STDOUT,
                      env=self._env)
            output.seek(0)
            content = output.read()
            if rc:
                raise RuntimeError(content)
            return content

    def run_tidy_and_check_result(self, options, input, expected):
        """Runs tidy and checks that output matches content of file `expected`."""
        result = self.run_tidy_and_return_output(options, input)
        self._assert_result(result, open(self._path(expected)).read())

    def _path(self, path):
        return path.replace('/', os.sep)

    def _assert_result(self, result, expected):
        result = result.decode('UTF-8')
        expected = expected.decode('UTF-8')
        for line1, line2 in zip(result.split(), expected.split()):
            msg = "\n%s\n!=\n%s\n" % (result, expected)
            assert_equals(repr(unicode(line1)), repr(unicode(line2)), msg)

    def run_tidy(self, argument_string):
        """Runs tidy programmatically. Fails if there are any expections."""
        runner = TidyCommandLine(robot.tidy.__doc__)
        try:
            runner.run([str(a) for a in argument_string.split()])
        except DataError, err:
            raise RuntimeError(unicode(err))
