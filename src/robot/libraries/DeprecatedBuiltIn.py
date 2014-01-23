#  Copyright 2008-2014 Nokia Solutions and Networks
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
import fnmatch


from robot.utils import asserts

import BuiltIn


BUILTIN = BuiltIn.BuiltIn()

class DeprecatedBuiltIn:
    ROBOT_LIBRARY_SCOPE = 'GLOBAL'

    integer = BUILTIN.convert_to_integer
    float = BUILTIN.convert_to_number
    string = BUILTIN.convert_to_string
    boolean = BUILTIN.convert_to_boolean
    list = BUILTIN.create_list

    equal = equals = fail_unless_equal = BUILTIN.should_be_equal
    not_equal = not_equals = fail_if_equal = BUILTIN.should_not_be_equal
    is_true = fail_unless = BUILTIN.should_be_true
    is_false = fail_if = BUILTIN.should_not_be_true
    fail_if_ints_equal = ints_not_equal = BUILTIN.should_not_be_equal_as_integers
    ints_equal = fail_unless_ints_equal = BUILTIN.should_be_equal_as_integers
    floats_not_equal = fail_if_floats_equal = BUILTIN.should_not_be_equal_as_numbers
    floats_equal = fail_unless_floats_equal = BUILTIN.should_be_equal_as_numbers
    does_not_start = fail_if_starts = BUILTIN.should_not_start_with
    starts = fail_unless_starts = BUILTIN.should_start_with
    does_not_end = fail_if_ends = BUILTIN.should_not_end_with
    ends = fail_unless_ends = BUILTIN.should_end_with
    does_not_contain = fail_if_contains = BUILTIN.should_not_contain
    contains = fail_unless_contains = BUILTIN.should_contain
    does_not_match = fail_if_matches = BUILTIN.should_not_match
    matches = fail_unless_matches = BUILTIN.should_match
    does_not_match_regexp = fail_if_regexp_matches = BUILTIN.should_not_match_regexp
    matches_regexp = fail_unless_regexp_matches = BUILTIN.should_match_regexp

    noop = BUILTIN.no_operation
    set_ = BUILTIN.set_variable
    message = BUILTIN.comment

    variable_exists = fail_unless_variable_exists = BUILTIN.variable_should_exist
    variable_does_not_exist = fail_if_variable_exists = BUILTIN.variable_should_not_exist

    def error(self, msg=None):
        """Errors the test immediately with the given message."""
        asserts.error(msg)

    def grep(self, text, pattern, pattern_type='literal string'):
        lines = self._filter_lines(text.splitlines(), pattern, pattern_type)
        return '\n'.join(lines)

    def _filter_lines(self, lines, pattern, ptype):
        ptype = ptype.lower().replace(' ','').replace('-','')
        if not pattern:
            filtr = lambda line: True
        elif 'simple' in ptype or 'glob' in ptype:
            if 'caseinsensitive' in ptype:
                pattern = pattern.lower()
                filtr = lambda line: fnmatch.fnmatchcase(line.lower(), pattern)
            else:
                filtr = lambda line: fnmatch.fnmatchcase(line, pattern)
        elif 'regularexpression' in ptype or 'regexp' in ptype:
            pattern = re.compile(pattern)
            filtr = lambda line: pattern.search(line)
        elif 'caseinsensitive' in ptype:
            pattern = pattern.lower()
            filtr = lambda line: pattern in line.lower()
        else:
            filtr = lambda line: pattern in line
        return [ line for line in lines if filtr(line) ]

