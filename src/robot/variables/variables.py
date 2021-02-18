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

from robot.utils import is_list_like, type_name

from .filesetter import VariableFileSetter
from .replacer import VariableReplacer
from .store import VariableStore
from .tablesetter import VariableTableSetter


class Variables(object):
    """Represents a set of variables.

    Contains methods for replacing variables from list, scalars, and strings.
    On top of ${scalar}, @{list} and &{dict} variables, these methods handle
    also %{environment} variables.
    """

    def __init__(self):
        self.store = VariableStore(self)
        self._replacer = VariableReplacer(self.store)

    def __setitem__(self, name, value):
        self.store.add(name, value)

    def __getitem__(self, name):
        return self.store.get(name)

    def __contains__(self, name):
        return name in self.store

    def resolve_delayed(self):
        self.store.resolve_delayed()

    def replace_list(self, items, replace_until=None, ignore_errors=False):
        if not is_list_like(items):
            raise ValueError("'replace_list' requires list-like input, "
                             "got %s." % type_name(items))
        return self._replacer.replace_list(items, replace_until, ignore_errors)

    def replace_scalar(self, item, ignore_errors=False):
        return self._replacer.replace_scalar(item, ignore_errors)

    def replace_string(self, item, custom_unescaper=None, ignore_errors=False):
        return self._replacer.replace_string(item, custom_unescaper, ignore_errors)

    def set_from_file(self, path_or_variables, args=None, overwrite=False):
        setter = VariableFileSetter(self.store)
        return setter.set(path_or_variables, args, overwrite)

    def set_from_variable_table(self, variables, overwrite=False):
        setter = VariableTableSetter(self.store)
        setter.set(variables, overwrite)

    def clear(self):
        self.store.clear()

    def copy(self):
        variables = Variables()
        variables.store.data = self.store.data.copy()
        return variables

    def update(self, variables):
        self.store.update(variables.store)

    def as_dict(self, decoration=True):
        return self.store.as_dict(decoration=decoration)
