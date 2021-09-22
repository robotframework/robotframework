import unittest
import sys

from robot.utils.asserts import assert_equal, assert_not_none
from robot.utils.encodingsniffer import get_console_encoding
from robot.utils import WINDOWS


class StreamStub(object):

    def __init__(self, encoding, isatty=True):
        self.encoding = encoding
        self.isatty = lambda: isatty


class TestGetConsoleEncodingFromStandardStreams(unittest.TestCase):

    def setUp(self):
        self._orig_streams = sys.__stdout__, sys.__stderr__, sys.__stdin__

    def tearDown(self):
        sys.__stdout__, sys.__stderr__, sys.__stdin__ = self._orig_streams

    def test_valid_encoding(self):
        sys.__stdout__ = StreamStub('ASCII')
        assert_equal(get_console_encoding(), 'ASCII')

    def test_invalid_encoding(self):
        sys.__stdout__ = StreamStub('invalid')
        sys.__stderr__ = StreamStub('ascII')
        assert_equal(get_console_encoding(), 'ascII')

    def test_no_encoding(self):
        sys.__stdout__ = object()
        sys.__stderr__ = object()
        sys.__stdin__ = StreamStub('ascii')
        assert_equal(get_console_encoding(), 'ascii')
        sys.__stdin__ = object()
        assert_not_none(get_console_encoding())

    def test_none_encoding(self):
        sys.__stdout__ = StreamStub(None)
        sys.__stderr__ = StreamStub(None)
        sys.__stdin__ = StreamStub('ascii')
        assert_equal(get_console_encoding(), 'ascii')
        sys.__stdin__ = StreamStub(None)
        assert_not_none(get_console_encoding())

    def test_non_tty_streams_are_not_used(self):
        sys.__stdout__ = StreamStub('utf-8', isatty=False)
        sys.__stderr__ = StreamStub('latin-1', isatty=False)
        sys.__stdin__ = StreamStub('ascii')
        assert_equal(get_console_encoding(), 'ascii')


# We don't look at streams on Windows. Our `isatty` doesn't consider StreamSub a tty.
if WINDOWS:
    del TestGetConsoleEncodingFromStandardStreams


if __name__ == '__main__':
    unittest.main()
