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

from robot.errors import DataError
from robot.utils import is_dict_like, is_list_like, DotDict, NormalizedDict

from .isvar import validate_var
from .notfound import raise_not_found
from .tablesetter import VariableTableValueBase


class VariableStore(object):

    def __init__(self, variables):
        self.data = NormalizedDict(ignore='_')
        self._variables = variables

    def resolve_delayed(self):
        for name, value in self.data.items():
            try:
                self._resolve_delayed(name, value)
            except DataError:
                pass

    def _resolve_delayed(self, name, value):
        if not isinstance(value, VariableTableValueBase):
            return value
        try:
            self.data[name] = value.resolve(self._variables)
        except DataError as err:
            # Recursive resolving may have already removed variable.
            if name in self:
                self.remove(name)
                value.report_error(err)
            raise_not_found('${%s}' % name, self.data,
                            "Variable '${%s}' not found." % name)
        return self.data[name]

    def find(self, name):
        return self._resolve_delayed(name, self.data[name])

    def __getitem__(self, name):
        return self.find(name)    # TODO: __getitem__ vs find

    def clear(self):
        self.data.clear()

    def add(self, name, value, overwrite=True, decorated=True):
        if decorated:
            name, value = self._undecorate(name, value)
        if overwrite or name not in self.data:
            self.data[name] = value

    def _undecorate(self, name, value):
        validate_var(name)
        if name[0] == '@':
            if not is_list_like(value):
                self._raise_cannot_set_type(name, value, 'list')
            value = list(value)
        if name[0] == '&':
            if not is_dict_like(value):
                self._raise_cannot_set_type(name, value, 'dictionary')
            value = DotDict(value)
        return name[2:-1], value

    def _raise_cannot_set_type(self, name, value, expected):
        raise DataError("Cannot set variable '%s': Expected %s-like value, got "
                        "%s instead." % (name, expected, type(value).__name__))

    def remove(self, name):
        if name in self.data:
            self.data.pop(name)

    def __len__(self):
        return len(self.data)

    def __iter__(self):
        return iter(self.data)

    def __contains__(self, name):
        return name in self.data
