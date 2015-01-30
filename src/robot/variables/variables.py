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

from robot.errors import DataError

from .filesetter import VariableFileSetter
from .finders import (EnvironmentFinder, ExtendedFinder, ListAsScalarFinder,
                      NumberFinder, ScalarAsListFinder)
from .notfound import raise_not_found
from .replacer import VariableReplacer
from .store import VariableStore
from .tablesetter import VariableTableSetter


class Variables(object):
    """Represents a set of variables including both ${scalars} and @{lists}.

    Contains methods for replacing variables from list, scalars, and strings.
    On top of ${scalar} and @{list} variables these methods handle also
    %{environment} variables.
    """

    def __init__(self):
        self.store = VariableStore(self)
        self.replacer = VariableReplacer(self)

    def __setitem__(self, name, value):
        self.store.add(name, value)

    def __getitem__(self, name):
        extended = ExtendedFinder(self)
        for finder in (EnvironmentFinder(self.store),
                       self.store,
                       NumberFinder(),
                       ListAsScalarFinder(self.store.find, extended.find),
                       ScalarAsListFinder(self.store.find, extended.find),
                       extended):
            try:
                return finder.find(name)
            except (KeyError, ValueError):
                pass
        raise_not_found(name, self.store)

    def resolve_delayed(self):
        self.store.resolve_delayed()

    def replace_list(self, items, replace_until=None):
        return self.replacer.replace_list(items, replace_until)

    def replace_scalar(self, item):
        return self.replacer.replace_scalar(item)

    def replace_string(self, item, ignore_errors=False):
        return self.replacer.replace_string(item, ignore_errors)

    def set_from_file(self, path_or_variables, args=None, overwrite=False):
        setter = VariableFileSetter(self.store)
        return setter.set(path_or_variables, args, overwrite)

    def set_from_variable_table(self, variables, overwrite=False):
        setter = VariableTableSetter(self.store)
        setter.set(variables, overwrite)

    def __contains__(self, name):
        try:
            self[name]
        except DataError:
            return False
        else:
            return True

    def clear(self):
        self.store.clear()

    def copy(self):
        # TODO: This is fugly!
        variables = Variables()
        variables.store.store = self.store.store.copy()
        return variables

    def update(self, variables):
        # TODO: Fugly!
        self.store.store.update(variables.store.store)

    def __iter__(self):
        return iter(self.store)

    def __len__(self):
        return len(self.store)
