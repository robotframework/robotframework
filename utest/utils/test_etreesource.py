from __future__ import with_statement
import os
import sys
import unittest

from robot.utils.asserts import assert_equals, assert_raises, assert_true
from robot.utils.etreewrapper import ETSource, ET
from robot.errors import DataError

IRONPYTHON = sys.platform == 'cli'
PATH = os.path.join(os.path.dirname(__file__), 'test_etreesource.py')


class TestETSource(unittest.TestCase):

    def test_path_to_file(self):
        source = ETSource(PATH)
        with source as src:
            if IRONPYTHON:
                assert_equals(src, PATH)
            else:
                assert_true(src.read().startswith('from __future__'))
        self._verify_string_representation(source, PATH)
        if IRONPYTHON:
            assert_true(source._opened is None)
        else:
            assert_true(source._opened.closed)

    def test_opened_file_object(self):
        source = ETSource(open(PATH))
        with source as src:
            assert_true(src.read().startswith('from __future__'))
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
            assert_equals(src.read().decode('UTF-8'), xml)
        self._verify_string_representation(source, '<in-memory file>')
        assert_true(source._opened.closed)
        with ETSource(xml) as src:
            assert_equals(ET.parse(src).getroot().tag, 'tag')

    def test_path_is_validated(self):
        def use(src):
            with src:
                pass
        assert_raises(IOError, use, ETSource('nonex.xml'))

    def test_non_ascii_string_repr(self):
        self._verify_string_representation(ETSource(u'\xe4'), u'\xe4')

    def _verify_string_representation(self, source, expected):
        assert_equals(unicode(source), expected)
        assert_equals('-%s-' % source, '-%s-' % expected)


if __name__ == '__main__':
    unittest.main()
