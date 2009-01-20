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
    
    """This library contains keywords related to string operations."""

    ROBOT_LIBRARY_SCOPE = 'GLOBAL'
        		        
    def get_first_line(self, lines):
        """
        
      Returns the first line of input: head -1
        """
        line_list = lines.splitlines(0)
        print "*INFO* Got '%d' lines" % len(line_list)
        if line_list:
            return line_list[0]
        return ''

    def get_second_part_of_lines_after_string(self, lines, split_string):
        """
        Splits each line using split_with, returns second part
        Like awk -F 'split_with' '{print $2}'
        Only lines containing requested string are taken.
        """
        result_lines=''
        line_list = lines.splitlines(0)
        for line in line_list:
            # include only lines which contain requested string
            if (split_string in line):
                splitLine = line.split(split_string)
                result_lines += splitLine[1] + '\n'
        return result_lines
    
    def get_head_lines_as_list(self, lines, line_count):
        """
        Returns the first line_count lines of input: head -line_count
        as a list
        """
        line_count = int(line_count)
        line_list = lines.splitlines(0)
        print "*INFO* Got '%d' lines" % len(line_list)
        if line_list:
            return line_list[0 : (line_count)]
        return ''

    def get_line_count(self, lines):
        """
      Returns the number of lines.
        """
        line_list = lines.splitlines(0)
        print "*INFO* Got '%d' lines" % len(line_list)
        line_count = len(line_list)
        return line_count
        
    def get_last_line(self, lines):
        """
        Returns the last line of input
        """
        line_list = lines.splitlines(0)
        print "*INFO* Got '%d' lines" % len(line_list)
        if line_list:
            return line_list[- 1]
        return ""

    def get_all_but_last_line_as_list(self, lines):
        """
        Returns list of all but the last line of input
        """
        line_list = lines.splitlines(0)
        print "*INFO* Got '%d' lines" % len(line_list)
        line_count = len(line_list)
        if line_list:
            return line_list[0 : line_count - 1]
        return []

    def get_all_but_last_line(self, lines):
        """
        Returns all but the last line of input as string (cuts out the last line)
        """
        line_list = lines.splitlines(0)
        all_but_last = "";
        print "*INFO* Got '%d' lines" % len(line_list)
        line_count = len(line_list)
        if (line_count < 2): return ""
        for i in range (0, line_count - 1):
        	all_but_last += line_list[i] + "\n"
        return all_but_last

    def get_lines_as_list(self, lines, remove_empty_lines = 0):
        """
        Converts multiline input to list of lines. Ends of lines removed.
        If removeEmptyLines != 0, empty lines are removed
        """
        line_list = lines.splitlines(0)
        print "*INFO* Got '%d' lines" % len(line_list)
        line_count = len(line_list)
        if (line_count == 0): return list()
        if (remove_empty_lines):
            line_list = self._remove_empty_elements_from_list(line_list)
        return line_list

    def _remove_empty_elements_from_list(self, elements):
        """
        Removes empty elements from list. Returns list.
        """
        newelements = []
        for element in elements:
            if element:
                newelement.append(element)
        return newelements

    def split_to_last_line_and_rest(self, lines):
        """
        Splits multiline input to all_but_last and last line.
        Returns a list [last_line, all_but_last_line]
        Used for getting RC and output from the command executed via SSH, RC being the last line.
        """
        line_list = lines.splitlines(0)
        line_count = len(line_list)
        
        # just last line. Return list of [last line, '']        
        if (line_count == 1):
            result_list = []
            result_list.append(line_list[0])
            result_list.append('')
            return result_list

        last_line = line_list[-1]
        # if line before last is empty, remove it
        # - comes from additional \n in the echo
        if (line_list [line_count-2] == ""): line_count = line_count - 1
        all_but_last = ""
        for i in range (0, line_count - 1):
            all_but_last += line_list[i] + "\n"
        result_list = [last_line, all_but_last]
        return result_list

    def add_crlf_to_all_lines(self, lines):
        """
        Adds \\r\\n to all lines
        """

        result_lines = ''
        # replace CRLF with LF (in case there's some inside)
        result_lines = lines.replace('\r\n','\n')
        result_lines = result_lines.replace('\n','\r\n')
        return result_lines

    def replace_string(self, replace_in, search_for, replace_with):
        """
        Searches search_for in replace_in and replaces with replace_with)
        """
        result = replace_in.replace(search_for, replace_with)
        return result
    
    def convert_list_to_csv(self, convert_list):
        """
        Converts a list of elements to comma-separated element string
        ['a','b','c'] => 'a,b,c'
        """
        result = ''
        if isinstance(convert_list, StringType):
            tempList = []
            tempList.append(convert_list)
            convert_list = tempList
        for listElement in convert_list:
            result += listElement + ","
        result = result[0 : -1]
        #result = result.rstrip(',')
        return result

    def convert_csv_to_list(self, csv_string):
        """
        Converts a comma-separated element string to a list of elements
        'a,b,c' => ['a','b','c']
        """
        result = csv_string.split(',')
        return result

    def split_string(self, to_split, split_with):
        """
        Split to_split, divided by split_with
        """
        result = to_split.split(split_with)
        return result
        
    def get_lines_not_matching_any_of_elements(self, to_match, to_exclude):
        """
        This keyword returns to_match without lines
        where any of to_exclude is a substring.
        """
        result_lines = ""
        some_matches = 0
        to_matchList = to_match.splitlines(0)
        for line_to_match in to_matchList:
            some_matches = 0
            for line_to_exclude in to_exclude:
                # check if is a substring
                if (line_to_exclude in line_to_match):
                    some_matches = 1
            if not (some_matches): result_lines = line_to_match + "\n"
        return result_lines

    def generate_random_string(self, length=8, chars=string.letters + string.digits):
        """
            Generates a random string of the required length (8 by default).
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


    def get_substring(self, string, left_index, right_index):
        """
        Returns a substring from left_index to right_index,
        which should be numbers (0, len-1)
        """
        return string[int(left_index) : int(right_index)]
    
    def is_a_string(self, item):
        """ Checks whether item is a string. Returns true or false"""
        if isinstance(item, basestring):
            print "*INFO* is a string '%s' lines" % item
            return True
        return False

    def should_be_a_string(self, item, msg=None):
        """ Fails if item is not a string (e.g. list, number)"""
        if not (self.is_a_string(item)):
            if msg is None:
                msg = "Given item is not a string"
            raise AssertionError(msg)
        
    def should_not_be_a_string(self, item, msg=None):
        """ Fails if item is a string (e.g. list, number)"""
        if (self.is_a_string(item)):
            if msg is None:
                msg = "Given item '%s' is a string" % item
            raise AssertionError(msg)
        
    
    def get_column(self, input_text, column_number, delimiter=' '):
        """
        Takes input text, splits into columns using delimiter
        and returns the column_number column.
        Column numbering starts from 1. Default delimiter is single space.
        """
        if (not delimiter):
            raise AssertionError("Delimiter should not be empty")
        
        lines = input_text.splitlines(0)
        column = ''
        
        column_number = int(column_number - 1)
        for line in lines:
            row = line.split(delimiter)
            try:
                item = row[column_number]
            except IndexError:
                item = ''
            column += item + '\n'
        return column    
