import unittest
import sys
import logging

from robot.utils.asserts import assert_equal, assert_true
from robot.api import logger


class MyStream:

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
        assert_equal(self.stdout.text, stdout)
        assert_equal(self.stderr.text, stderr)


class MockHandler(logging.Handler):

    def __init__(self):
        logging.Handler.__init__(self)
        self.messages = []

    def emit(self, record):
        self.messages.append(record.getMessage())


class TestRedirectToPythonLogging(unittest.TestCase):

    def setUp(self):
        self.handler = MockHandler()
        root = logging.getLogger()
        root.addHandler(self.handler)
        root.setLevel(logging.NOTSET)

    def tearDown(self):
        logging.getLogger().removeHandler(self.handler)

    def test_logged_to_python(self):
        logger.info("Foo")
        logger.debug("Boo")
        logger.trace("Goo")
        logger.write("Doo", 'INFO')
        assert_equal(self.handler.messages, ['Foo', 'Boo', 'Goo', 'Doo'])

    def test_logger_to_python_with_html(self):
        logger.info("Foo", html=True)
        logger.write("Doo", 'INFO', html=True)
        logger.write("Joo", 'HTML')
        assert_equal(self.handler.messages, ['Foo', 'Doo', 'Joo'])

    def test_logger_to_python_with_console(self):
        logger.write("Foo", 'CONSOLE')
        assert_equal(self.handler.messages, ['Foo'])

if __name__ == '__main__':
    unittest.main()
