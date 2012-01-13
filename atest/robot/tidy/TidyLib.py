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

    def run_tidy_and_return_output(self, input, options):
        options = options.split(' ') if options else []
        with tempfile.TemporaryFile() as output:
            rc = call(self._cmd + options + [self._path(input)],
                      stdout=output, stderr=STDOUT,
                      env={'PYTHONPATH': ROBOT_SRC})
            output.seek(0)
            content = output.read()
            if rc:
                raise RuntimeError(content)
            return content

    def _path(self, path):
        return path.replace('/', os.sep)

    def run_tidy_and_check_result(self, input, options, expected):
        result = self.run_tidy_and_return_output(input, options)
        self._assert_result(result, open(self._path(expected)).read())

    def _assert_result(self, result, expected):
        for line1, line2 in zip(result.split(), expected.split()):
            msg = "\n%s\n!=\n%s\n" % (result, expected)
            assert_equals(repr(unicode(line1)), repr(unicode(line2)), msg)
