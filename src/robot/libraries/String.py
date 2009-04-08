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
import os
import re
import shutil
import time
import fnmatch
import glob
from types import ListType
from types import StringType

from robot import utils
from robot.errors import DataError
import robot.output
from random import Random
import string as STRING


class String:
    
    """
    This library contains keywords related to string manipulation.

    Following keywords from the BuiltIn library can be used with strings:

    - `Catenate`
    - `Get Length`
    - `Grep`
    - `Should (Not) Match (Regexp)`
    - `Should (Not) Be Empty`
    - `Should (Not) Be Equal As Strings`
    - `Should (Not) Contain`
    - `Should (Not) End With`
    - `Should (Not) Start With`
    
    From Collections library, `Length Should Be` can be used with strings as well.

    """

    ROBOT_LIBRARY_SCOPE = 'GLOBAL'

    def get_line_count(self, string):
        """Returns the number of lines."""
        return len(string.splitlines(0))

    def split_to_lines(self, string, start=0, end=-1):
        """Converts `string` to list of lines. 
        
        Ends of lines are removed. It is possible to get only selection of 
        lines, from `start` to `end`. Line numbering starts from 0.

        Example:
        | @{lines} = | Get Lines as List | ${multilines} |
        | @{first two lines} = | Get Lines as List | ${multilines} | 0 | 1 |
        """
        lines = string.splitlines()
        start = self._convert_to_int(start, 'start')
        end = self._convert_to_int(end, 'end')
        print "*TRACE* Got '%d' lines. Returning from %d to %d" % (len(lines), start, end)        
        if not lines:
            return []
        if end == -1:
            return lines[start:]
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

    #TODO: Better name: replace_string_with_regexp
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
        # Add doc for separator
        """
        Return a list of the words in the `string`,
        using `split_with` as the delimiter string.
        If max_split is given, at most `max_split` splits are done
        (thus, the list will have at most 'max_split+1' elements) 
        """
        self._convert_to_int(max_split, 'max_split')
        return string.split(separator, max_split)

    def split_string_from_right(self, string, separator=None, max_split=-1):
        #no need to to have separate fetch from left
        pass
    
    def generate_random_string(self, length=8, chars=STRING.letters+STRING.digits):
        """
        Generates a random string of the required `length` (8 by default).
        Second argument is a set of characters to draw from,
        lower and upper case letters, and digits by default.
         
         
        """
        length = self._convert_to_int(length, 'length')
        return ''.join( Random().sample(chars, length) )


    # TODO: Should this be position, length or start, end. If start, end is used, there is 
    # possibility to remove x characters from behind of the string by using negative index.
    def get_substring(self, string, position, length):
        """
        Returns a substring of given `length` starting from position of `position` ,
        which should be numbers.
        Position starts from '0'. 

        Example:
        | ${first two}= | Get Substring | Robot | 0 | 2 |
        """
        position = self._convert_to_int(position, 'position')
        length = self._convert_to_int(length, 'length')
        return string[position : position + length]

    def should_be_string(self, item, msg=None):
        """ Fails if item is not a string (e.g. list, number)"""
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
    
    def get_columns(self, string, column_number, delimiter=' '):
        """
        Takes `string`, splits into columns using delimiter
        and returns the `column_number` column.
        Column numbering starts from 0. Default delimiter is single space.
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

