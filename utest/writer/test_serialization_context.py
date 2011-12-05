import unittest

from robot.writer.serializer import SerializationContext
from robot.parsing.model import TestCaseFile
from robot.utils.asserts import assert_equals


class TestSerializationContext(unittest.TestCase):

    def test_format_from_source_file_is_used_by_default(self):
        self._assert_format('html', source='foo.html')

    def test_extension_in_path_override_format(self):
        self._assert_format('txt', format='html', path='foo.txt')

    def test_extension_in_given_path_override_extension_in_sources(self):
        self._assert_format('txt', source='foo.html', path='foo.txt')

    def _assert_format(self, expected, source=None, format=None, path=None):
        data = TestCaseFile(source=source)
        ctx = SerializationContext(data, format=format, path=path)
        assert_equals(ctx.format, expected)
