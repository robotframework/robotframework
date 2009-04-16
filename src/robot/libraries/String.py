#  Copyright 2008 Nokia Siemens Networks Oyj
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


import re
from fnmatch import fnmatchcase
import string as STRING
try:
    from random import sample
except ImportError:   # No random.sample in Jython 2.2
    from random import randint
    def sample(chars, length):
        max_index = len(chars) - 1
        return [ chars[randint(0, max_index)] for i in xrange(length) ]

from robot import utils


class String:
    
    """A test library for string manipulation and verification.

    `String` is Robot Framework's standard library for manipulating
    strings (e.g. `Replace String With Regexp`, `Split To Lines`) and
    verifying their contents (e.g. `Should Be String`).

    Following keywords from the BuiltIn library can also be used with
    strings:
    - `Catenate`
    - `Get Length`
    - `Length Should Be`
    - `Should (Not) Match (Regexp)`
    - `Should (Not) Be Empty`
    - `Should (Not) Be Equal (As Strings/Integers/Numbers)`
    - `Should (Not) Contain`
    - `Should (Not) Start With`
    - `Should (Not) End With`
    """

    ROBOT_LIBRARY_SCOPE = 'GLOBAL'
    ROBOT_LIBRARY_VERSION = utils.get_version()

    def get_line_count(self, string):
        """Returns the number of lines in the given `string`."""
        return len(string.splitlines())

    def split_to_lines(self, string, start=0, end=None):
        """Converts the `string` into a list of lines. 
        
        It is possible to get only a selection of lines from `start`
        to `end` so that `start` index is inclusive and `end` is
        exclusive. Line numbering starts from 0, and it is possible to
        use negative indices to refer lines from the end.

        Lines are returned without the newlines. The number of
        returned lines is automatically logged.

        Example:
        | @{lines} =        | Split To Lines | ${manylines} |    |    |
        | @{ignore first} = | Split To Lines | ${manylines} | 1  |    |
        | @{ignore last} =  | Split To Lines | ${manylines} |    | -1 |
        | @{5th to 10th} =  | Split To Lines | ${manylines} | 4  | 10 |
        | @{first two} =    | Split To Lines | ${manylines} |    | 1  |
        | @{last two} =     | Split To Lines | ${manylines} | -2 |    |
        """
        start = self._convert_to_index(start, 'start')
        end = self._convert_to_index(end, 'end')
        lines = string.splitlines()[start:end]
        print '*INFO* %d lines returned' % len(lines)
        return lines

    def get_lines_containing_string(self, string, pattern, case_insensitive=False):
        """Returns lines of the given `string` that contain the `pattern`.

        The `pattern` is always considered to be a normal string and a
        line matches if the `pattern` is found anywhere in it. By
        default the match is case-sensitive, but setting
        `case_insensitive` to any value makes it case-insensitive.
        
        Lines are returned as one string catenated back together with
        newlines. Possible trailing newline is never returned. The
        number of matching lines is automatically logged.

        Examples:
        | ${lines} = | Get Lines Containing String | ${result} | An example |
        | ${ret} =   | Get Lines Containing String | ${ret} | FAIL | case-insensitive |

        See `Get Lines Matching Pattern` and `Get Lines Matching Regexp`
        if you need more complex pattern matching.
        """
        if case_insensitive:
            pattern = pattern.lower()
            contains = lambda line: pattern in line.lower()
        else:
            contains = lambda line: pattern in line
        return self._get_matching_lines(string, contains)

    def get_lines_matching_pattern(self, string, pattern, case_insensitive=False):
        """Returns lines of the given `string` that match the `pattern`.

        The `pattern` is a _glob pattern_ where:
        | *        | matches everything |
        | ?        | matches any single character |
        | [chars]  | matches any character inside square brackets (e.g. '[abc]' matches either 'a', 'b' or 'c') |
        | [!chars] | matches any character not inside square brackets |

        A line matches only if it matches the `pattern` fully.  By
        default the match is case-sensitive, but setting
        `case_insensitive` to any value makes it case-insensitive.
        
        Lines are returned as one string catenated back together with
        newlines. Possible trailing newline is never returned. The
        number of matching lines is automatically logged.

        Examples:
        | ${lines} = | Get Lines Matching Pattern | ${result} | Wild???? example |
        | ${ret} = | Get Lines Matching Pattern | ${ret} | FAIL: * | case-insensitive |

        See `Get Lines Matching Regexp` if you need more complex
        patterns and `Get Lines Containing String` if searching
        literal strings is enough.
        """
        if case_insensitive:
            pattern = pattern.lower()
            matches = lambda line: fnmatchcase(line.lower(), pattern)
        else:
            matches = lambda line: fnmatchcase(line, pattern)
        return self._get_matching_lines(string, matches)

    def get_lines_matching_regexp(self, string, pattern):
        """Returns lines of the given `string` that match the regexp `pattern`.

        See `BuiltIn.Should Match Regexp` for more information about
        Python regular expression syntax in general and how to use it
        in Robot Framework test data in particular. A line matches
        only if it matches the `pattern` fully. Notice that to make
        the match case-insensitive, you need to embed case-insensitive
        flag into the pattern.
        
        Lines are returned as one string catenated back together with
        newlines. Possible trailing newline is never returned. The
        number of matching lines is automatically logged.

        Examples:
        | ${lines} = | Get Lines Matching Regexp | ${result} | Reg\\\\w{3} example |
        | ${ret} = | Get Lines Matching Pattern | ${ret} | (?i)FAIL: .* |

        See `Get Lines Matching Pattern` and `Get Lines Containing
        String` if you do not need full regular expression powers.
        """
        regexp = re.compile('^%s$' % pattern)
        return self._get_matching_lines(string, regexp.match)

    def _get_matching_lines(self, string, matches):
        lines = string.splitlines()
        matching = [ line for line in lines if matches(line) ]
        print '*INFO* %d out of %d lines matched' % (len(matching), len(lines))
        return '\n'.join(matching)
    
    def replace_string(self, string, search_for, replace_with, count=-1):
        """ Replaces `search_for` in `string` with `replace_with`.

        If the optional argument `count` is given and positive, only that many
        occurrences from left are replaced.

        Examples:
        | ${str} = | Replace String | ${str} | Hello | Hi     |   |
        | ${str} = | Replace String | ${str} | world | tellus | 1 |
        """        
        count = self._convert_to_index(count, 'count')
        if count <= 0: count = -1
        return string.replace(search_for, replace_with, count)

    def replace_string_with_regexp(self, string, pattern, replace_with, count=-1):
        """Replaces matches with `pattern` in `string` with `replace_with`.

        See `BuiltIn.Should Match Regexp` for more information about
        Python regular expression syntax in general and how to use it
        in Robot Framework test data in particular.

        If the optional argument `count` is given and positive, only that many
        occurrences from left are replaced.

        Examples:
        | ${str} = | Replace String With Regexp | ${str} | (Hello|Hi) | Hei  |   |
        | ${str} = | Replace String With Regexp | ${str} | 20\\d\\d-\\d\\d-\\dd\\d | <DATE>  | 2  |
        """
        count = self._convert_to_index(count, 'count')
        if count <= 0: count = 0
        return re.sub(pattern, replace_with, string, count)

    def split_string(self, string, separator=None, max_split=-1):
        #TODO: Improve short doc
        """Return a list of the words in the `string`.

        Uses `separator` as the delimiter string. If `separator` is not
        specified: runs of consecutive whitespace are regarded as a
        single separator, and the result will contain no empty strings
        at the start or end if the string has leading or trailing whitespace.
        
        If max_split is given, at most `max_split` splits are done
        (thus, the list will have at most 'max_split+1' elements) 
        """
        max_split = self._convert_to_index(max_split, 'max_split')
        return string.split(separator, max_split)

    def split_string_from_right(self, string, separator=None, max_split=-1):
        #TODO: Improve short doc
        """Return a list of the words in the `string`, starting from right.

        Uses `separator` as the delimiter string.
        If max_split is given, at most `max_split` splits are done from right.
        (thus, the list will have at most 'max_split+1' elements) 
        """
        # Jython does not have rsplit for string
        reversed = self.split_string(string[::-1], separator, max_split)
        reversed = [ r[::-1] for r in reversed ]
        return reversed[::-1]
    
    def generate_random_string(self, length=8, chars=STRING.letters+STRING.digits):
        """
        Generates a random string of the required `length` (8 by default).
        
        Second argument is a set of characters to draw from:
        letters (lower and upper case) and digits by default. 
        """
        length = self._convert_to_index(length, 'length')
        return ''.join(sample(chars, length))


    def get_substring(self, string, start, end=None):
        """Returns a substring from `start` index to `end` index. 

        First item's index is 0. it is possible to use also negative `start` and   
        end indexes which means 
        Example:
        | ${first two} =           | Get Substring | Robot       | 0  |  2 |
        | Should Be Equal          | ${first two}  | Ro          |
        | ${two from almost end} = | Get Substring | Hello Robot | -3 | -1 |
        | Should Be Equal          | ${two from almost end} | bo |
        """
        
        start = self._convert_to_index(start, 'start')
        if not end:
            return string[start:]
        end = self._convert_to_index(end, 'end')
        return string[start:end]

    def should_be_string(self, item, msg=None):
        """ Fails if item is not a string (e.g. boolean, number)"""
        if not isinstance(item, basestring):
            if msg is None:
                msg = "Given item is not a string"
            raise AssertionError(msg)
        
    def should_not_be_string(self, item, msg=None):
        """ Fails if item is a string """
        if isinstance(item, basestring):
            if msg is None:
                msg = "Given item '%s' is a string" % item
            raise AssertionError(msg)

    def get_line(self, string, number):
        """
        From given `string`, extracts line with given `number`.
        
        '0' is the first line. '-1' is the last line.
        Line is returned without the end-of-line character.

        Example:
        | ${first line}= | Get Line | ${string} | 0 |
        """
        number = self._convert_to_index(number, 'number')
        return string.splitlines()[number]

    def fetch_from_left(self, string, to_find):
        """
        Fetches the `string` part before the FIRST occurrence of `to_find`.
        
        If `to_find` is not found, whole string is returned.
        """
        return string.split(to_find)[0]
        
    def fetch_from_right(self, string, to_find):
        """
        Fetches the `string` after the LAST occurence of `to_find`.
        
        If `to_find` not found within `string`, whole string is returned.
        """
        return string.split(to_find)[-1]

    def _convert_to_index(self, value, name):
        if value == '':
            return 0
        if value is None:
            return None
        try:
            return int(value)
        except ValueError:
            raise ValueError("Cannot convert '%s' argument '%s' to an integer" % (name, value))

