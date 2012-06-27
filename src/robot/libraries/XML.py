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

import re
from functools import partial

from robot.utils import ET, ETSource
from robot.libraries.BuiltIn import BuiltIn


class XML(object):
    _should_be_equal = BuiltIn().should_be_equal
    _should_match = BuiltIn().should_match
    _normalize_whitespace = partial(re.compile('\s+').sub, ' ')

    def parse_xml(self, source):
        with ETSource(source) as source:
            return ET.parse(source).getroot()

    def _get_parent(self, source):
        if isinstance(source, basestring):
            return self.parse_xml(source)
        return source

    def get_element(self, source, match):
        if match == '.':  # TODO: Is this good workaround for ET 1.2 not supporting '.'?
            return self._get_parent(source)
        elements = self.get_elements(source, match)
        if not elements:
            raise RuntimeError("No element matching '%s' found." % match)
        if len(elements) > 1:
            raise RuntimeError("Multiple elements (%d) matching '%s' found."
                               % (len(elements), match))
        return elements[0]

    def get_elements(self, source, match):
        return self._get_parent(source).findall(match)

    def get_element_text(self, source, match='.', normalize_whitespace=False):
        element = self.get_element(source, match)
        text = ''.join(self._yield_texts(element))
        if normalize_whitespace:
            text = self._normalize_whitespace(text).strip()
        return text

    def _yield_texts(self, element, top=True):
        if element.text:
            yield element.text
        for child in element:
            for text in self._yield_texts(child, top=False):
                yield text
        if element.tail and not top:
            yield element.tail

    def get_elements_texts(self, source, match, normalize_whitespace=False):
        return [self.get_element_text(elem, normalize_whitespace=normalize_whitespace)
                for elem in self.get_elements(source, match)]

    def element_text_should_be(self, source, expected, match='.'):
        self._should_be_equal(self.get_element_text(source, match), expected)

    def element_text_should_match(self, source, pattern, match='.'):
        self._should_match(self.get_element_text(source, match), pattern)

    def get_element_attribute(self, source, name, match=None):
        return self.get_element(source, match).get(name)

    def element_attribute_should_match(self, source, name, pattern, match=None):
        self._should_match(self.get_attribute(source, name, match), pattern)

    def element_attribute_should_be(self, source, name, expected, match=None):
        self._should_be_equal(self.get_attribute(source, name, match), expected)
