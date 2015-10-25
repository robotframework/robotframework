import os
import unittest

from robot.utils.asserts import assert_equals, assert_true
from robot.utils.etreewrapper import ETSource, ET
from robot.utils import IRONPYTHON, PY3


PATH = os.path.join(os.path.dirname(__file__), 'test_etreesource.py')
if PY3:
    unicode = str


class TestETSource(unittest.TestCase):

    def test_path_to_file(self):
        source = ETSource(PATH)
        with source as src:
            assert_equals(src, PATH)
        self._verify_string_representation(source, PATH)
        assert_true(source._opened is None)

    def test_opened_file_object(self):
        source = ETSource(open(PATH))
        with source as src:
            assert_true(src.read().startswith('import os'))
        assert_true(src.closed is False)
        self._verify_string_representation(source, PATH)
        assert_true(source._opened is None)

    def test_byte_string(self):
        self._test_string('\n<tag>content</tag>\n')

    def test_unicode_string(self):
        self._test_string(u'\n<tag>hyv\xe4</tag>\n')

    def _test_string(self, xml):
        source = ETSource(xml)
        with source as src:
            content = src.read()
            if not IRONPYTHON:
                content = content.decode('UTF-8')
            assert_equals(content, xml)
        self._verify_string_representation(source, '<in-memory file>')
        assert_true(source._opened.closed)
        with ETSource(xml) as src:
            assert_equals(ET.parse(src).getroot().tag, 'tag')

    def test_non_ascii_string_repr(self):
        self._verify_string_representation(ETSource(u'\xe4'), u'\xe4')

    def _verify_string_representation(self, source, expected):
        assert_equals(unicode(source), expected)
        assert_equals('-%s-' % source, '-%s-' % expected)


if __name__ == '__main__':
    unittest.main()
