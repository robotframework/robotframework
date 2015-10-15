#  Copyright 2008-2015 Nokia Solutions and Networks
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

from robot.utils import is_string, py2to3


class VariableSplitter(object):

    def __init__(self, string, identifiers='$@%&*'):
        self.identifier = None
        self.base = None
        self.index = None
        self.start = -1
        self.end = -1
        self._identifiers = identifiers
        self._may_have_internal_variables = False
        if not is_string(string):
            self._max_end = -1
            return
        self._max_end = len(string)
        try:
            self._split(string)
        except ValueError:
            pass
        else:
            self._finalize()

    def get_replaced_variable(self, replacer):
        if self._may_have_internal_variables:
            base = replacer.replace_string(self.base)
        else:
            base = self.base
        # This omits possible list/dict variable index.
        return '%s{%s}' % (self.identifier, base)

    def is_variable(self):
        return bool(self.identifier and self.base and
                    self.start == 0 and self.end == self._max_end)

    def is_list_variable(self):
        return bool(self.identifier == '@' and self.base and
                    self.start == 0 and self.end == self._max_end and
                    self.index is None)

    def is_dict_variable(self):
        return bool(self.identifier == '&' and self.base and
                    self.start == 0 and self.end == self._max_end and
                    self.index is None)

    def _finalize(self):
        self.identifier = self._variable_chars[0]
        self.base = ''.join(self._variable_chars[2:-1])
        self.end = self.start + len(self._variable_chars)
        if self._has_index():
            self.index = ''.join(self._index_chars[1:-1])
            self.end += len(self._index_chars)

    def _has_index(self):
        return self._index_chars and self._index_chars[-1] == ']'

    def _split(self, string):
        start_index, max_index = self._find_variable(string)
        self.start = start_index
        self._open_curly = 1
        self._state = self._variable_state
        self._variable_chars = [string[start_index], '{']
        self._index_chars = []
        self._string = string
        start_index += 2
        for index, char in enumerate(string[start_index:]):
            index += start_index  # Giving start to enumerate only in Py 2.6+
            try:
                self._state(char, index)
            except StopIteration:
                return
            if index == max_index and not self._scanning_index():
                return

    def _scanning_index(self):
        return self._state in (self._waiting_index_state, self._index_state)

    def _find_variable(self, string):
        max_end_index = string.rfind('}')
        if max_end_index == -1:
            raise ValueError('No variable end found')
        if self._is_escaped(string, max_end_index):
            return self._find_variable(string[:max_end_index])
        start_index = self._find_start_index(string, 1, max_end_index)
        if start_index == -1:
            raise ValueError('No variable start found')
        return start_index, max_end_index

    def _find_start_index(self, string, start, end):
        while True:
            index = string.find('{', start, end) - 1
            if index < 0:
                return -1
            if self._start_index_is_ok(string, index):
                return index
            start = index + 2

    def _start_index_is_ok(self, string, index):
        return string[index] in self._identifiers \
            and not self._is_escaped(string, index)

    def _is_escaped(self, string, index):
        escaped = False
        while index > 0 and string[index-1] == '\\':
            index -= 1
            escaped = not escaped
        return escaped

    def _variable_state(self, char, index):
        self._variable_chars.append(char)
        if char == '}' and not self._is_escaped(self._string, index):
            self._open_curly -= 1
            if self._open_curly == 0:
                if not self._can_contain_index():
                    raise StopIteration
                self._state = self._waiting_index_state
        elif char in self._identifiers:
            self._state = self._internal_variable_start_state

    def _can_contain_index(self):
        return self._variable_chars[0] in '@&'

    def _internal_variable_start_state(self, char, index):
        self._state = self._variable_state
        if char == '{':
            self._variable_chars.append(char)
            self._open_curly += 1
            self._may_have_internal_variables = True
        else:
            self._variable_state(char, index)

    def _waiting_index_state(self, char, index):
        if char != '[':
            raise StopIteration
        self._index_chars.append(char)
        self._state = self._index_state

    def _index_state(self, char, index):
        self._index_chars.append(char)
        if char == ']':
            raise StopIteration


@py2to3
class VariableIterator(object):

    def __init__(self, string, identifiers='$@%&*'):
        self._string = string
        self._identifiers = identifiers

    def __iter__(self):
        string = self._string
        while True:
            var = VariableSplitter(string, self._identifiers)
            if var.identifier is None:
                break
            before = string[:var.start]
            variable = '%s{%s}' % (var.identifier, var.base)
            string = string[var.end:]
            yield before, variable, string

    def __len__(self):
        return sum(1 for _ in self)

    def __nonzero__(self):
        try:
            next(iter(self))
        except StopIteration:
            return False
        else:
            return True
