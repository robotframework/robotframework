import unittest
import sys
from robot.api.logger import console

class FakeStdout(object):

    def __init__(self):
        self.flushed = False

    def write(self, text):
        self.text = text

    def flush(self):
        self.flushed = True


class TestLoggingApi(unittest.TestCase):

    def setUp(self):
        self._fake_stdout = FakeStdout()
        sys.__stdout__, self._original = self._fake_stdout, sys.__stdout__

    def tearDown(self):
        sys.__stdout__ = self._original

    def test_console_flushes(self):
        console('foo', newline=False)
        self.assertTrue(self._fake_stdout.flushed)
        self.assertEqual(self._fake_stdout.text, 'foo')


if __name__ == '__main__':
    unittest.main()
