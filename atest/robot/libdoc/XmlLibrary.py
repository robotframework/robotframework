#  Copyright 2008-2012 Nokia Siemens Networks Oyj
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

from __future__ import with_statement

from robot.utils import ET, ETSource
from robot.libraries.BuiltIn import BuiltIn


def should_be_equal(text, expected):
    BuiltIn().should_be_equal(text, expected)

def should_match(text, pattern):
    BuiltIn().should_match(text, pattern)


class XmlLibrary(object):

    def parse_xml(self, source):
        with ETSource(source) as source:
            return ET.parse(source).getroot()

    def get_element(self, node, path=None):
        return node.find(path) if path else node

    def get_elements(self, node, path):
        return node.findall(path)

    def get_element_text(self, node, path):
        return self.get_element(node, path).text or ''

    def get_elements_texts(self, node, path):
        return [elem.text or '' for elem in self.get_elements(node, path)]

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
