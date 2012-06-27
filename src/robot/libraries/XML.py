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


should_be_equal = BuiltIn().should_be_equal
should_match = BuiltIn().should_match


class XML(object):

    def parse_xml(self, source):
        with ETSource(source) as source:
            return ET.parse(source).getroot()

    def _get_parent(self, source):
        if isinstance(source, basestring):
            return self.parse_xml(source)
        return source

    def get_element(self, source, match):
        parent = self._get_parent(source)
        return parent.find(match) if match else parent

    def get_elements(self, source, match):
        return self._get_parent(source).findall(match)

    def get_element_text(self, source, match):
        return self.get_element(source, match).text or ''

    def get_elements_texts(self, source, match):
        return [elem.text or '' for elem in self.get_elements(source, match)]

    def element_text_should_be(self, source, expected, match=None):
        should_be_equal(self.get_element_text(source, match), expected)

    def element_text_should_match(self, source, pattern, match=None):
        should_match(self.get_element_text(source, match), pattern)

    def get_attribute(self, source, name, match=None):
        return self.get_element(source, match).get(name)

    def element_attribute_should_match(self, source, name, pattern, match=None):
        should_match(self.get_attribute(source, name, match), pattern)

    def element_attribute_should_be(self, source, name, expected, match=None):
        should_be_equal(self.get_attribute(source, name, match), expected)
