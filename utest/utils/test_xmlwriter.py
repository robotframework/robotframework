from collections import OrderedDict
import os
import unittest
import tempfile

from robot. errors import DataError
from robot.utils import ET, ETSource, XmlWriter
from robot.utils.asserts import assert_equal, assert_raises, assert_true

PATH = os.path.join(tempfile.gettempdir(), 'test_xmlwriter.xml')


class XmlWriterWithoutPreamble(XmlWriter):

    def _preamble(self):
        pass


class TestXmlWriter(unittest.TestCase):

    def setUp(self):
        self.writer = XmlWriterWithoutPreamble(PATH)

    def tearDown(self):
        self.writer.close()
        os.remove(PATH)

    def test_write_element_in_pieces(self):
        self.writer.start('name', {'attr': 'value'}, newline=False)
        self.writer.content('Some content here!!')
        self.writer.end('name')
        self._verify_node(None, 'name', 'Some content here!!', {'attr': 'value'})
        self._verify_content('<name attr="value">Some content here!!</name>\n')

    def test_calling_content_multiple_times(self):
        self.writer.start('element', newline=False)
        self.writer.content('Hello world!\n')
        self.writer.content('Hi again!')
        self.writer.content('\tMy name is John')
        self.writer.end('element')
        self._verify_node(None, 'element', 'Hello world!\nHi again!\tMy name is John')
        self._verify_content('<element>Hello world!\nHi again!\tMy name is John</element>\n')

    def test_write_element(self):
        self.writer.element('elem', 'Node\n content',
                            OrderedDict([('a', '1'), ('b', '2'), ('c', '3')]))
        self._verify_node(None, 'elem', 'Node\n content', {'a': '1', 'b': '2', 'c': '3'})
        self._verify_content('<elem a="1" b="2" c="3">Node\n content</elem>\n')

    def test_element_without_content_is_self_closing(self):
        self.writer.element('elem')
        self._verify_node(None, 'elem')
        self._verify_content('<elem/>\n')

    def test_element_with_empty_string_content_is_self_closing(self):
        self.writer.element('elem', '')
        self._verify_node(None, 'elem')
        self._verify_content('<elem/>\n')

    def test_element_with_attributes_but_without_content_is_self_closing(self):
        self.writer.element('elem', attrs={'attr': 'value'})
        self._verify_node(None, 'elem', attrs={'attr': 'value'})
        self._verify_content('<elem attr="value"/>\n')

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
        assert_equal(len(lines), 5)

    def test_none_content(self):
        self.writer.element('robot-log', None)
        self._verify_node(None, 'robot-log')

    def test_none_and_empty_attrs(self):
        self.writer.element('foo', attrs={'empty': '', 'none': None})
        self._verify_node(None, 'foo', attrs={'empty': '', 'none': ''})

    def test_content_with_invalid_command_char(self):
        self.writer.element('robot-log', '\033[31m\033[32m\033[33m\033[m')
        self._verify_node(None, 'robot-log', '[31m[32m[33m[m')

    def test_content_with_invalid_command_char_unicode(self):
        self.writer.element('robot-log', '\x1b[31m\x1b[32m\x1b[33m\x1b[m')
        self._verify_node(None, 'robot-log', '[31m[32m[33m[m')

    def test_content_with_non_ascii(self):
        self.writer.start('root')
        self.writer.element('e', 'Circle is 360°')
        self.writer.element('f', 'Hyvää üötä')
        self.writer.end('root')
        root = self._get_root()
        self._verify_node(root.find('e'), 'e', 'Circle is 360°')
        self._verify_node(root.find('f'), 'f', 'Hyvää üötä')

    def test_content_with_entities(self):
        self.writer.element('I', 'Me, Myself & I > you')
        self._verify_content('<I>Me, Myself &amp; I &gt; you</I>\n')

    def test_remove_illegal_chars(self):
        assert_equal(self.writer._escape('\x1b[31m'), '[31m')
        assert_equal(self.writer._escape('\x00'), '')

    def test_dataerror_when_file_is_invalid(self):
        err = assert_raises(DataError, XmlWriter, os.path.dirname(__file__))
        assert_true(err.message.startswith('Opening file'))

    def test_dataerror_when_file_is_invalid_contains_optional_usage(self):
        err = assert_raises(DataError, XmlWriter, os.path.dirname(__file__),
                            usage='testing')
        assert_true(err.message.startswith('Opening testing file'))

    def test_dont_write_empty(self):
        self.tearDown()
        self.writer = XmlWriterWithoutPreamble(PATH, write_empty=False)
        self.writer.element('e0')
        self.writer.element('e1', content='', attrs={})
        self.writer.element('e2', attrs={'empty': '', 'None': None})
        self.writer.element('e3', attrs={'empty': '', 'value': 'value'})
        assert_equal(self._get_content(), '<e3 value="value"/>\n')

    def _verify_node(self, node, name, text=None, attrs={}):
        if node is None:
            node = self._get_root()
        assert_equal(node.tag, name)
        if text is not None:
            assert_equal(node.text, text)
        assert_equal(node.attrib, attrs)

    def _verify_content(self, expected):
        content = self._get_content()
        assert_equal(expected, content)

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
