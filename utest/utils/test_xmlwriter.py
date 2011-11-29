import os
import unittest
import tempfile

from robot import utils
from robot.utils.asserts import *

PATH = os.path.join(tempfile.gettempdir(), 'test_xmlwriter.xml')


class TestXmlWriter(unittest.TestCase):

    def setUp(self):
        self.writer = utils.XmlWriter(PATH)

    def tearDown(self):
        self.writer.close()
        os.remove(PATH)

    def test_write_element_in_pieces(self):
        self.writer.start('name', {'attr': 'value'}, True)
        self.writer.content('Some content here!!')
        self.writer.end('name', True)
        self.writer.close()
        self._verify_node(None, 'name', '\nSome content here!!',
                          {'attr': 'value'})

    def test_calling_content_multiple_times(self):
        self.writer.start(u'robot-log', newline=False)
        self.writer.content(u'Hello world!\n')
        self.writer.content(u'Hi again!')
        self.writer.content('\tMy name is John')
        self.writer.end('robot-log')
        self.writer.close()
        self._verify_node(None, 'robot-log',
                          'Hello world!\nHi again!\tMy name is John')

    def test_write_element(self):
        self.writer.element('foo', 'Node\n content', {'a1':'attr1', 'a2':'attr2'})
        self.writer.close()
        self._verify_node(None, 'foo', 'Node\n content',
                          {'a1': 'attr1', 'a2': 'attr2'})

    def test_write_many_elements(self):
        self.writer.start('root', {'version': 'test'})
        self.writer.start('child1', {'my-attr': 'my value'})
        self.writer.element('leaf1.1', 'leaf content', {'type': 'kw'})
        self.writer.element('leaf1.2')
        self.writer.end('child1')
        self.writer.element('child2', attributes={'class': 'foo'})
        self.writer.end('root')
        self.writer.close()
        root = utils.ET.parse(PATH).getroot()
        self._verify_node(root, 'root', attrs={'version': 'test'})
        self._verify_node(root.find('child1'), 'child1', attrs={'my-attr': 'my value'})
        self._verify_node(root.find('child1/leaf1.1'), 'leaf1.1',
                          'leaf content', {'type': 'kw'})
        self._verify_node(root.find('child1/leaf1.2'), 'leaf1.2')
        self._verify_node(root.find('child2'), 'child2', attrs={'class': 'foo'})

    def test_newline_insertion(self):
        self.writer.start('root')
        self.writer.start('suite', {'type': 'directory_suite'})
        self.writer.element('test', attributes={'name': 'my_test'},
                                  newline=False)
        self.writer.element('test', attributes={'name': 'my_2nd_test'})
        self.writer.end('suite', False)
        self.writer.start('suite', {'name': 'another suite'},
                                  newline=False)
        self.writer.content('Suite 2 content')
        self.writer.end('suite')
        self.writer.end('root')
        self.writer.close()
        f = open(PATH)
        lines = [ line for line in f.readlines() if line != '\n' ]
        f.close()
        assert_equal(len(lines), 6)

    def test_none_content(self):
        self.writer.element(u'robot-log', None)
        self.writer.close()
        self._verify_node(None, 'robot-log')

    def test_content_with_invalid_command_char(self):
        self.writer.element('robot-log', '\033[31m\033[32m\033[33m\033[m')
        self.writer.close()
        self._verify_node(None, 'robot-log', '[31m[32m[33m[m')

    def test_content_with_invalid_command_char_unicode(self):
        self.writer.element('robot-log', u'\x1b[31m\x1b[32m\x1b[33m\x1b[m')
        self.writer.close()
        self._verify_node(None, 'robot-log', '[31m[32m[33m[m')

    def test_content_with_unicode(self):
        self.writer.start('root')
        self.writer.element(u'e', u'Circle is 360\u00B0')
        self.writer.element(u'f', u'Hyv\u00E4\u00E4 \u00FC\u00F6t\u00E4')
        self.writer.end('root')
        self.writer.close()
        root = utils.ET.parse(PATH).getroot()
        self._verify_node(root.find('e'), 'e', u'Circle is 360\u00B0')
        self._verify_node(root.find('f'), 'f',
                         u'Hyv\u00E4\u00E4 \u00FC\u00F6t\u00E4')


    def test_content_with_entities(self):
        self.writer.element(u'robot-log', 'Me, Myself & I > you')
        self.writer.close()
        f = open(PATH)
        content = f.read()
        f.close()
        assert_true(content.count('Me, Myself &amp; I &gt; you') > 0)

    def test_remove_illegal_chars(self):
        assert_equals(self.writer._escape(u'\x1b[31m'), '[31m')
        assert_equals(self.writer._escape(u'\x00'), '')

    def _verify_node(self, node, name, text=None, attrs={}):
        if node is None:
            node = utils.ET.parse(PATH).getroot()
        assert_equals(node.tag, name)
        if text is not None:
            assert_equals(node.text, text)
        assert_equals(node.attrib, attrs)


if __name__ == '__main__':
    unittest.main()
