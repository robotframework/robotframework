import unittest
import sys

from robot.utils.asserts import assert_equals, assert_true
from robot.api import logger


class MyStream(object):

    def __init__(self):
        self.flushed = False
        self.text = ''

    def write(self, text):
        self.text += text

    def flush(self):
        self.flushed = True


class TestConsole(unittest.TestCase):

    def setUp(self):
        self.original_stdout = sys.__stdout__
        sys.__stdout__ = self.stdout = MyStream()
        self.original_stderr = sys.__stderr__
        sys.__stderr__ = self.stderr = MyStream()

    def tearDown(self):
        sys.__stdout__ = self.original_stdout
        sys.__stderr__ = self.original_stderr

    def test_automatic_newline(self):
        logger.console('foo')
        self._verify('foo\n')

    def test_flushing(self):
        logger.console('foo', newline=False)
        self._verify('foo')
        assert_true(self.stdout.flushed)

    def test_streams(self):
        logger.console('to stdout', stream='stdout')
        logger.console('to stderr', stream='stdERR')
        logger.console('to stdout too', stream='invalid')
        self._verify('to stdout\nto stdout too\n', 'to stderr\n')

    def _verify(self, stdout='', stderr=''):
        assert_equals(self.stdout.text, stdout)
        assert_equals(self.stderr.text, stderr)


if __name__ == '__main__':
    unittest.main()
