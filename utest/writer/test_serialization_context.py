import unittest
import os

from robot.writer.serializer import SerializationContext
from robot.parsing.model import TestCaseFile
from robot.utils.asserts import assert_equals

HTML_SOURCE = os.path.abspath('foo.html')
TXT_SOURCE= os.path.abspath('foo.txt')


class TestOutput(unittest.TestCase):

    def test_source_file_is_used_by_default(self):
        self._assert_source(HTML_SOURCE, source=HTML_SOURCE)

    def test_given_path_override_source(self):
        self._assert_source(TXT_SOURCE, source=HTML_SOURCE, path=TXT_SOURCE)

    def _assert_source(self, expected, source=None, path=None):
        ctx = SerializationContext(TestCaseFile(source=source), path=path)
        assert_equals(ctx._get_source(), expected)


class TestFormat(unittest.TestCase):

    def test_format_from_source_file_is_used_by_default(self):
        self._assert_format('html', source=HTML_SOURCE)

    def test_extension_in_path_override_format(self):
        self._assert_format('txt', format='html', path=TXT_SOURCE)

    def test_extension_in_given_path_override_extension_in_source(self):
        self._assert_format('txt', source=HTML_SOURCE, path=TXT_SOURCE)

    def _assert_format(self, expected, source=None, format=None, path=None):
        data = TestCaseFile(source=source)
        ctx = SerializationContext(data, format=format, path=path)
        assert_equals(ctx.format, expected)
