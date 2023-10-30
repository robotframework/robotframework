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

from robot.errors import DataError, VariableError
from robot.utils import (DotDict, is_dict_like, is_list_like, NormalizedDict, NOT_SET,
                         type_name)

from .notfound import variable_not_found
from .resolvable import GlobalVariableValue, Resolvable
from .search import is_assign, unescape_variable_syntax


class VariableStore:

    def __init__(self, variables):
        self.data = NormalizedDict(ignore='_')
        self._variables = variables

    def resolve_delayed(self, item=None):
        if item:
            return self._resolve_delayed(*item)
        for name, value in list(self.data.items()):
            try:
                self._resolve_delayed(name, value)
            except DataError:
                pass

    def _resolve_delayed(self, name, value):
        if not self._is_resolvable(value):
            return value
        try:
            self.data[name] = value.resolve(self._variables)
        except DataError as err:
            # Recursive resolving may have already removed variable.
            if name in self.data:
                self.data.pop(name)
                value.report_error(str(err))
            variable_not_found('${%s}' % name, self.data)
        return self.data[name]

    def _is_resolvable(self, value):
        try:
            return isinstance(value, Resolvable)
        except Exception:
            return False

    def __getitem__(self, name):
        if name not in self.data:
            variable_not_found('${%s}' % name, self.data)
        return self._resolve_delayed(name, self.data[name])

    def get(self, name, default=NOT_SET, decorated=True):
        try:
            if decorated:
                name = self._undecorate(name)
            return self[name]
        except DataError:
            if default is NOT_SET:
                raise
            return default

    def update(self, store):
        self.data.update(store.data)

    def clear(self):
        self.data.clear()

    def add(self, name, value, overwrite=True, decorated=True):
        if decorated:
            name, value = self._undecorate_and_validate(name, value)
        if (overwrite
                or name not in self.data
                or isinstance(self.data[name], GlobalVariableValue)):
            self.data[name] = value

    def _undecorate(self, name):
        if not is_assign(name, allow_nested=True):
            raise DataError(f"Invalid variable name '{name}'.")
        return self._variables.replace_string(
            name[2:-1], custom_unescaper=unescape_variable_syntax
        )

    def _undecorate_and_validate(self, name, value):
        undecorated = self._undecorate(name)
        if isinstance(value, Resolvable):
            return undecorated, value
        if name[0] == '@':
            if not is_list_like(value):
                raise DataError(f'Expected list-like value, got {type_name(value)}.')
            value = list(value)
        if name[0] == '&':
            if not is_dict_like(value):
                raise DataError(f'Expected dictionary-like value, got {type_name(value)}.')
            value = DotDict(value)
        return undecorated, value

    def __len__(self):
        return len(self.data)

    def __iter__(self):
        return iter(self.data)

    def __contains__(self, name):
        return name in self.data

    def as_dict(self, decoration=True):
        if decoration:
            variables = (self._decorate(name, self[name]) for name in self)
        else:
            variables = self.data
        return NormalizedDict(variables,  ignore='_')

    def _decorate(self, name, value):
        if is_dict_like(value):
            name = '&{%s}' % name
        elif is_list_like(value):
            name = '@{%s}' % name
        else:
            name = '${%s}' % name
        return name, value
