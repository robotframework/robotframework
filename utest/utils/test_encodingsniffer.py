import unittest
import sys
import os

from robot.utils.encodingsniffer import get_output_encoding
from robot.utils.asserts import assert_equals, assert_not_none


ON_BUGGY_JYTHON = os.sep == '\\' and (sys.platform.startswith('java1.5') or
                                      sys.version_info < (2, 5, 2))


class StreamStub(object):

    def __init__(self, encoding):
        self.encoding = encoding


class TestGetOutputEncodingFromStandardStreams(unittest.TestCase):

    def setUp(self):
        self._orig_streams = sys.__stdout__, sys.__stderr__, sys.__stdin__

    def tearDown(self):
        sys.__stdout__, sys.__stderr__, sys.__stdin__ = self._orig_streams

    def test_valid_encoding(self):
        sys.__stdout__ = StreamStub('ASCII')
        assert_equals(get_output_encoding(), self._get_encoding('ASCII'))

    def test_invalid_encoding(self):
        sys.__stdout__ = StreamStub('invalid')
        sys.__stderr__ = StreamStub('ascII')
        assert_equals(get_output_encoding(), self._get_encoding('ascII'))

    def test_no_encoding(self):
        sys.__stdout__ = object()
        sys.__stderr__ = object()
        sys.__stdin__ = StreamStub('ascii')
        assert_equals(get_output_encoding(), self._get_encoding('ascii'))
        sys.__stdin__ = object()
        assert_not_none(get_output_encoding())

    def test_none_encoding(self):
        sys.__stdout__ = StreamStub(None)
        sys.__stderr__ = StreamStub(None)
        sys.__stdin__ = StreamStub('ascii')
        assert_equals(get_output_encoding(), self._get_encoding('ascii'))
        sys.__stdin__ = StreamStub(None)
        assert_not_none(get_output_encoding())

    def _get_encoding(self, default):
        return default if not ON_BUGGY_JYTHON else 'cp437'


if __name__ == '__main__':
    unittest.main()

