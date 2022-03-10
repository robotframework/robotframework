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

import re

from robot.errors import VariableError
from robot.utils import is_string


def search_variable(string, identifiers='$@&%*', ignore_errors=False):
    if not (is_string(string) and '{' in string):
        return VariableMatch(string)
    return VariableSearcher(identifiers, ignore_errors).search(string)


def contains_variable(string, identifiers='$@&'):
    match = search_variable(string, identifiers, ignore_errors=True)
    return bool(match)


def is_variable(string, identifiers='$@&'):
    match = search_variable(string, identifiers, ignore_errors=True)
    return match.is_variable()


def is_scalar_variable(string):
    return is_variable(string, '$')


def is_list_variable(string):
    return is_variable(string, '@')


def is_dict_variable(string):
    return is_variable(string, '&')


def is_assign(string, identifiers='$@&', allow_assign_mark=False):
    match = search_variable(string, identifiers, ignore_errors=True)
    return match.is_assign(allow_assign_mark)


def is_scalar_assign(string, allow_assign_mark=False):
    return is_assign(string, '$', allow_assign_mark)


def is_list_assign(string, allow_assign_mark=False):
    return is_assign(string, '@', allow_assign_mark)


def is_dict_assign(string, allow_assign_mark=False):
    return is_assign(string, '&', allow_assign_mark)


class VariableMatch:

    def __init__(self, string, identifier=None, base=None, items=(), start=-1, end=-1):
        self.string = string
        self.identifier = identifier
        self.base = base
        self.items = items
        self.start = start
        self.end = end

    def resolve_base(self, variables, ignore_errors=False):
        if self.identifier:
            internal = search_variable(self.base)
            self.base = variables.replace_string(
                internal,
                custom_unescaper=unescape_variable_syntax,
                ignore_errors=ignore_errors,
            )

    @property
    def name(self):
        return '%s{%s}' % (self.identifier, self.base) if self else None

    @property
    def before(self):
        return self.string[:self.start] if self.identifier else self.string

    @property
    def match(self):
        return self.string[self.start:self.end] if self.identifier else None

    @property
    def after(self):
        return self.string[self.end:] if self.identifier else None

    def is_variable(self):
        return bool(self.identifier
                    and self.base
                    and self.start == 0
                    and self.end == len(self.string))

    def is_scalar_variable(self):
        return self.identifier == '$' and self.is_variable()

    def is_list_variable(self):
        return self.identifier == '@' and self.is_variable()

    def is_dict_variable(self):
        return self.identifier == '&' and self.is_variable()

    def is_assign(self, allow_assign_mark=False):
        if allow_assign_mark and self.string.endswith('='):
            match = search_variable(self.string[:-1].rstrip(), ignore_errors=True)
            return match.is_assign()
        return (self.is_variable()
                and self.identifier in '$@&'
                and not self.items
                and not search_variable(self.base))

    def is_scalar_assign(self, allow_assign_mark=False):
        return self.identifier == '$' and self.is_assign(allow_assign_mark)

    def is_list_assign(self, allow_assign_mark=False):
        return self.identifier == '@' and self.is_assign(allow_assign_mark)

    def is_dict_assign(self, allow_assign_mark=False):
        return self.identifier == '&' and self.is_assign(allow_assign_mark)

    def __bool__(self):
        return self.identifier is not None

    def __str__(self):
        if not self:
            return '<no match>'
        items = ''.join('[%s]' % i for i in self.items) if self.items else ''
        return '%s{%s}%s' % (self.identifier, self.base, items)


class VariableSearcher:

    def __init__(self, identifiers, ignore_errors=False):
        self.identifiers = identifiers
        self._ignore_errors = ignore_errors
        self.start = -1
        self.variable_chars = []
        self.item_chars = []
        self.items = []
        self._open_brackets = 0    # Used both with curly and square brackets
        self._escaped = False

    def search(self, string):
        if not self._search(string):
            return VariableMatch(string)
        match = VariableMatch(string=string,
                              identifier=self.variable_chars[0],
                              base=''.join(self.variable_chars[2:-1]),
                              start=self.start,
                              end=self.start + len(self.variable_chars))
        if self.items:
            match.items = tuple(self.items)
            match.end += sum(len(i) for i in self.items) + 2 * len(self.items)
        return match

    def _search(self, string):
        start = self._find_variable_start(string)
        if start == -1:
            return False
        self.start = start
        self._open_brackets += 1
        self.variable_chars = [string[start], '{']
        start += 2
        state = self.variable_state
        for char in string[start:]:
            state = state(char)
            self._escaped = False if char != '\\' else not self._escaped
            if state is None:
                break
        if state:
            try:
                self._validate_end_state(state)
            except VariableError:
                if self._ignore_errors:
                    return False
                raise
        return True

    def _find_variable_start(self, string):
        start = 1
        while True:
            start = string.find('{', start) - 1
            if start < 0:
                return -1
            if self._start_index_is_ok(string, start):
                return start
            start += 2

    def _start_index_is_ok(self, string, index):
        return (string[index] in self.identifiers
                and not self._is_escaped(string, index))

    def _is_escaped(self, string, index):
        escaped = False
        while index > 0 and string[index-1] == '\\':
            index -= 1
            escaped = not escaped
        return escaped

    def variable_state(self, char):
        self.variable_chars.append(char)
        if char == '}' and not self._escaped:
            self._open_brackets -= 1
            if self._open_brackets == 0:
                if not self._can_have_items():
                    return None
                return self.waiting_item_state
        elif char == '{' and not self._escaped:
            self._open_brackets += 1
        return self.variable_state

    def _can_have_items(self):
        return self.variable_chars[0] in '$@&'

    def waiting_item_state(self, char):
        if char == '[':
            self._open_brackets += 1
            return self.item_state
        return None

    def item_state(self, char):
        if char == ']' and not self._escaped:
            self._open_brackets -= 1
            if self._open_brackets == 0:
                self.items.append(''.join(self.item_chars))
                self.item_chars = []
                return self.waiting_item_state
        elif char == '[' and not self._escaped:
            self._open_brackets += 1
        self.item_chars.append(char)
        return self.item_state

    def _validate_end_state(self, state):
        if state == self.variable_state:
            incomplete = ''.join(self.variable_chars)
            raise VariableError("Variable '%s' was not closed properly."
                                % incomplete)
        if state == self.item_state:
            variable = ''.join(self.variable_chars)
            items = ''.join('[%s]' % i for i in self.items)
            incomplete = ''.join(self.item_chars)
            raise VariableError("Variable item '%s%s[%s' was not closed "
                                "properly." % (variable, items, incomplete))


def unescape_variable_syntax(item):

    def handle_escapes(match):
        escapes, text = match.groups()
        if len(escapes) % 2 == 1 and starts_with_variable_or_curly(text):
            return escapes[1:]
        return escapes

    def starts_with_variable_or_curly(text):
        if text[0] in '{}':
            return True
        match = search_variable(text, ignore_errors=True)
        return match and match.start == 0

    return re.sub(r'(\\+)(?=(.+))', handle_escapes, item)


class VariableIterator:

    def __init__(self, string, identifiers='$@&%', ignore_errors=False):
        self.string = string
        self.identifiers = identifiers
        self.ignore_errors = ignore_errors

    def __iter__(self):
        remaining = self.string
        while True:
            match = search_variable(remaining, self.identifiers, self.ignore_errors)
            if not match:
                break
            remaining = match.after
            yield match.before, match.match, remaining

    def __len__(self):
        return sum(1 for _ in self)

    def __bool__(self):
        try:
            next(iter(self))
        except StopIteration:
            return False
        else:
            return True
