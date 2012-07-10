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
import sys

from robot.api import logger
from robot.libraries.BuiltIn import BuiltIn
from robot.utils import ET, ETSource


should_be_equal = BuiltIn().should_be_equal
should_match = BuiltIn().should_match


class XML(object):
    """Robot Framework test library for XML verification.

    As the name implies, `XML` is a test library for verifying contents of XML
    files. In practice this library is a pretty thin wrapper on top of Python's
    [http://docs.python.org/library/xml.etree.elementtree.html|ElementTree XML API].

    The library has the following three main usages:

    - Parsing an XML file, or a string containing XML, into an element structure
      and finding certain elements from it for for further analysis
      (e.g. `Parse XML` and `Get Element` keywords).
    - Getting text or attributes of a certain element
      (e.g. `Get Element Text` and `Get Element Attribute`)
    - Directly verifying text or attributes of a certain element
      (e.g `Element Text Should Be` and `Element Attribute Should Match`)

    *Finding elements with xpath*

    ElementTree, and thus also this library, supports finding elements using
    xpath expressions. ElementTree does not, however, support the full xpath
    syntax, and what is supported depends on its version. ElementTree 1.3 that
    is distributed with Python/Jython 2.7 supports richer syntax than versions
    distributed with earlier Python interpreters.

    Supported xpath syntax is explained below and
    [http://effbot.org/zone/element-xpath.htm|ElementTree documentation]
    provides more details. In the examples `${XML}` refers to the following
    example structure:

    | <example>
    |   <first>text</first>
    |   <second id="2">
    |     <child/>
    |   </second>
    |   <third>
    |     <child>more text</child>
    |     <second id="child"/>
    |     <child><grandchild/></child>
    |   </third>
    |   <html>
    |     <p>
    |       Text with <b>bold</b> and <i>italics</i>.
    |     </p>
    |   </html>
    | </example>

    The actual contents fo ${XML} can be either path to a file containing the above
    structure, the string containing the above structure, or the parsed ElementTree
    element.

    _Tag names_

    When just a single tag name is used, xpath matches all direct child
    elements that have that tag name.

    | ${elem} =        | Get Element   | ${XML}      | third  |
    | Should Be Equal  | ${elem.tag}   | third       |        |
    | @{children} =    | Get Elements  | ${elem}     | child  |
    | Length Should Be | ${children}   | 2           |        |

    _Paths_

    Paths are created by combining tag names with a forward slash (`/`).
    For example, `parent/child` matches all `child` elements under `parent`
    element. Notice that if there are multiple `parent` elements that all
    have `child` elements, `parent/child` xpath will match all these `child`
    elements.

    | ${elem} = | Get Element | ${XML} | second/child            |
    | ${elem} = | Get Element | ${XML} | third/child/grandchild  |

    _Wildcards_

    An asterisk (`*`) can be used in paths instead of a tag name to denote
    any element.

    | @{children} =    | Get Elements | ${XML} | */child |
    | Length Should Be | ${children}  | 3      |         |

    _Current element_

    The current element is denoted with a dot (`.`). Normally the current
    element is implicit and does not need to be included in the path.

    _Parent element_

    The parent element of another element is denoted with two dots (`..`).
    Notice that it is not possible to refer to the parent of the current
    element. This syntax is supported only in ElementTree 1.3 that is
    distributed with Python/Jython 2.7.

    | ${elem} =       | Get Element | ${XML} | */second/.. |
    | Should Be Equal | ${elem.tag} | third  |             |

    _Search all sub elements_

    Two forward slashes (`//`) mean that all sub elements, not only the
    direct children, are searched. If the search is started from the current
    element, an explicit dot is required.

    | @{elements} =    | Get Elements | ${XML} | .//second |
    | Length Should Be | ${elements}  | 2      |           |

    _Predicates_

    Predicates allow selecting elements using also other criteria than tag
    names such as attributes or position. They are specified after the normal
    tag name or path using syntax `path[predicate]`. The path can have
    wildcards and other special syntax explained above.

    Notice that predicates are supported only in ElementTree 1.3 that is
    shipped with Python/Jython 2.7. What predicates are supported in that
    version is explained in the table below.

    | _Predicate_     | _Matches_ | _Example_ |
    | @attrib         | Elements with attribute `attrib`. | second[@id] |
    | @attrib="value" | Elements with attribute `attrib` having value `value`. | *[@id="2"] |
    | position        | Elements at the specified position. Position can be an integer (starting from 1), expression `last()`, or relative expression like `last() - 1`. | third/child[1] |
    | tag             | Elements with a child element named `tag`. | third/child[grandchild] |

    Predicates can also be stacked like `path[predicate1][predicate2]`.
    A limitation is that possible position predicate must always be first.

    *Elements attributes*

    All keywords returning elements, such as `Parse XML`, and `Get Element`,
    return ElementTree's
    [http://docs.python.org/library/xml.etree.elementtree.html#xml.etree.ElementTree.Element|Element classes].
    These elements can be used as inputs for other keywords, but they also
    contain several useful attributes that can be accessed directly using
    the extended variable syntax.

    The attributes that are both useful and convenient to use in the test
    data are explained below. Also other attributes, including methods, can
    be accessed, but that is typically better to do in custom libraries than
    directly in the test data.

    The examples use same `${XML}` structure as earlier examples.

    _tag_

    The tag of the element.

    | ${root} =       | Parse XML   | ${XML}  |
    | Should Be Equal | ${root.tag} | example |

    _text_

    The text that the element contains or Python `None` if the element has no
    text. Notice that the text _does not_ contain texts of possible child
    elements nor text after or between children. Notice also that in XML
    whitespace is significant, so the text contains also possible indentation
    and newlines. To get also text of the possible children, optionally
    whitespace normalized, use `Get Element Text` keyword.

    | ${1st} =        | Get Element | ${XML}  | first        |
    | Should Be Equal | ${1st.text} | text    |              |
    | ${2nd} =        | Get Element | ${XML}  | second/child |
    | Should Be Equal | ${2nd.text} | ${NONE} |              |
    | ${p} =          | Get Element | ${XML}  | html/p       |
    | Should Be Equal | ${p.text}   | \\n${SPACE*6}Text with${SPACE} |

    _tail_

    The text after the element before the next opening or closing tag. Python
    `None` if the element has no tail. Similarly as with `text`, also `tail`
    contains possible indentation and newlines.

    | ${b} =          | Get Element    | ${XML}  | html/p/b  |
    | Should Be Equal | ${b.tail}      | ${SPACE}and${SPACE} |

    _attrib_

    A Python dictionary containing attributes of the element.

    | ${1st} =        | Get Element         | ${XML} | first  |
    | Should Be Empty | ${1st.attrib}       |        |        |
    | ${2nd} =        | Get Element         | ${XML} | second |
    | Should Be Equal | ${2nd.attrib['id']} | 2      |        |
    """

    ROBOT_LIBRARY_SCOPE = 'GLOBAL'
    _whitespace = re.compile('\s+')
    _xml_declaration = re.compile('^<\?xml .*\?>\n')

    def parse_xml(self, source):
        with ETSource(source) as source:
            return ET.parse(source).getroot()

    def get_element(self, source, xpath='.'):
        elements = self.get_elements(source, xpath)
        if not elements:
            raise RuntimeError("No element matching '%s' found." % xpath)
        if len(elements) > 1:
            raise RuntimeError("Multiple elements (%d) matching '%s' found."
                               % (len(elements), xpath))
        return elements[0]

    def get_elements(self, source, xpath):
        source = self._parse_xml(source)
        if xpath == '.':  # ET < 1.3 does not support '.' alone.
            return [source]
        return source.findall(self._get_xpath(xpath))

    def _parse_xml(self, source):
        if isinstance(source, basestring):
            return self.parse_xml(source)
        return source

    if sys.version_info >= (2, 7):
        def _get_xpath(self, xpath):
            return xpath
    else:
        def _get_xpath(self, xpath):
            try:
                return str(xpath)
            except UnicodeError:
                if not xpath.replace('/', '').isalnum():
                    logger.warn('XPATHs containing non-ASCII characters and '
                                'other than tag names do not always work with '
                                'Python/Jython versions prior to 2.7. Verify '
                                'results manually and consider upgrading to 2.7.')
                return xpath

    def get_child_elements(self, source, xpath='.'):
        return list(self.get_element(source, xpath))

    def get_element_text(self, source, xpath='.', normalize_whitespace=False):
        element = self.get_element(source, xpath)
        text = ''.join(self._yield_texts(element))
        if normalize_whitespace:
            text = self._normalize_whitespace(text)
        return text

    def _yield_texts(self, element, top=True):
        if element.text:
            yield element.text
        for child in element:
            for text in self._yield_texts(child, top=False):
                yield text
        if element.tail and not top:
            yield element.tail

    def _normalize_whitespace(self, text):
        return self._whitespace.sub(' ', text.strip())

    def get_elements_texts(self, source, xpath, normalize_whitespace=False):
        return [self.get_element_text(elem, normalize_whitespace=normalize_whitespace)
                for elem in self.get_elements(source, xpath)]

    def element_text_should_be(self, source, expected, xpath='.',
                               normalize_whitespace=False, message=None):
        text = self.get_element_text(source, xpath, normalize_whitespace)
        should_be_equal(text, expected, message, values=False)

    def element_text_should_match(self, source, pattern, xpath='.',
                                  normalize_whitespace=False, message=None):
        text = self.get_element_text(source, xpath, normalize_whitespace)
        should_match(text, pattern, message, values=False)

    def get_element_attribute(self, source, name, xpath='.', default=None):
        return self.get_element(source, xpath).get(name, default)

    def get_element_attributes(self, source, xpath='.'):
        return self.get_element(source, xpath).attrib.copy()

    def element_attribute_should_be(self, source, name, expected, xpath='.',
                                    message=None):
        attr = self.get_element_attribute(source, name, xpath)
        should_be_equal(attr, expected, message, values=False)

    def element_attribute_should_match(self, source, name, pattern, xpath='.',
                                       message=None):
        attr = self.get_element_attribute(source, name, xpath)
        if attr is None:
            raise AssertionError("Attribute '%s' does not exist." % name)
        should_match(attr, pattern, message, values=False)

    def elements_should_be_equal(self, source, expected, normalize_whitespace=False):
        self._compare_elements(source, expected, should_be_equal, normalize_whitespace)

    def elements_should_match(self, source, expected, normalize_whitespace=False):
        self._compare_elements(source, expected, should_match, normalize_whitespace)

    def _compare_elements(self, source, expected, comparator, normalize_whitespace):
        normalizer = self._normalize_whitespace if normalize_whitespace else None
        comparator = ElementComparator(comparator, normalizer)
        comparator.compare(self.get_element(source), self.get_element(expected))

    def element_to_string(self, source):
        string = ET.tostring(self.get_element(source), encoding='UTF-8')
        return self._xml_declaration.sub('', string.decode('UTF-8'))

    def log_element(self, source, level='INFO'):
        string = self.element_to_string(source)
        logger.write(string, level)
        return string


class ElementComparator(object):

    def __init__(self, comparator, normalizer=None):
        self._comparator = comparator
        self._normalizer = normalizer

    def compare(self, actual, expected, location=None):
        self._compare_tags(actual, expected, location)
        self._compare_attributes(actual, expected, location)
        self._compare_texts(actual, expected, location)
        self._compare_tails(actual, expected, location)
        self._compare_children(actual, expected, location)

    def _compare(self, actual, expected, message, location, comparator=None):
        if location:
            message = "%s at '%s'" % (message, location)
        if not comparator:
            comparator = self._comparator
        comparator(actual, expected, message)

    def _compare_tags(self, actual, expected, location):
        self._compare(actual.tag, expected.tag, 'Different tag name', location,
                      should_be_equal)

    def _compare_texts(self, actual, expected, location):
        self._compare(self._text(actual.text), self._text(expected.text),
                      'Different text', location)

    def _text(self, text):
        if not text:
            return ''
        if not self._normalizer:
            return text
        return self._normalizer(text)

    def _compare_attributes(self, actual, expected, location):
        self._compare(sorted(actual.attrib), sorted(expected.attrib),
                     'Different attribute names', location, should_be_equal)
        for key in actual.attrib:
            self._compare(actual.attrib[key], expected.attrib[key],
                          "Different value for attribute '%s'" % key, location)

    def _compare_tails(self, actual, expected, location):
        self._compare(self._text(actual.tail), self._text(expected.tail),
                      'Different tail text', location)

    def _compare_children(self, actual, expected, location):
        self._compare(len(actual), len(expected), 'Different number of child elements',
                      location, should_be_equal)
        if not location:
            location = Location(actual.tag)
        for act, exp in zip(actual, expected):
            self.compare(act, exp, location.child(act.tag))


class Location(object):

    def __init__(self, path):
        self._path = path
        self._children = {}

    def child(self, tag):
        if tag not in self._children:
            self._children[tag] = 1
        else:
            self._children[tag] += 1
            tag += '[%d]' % self._children[tag]
        return Location('%s/%s' % (self._path, tag))

    def __str__(self):
        return self._path
