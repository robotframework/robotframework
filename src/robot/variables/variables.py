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
from robot.utils import is_dict_like, is_list_like

from .filesetter import VariableFileSetter
from .finders import (EnvironmentFinder, EmptyFinder, ExtendedFinder,
                      NumberFinder, StoredFinder)
from .isvar import validate_var
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
        validate_var(name)
        if name[0] == '@' and not is_list_like(value):
            raise DataError('TODO')
        # TODO: Validate '&' variables. Tests.
        self.store.add(name[2:-1], value)

    def __getitem__(self, name):
        # TODO: Move to finder module
        validate_var(name, '$@&%')
        for finder in (StoredFinder(self.store),
                       NumberFinder(),
                       EmptyFinder(),
                       EnvironmentFinder(),
                       ExtendedFinder(self)):
            try:
                value = finder.find(name)
            except (KeyError, ValueError):
                continue
            if name[0] == '@':
                # TODO: Should we also allow dicts here?
                if not is_list_like(value):
                    raise DataError("Value of variable '%s' is not list or "
                                    "list-like." % name)
                return list(value)
            if name[0] == '&':
                if not is_dict_like(value):
                    raise DataError("Value of variable '%s' is not dictionary "
                                    "or dictionary-like." % name)
                return dict(value)
            return value
        raise_not_found(name, self.store.store)

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

    # TODO: Try to get rid of all/most of the methods below.
    # __iter__ and __len__ may be useful.

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
        # TODO: Returns names w/o decoration -- cannot be used w/ __getitem__
        return iter(self.store)

    def __len__(self):
        return len(self.store)
