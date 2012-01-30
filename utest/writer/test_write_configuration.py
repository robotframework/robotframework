import unittest
import os

from robot.errors import DataError
from robot.writer.datafilewriter import WritingContext
from robot.parsing.model import TestCaseFile
from robot.utils.asserts import assert_equals, assert_raises

HTML_SOURCE = os.path.abspath('foo.html')
TXT_SOURCE= os.path.abspath('foo.txt')


class TestOutputFile(unittest.TestCase):

    def test_source_file_is_used_by_default(self):
        self._assert_output_file(HTML_SOURCE, source=HTML_SOURCE)

    def test_given_format_overrides_source_extension(self):
        self._assert_output_file(TXT_SOURCE, HTML_SOURCE, format='txt')

    def _assert_output_file(self, expected, source=None, format=''):
        ctx = WritingContext(TestCaseFile(source=source), format=format)
        assert_equals(ctx._output_path()  , expected)


class TestFormat(unittest.TestCase):

    def test_format_from_source_file_is_used_by_default(self):
        self._assert_format('html', source=HTML_SOURCE)

    def test_explicit_format_overrides_default(self):
        self._assert_format('txt', source=HTML_SOURCE, format='txt')

    def test_creating_with_invalid_format_fails(self):
        assert_raises(DataError, WritingContext, datafile=None, format='inv')

    def _assert_format(self, expected, source, format=''):
        data = TestCaseFile(source=source)
        ctx = WritingContext(data, format=format)
        assert_equals(ctx.format, expected)
