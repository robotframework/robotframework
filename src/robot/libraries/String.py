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

from robot import utils
from robot.errors import DataError
from types import ListType
from types import StringType
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
        multiLines = lines.splitlines(0)
        print "*INFO* Got '%d' lines" % len(multiLines)
        lineCount = len(multiLines)
        if (lineCount == 0): return ""
        return multiLines[0]

    def get_second_part_of_lines_after_string(self, lines, splitString):
        """
        Splits each line using splitString, returns second part
        Like awk -F 'splitString' '{print $2}'
        Only lines containing requested string are taken.
        """
        resultLines=''
        multilines = lines.splitlines(0)
        for line in multilines:
            # include only lines which contain requested string
            if line.count(splitString):
                splitLine = line.split(splitString)
                resultLines += splitLine[1] + '\n'
        return resultLines
    
    def get_head_lines_as_list(self, lines, lineCount):
        """
      Returns the first lineCount lines of input: head -lineCount
      as a list
        """
        lineCount = int(lineCount)
        multiLines = lines.splitlines(0)
        print "*INFO* Got '%d' lines" % len(multiLines)
        totalLineCount = len(multiLines)
        if (totalLineCount == 0): return ""
        return multiLines[0 : (lineCount)]

    def get_line_count(self, lines):
        """
      Returns the number of lines.
        """
        multiLines = lines.splitlines(0)
        print "*INFO* Got '%d' lines" % len(multiLines)
        lineCount = len(multiLines)
        return lineCount
        
    def get_last_line(self, lines):
        """
      Returns the last line of input: tail -1
        """
        multiLines = lines.splitlines(0)
        print "*INFO* Got '%d' lines" % len(multiLines)
        lineCount = len(multiLines)
        if (lineCount == 0): return ""
        return multiLines[lineCount - 1]

    def get_all_but_last_line_as_list(self, lines):
        """
      Returns list of all but the last line of input
        """
        multiLines = lines.splitlines(0)
        print "*INFO* Got '%d' lines" % len(multiLines)
        lineCount = len(multiLines)
        if (lineCount == 0): return []
        return multiLines[0 : lineCount - 1]

    def get_all_but_last_line(self, lines):
        """
      Returns all but the last line of input as string (cuts out the last line)
        """
        multiLines = lines.splitlines(0)
        allButLast = "";
        print "*INFO* Got '%d' lines" % len(multiLines)
        lineCount = len(multiLines)
        if (lineCount < 2): return ""
        for i in range (0, lineCount - 1):
        	allButLast += multiLines[i] + "\n"
        return allButLast

    def get_lines_as_list(self, lines, removeEmptyLines = 0):
        """
        
      Converts multiline input to list of lines. Ends of lines removed.
      If removeEmptyLines != 0, empty lines are removed
      
        """
        multiLines = lines.splitlines(0)
        print "*INFO* Got '%d' lines" % len(multiLines)
        lineCount = len(multiLines)
        if (lineCount == 0): return list()
        if (removeEmptyLines):
            multiLines = self._remove_empty_elements_from_list(multiLines)
        return multiLines

    def _remove_empty_elements_from_list(self, elements):
        """
        Removes empty elements from list. Returns list.
        """
        newelements = []
        for i in range (0, len(elements) ):
            if (elements[i] != ''):
                newelements.append(elements[i])
        return newelements         

    def split_to_last_line_and_rest(self, lines):
        """
        Splits multiline input to all_but_last and last line.
        Returns a list [lastline, all_but_last_line]
        Used for getting RC and output from the command executed via SSH, RC being the last line.
        """
        multiLines = lines.splitlines(0)
        lineCount = len(multiLines)
        # we have 1 line
        if (lineCount < 2):
            retLines = []
            retLines.append(multiLines[0])
            retLines.append('')
            return retLines
        lastLine = multiLines[lineCount - 1]
        # if line before last is empty, remove it - comes from additional \n in the echo
        if (multiLines [lineCount-2] == ""): lineCount = lineCount - 1
        allButLast = ""
        for i in range (0, lineCount - 1):
        	allButLast += multiLines[i] + "\n"

        retLines = [lastLine, allButLast]
        return retLines

    def add_crlf_to_all_lines(self, lines):
        """
        Adds \\r\\n to all lines
        """
        # replace CRLF with LF (in case there's some inside)
        retLines = ''
        retLines = lines.replace('\r\n','\n')
        retLines = retLines.replace('\n','\r\n')
        return retLines

    def replace_string(self, stringToReplaceIn, stringToSearchFor, stringToReplaceWith):
        """
        Searches stringToSearchFor in stringToReplaceIn and replaces with stringToReplaceWith)
        """
        result = stringToReplaceIn.replace(stringToSearchFor, stringToReplaceWith)
        return result
    
    def convert_list_to_csv(self, convertList):
        """
        Converts a list of elements to comma-separated element string
        ['a','b','c'] => 'a,b,c'
        """
        result = ''
        if isinstance(convertList, StringType):
            tempList = []
            tempList.append(convertList)
            convertList = tempList
        for listElement in convertList:
            result += listElement + ","
        result = result.rstrip(',')
        return result

    def convert_csv_to_list(self, convertCsv):
        """
        Converts a comma-separated element string to a list of elements
        'a,b,c' => ['a','b','c']
        """
        result = convertCsv.split(',')
        return result

    def split_string(self, stringToSplit, splitString):
        """
        Split stringToSplit, divided by splitString
        """
        result = stringToSplit.split(splitString)
        return result
        
    def get_lines_not_matching_any_of_elements(self, linesToMatch, linesToExcludeList):
        """
        This keyword returns linesToMatch without lines where any of linesToExclude is a substring.
        Works like grep -v ???
        """
        resultLines = ""
        someElementMatches = 0
        linesToMatchList = linesToMatch.splitlines(0)
        for lineToMatch in linesToMatchList:
            someElementMatches = 0
            for lineToExclude in linesToExcludeList:
                # check if is a substring
                if (lineToMatch.count(lineToExclude)):
                    someElementMatches = 1
            if not (someElementMatches): resultLines = lineToMatch + "\n"
        return resultLines

    def generate_Random_String(self,strLength=8, chars=string.letters + string.digits):
        """
            Generates a random string of the required length (8 by default).
            Second argument is a set of characters to draw from, letters + digits for default
        """        
        strLength = int(strLength)
        fromCharsLen = len(chars)
        times = int(strLength / fromCharsLen)
        result = ''
        for i in range (0, times):
            result += ''.join( Random().sample(chars, fromCharsLen) )
        rest = strLength % fromCharsLen
        result += ''.join(Random().sample(chars, rest) )
        #print "Len : %d" % len(chars)
        return result


    def get_substring(self, sourceStr, leftIndex, rightIndex):
        """
        Returns a substring from leftIndex to rightIndex, which should be numbers (0, len-1)
        """
        return sourceStr[int(leftIndex) : int(rightIndex)]
    
    
