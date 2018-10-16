import os
import unittest

from robot.utils.asserts import assert_equal, assert_true
from robot.utils.etreewrapper import ETSource, ET, IRONPYTHON_WITH_BROKEN_ETREE
from robot.utils import unicode


PATH = os.path.join(os.path.dirname(__file__), 'test_etreesource.py')


class TestETSource(unittest.TestCase):

    def test_path_to_file(self):
        source = ETSource(PATH)
        with source as src:
            assert_equal(src, PATH)
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
            if not IRONPYTHON_WITH_BROKEN_ETREE:
                content = content.decode('UTF-8')
            assert_equal(content, xml)
        self._verify_string_representation(source, '<in-memory file>')
        assert_true(source._opened.closed)
        with ETSource(xml) as src:
            assert_equal(ET.parse(src).getroot().tag, 'tag')

    def test_non_ascii_string_repr(self):
        self._verify_string_representation(ETSource(u'\xe4'), u'\xe4')

    def _verify_string_representation(self, source, expected):
        assert_equal(unicode(source), expected)
        assert_equal(u'-%s-' % source, '-%s-' % expected)


if __name__ == '__main__':
    unittest.main()
