import os
import unittest
import tempfile

from robot. errors import DataError
from robot.utils import XmlWriter, ET, ETSource
from robot.utils.asserts import *

PATH = os.path.join(tempfile.gettempdir(), 'test_xmlwriter.xml')


class TestXmlWriter(unittest.TestCase):

    def setUp(self):
        self.writer = XmlWriter(PATH)

    def tearDown(self):
        self.writer.close()
        os.remove(PATH)

    def test_write_element_in_pieces(self):
        self.writer.start('name', {'attr': 'value'}, newline=False)
        self.writer.content('Some content here!!')
        self.writer.end('name')
        self._verify_node(None, 'name', 'Some content here!!', {'attr': 'value'})

    def test_calling_content_multiple_times(self):
        self.writer.start(u'robot-log', newline=False)
        self.writer.content(u'Hello world!\n')
        self.writer.content(u'Hi again!')
        self.writer.content('\tMy name is John')
        self.writer.end('robot-log')
        self._verify_node(None, 'robot-log',
                          'Hello world!\nHi again!\tMy name is John')

    def test_write_element(self):
        self.writer.element('foo', 'Node\n content',
                            {'a1': 'attr1', 'a2': 'attr2'})
        self._verify_node(None, 'foo', 'Node\n content',
                          {'a1': 'attr1', 'a2': 'attr2'})

    def test_write_many_elements(self):
        self.writer.start('root', {'version': 'test'})
        self.writer.start('child1', {'my-attr': 'my value'})
        self.writer.element('leaf1.1', 'leaf content', {'type': 'kw'})
        self.writer.element('leaf1.2')
        self.writer.end('child1')
        self.writer.element('child2', attrs={'class': 'foo'})
        self.writer.end('root')
        root = self._get_root()
        self._verify_node(root, 'root', attrs={'version': 'test'})
        self._verify_node(root.find('child1'), 'child1', attrs={'my-attr': 'my value'})
        self._verify_node(root.find('child1/leaf1.1'), 'leaf1.1',
                          'leaf content', {'type': 'kw'})
        self._verify_node(root.find('child1/leaf1.2'), 'leaf1.2')
        self._verify_node(root.find('child2'), 'child2', attrs={'class': 'foo'})

    def test_newline_insertion(self):
        self.writer.start('root')
        self.writer.start('suite', {'type': 'directory_suite'})
        self.writer.element('test', attrs={'name': 'my_test'}, newline=False)
        self.writer.element('test', attrs={'name': 'my_2nd_test'})
        self.writer.end('suite', False)
        self.writer.start('suite', {'name': 'another suite'}, newline=False)
        self.writer.content('Suite 2 content')
        self.writer.end('suite')
        self.writer.end('root')
        content = self._get_content()
        lines = [line for line in content.splitlines() if line != '\n']
        assert_equal(len(lines), 6)

    def test_none_content(self):
        self.writer.element(u'robot-log', None)
        self._verify_node(None, 'robot-log')

    def test_none_and_empty_attrs(self):
        self.writer.element('foo', attrs={'empty': '', 'none': None})
        self._verify_node(None, 'foo', attrs={'empty': '', 'none': ''})

    def test_content_with_invalid_command_char(self):
        self.writer.element('robot-log', '\033[31m\033[32m\033[33m\033[m')
        self._verify_node(None, 'robot-log', '[31m[32m[33m[m')

    def test_content_with_invalid_command_char_unicode(self):
        self.writer.element('robot-log', u'\x1b[31m\x1b[32m\x1b[33m\x1b[m')
        self._verify_node(None, 'robot-log', '[31m[32m[33m[m')

    def test_content_with_non_ascii(self):
        self.writer.start('root')
        self.writer.element(u'e', u'Circle is 360\xB0')
        self.writer.element(u'f', u'Hyv\xE4\xE4 \xFC\xF6t\xE4')
        self.writer.end('root')
        root = self._get_root()
        self._verify_node(root.find('e'), 'e', u'Circle is 360\xB0')
        self._verify_node(root.find('f'), 'f', u'Hyv\xE4\xE4 \xFC\xF6t\xE4')

    def test_content_with_entities(self):
        self.writer.element(u'robot-log', 'Me, Myself & I > you')
        self._verify_content('Me, Myself &amp; I &gt; you')

    def test_remove_illegal_chars(self):
        assert_equal(self.writer._escape(u'\x1b[31m'), '[31m')
        assert_equal(self.writer._escape(u'\x00'), '')

    def test_dataerror_when_file_is_invalid(self):
        err = assert_raises(DataError, XmlWriter, os.path.dirname(__file__))
        assert_true(err.message.startswith('Opening file'))

    def test_dataerror_when_file_is_invalid_contains_optional_usage(self):
        err = assert_raises(DataError, XmlWriter, os.path.dirname(__file__),
                            usage='testing')
        assert_true(err.message.startswith('Opening testing file'))

    def test_dont_write_empty(self):
        self.tearDown()
        class NoPreamble(XmlWriter):
            def _preamble(self):
                pass
        self.writer = NoPreamble(PATH, write_empty=False)
        self.writer.element('foo1', content='', attrs={})
        self.writer.element('foo2', attrs={'bar': '', 'None': None})
        self.writer.element('foo3', attrs={'bar': '', 'value': 'value'})
        assert_equal(self._get_content(), '<foo3 value="value"></foo3>\n')

    def _verify_node(self, node, name, text=None, attrs={}):
        if node is None:
            node = self._get_root()
        assert_equal(node.tag, name)
        if text is not None:
            assert_equal(node.text, text)
        assert_equal(node.attrib, attrs)

    def _verify_content(self, expected):
        content = self._get_content()
        assert_true(expected in content,
                    'Failed to find:\n%s\n\nfrom:\n%s' % (expected, content))

    def _get_root(self):
        self.writer.close()
        with ETSource(PATH) as source:
            return ET.parse(source).getroot()

    def _get_content(self):
        self.writer.close()
        with open(PATH) as f:
            return f.read()


if __name__ == '__main__':
    unittest.main()
