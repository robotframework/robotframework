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

from robot.errors import DataError
from robot.utils import is_string

from .splitter import VariableIterator


def is_var(string, identifiers='$@&'):
    if not string or not is_string(string) or len(string) < 4:
        return False
    if string[0] not in identifiers or string[1] != '{' or string[-1] != '}':
        return False
    body = string[2:-1]
    return '{' not in body and '}' not in body


def is_scalar_var(string):
    return is_var(string, identifiers='$')


def is_list_var(string):
    return is_var(string, identifiers='@')


def is_dict_var(string):
    return is_var(string, identifiers='&')


def contains_var(string, identifiers='$@&'):
    return (is_string(string) and
            any(i in string for i in identifiers) and
            '{' in string and '}' in string and
            bool(VariableIterator(string, identifiers)))


def validate_var(string, identifiers='$@&'):
    if not is_var(string, identifiers):
        raise DataError("Invalid variable name '%s'." % string)
