import os
import unittest

from robot.utils.asserts import assert_equal, assert_true
from robot.utils.etreewrapper import ETSource, ET, IRONPYTHON_WITH_BROKEN_ETREE
from robot.utils import console_decode as fsencode, unicode, PY_VERSION, PY3

if PY3:
    import pathlib
    from os import fsencode

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
        self._test_path(fsencode(PATH), PATH)

    if PY3:

        def test_pathlib_path(self):
            expected = PATH if PY_VERSION < (3, 6) else pathlib.Path(PATH)
            self._test_path(pathlib.Path(PATH), PATH, expected)

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
        self._test_string(u'<tag>hyv\xe4</tag>'.encode('utf8'))
        self._test_string(u'<?xml version="1.0" encoding="Latin1"?>\n'
                          u'<tag>hyv\xe4</tag>'.encode('latin-1'), 'latin-1')

    def test_unicode_string(self):
        self._test_string(u'\n<tag>hyv\xe4</tag>\n')
        self._test_string(u'<?xml version="1.0" encoding="latin1"?>\n'
                          u'<tag>hyv\xe4</tag>', 'latin-1')
        self._test_string(u"<?xml version='1.0' encoding='iso-8859-1' standalone='yes'?>\n"
                          u"<tag>hyv\xe4</tag>", 'latin-1')

    def _test_string(self, xml, encoding='UTF-8'):
        source = ETSource(xml)
        with source as src:
            content = src.read()
            if IRONPYTHON_WITH_BROKEN_ETREE:
                content = content.encode(encoding)
            expected = xml if isinstance(xml, bytes) else xml.encode(encoding)
            assert_equal(content, expected)
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
