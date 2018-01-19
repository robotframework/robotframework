#  Copyright 2008-2015 Nokia Networks
#  Copyright 2016-     Robot Framework Foundation
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

from __future__ import absolute_import

import re
from fnmatch import fnmatchcase
from random import randint
from string import ascii_lowercase, ascii_uppercase, digits

from robot.api import logger
from robot.utils import (is_bytes, is_string, is_truthy, is_unicode, lower,
                         unic, PY3)
from robot.version import get_version


class String(object):
    """A test library for string manipulation and verification.

    ``String`` is Robot Framework's standard library for manipulating
    strings (e.g. `Replace String Using Regexp`, `Split To Lines`) and
    verifying their contents (e.g. `Should Be String`).

    Following keywords from ``BuiltIn`` library can also be used with strings:

    - `Catenate`
    - `Get Length`
    - `Length Should Be`
    - `Should (Not) Be Empty`
    - `Should (Not) Be Equal (As Strings/Integers/Numbers)`
    - `Should (Not) Match (Regexp)`
    - `Should (Not) Contain`
    - `Should (Not) Start With`
    - `Should (Not) End With`
    - `Convert To String`
    - `Convert To Bytes`
    """
    ROBOT_LIBRARY_SCOPE = 'GLOBAL'
    ROBOT_LIBRARY_VERSION = get_version()

    def convert_to_lowercase(self, string):
        """Converts string to lowercase.

        Examples:
        | ${str1} = | Convert To Lowercase | ABC |
        | ${str2} = | Convert To Lowercase | 1A2c3D |
        | Should Be Equal | ${str1} | abc |
        | Should Be Equal | ${str2} | 1a2c3d |

        New in Robot Framework 2.8.6.
        """
        # Custom `lower` needed due to IronPython bug. See its code and
        # comments for more details.
        return lower(string)

    def convert_to_uppercase(self, string):
        """Converts string to uppercase.

        Examples:
        | ${str1} = | Convert To Uppercase | abc |
        | ${str2} = | Convert To Uppercase | 1a2C3d |
        | Should Be Equal | ${str1} | ABC |
        | Should Be Equal | ${str2} | 1A2C3D |

        New in Robot Framework 2.8.6.
        """
        return string.upper()

    def encode_string_to_bytes(self, string, encoding, errors='strict'):
        """Encodes the given Unicode ``string`` to bytes using the given ``encoding``.

        ``errors`` argument controls what to do if encoding some characters fails.
        All values accepted by ``encode`` method in Python are valid, but in
        practice the following values are most useful:

        - ``strict``: fail if characters cannot be encoded (default)
        - ``ignore``: ignore characters that cannot be encoded
        - ``replace``: replace characters that cannot be encoded with
          a replacement character

        Examples:
        | ${bytes} = | Encode String To Bytes | ${string} | UTF-8 |
        | ${bytes} = | Encode String To Bytes | ${string} | ASCII | errors=ignore |

        Use `Convert To Bytes` in ``BuiltIn`` if you want to create bytes based
        on character or integer sequences. Use `Decode Bytes To String` if you
        need to convert byte strings to Unicode strings and `Convert To String`
        in ``BuiltIn`` if you need to convert arbitrary objects to Unicode.
        """
        return bytes(string.encode(encoding, errors))

    def decode_bytes_to_string(self, bytes, encoding, errors='strict'):
        """Decodes the given ``bytes`` to a Unicode string using the given ``encoding``.

        ``errors`` argument controls what to do if decoding some bytes fails.
        All values accepted by ``decode`` method in Python are valid, but in
        practice the following values are most useful:

        - ``strict``: fail if characters cannot be decoded (default)
        - ``ignore``: ignore characters that cannot be decoded
        - ``replace``: replace characters that cannot be decoded with
          a replacement character

        Examples:
        | ${string} = | Decode Bytes To String | ${bytes} | UTF-8 |
        | ${string} = | Decode Bytes To String | ${bytes} | ASCII | errors=ignore |

        Use `Encode String To Bytes` if you need to convert Unicode strings to
        byte strings, and `Convert To String` in ``BuiltIn`` if you need to
        convert arbitrary objects to Unicode strings.
        """
        if PY3 and is_unicode(bytes):
            raise TypeError('Can not decode strings on Python 3.')
        return bytes.decode(encoding, errors)

    def get_line_count(self, string):
        """Returns and logs the number of lines in the given string."""
        count = len(string.splitlines())
        logger.info('%d lines' % count)
        return count

    def split_to_lines(self, string, start=0, end=None):
        """Splits the given string to lines.

        It is possible to get only a selection of lines from ``start``
        to ``end`` so that ``start`` index is inclusive and ``end`` is
        exclusive. Line numbering starts from 0, and it is possible to
        use negative indices to refer to lines from the end.

        Lines are returned without the newlines. The number of
        returned lines is automatically logged.

        Examples:
        | @{lines} =        | Split To Lines | ${manylines} |    |    |
        | @{ignore first} = | Split To Lines | ${manylines} | 1  |    |
        | @{ignore last} =  | Split To Lines | ${manylines} |    | -1 |
        | @{5th to 10th} =  | Split To Lines | ${manylines} | 4  | 10 |
        | @{first two} =    | Split To Lines | ${manylines} |    | 1  |
        | @{last two} =     | Split To Lines | ${manylines} | -2 |    |

        Use `Get Line` if you only need to get a single line.
        """
        start = self._convert_to_index(start, 'start')
        end = self._convert_to_index(end, 'end')
        lines = string.splitlines()[start:end]
        logger.info('%d lines returned' % len(lines))
        return lines

    def get_line(self, string, line_number):
        """Returns the specified line from the given ``string``.

        Line numbering starts from 0 and it is possible to use
        negative indices to refer to lines from the end. The line is
        returned without the newline character.

        Examples:
        | ${first} =    | Get Line | ${string} | 0  |
        | ${2nd last} = | Get Line | ${string} | -2 |

        Use `Split To Lines` if all lines are needed.
        """
        line_number = self._convert_to_integer(line_number, 'line_number')
        return string.splitlines()[line_number]

    def get_lines_containing_string(self, string, pattern, case_insensitive=False):
        """Returns lines of the given ``string`` that contain the ``pattern``.

        The ``pattern`` is always considered to be a normal string, not a glob
        or regexp pattern. A line matches if the ``pattern`` is found anywhere
        on it.

        The match is case-sensitive by default, but giving ``case_insensitive``
        a true value makes it case-insensitive. The value is considered true
        if it is a non-empty string that is not equal to ``false``, ``none`` or
        ``no``. If the value is not a string, its truth value is got directly
        in Python. Considering ``none`` false is new in RF 3.0.3.

        Lines are returned as one string catenated back together with
        newlines. Possible trailing newline is never returned. The
        number of matching lines is automatically logged.

        Examples:
        | ${lines} = | Get Lines Containing String | ${result} | An example |
        | ${ret} =   | Get Lines Containing String | ${ret} | FAIL | case-insensitive |

        See `Get Lines Matching Pattern` and `Get Lines Matching Regexp`
        if you need more complex pattern matching.
        """
        if is_truthy(case_insensitive):
            pattern = pattern.lower()
            contains = lambda line: pattern in line.lower()
        else:
            contains = lambda line: pattern in line
        return self._get_matching_lines(string, contains)

    def get_lines_matching_pattern(self, string, pattern, case_insensitive=False):
        """Returns lines of the given ``string`` that match the ``pattern``.

        The ``pattern`` is a _glob pattern_ where:
        | ``*``        | matches everything |
        | ``?``        | matches any single character |
        | ``[chars]``  | matches any character inside square brackets (e.g. ``[abc]`` matches either ``a``, ``b`` or ``c``) |
        | ``[!chars]`` | matches any character not inside square brackets |

        A line matches only if it matches the ``pattern`` fully.

        The match is case-sensitive by default, but giving ``case_insensitive``
        a true value makes it case-insensitive. The value is considered true
        if it is a non-empty string that is not equal to ``false``, ``none`` or
        ``no``. If the value is not a string, its truth value is got directly
        in Python. Considering ``none`` false is new in RF 3.0.3.

        Lines are returned as one string catenated back together with
        newlines. Possible trailing newline is never returned. The
        number of matching lines is automatically logged.

        Examples:
        | ${lines} = | Get Lines Matching Pattern | ${result} | Wild???? example |
        | ${ret} = | Get Lines Matching Pattern | ${ret} | FAIL: * | case_insensitive=true |

        See `Get Lines Matching Regexp` if you need more complex
        patterns and `Get Lines Containing String` if searching
        literal strings is enough.
        """
        if is_truthy(case_insensitive):
            pattern = pattern.lower()
            matches = lambda line: fnmatchcase(line.lower(), pattern)
        else:
            matches = lambda line: fnmatchcase(line, pattern)
        return self._get_matching_lines(string, matches)

    def get_lines_matching_regexp(self, string, pattern, partial_match=False):
        """Returns lines of the given ``string`` that match the regexp ``pattern``.

        See `BuiltIn.Should Match Regexp` for more information about
        Python regular expression syntax in general and how to use it
        in Robot Framework test data in particular.

        By default lines match only if they match the pattern fully, but
        partial matching can be enabled by giving the ``partial_match``
        argument a true value. The value is considered true
        if it is a non-empty string that is not equal to ``false``, ``none`` or
        ``no``. If the value is not a string, its truth value is got directly
        in Python. Considering ``none`` false is new in RF 3.0.3.

        If the pattern is empty, it matches only empty lines by default.
        When partial matching is enabled, empty pattern matches all lines.

        Notice that to make the match case-insensitive, you need to prefix
        the pattern with case-insensitive flag ``(?i)``.

        Lines are returned as one string concatenated back together with
        newlines. Possible trailing newline is never returned. The
        number of matching lines is automatically logged.

        Examples:
        | ${lines} = | Get Lines Matching Regexp | ${result} | Reg\\\\w{3} example |
        | ${lines} = | Get Lines Matching Regexp | ${result} | Reg\\\\w{3} example | partial_match=true |
        | ${ret} =   | Get Lines Matching Regexp | ${ret}    | (?i)FAIL: .* |

        See `Get Lines Matching Pattern` and `Get Lines Containing
        String` if you do not need full regular expression powers (and
        complexity).

        ``partial_match`` argument is new in Robot Framework 2.9. In earlier
         versions exact match was always required.
        """
        if not is_truthy(partial_match):
            pattern = '^%s$' % pattern
        return self._get_matching_lines(string, re.compile(pattern).search)

    def _get_matching_lines(self, string, matches):
        lines = string.splitlines()
        matching = [line for line in lines if matches(line)]
        logger.info('%d out of %d lines matched' % (len(matching), len(lines)))
        return '\n'.join(matching)

    def get_regexp_matches(self, string, pattern, *groups):
        """Returns a list of all non-overlapping matches in the given string.

        ``string`` is the string to find matches from and ``pattern`` is the
        regular expression. See `BuiltIn.Should Match Regexp` for more
        information about Python regular expression syntax in general and how
        to use it in Robot Framework test data in particular.

        If no groups are used, the returned list contains full matches. If one
        group is used, the list contains only contents of that group. If
        multiple groups are used, the list contains tuples that contain
        individual group contents. All groups can be given as indexes (starting
        from 1) and named groups also as names.

        Examples:
        | ${no match} =    | Get Regexp Matches | the string | xxx     |
        | ${matches} =     | Get Regexp Matches | the string | t..     |
        | ${one group} =   | Get Regexp Matches | the string | t(..)   | 1 |
        | ${named group} = | Get Regexp Matches | the string | t(?P<name>..) | name |
        | ${two groups} =  | Get Regexp Matches | the string | t(.)(.) | 1 | 2 |
        =>
        | ${no match} = []
        | ${matches} = ['the', 'tri']
        | ${one group} = ['he', 'ri']
        | ${named group} = ['he', 'ri']
        | ${two groups} = [('h', 'e'), ('r', 'i')]

        New in Robot Framework 2.9.
        """
        regexp = re.compile(pattern)
        groups = [self._parse_group(g) for g in groups]
        return [m.group(*groups) for m in regexp.finditer(string)]

    def _parse_group(self, group):
        try:
            return int(group)
        except ValueError:
            return group

    def replace_string(self, string, search_for, replace_with, count=-1):
        """Replaces ``search_for`` in the given ``string`` with ``replace_with``.

        ``search_for`` is used as a literal string. See `Replace String
        Using Regexp` if more powerful pattern matching is needed.
        If you need to just remove a string see `Remove String`.

        If the optional argument ``count`` is given, only that many
        occurrences from left are replaced. Negative ``count`` means
        that all occurrences are replaced (default behaviour) and zero
        means that nothing is done.

        A modified version of the string is returned and the original
        string is not altered.

        Examples:
        | ${str} =        | Replace String | Hello, world!  | world | tellus   |
        | Should Be Equal | ${str}         | Hello, tellus! |       |          |
        | ${str} =        | Replace String | Hello, world!  | l     | ${EMPTY} | count=1 |
        | Should Be Equal | ${str}         | Helo, world!   |       |          |
        """
        count = self._convert_to_integer(count, 'count')
        return string.replace(search_for, replace_with, count)

    def replace_string_using_regexp(self, string, pattern, replace_with, count=-1):
        """Replaces ``pattern`` in the given ``string`` with ``replace_with``.

        This keyword is otherwise identical to `Replace String`, but
        the ``pattern`` to search for is considered to be a regular
        expression.  See `BuiltIn.Should Match Regexp` for more
        information about Python regular expression syntax in general
        and how to use it in Robot Framework test data in particular.

        If you need to just remove a string see `Remove String Using Regexp`.

        Examples:
        | ${str} = | Replace String Using Regexp | ${str} | 20\\\\d\\\\d-\\\\d\\\\d-\\\\d\\\\d | <DATE> |
        | ${str} = | Replace String Using Regexp | ${str} | (Hello|Hi) | ${EMPTY} | count=1 |
        """
        count = self._convert_to_integer(count, 'count')
        # re.sub handles 0 and negative counts differently than string.replace
        if count == 0:
            return string
        return re.sub(pattern, replace_with, string, max(count, 0))

    def remove_string(self, string, *removables):
        """Removes all ``removables`` from the given ``string``.

        ``removables`` are used as literal strings. Each removable will be
        matched to a temporary string from which preceding removables have
        been already removed. See second example below.

        Use `Remove String Using Regexp` if more powerful pattern matching is
        needed. If only a certain number of matches should be removed,
        `Replace String` or `Replace String Using Regexp` can be used.

        A modified version of the string is returned and the original
        string is not altered.

        Examples:
        | ${str} =        | Remove String | Robot Framework | work   |
        | Should Be Equal | ${str}        | Robot Frame     |
        | ${str} =        | Remove String | Robot Framework | o | bt |
        | Should Be Equal | ${str}        | R Framewrk      |

        New in Robot Framework 2.8.2.
        """
        for removable in removables:
            string = self.replace_string(string, removable, '')
        return string

    def remove_string_using_regexp(self, string, *patterns):
        """Removes ``patterns`` from the given ``string``.

        This keyword is otherwise identical to `Remove String`, but
        the ``patterns`` to search for are considered to be a regular
        expression. See `Replace String Using Regexp` for more information
        about the regular expression syntax. That keyword can also be
        used if there is a need to remove only a certain number of
        occurrences.

        New in Robot Framework 2.8.2.
        """
        for pattern in patterns:
            string = self.replace_string_using_regexp(string, pattern, '')
        return string

    def split_string(self, string, separator=None, max_split=-1):
        """Splits the ``string`` using ``separator`` as a delimiter string.

        If a ``separator`` is not given, any whitespace string is a
        separator. In that case also possible consecutive whitespace
        as well as leading and trailing whitespace is ignored.

        Split words are returned as a list. If the optional
        ``max_split`` is given, at most ``max_split`` splits are done, and
        the returned list will have maximum ``max_split + 1`` elements.

        Examples:
        | @{words} =         | Split String | ${string} |
        | @{words} =         | Split String | ${string} | ,${SPACE} |
        | ${pre} | ${post} = | Split String | ${string} | ::    | 1 |

        See `Split String From Right` if you want to start splitting
        from right, and `Fetch From Left` and `Fetch From Right` if
        you only want to get first/last part of the string.
        """
        if separator == '':
            separator = None
        max_split = self._convert_to_integer(max_split, 'max_split')
        return string.split(separator, max_split)

    def split_string_from_right(self, string, separator=None, max_split=-1):
        """Splits the ``string`` using ``separator`` starting from right.

        Same as `Split String`, but splitting is started from right. This has
        an effect only when ``max_split`` is given.

        Examples:
        | ${first} | ${rest} = | Split String            | ${string} | - | 1 |
        | ${rest}  | ${last} = | Split String From Right | ${string} | - | 1 |
        """
        if separator == '':
            separator = None
        max_split = self._convert_to_integer(max_split, 'max_split')
        return string.rsplit(separator, max_split)

    def split_string_to_characters(self, string):
        """Splits the given ``string`` to characters.

        Example:
        | @{characters} = | Split String To Characters | ${string} |
        """
        return list(string)

    def fetch_from_left(self, string, marker):
        """Returns contents of the ``string`` before the first occurrence of ``marker``.

        If the ``marker`` is not found, whole string is returned.

        See also `Fetch From Right`, `Split String` and `Split String
        From Right`.
        """
        return string.split(marker)[0]

    def fetch_from_right(self, string, marker):
        """Returns contents of the ``string`` after the last occurrence of ``marker``.

        If the ``marker`` is not found, whole string is returned.

        See also `Fetch From Left`, `Split String` and `Split String
        From Right`.
        """
        return string.split(marker)[-1]

    def generate_random_string(self, length=8, chars='[LETTERS][NUMBERS]'):
        """Generates a string with a desired ``length`` from the given ``chars``.

        The population sequence ``chars`` contains the characters to use
        when generating the random string. It can contain any
        characters, and it is possible to use special markers
        explained in the table below:

        |  = Marker =   |               = Explanation =                   |
        | ``[LOWER]``   | Lowercase ASCII characters from ``a`` to ``z``. |
        | ``[UPPER]``   | Uppercase ASCII characters from ``A`` to ``Z``. |
        | ``[LETTERS]`` | Lowercase and uppercase ASCII characters.       |
        | ``[NUMBERS]`` | Numbers from 0 to 9.                            |

        Examples:
        | ${ret} = | Generate Random String |
        | ${low} = | Generate Random String | 12 | [LOWER]         |
        | ${bin} = | Generate Random String | 8  | 01              |
        | ${hex} = | Generate Random String | 4  | [NUMBERS]abcdef |
        """
        if length == '':
            length = 8
        length = self._convert_to_integer(length, 'length')
        for name, value in [('[LOWER]', ascii_lowercase),
                            ('[UPPER]', ascii_uppercase),
                            ('[LETTERS]', ascii_lowercase + ascii_uppercase),
                            ('[NUMBERS]', digits)]:
            chars = chars.replace(name, value)
        maxi = len(chars) - 1
        return ''.join(chars[randint(0, maxi)] for _ in range(length))

    def get_substring(self, string, start, end=None):
        """Returns a substring from ``start`` index to ``end`` index.

        The ``start`` index is inclusive and ``end`` is exclusive.
        Indexing starts from 0, and it is possible to use
        negative indices to refer to characters from the end.

        Examples:
        | ${ignore first} = | Get Substring | ${string} | 1  |    |
        | ${ignore last} =  | Get Substring | ${string} |    | -1 |
        | ${5th to 10th} =  | Get Substring | ${string} | 4  | 10 |
        | ${first two} =    | Get Substring | ${string} |    | 1  |
        | ${last two} =     | Get Substring | ${string} | -2 |    |
        """
        start = self._convert_to_index(start, 'start')
        end = self._convert_to_index(end, 'end')
        return string[start:end]

    def strip_string(self, string, mode='both', characters=None):
        """Remove leading and/or trailing whitespaces from the given string.

        ``mode`` is either ``left`` to remove leading characters, ``right`` to
        remove trailing characters, ``both`` (default) to remove the
        characters from both sides of the string or ``none`` to return the
        unmodified string.

        If the optional ``characters`` is given, it must be a string and the
        characters in the string will be stripped in the string. Please note,
        that this is not a substring to be removed but a list of characters,
        see the example below.

        Examples:
        | ${stripped}=  | Strip String | ${SPACE}Hello${SPACE} | |
        | Should Be Equal | ${stripped} | Hello | |
        | ${stripped}=  | Strip String | ${SPACE}Hello${SPACE} | mode=left |
        | Should Be Equal | ${stripped} | Hello${SPACE} | |
        | ${stripped}=  | Strip String | aabaHelloeee | characters=abe |
        | Should Be Equal | ${stripped} | Hello | |

        New in Robot Framework 3.0.
        """
        try:
            method = {'BOTH': string.strip,
                      'LEFT': string.lstrip,
                      'RIGHT': string.rstrip,
                      'NONE': lambda characters: string}[mode.upper()]
        except KeyError:
            raise ValueError("Invalid mode '%s'." % mode)
        return method(characters)

    def should_be_string(self, item, msg=None):
        """Fails if the given ``item`` is not a string.

        With Python 2, except with IronPython, this keyword passes regardless
        is the ``item`` a Unicode string or a byte string. Use `Should Be
        Unicode String` or `Should Be Byte String` if you want to restrict
        the string type. Notice that with Python 2, except with IronPython,
        ``'string'`` creates a byte string and ``u'unicode'`` must be used to
        create a Unicode string.

        With Python 3 and IronPython, this keyword passes if the string is
        a Unicode string but fails if it is bytes. Notice that with both
        Python 3 and IronPython, ``'string'`` creates a Unicode string, and
        ``b'bytes'`` must be used to create a byte string.

        The default error message can be overridden with the optional
        ``msg`` argument.
        """
        if not is_string(item):
            self._fail(msg, "'%s' is not a string.", item)

    def should_not_be_string(self, item, msg=None):
        """Fails if the given ``item`` is a string.

        See `Should Be String` for more details about Unicode strings and byte
        strings.

        The default error message can be overridden with the optional
        ``msg`` argument.
        """
        if is_string(item):
            self._fail(msg, "'%s' is a string.", item)

    def should_be_unicode_string(self, item, msg=None):
        """Fails if the given ``item`` is not a Unicode string.

        Use `Should Be Byte String` if you want to verify the ``item`` is a
        byte string, or `Should Be String` if both Unicode and byte strings
        are fine. See `Should Be String` for more details about Unicode
        strings and byte strings.

        The default error message can be overridden with the optional
        ``msg`` argument.
        """
        if not is_unicode(item):
            self._fail(msg, "'%s' is not a Unicode string.", item)

    def should_be_byte_string(self, item, msg=None):
        """Fails if the given ``item`` is not a byte string.

        Use `Should Be Unicode String` if you want to verify the ``item`` is a
        Unicode string, or `Should Be String` if both Unicode and byte strings
        are fine. See `Should Be String` for more details about Unicode strings
        and byte strings.

        The default error message can be overridden with the optional
        ``msg`` argument.
        """
        if not is_bytes(item):
            self._fail(msg, "'%s' is not a byte string.", item)

    def should_be_lowercase(self, string, msg=None):
        """Fails if the given ``string`` is not in lowercase.

        For example, ``'string'`` and ``'with specials!'`` would pass, and
        ``'String'``, ``''`` and ``' '`` would fail.

        The default error message can be overridden with the optional
        ``msg`` argument.

        See also `Should Be Uppercase` and `Should Be Titlecase`.
        """
        if not string.islower():
            self._fail(msg, "'%s' is not lowercase.", string)

    def should_be_uppercase(self, string, msg=None):
        """Fails if the given ``string`` is not in uppercase.

        For example, ``'STRING'`` and ``'WITH SPECIALS!'`` would pass, and
        ``'String'``, ``''`` and ``' '`` would fail.

        The default error message can be overridden with the optional
        ``msg`` argument.

        See also `Should Be Titlecase` and `Should Be Lowercase`.
        """
        if not string.isupper():
            self._fail(msg, "'%s' is not uppercase.", string)

    def should_be_titlecase(self, string, msg=None):
        """Fails if given ``string`` is not title.

        ``string`` is a titlecased string if there is at least one
        character in it, uppercase characters only follow uncased
        characters and lowercase characters only cased ones.

        For example, ``'This Is Title'`` would pass, and ``'Word In UPPER'``,
        ``'Word In lower'``, ``''`` and ``' '`` would fail.

        The default error message can be overridden with the optional
        ``msg`` argument.

        See also `Should Be Uppercase` and `Should Be Lowercase`.
        """
        if not string.istitle():
            self._fail(msg, "'%s' is not titlecase.", string)

    def _convert_to_index(self, value, name):
        if value == '':
            return 0
        if value is None:
            return None
        return self._convert_to_integer(value, name)

    def _convert_to_integer(self, value, name):
        try:
            return int(value)
        except ValueError:
            raise ValueError("Cannot convert '%s' argument '%s' to an integer."
                             % (name, value))

    def _fail(self, message, default_template, *items):
        if not message:
            message = default_template % tuple(unic(item) for item in items)
        raise AssertionError(message)
