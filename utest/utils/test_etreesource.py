import os
import unittest
import pathlib

from robot.utils.asserts import assert_equal, assert_true
from robot.utils.etreewrapper import ETSource, ET


PATH = os.path.join(os.path.dirname(__file__), 'test_etreesource.py')


class TestETSource(unittest.TestCase):

    def test_path(self):
        self._test_path(PATH)

    def _test_path(self, path, string_repr=None, expected=None):
        source = ETSource(path)
        with source as src:
            assert_equal(src, expected or path)
        self._verify_string_representation(source, string_repr or path)
        assert_true(source._opened is None)

    def test_bytes_path(self):
        self._test_path(os.fsencode(PATH), PATH)

    def test_pathlib_path(self):
        self._test_path(pathlib.Path(PATH), PATH, pathlib.Path(PATH))

    def test_opened_file_object(self):
        with open(PATH) as f:
            source = ETSource(f)
            with source as src:
                assert_true(src.read().startswith('import os'))
                assert_true(src is f)
            assert_true(src.closed is False)
            self._verify_string_representation(source, PATH)
            assert_true(source._opened is None)
            assert_true(src is f)
        assert_true(src.closed is True)

    def test_string(self):
        self._test_string('\n<tag>content</tag>\n')

    def test_byte_string(self):
        self._test_string(b'\n<tag>content</tag>')
        self._test_string('<tag>hyv\xe4</tag>'.encode('utf8'))
        self._test_string('<?xml version="1.0" encoding="Latin1"?>\n'
                          '<tag>hyv\xe4</tag>'.encode('latin-1'), 'latin-1')

    def test_unicode_string(self):
        self._test_string('\n<tag>hyv\xe4</tag>\n')
        self._test_string('<?xml version="1.0" encoding="latin1"?>\n'
                          '<tag>hyv\xe4</tag>', 'latin-1')
        self._test_string("<?xml version='1.0' encoding='iso-8859-1' standalone='yes'?>\n"
                          "<tag>hyv\xe4</tag>", 'latin-1')

    def _test_string(self, xml, encoding='UTF-8'):
        source = ETSource(xml)
        with source as src:
            content = src.read()
            expected = xml if isinstance(xml, bytes) else xml.encode(encoding)
            assert_equal(content, expected)
        self._verify_string_representation(source, '<in-memory file>')
        assert_true(source._opened.closed)
        with ETSource(xml) as src:
            assert_equal(ET.parse(src).getroot().tag, 'tag')

    def test_non_ascii_string_repr(self):
        self._verify_string_representation(ETSource('\xe4'), '\xe4')

    def _verify_string_representation(self, source, expected):
        assert_equal(str(source), expected)
        assert_equal('-%s-' % source, '-%s-' % expected)


if __name__ == '__main__':
    unittest.main()
