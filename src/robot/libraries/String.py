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


# TODO: assertions, checks, generate html and check, write internal tests
# TODO: `` comments
# TODO: Check documentation and use short docs. Is some more examples needed?
import re
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
    - `Should (Not) Be Equal (As Strings)`
    - `Should (Not) Contain`
    - `Should (Not) Start With`
    - `Should (Not) End With`
    """

    ROBOT_LIBRARY_SCOPE = 'GLOBAL'
    ROBOT_LIBRARY_VERSION = utils.get_version()

    def get_line_count(self, string):
        """Returns the number of lines."""
        return len(string.splitlines())

    def split_to_lines(self, string, start=0, end=None):
        """Converts `string` to list of lines. 
        
        Ends of lines are removed. It is possible to get only selection of 
        lines, from `start` to `end`. Line numbering starts from 0. 

        Example:
        | @{lines} = | Split to lines | ${manylines} |
        | @{first two lines} = | Split to lines | ${manylines} | 0 | 1 |
        """
        lines = string.splitlines()
        start = self._convert_to_int(start, 'start')
        if not lines:
            return []
        if not end:
            return lines[start:]
        end = self._convert_to_int(end, 'end')
        return lines[start:end]

    def replace_string(self, string, search_for, replace_with, count=0):
        """ Replaces `search_for` in `string` with `replace_with`.

        You can specify how many occurrences are replaced with `count`,
        otherwise all occurrences are replaced.
        """        
        count = self._convert_to_int(count, 'count')
        if count <= 0:
            return string.replace(search_for, replace_with)
        return string.replace(search_for, replace_with, count)

    def replace_string_with_regexp(self, string, pattern, replace_with, count=0):
        """Replaces matches with `pattern` in `string` with `replace_with`.

        You can specify how many `pattern` occurrences are replaced with `count`,
        otherwise all occurrences are replaced.

        Regular expression format is according to Python 're' module, which
        has a pattern syntax derived from Perl, and thus also very similar to
        the one in Java. See the following documents for more details about
        regular expressions in general and Python implementation in particular.
        
        * http://docs.python.org/lib/module-re.html
        """
        count = self._convert_to_int(count, 'count')
        p = re.compile(pattern)
        return p.sub(replace_with, string, count)

    def split_string(self, string, separator=None, max_split=-1):
        """Return a list of the words in the `string`.

        Uses `separator` as the delimiter string. If `separator` is not
        specified: runs of consecutive whitespace are regarded as a
        single separator, and the result will contain no empty strings
        at the start or end if the string has leading or trailing whitespace.
        
        If max_split is given, at most `max_split` splits are done
        (thus, the list will have at most 'max_split+1' elements) 
        """
        max_split = self._convert_to_int(max_split, 'max_split')
        return string.split(separator, max_split)

    def split_string_from_right(self, string, separator=None, max_split=-1):
        """Return a list of the words in the `string`, starting from right.

        Uses `split_with` as the delimiter string.
        If max_split is given, at most `max_split` splits are done from right.
        (thus, the list will have at most 'max_split+1' elements) 
        """
        # Jython does not have rsplit for string and therefore 
        reversed = self.split_string(string[::-1], separator, max_split)
        reversed = [ r[::-1] for r in reversed ]
        return reversed[::-1]
    
    def generate_random_string(self, length=8, chars=STRING.letters+STRING.digits):
        """
        Generates a random string of the required `length` (8 by default).
        
        Second argument is a set of characters to draw from,
        lower and upper case letters, and digits by default. 
        """
        length = self._convert_to_int(length, 'length')
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
        
        start = self._convert_to_int(start, 'start')
        if not end:
            return string[start:]
        end = self._convert_to_int(end, 'end')
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
    
    def get_columns(self, string, column_number, delimiter=None):
        """
        Takes `string`, splits into columns using delimiter.
        
        Returns the columns as list.
        See `split_string` for the description of default delimiter.
        """
        if not delimiter:
            raise AssertionError("Delimiter should not be empty")
        column_number = self._convert_to_int(column_number, 'column_number')

        columns = []
        for line in string.splitlines():
            items = line.split(delimiter)
            try:
                columns.append(items[column_number])
            except IndexError:
                columns.append('')
        return columns

    def get_line(self, string, number):
        """
        From given `string`, extracts line with given `number`.
        
        '0' is the first line. '-1' is the last line.
        Line is returned without the end-of-line character.

        Example:
        | ${first line}= | Get Line | ${string} | 0 |
        """
        number = self._convert_to_int(number, 'number')
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

    def _convert_to_int(self, value, name):
        try:
            return int(value)
        except ValueError:
            raise ValueError("Cannot convert '%s' value '%s' to an integer" % (name, value))

