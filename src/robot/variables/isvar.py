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

from .variablesplitter import VariableIterator


def is_var(string):
    if not isinstance(string, basestring):
        return False
    length = len(string)
    return length > 3 and string[0] in ['$','@'] and string.rfind('{') == 1 \
            and string.find('}') == length - 1


def is_scalar_var(string):
    return is_var(string) and string[0] == '$'


def is_list_var(string):
    return is_var(string) and string[0] == '@'


def contains_var(string):
    return bool(isinstance(string, basestring) and
                VariableIterator(string, '$@'))
