from __future__ import with_statement
import os
import unittest

from robot.utils.asserts import assert_equals, assert_raises, assert_true
from robot.utils.xmlsource import XmlSource
from robot.errors import DataError


class TestXmlSource(unittest.TestCase):

    def test_creating_from_filename(self):
        source = XmlSource(__file__)
        with source as src:
            assert_equals(src, __file__)
        self._verify_string_representation(source, __file__)

    def test_xml_like_string_is_opened(self):
        xml = '<tag>content</tag>'
        source = XmlSource(xml)
        with source as src:
            assert_equals(src.read(), xml)
        self._verify_string_representation(source, '<in-memory file>')

    def test_opened_file_object_can_be_used(self):
        fname = os.path.join(os.path.dirname(__file__), 'test_xmlsource.py')
        source = XmlSource(open(fname))
        with source as src:
            assert_true(src.read().startswith('from __future__'))
        assert_true(src.closed is False)
        self._verify_string_representation(source, fname)

    def test_filename_is_validated(self):
        def use(src):
            with src:
                pass
        assert_raises(DataError, use, XmlSource('nonex.xml'))

    def test_non_ascii_string_repr(self):
        self._verify_string_representation(XmlSource(u'\xe4'), u'\xe4')

    def _verify_string_representation(self, source, expected):
        assert_equals(unicode(source), expected)
        assert_equals('-%s-' % source, '-%s-' % expected)
