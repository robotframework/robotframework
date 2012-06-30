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

from robot.libraries.BuiltIn import BuiltIn
from robot.api import logger
from robot.utils import ET, ETSource


class XML(object):
    """
    Supported xpath is documented here: http://effbot.org/zone/element-xpath.htm
    Notice that support for predicates (e.g. tag[@id="1"]) is supported
    only in 1.3 i.e in Python 2.7!
    """

    _should_be_equal = BuiltIn().should_be_equal
    _should_match = BuiltIn().should_match
    _normalize_whitespace = partial(re.compile('\s+').sub, ' ')
    _xml_declaration = re.compile('^<\?xml .*\?>\n')

    def parse_xml(self, source):
        with ETSource(source) as source:
            return ET.parse(source).getroot()

    def _get_parent(self, source):
        if isinstance(source, basestring):
            return self.parse_xml(source)
        return source

    def get_element(self, source, xpath='.'):
        if xpath == '.':  # TODO: Is this good workaround for ET 1.2 not supporting '.'?
            return self._get_parent(source)
        elements = self.get_elements(source, xpath)
        if not elements:
            raise RuntimeError("No element matching '%s' found." % xpath)
        if len(elements) > 1:
            raise RuntimeError("Multiple elements (%d) matching '%s' found."
                               % (len(elements), xpath))
        return elements[0]

    def get_elements(self, source, xpath):
        return self._get_parent(source).findall(xpath)

    def get_element_text(self, source, xpath='.', normalize_whitespace=False):
        element = self.get_element(source, xpath)
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

    def get_elements_texts(self, source, xpath, normalize_whitespace=False):
        return [self.get_element_text(elem, normalize_whitespace=normalize_whitespace)
                for elem in self.get_elements(source, xpath)]

    def element_text_should_be(self, source, expected, xpath='.',
                               normalize_whitespace=False, message=None):
        text = self.get_element_text(source, xpath, normalize_whitespace)
        self._should_be_equal(text, expected, message, values=False)

    def element_text_should_match(self, source, pattern, xpath='.',
                                  normalize_whitespace=False, message=None):
        text = self.get_element_text(source, xpath, normalize_whitespace)
        self._should_match(text, pattern, message, values=False)

    def get_element_attribute(self, source, name, xpath='.', default=None):
        return self.get_element(source, xpath).get(name, default)

    def get_element_attributes(self, source, xpath='.'):
        return self.get_element(source, xpath).attrib.copy()

    def element_attribute_should_be(self, source, name, expected, xpath='.',
                                    message=None):
        attr = self.get_element_attribute(source, name, xpath)
        self._should_be_equal(attr, expected, message, values=False)

    def element_attribute_should_match(self, source, name, pattern, xpath='.',
                                       message=None):
        attr = self.get_element_attribute(source, name, xpath)
        if attr is None:
            raise AssertionError("Attribute '%s' does not exist." % name)
        self._should_match(attr, pattern, message, values=False)

    def elements_should_be_equal(self, source, expected,
                                 normalize_whitespace=False):
        ElementComparator(self._should_be_equal).compare(self.get_element(source),
            self.get_element(expected), normalize_whitespace)

    def elements_should_match(self, source, expected, normalize_whitespace=False):
        ElementComparator(self._should_match).compare(self.get_element(source),
                self.get_element(expected), normalize_whitespace)

    def element_to_string(self, source):
        string = ET.tostring(self.get_element(source), encoding='UTF-8')
        return self._xml_declaration.sub('', string.decode('UTF-8'))

    def log_element(self, source, level='INFO'):
        string = self.element_to_string(source)
        logger.write(string, level)
        return string


class ElementComparator(object):
    _should_be_equal = BuiltIn().should_be_equal

    def __init__(self, comparator):
        self._comparator = comparator

    def compare(self, actual, expected, normalize_whitespace):
        self._compare_tag_name(actual, expected)
        self._compare_texts(actual, expected)
        self._compare_attributes(actual, expected)
        self._compare_tails(actual, expected)
        self._compare_children(actual, expected, normalize_whitespace)

    def _compare_tag_name(self, actual, expected):
        self._should_be_equal(actual.tag, expected.tag, 'Different tag name')

    def _compare_texts(self, actual, expected):
        self._comparator(actual.text or '', expected.text or '',
                         'Different text')

    def _compare_attributes(self, actual, expected):
        act_names = sorted(actual.attrib.keys())
        exp_names = sorted(expected.attrib.keys())
        self._should_be_equal(act_names, exp_names, 'Different attribute names')
        for key in actual.attrib:
            act, exp = actual.attrib[key], expected.attrib[key]
            self._comparator(act, exp, 'Different value for attribute %s' % key)

    def _compare_tails(self, actual, expected):
        self._comparator(actual.tail or '', expected.tail or '',
                         'Different tail text')

    def _compare_children(self, actual, expected, normalize_whitespace):
        self._should_be_equal(len(actual), len(expected),
                              'Different number of child elements')
        for a, e in zip(actual, expected):
            self.compare(a, e, normalize_whitespace)
