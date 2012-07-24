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

# TODO: Use robot.utils.asserts directly
should_be_equal = BuiltIn().should_be_equal
should_match = BuiltIn().should_match


class XML(object):
    """Robot Framework test library for XML verification.

    As the name implies, `XML` is a test library for verifying contents of XML
    files. In practice it is a pretty thin wrapper on top of Python's
    [http://docs.python.org/library/xml.etree.elementtree.html|ElementTree XML API].

    The library has the following three main usages:

    - Parsing an XML file, or a string containing XML, into an XML element
      structure and finding certain elements from it for for further analysis
      (e.g. `Parse XML` and `Get Element` keywords).
    - Getting text or attributes of elements
      (e.g. `Get Element Text` and `Get Element Attribute`).
    - Directly verifying text or attributes of elements
      (e.g `Element Text Should Be` and `Element Attribute Should Match`).

    In the future this library may grow functionality for modifying and
    creating XML content.

    *Parsing XML*

    XML can be parsed into an element structure using `Parse XML` keyword.
    It accepts both paths to XML files and strings that contains XML. The
    keyword returns the root element of the structure, which then contains
    other elements as its children and their children.

    The element structure returned by `Parse XML`, as well as elements
    returned by keywords such as `Get Element`, can be used as the `source`
    argument with other keywords. In addition to an already parsed XML
    structure, other keywords also accept paths to XML files and strings
    containing XML similarly as `Parse XML`.

    *Example*

    This simple example demonstrates parsing XML and verifying its contents
    both using keywords in this library and in BuiltIn. How to use xpath
    expressions to find elements and what attributes the returned elements
    contain are discussed, with more examples, in subsequent sections.

    In the example, `${XML}` refers to the following example XML content.
    It could either be a path to file containing it or it could contain the
    XML itself. The same example structure is used also in the subsequent
    examples.

    | <example>
    |   <first id="1">text</first>
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

    | ${root} =                | `Parse XML`   | ${XML}  |       |             |
    | `Should Be Equal`        | ${root.tag}   | example |       |             |
    | ${first} =               | `Get Element` | ${root} | first |             |
    | `Should Be Equal`        | ${first.text} | text    |       |             |
    | `Element Text Should Be` | ${first}      | text    |       |             |
    | `Element Attribute Should Be` | ${first} | id      | 1     |             |
    | `Element Attribute Should Be` | ${root}  | id      | 1     | xpath=first |
    | `Element Attribute Should Be` | ${XML}   | id      | 1     | xpath=first |

    Notice that in the example three last lines are equivalent. Which one to
    use in practice depends on which other elements you need to get or verify.
    If you only need to do one test, using the last line alone would suffice.
    If more tests were needed, parsing the XML with `Parse XML` only once would
    be more efficient.

    *Finding elements with xpath*

    ElementTree, and thus also this library, supports finding elements using
    xpath expressions. ElementTree does not, however, support the full xpath
    syntax, and what is supported depends on its version. ElementTree 1.3 that
    is distributed with Python/Jython 2.7 supports richer syntax than versions
    distributed with earlier Python interpreters.

    Supported xpath syntax is explained below and
    [http://effbot.org/zone/element-xpath.htm|ElementTree documentation]
    provides more details. In the examples `${XML}` refers to the same XML
    structure as in the earlier example.

    _Tag names_

    When just a single tag name is used, xpath matches all direct child
    elements that have that tag name.

    | ${elem} =          | `Get Element`  | ${XML}      | third |
    | `Should Be Equal`  | ${elem.tag}    | third       |       |
    | @{children} =      | `Get Elements` | ${elem}     | child |
    | `Length Should Be` | ${children}    | 2           |       |

    _Paths_

    Paths are created by combining tag names with a forward slash (`/`).
    For example, `parent/child` matches all `child` elements under `parent`
    element. Notice that if there are multiple `parent` elements that all
    have `child` elements, `parent/child` xpath will match all these `child`
    elements.

    | ${elem} = | `Get Element` | ${XML} | second/child            |
    | ${elem} = | `Get Element` | ${XML} | third/child/grandchild  |

    _Wildcards_

    An asterisk (`*`) can be used in paths instead of a tag name to denote
    any element.

    | @{children} =      | `Get Elements` | ${XML} | */child |
    | `Length Should Be` | ${children}    | 3      |         |

    _Current element_

    The current element is denoted with a dot (`.`). Normally the current
    element is implicit and does not need to be included in the path.

    _Parent element_

    The parent element of another element is denoted with two dots (`..`).
    Notice that it is not possible to refer to the parent of the current
    element. This syntax is supported only in ElementTree 1.3 that is
    distributed with Python/Jython 2.7.

    | ${elem} =         | `Get Element` | ${XML} | */second/.. |
    | `Should Be Equal` | ${elem.tag}   | third  |             |

    _Search all sub elements_

    Two forward slashes (`//`) mean that all sub elements, not only the
    direct children, are searched. If the search is started from the current
    element, an explicit dot is required.

    | @{elements} =      | `Get Elements` | ${XML} | .//second |
    | `Length Should Be` | ${elements}    | 2      |           |

    _Predicates_

    Predicates allow selecting elements using also other criteria than tag
    names such as attributes or position. They are specified after the normal
    tag name or path using syntax `path[predicate]`. The path can have
    wildcards and other special syntax explained above.

    Notice that predicates are supported only in ElementTree 1.3 that is
    shipped with Python/Jython 2.7. What predicates are supported in that
    version is explained in the table below.

    | _Predicate_     | _Matches_                         | _Example_          |
    | @attrib         | Elements with attribute `attrib`. | second[@id]        |
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

    The examples use the same `${XML}` structure as the earlier examples.

    _tag_

    The tag of the element.

    | ${root} =         | `Parse XML` | ${XML}  |
    | `Should Be Equal` | ${root.tag} | example |

    _text_

    The text that the element contains or Python `None` if the element has no
    text. Notice that the text _does not_ contain texts of possible child
    elements nor text after or between children. Notice also that in XML
    whitespace is significant, so the text contains also possible indentation
    and newlines. To get also text of the possible children, optionally
    whitespace normalized, use `Get Element Text` keyword.

    | ${1st} =          | `Get Element` | ${XML}  | first        |
    | `Should Be Equal` | ${1st.text}   | text    |              |
    | ${2nd} =          | `Get Element` | ${XML}  | second/child |
    | `Should Be Equal` | ${2nd.text}   | ${NONE} |              |
    | ${p} =            | `Get Element` | ${XML}  | html/p       |
    | `Should Be Equal` | ${p.text}     | \\n${SPACE*6}Text with${SPACE} |

    _tail_

    The text after the element before the next opening or closing tag. Python
    `None` if the element has no tail. Similarly as with `text`, also `tail`
    contains possible indentation and newlines.

    | ${b} =            | `Get Element` | ${XML}  | html/p/b  |
    | `Should Be Equal` | ${b.tail}     | ${SPACE}and${SPACE} |

    _attrib_

    A Python dictionary containing attributes of the element.

    | ${2nd} =          | `Get Element`       | ${XML} | second |
    | `Should Be Equal` | ${2nd.attrib['id']} | 2      |        |
    | ${3rd} =          | `Get Element`       | ${XML} | third  |
    | `Should Be Empty` | ${3rd.attrib}       |        |        |
    """

    ROBOT_LIBRARY_SCOPE = 'GLOBAL'
    _whitespace = re.compile('\s+')
    _xml_declaration = re.compile('^<\?xml .*\?>\n')

    def parse_xml(self, source):
        """Parses the given XML file or string into an element structure.

        The `source` can either be a path to an XML file or a string containing
        XML. In both cases the XML is parsed into ElementTree
        [http://docs.python.org/library/xml.etree.elementtree.html#xml.etree.ElementTree.Element|element structure]
        and the root element is returned.

        Examples:
        | ${xml} =  | Parse XML | ${CURDIR}/test.xml    |
        | ${root} = | Parse XML | <root><child/></root> |

        For more details and examples, see `Parsing XML` section in
        `introduction`.
        """
        with ETSource(source) as source:
            return ET.parse(source).getroot()

    def get_element(self, source, xpath='.'):
        """Returns an element in the `source` matching the `xpath`.

        The `source` can be a path to an XML file, a string containing XML, or
        an already parsed XML element. The `xpath` specifies which element to
        find. See the `introduction` for more details.

        The keyword fails if more or less than one element matches the `xpath`.
        Use `Get Elements` if you want all matching elements to be returned.

        Examples using `${XML}` structure from the `introduction`:
        | ${element} = | Get Element | ${XML}     | second |
        | ${child} =   | Get Element | ${element} | child  |
        """
        elements = self.get_elements(source, xpath)
        if not elements:
            raise RuntimeError("No element matching '%s' found." % xpath)
        if len(elements) > 1:
            raise RuntimeError("Multiple elements (%d) matching '%s' found."
                               % (len(elements), xpath))
        return elements[0]

    def get_elements(self, source, xpath):
        """Returns a list of elements in the `source` matching the `xpath`.

        The `source` can be a path to an XML file, a string containing XML, or
        an already parsed XML element. The `xpath` specifies which element to
        find. See the `introduction` for more details.

        Elements matching the `xpath` are returned as a list. If no elements
        match, an empty list is returned. Use `Get Element` if you want to get
        exactly one match.

        Examples using `${XML}` structure from the `introduction`:
        | ${children} =    | Get Elements | ${XML} | third/child |
        | Length Should Be | ${children}  | 2      |             |
        | ${children} =    | Get Elements | ${XML} | first/child |
        | Should Be Empty  |  ${children} |        |             |
        """
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
        """Returns the child elements of the specified element as a list.

        The element whose text to return is specified using `source` and
        `xpath`. They have exactly the same semantics as with `Get Element`
        keyword.

        All the direct child elements of the specified element are returned.
        If the element has no children, an empty list is returned.

        See the `introduction` for more details about both the `source` and
        the `xpath` syntax.

        Examples using `${XML}` structure from the `introduction`:
        | ${children} =    | Get Child Elements | ${XML} |             |
        | Length Should Be | ${children}        | 4      |             |
        | ${children} =    | Get Child Elements | ${XML} | xpath=first |
        | Should Be Empty  | ${children}        |        |             |
        """
        return list(self.get_element(source, xpath))

    def get_element_text(self, source, xpath='.', normalize_whitespace=False):
        """Returns all text of the element, possibly whitespace normalized.

        The element whose text to return is specified using `source` and
        `xpath`. They have exactly the same semantics as with `Get Element`
        keyword.

        This keyword returns all the text of the specified element, including
        all the text its children and grandchildren contains. If the element
        has no text, an empty string is returned. As discussed in the
        `introduction`, the returned text is thus not always the same as
        the `text` attribute of the element.

        Be default all whitespace, including newlines and indentation, inside
        the element is returned as-is. If `normalize_whitespace` is given any
        non-false value, then leading and trailing whitespace is stripped,
        newlines and tabs converted to spaces, and multiple spaces collapsed
        into one. This is especially useful when dealing with HTML data.

        Examples using `${XML}` structure from the `introduction`:
        | ${text} =       | Get Element Text | ${XML}       | first        |
        | Should Be Equal | ${text}          | text         |              |
        | ${text} =       | Get Element Text | ${XML}       | second/child |
        | Should Be Empty | ${text}          |              |              |
        | ${paragraph} =  | Get Element      | ${XML}       | html/p       |
        | ${text} =       | Get Element Text | ${paragraph} | normalize_whitespace=yes |
        | Should Be Equal | ${text}          | Text with bold and italics. |

        See also `Get Elements Texts`, `Element Text Should Be` and
        `Element Text Should Match`.
        """
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
        """Returns text of all elements matching `xpath` as a list.

        The elements whose text to return is specified using `source` and
        `xpath`. They have exactly the same semantics as with `Get Elements`
        keyword.

        The text of the matched elements is returned using the same logic
        as with `Get Element Text`. This includes optional whitespace
        normalization using the `normalize_whitespace` option.

        Examples using `${XML}` structure from the `introduction`:
        | @{texts} =       | Get Elements Texts | ${XML}    | third/child |
        | Length Should Be | ${texts}           | 2         |             |
        | Should Be Equal  | @{texts}[0]        | more text |             |
        | Should Be Equal  | @{texts}[1]        | ${EMPTY}  |             |

        See also `Get Element Text`, `Element Text Should Be` and
        `Element Text Should Match`.
        """
        return [self.get_element_text(elem, normalize_whitespace=normalize_whitespace)
                for elem in self.get_elements(source, xpath)]

    def element_text_should_be(self, source, expected, xpath='.',
                               normalize_whitespace=False, message=None):
        """Verifies that the text of the specified element is `expected`.

        The element whose text is verified is specified using `source` and
        `xpath`. They have exactly the same semantics as with `Get Element`
        keyword.

        The text to verify is got from the specified element using the same
        logic as with `Get Element Text`. This includes optional whitespace
        normalization using the `normalize_whitespace` option.

        The keyword passes if the text of the element is equal to the
        `expected` value, and otherwise it fails. The default error message can
        be overridden with the `message` argument.

        Examples using `${XML}` structure from the `introduction`:
        | Element Text Should Be | ${XML}       | text     | xpath=first      |
        | Element Text Should Be | ${XML}       | ${EMPTY} | xpath=second/child |
        | ${paragraph} =         | Get Element  | ${XML}   | xpath=html/p     |
        | Element Text Should Be | ${paragraph} | Text with bold and italics. | normalize_whitespace=yes |

        See also `Get Element Text`, `Get Elements Texts` and
        `Element Text Should Match`.
        """
        text = self.get_element_text(source, xpath, normalize_whitespace)
        should_be_equal(text, expected, message, values=False)

    def element_text_should_match(self, source, pattern, xpath='.',
                                  normalize_whitespace=False, message=None):
        """Verifies that the text of the specified element matches `expected`.

        This keyword works exactly like `Element Text Should Be` except that
        the expected value can be given as a pattern that the text of the
        element must match.

        Pattern matching is similar as matching files in a shell, and it is
        always case-sensitive. In the pattern, '*' matches anything and '?'
        matches any single character.

        Examples using `${XML}` structure from the `introduction`:
        | Element Text Should Match | ${XML}       | t???   | xpath=first  |
        | ${paragraph} =            | Get Element  | ${XML} | xpath=html/p |
        | Element Text Should Match | ${paragraph} | Text with * and *. | normalize_whitespace=yes |

        See also `Get Element Text`, `Get Elements Texts` and
        `Element Text Should Be`.
        """
        text = self.get_element_text(source, xpath, normalize_whitespace)
        should_match(text, pattern, message, values=False)

    def get_element_attribute(self, source, name, xpath='.', default=None):
        """Returns the named attribute of the specified element.

        The element whose attribute to return is specified using `source` and
        `xpath`. They have exactly the same semantics as with `Get Element`
        keyword.

        The value of the attribute `name` of the specified element is returned.
        If the element does not have such element, the `default` value is
        returned instead.

        Examples using `${XML}` structure from the `introduction`:
        | ${attribute} =  | Get Element Attribute | ${XML} | id | xpath=first |
        | Should Be Equal | ${attribute}          | 1      |    |             |
        | ${attribute} =  | Get Element Attribute | ${XML} | xx | xpath=first | default=value |
        | Should Be Equal | ${attribute}          | value  |    |             |

        See also `Get Element Attributes`, `Element Attribute Should Be`,
        and `Element Attribute Should Match`.
        """
        return self.get_element(source, xpath).get(name, default)

    def get_element_attributes(self, source, xpath='.'):
        """Returns all attributes of the specified element.

        The element whose attributes to return is specified using `source` and
        `xpath`. They have exactly the same semantics as with `Get Element`
        keyword.

        Attributes are returned as a Python dictionary. It is a copy of the
        original attributes so modifying it has no effect on the XML structure.

        Examples using `${XML}` structure from the `introduction`:
        | ${attributes} = | Get Element Attributes       | ${XML} | first |
        | Should Be True  | ${attributes} == {'id': '1'} |        |       |
        | ${attributes} = | Get Element Attributes       | ${XML} | third |
        | Should Be Empty | ${attributes}                |        |       |

        See also `Get Element Attribute`, `Element Attribute Should Be`,
        and `Element Attribute Should Match`.
        """
        return self.get_element(source, xpath).attrib.copy()

    def element_attribute_should_be(self, source, name, expected, xpath='.',
                                    message=None):
        """Verifies that the specified attribute is `expected`.

        The element whose attribute is verified is specified using `source`
        and `xpath`. They have exactly the same semantics as with `Get Element`
        keyword.

        The keyword passes if the attribute `name` of the element is equal to
        the `expected` value, and otherwise it fails. To test that the element
        does not have certain attribute, use Python `None` (i.e. variable
        `${NONE}`) as the `expected` value. The default error message can be
        overridden with the `message` argument.

        Examples using `${XML}` structure from the `introduction`:
        | Element Attribute Should Be | ${XML} | id | 1       | xpath=first |
        | Element Attribute Should Be | ${XML} | id | ${NONE} |             |

        See also `Get Element Attribute`, `Get Element Attributes` and
        `Element Text Should Match`.
        """
        attr = self.get_element_attribute(source, name, xpath)
        should_be_equal(attr, expected, message, values=False)

    def element_attribute_should_match(self, source, name, pattern, xpath='.',
                                       message=None):
        """Verifies that the specified attribute matches `expected`.

        This keyword works exactly like `Element Attribute Should Be` except
        that the expected value can be given as a pattern that the attribute of
        the element must match.

        Pattern matching is similar as matching files in a shell, and it is
        always case-sensitive. In the pattern, '*' matches anything and '?'
        matches any single character.

        Examples using `${XML}` structure from the `introduction`:
        | Element Attribute Should Match | ${XML} | id | ?   | xpath=first |
        | Element Attribute Should Match | ${XML} | id | c*d | xpath=third/second |

        See also `Get Element Attribute`, `Get Element Attributes` and
        `Element Text Should Be`.
        """
        attr = self.get_element_attribute(source, name, xpath)
        if attr is None:
            raise AssertionError("Attribute '%s' does not exist." % name)
        should_match(attr, pattern, message, values=False)

    def elements_should_be_equal(self, source, expected, normalize_whitespace=False,
                                 exclude_children=False):
        self._compare_elements(source, expected, should_be_equal,
                               normalize_whitespace, exclude_children)

    def elements_should_match(self, source, expected, normalize_whitespace=False,
                              exclude_children=False):
        self._compare_elements(source, expected, should_match,
                               normalize_whitespace, exclude_children)

    def _compare_elements(self, source, expected, comparator,
                          normalize_whitespace, exclude_children):
        normalizer = self._normalize_whitespace if normalize_whitespace else None
        comparator = ElementComparator(comparator, normalizer, exclude_children)
        comparator.compare(self.get_element(source), self.get_element(expected))

    def element_to_string(self, source, xpath='.'):
        """Returns the string representation of the specified element.

        The element to convert to a string is specified using `source` and
        `xpath`. They have exactly the same semantics as with `Get Element`
        keyword.

        The returned string does not contain any XML declaration.

        See also `Log Element`.
        """
        string = ET.tostring(self.get_element(source, xpath), encoding='UTF-8')
        return self._xml_declaration.sub('', string.decode('UTF-8')).strip()

    def log_element(self, source, level='INFO', xpath='.'):
        """Logs the string representation of the specified element.

        The element specified with `source` and `xpath` is first converted to
        a string using `Element To String` keyword internally. The resulting
        string is then logged using the given `level`.

        The logged string is also returned.
        """
        string = self.element_to_string(source, xpath)
        logger.write(string, level)
        return string


class ElementComparator(object):

    def __init__(self, comparator, normalizer=None, exclude_children=False):
        self._comparator = comparator
        self._normalizer = normalizer
        self._exclude_children = exclude_children

    def compare(self, actual, expected, location=None):
        self._compare_tags(actual, expected, location)
        self._compare_attributes(actual, expected, location)
        self._compare_texts(actual, expected, location)
        self._compare_tails(actual, expected, location)
        if not self._exclude_children:
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
