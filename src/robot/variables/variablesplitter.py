#  Copyright 2008-2011 Nokia Siemens Networks Oyj
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


class VariableSplitter:

    def __init__(self, string, identifiers):
        self.identifier = None
        self.base = None
        self.index = None
        self.start = -1
        self.end = -1
        self._identifiers = identifiers
        self._may_have_internal_variables = False
        if self._split(string):
            self._finalize()

    def get_replaced_base(self, variables):
        if self._may_have_internal_variables:
            return variables.replace_string(self.base)
        return self.base

    def _finalize(self):
        self.identifier = self._variable_chars[0]
        self.base = ''.join(self._variable_chars[2:-1])
        self.end = self.start + len(self._variable_chars)
        if self._index_chars and self._index_chars[-1] == ']':
            self.index = ''.join(self._index_chars[1:-1])
            self.end += len(self._index_chars)

    def _split(self, string):
        start_index, max_index = self._find_variable(string)
        if start_index < 0:
            return False
        self.start = start_index
        self._started_vars = 1
        self._state_handler = self._variable_state_handler
        self._variable_chars = [ string[start_index], '{' ]
        self._index_chars = []
        start_index += 2
        for index, char in enumerate(string[start_index:]):
            try:
                self._state_handler(char)
            except StopIteration:
                break
            if self._state_handler not in [ self._waiting_index_state_handler,
                  self._index_state_handler ] and start_index+index > max_index:
                break
        return True

    def _find_variable(self, string):
        max_index = string.rfind('}')
        if max_index == -1:
            return -1, -1
        start_index = self._find_start_index(string, 1, max_index)
        if start_index == -1:
            return -1, -2
        return start_index, max_index

    def _find_start_index(self, string, start, end):
        index = string.find('{', start, end) - 1
        if index < 0:
            return -1
        elif self._start_index_is_ok(string, index):
            return index
        else:
            return self._find_start_index(string, index+2, end)

    def _start_index_is_ok(self, string, index):
        if string[index] not in self._identifiers:
            return False
        backslash_count = 0
        while index - backslash_count > 0:
            if string[index - backslash_count - 1] == '\\':
                backslash_count += 1
            else:
                break
        return backslash_count % 2 == 0

    def _variable_state_handler(self, char):
        self._variable_chars.append(char)
        if char == '}':
            self._started_vars -= 1
            if self._started_vars == 0:
                if self._variable_chars[0] == '@':
                    self._state_handler = self._waiting_index_state_handler
                else:
                    raise StopIteration
        elif char in self._identifiers:
            self._state_handler = self._internal_variable_start_state_handler

    def _internal_variable_start_state_handler(self, char):
        self._state_handler = self._variable_state_handler
        if char == '{':
            self._variable_chars.append(char)
            self._started_vars += 1
            self._may_have_internal_variables = True
        else:
            self._variable_state_handler(char)

    def _waiting_index_state_handler(self, char):
        if char == '[':
            self._index_chars.append(char)
            self._state_handler = self._index_state_handler
        else:
            raise StopIteration

    def _index_state_handler(self, char):
        self._index_chars.append(char)
        if char == ']':
            raise StopIteration
