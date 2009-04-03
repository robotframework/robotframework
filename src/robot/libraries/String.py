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
import string


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

    def get_line_count(self, lines):
        """
        Returns the number of lines.
        """
        line_list = lines.splitlines(0)
        print "*INFO* Got '%d' lines" % len(line_list)
        return len(line_list)

    def get_lines_as_list(self, lines, start=0, end=-1):
        """
        Converts multiline input to list of lines. Ends of lines removed.
        It is possible to get only selection of lines, from `start` to `end`.
        Line numbering starts from 0.

        Example:
        | @{lines} | Get Lines as List | ${multilines} |
        | @{first two lines} | Get Lines as List | ${multilines} | 0 | 1 |
        """
        line_list = lines.splitlines(0)
        line_count = len(line_list)

        start = self._index_to_int(start)
        end = self._index_to_int(end)
        if (end == -1):
            end = line_count
        print "*TRACE* Got '%d' lines. Returning from %d to %d" % (line_count, start, end)
        
        if (line_count == 0):
            return list()
        
        return line_list[start : end]

    def _remove_empty_elements_from_list(self, elements):
        """
        Removes empty elements from list. Returns list.
        """
        newelements = []
        for element in elements:
            if element:
                newelements.append(element)
        return newelements

    def replace_string(self, replace_in, search_for, replace_with):
        """
        Searches `search_for` in `replace_in` and replaces with `replace_with`
        """
        result = replace_in.replace(search_for, replace_with)
        return result

    def replace_pattern(self, replace_in, pattern, replace_with, count=0):
        """
        Searches for pattern matching `regexp` in `replace_in`
        and replaces with `replace_with`.
        You can specify that maximum `count` pattern occurrences are replaced,
        otherwise all are replaced.

        Regular expression format is according to Python 're' module, which
        has a pattern syntax derived from Perl, and thus also very similar to
        the one in Java. See the following documents for more details about
        regular expressions in general and Python implementation in particular.
        
        * http://docs.python.org/lib/module-re.html
        
        """
        p = re.compile(pattern)
        return p.sub(replace_with, replace_in, count)

    def split_string(self, to_split, split_with, max_split=-1):
        """
        Return a list of the words in the `to_split` string,
        using `split_with` as the delimiter string.
        If maxsplit is given, at most `maxsplit` splits are done
        (thus, the list will have at most 'maxsplit+1' elements) 
        """
        return to_split.split(split_with, max_split)

    def generate_random_string(self, length=8, chars=string.letters \
                               + string.digits):
        """
        Generates a random string of the required `length` (8 by default).
        Second argument is a set of characters to draw from,
         letters + digits for default
        """        
        length = int(length)
        src_len = len(chars)
        times = int(length / src_len)
        result = ''
        for i in range (0, times):
            result += ''.join( Random().sample(chars, src_len) )
        rest = length % src_len
        result += ''.join(Random().sample(chars, rest) )
        return result


    def get_substring(self, string, position, length):
        """
        Returns a substring of given `length` starting from position of `position` ,
        which should be numbers.
        Position starts from '0'. 

        Example:
        | ${first two}= | Get Substring | Robot | 0 | 2 |
        """
        position = self._index_to_int(position)
        length = self._index_to_int(length)
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
        
    def get_column(self, input_text, column_number, delimiter=' '):
        """
        Takes input text, splits into columns using delimiter
        and returns the `column_number` column.
        Column numbering starts from 0. Default delimiter is single space.
        """
        if not delimiter:
            raise AssertionError("Delimiter should not be empty")
        
        lines = input_text.splitlines(0)
        column = ''
        
        column_number = self._index_to_int(column_number)
        for line in lines:
            row = line.split(delimiter)
            try:
                item = row[column_number]
            except IndexError:
                item = ''
            column += item + '\n'
        return column    

    def get_line(self, lines, number):
        """
        From given `lines`, extracts line with given `number`.
        '0' is the first line. '-1' is the last line.
        Line is returned without the end-of-line character.

        Example:
        | ${first line}= | Get Line | ${lines} | 0 |
        """
        lines_list = lines.splitlines(0)
        number = self._index_to_int(number)
        return lines_list[number]

    def fetch_from_left(self, string, to_find):
        """
        Fetches the `string` part before the FIRST occurence of `to_find`.
        If `to_find` is not found, whole string is returned.
        """
        split_string = string.split(to_find)
        return split_string[0]
        
        
    def fetch_from_right(self, string, to_find):
        """
        Fetches the `string` after the LAST occurence of `to_find`.
        If `to_find` not found within `string`, whole string is returned.
        """
        split_string = string.split(to_find)
        return split_string[-1]

    def _index_to_int(self, index, empty_to_zero=False):
        # copied from Collections
        if empty_to_zero and not index:
            return 0
        try:
            return int(index)
        except ValueError:
            raise ValueError("Cannot convert index '%s' to an integer" % index)


