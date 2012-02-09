from xml.etree import ElementTree as ET
from robot.libraries.BuiltIn import BuiltIn


def should_be_equal(text, expected):
    BuiltIn().should_be_equal(text, expected)

def should_match(text, pattern):
    BuiltIn().should_match(text, pattern)


class XmlLibrary(object):

    def parse_xml_file(self, source):
        return ET.parse(source).getroot()

    def parse_xml_text(self, text):
        return ET.XML(text)

    def get_element(self, node, path=None):
        return node.find(path) if path else node

    def get_elements(self, node, path):
        return node.findall(path)

    def get_element_text(self, node, path):
        return self.get_element(node, path).text

    def element_text_should_be(self, node, expected, path=None):
        should_be_equal(self.get_element_text(node, path), expected)

    def element_text_should_match(self, node, pattern, path=None):
        should_match(self.get_element_text(node, path), pattern)

    def get_attribute(self, node, name, path=None):
        return self.get_element(node, path).get(name)

    def attribute_should_match(self, node, name, pattern, path=None):
        should_match(self.get_attribute(node, name, path), pattern)

    def attribute_should_be(self, node, name, expected, path=None):
        should_be_equal(self.get_attribute(node, name, path), expected)
