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

from robot import utils
from robot.errors import DataError
from robot.output import LOGGER

from .filesetter import VariableFileSetter
from .finders import (EnvironmentFinder, ExtendedFinder, ListAsScalarFinder,
                      NumberFinder, ScalarAsListFinder)
from .notfound import raise_not_found
from .store import VariableStore
from .tablesetter import VariableTableSetter
from .variablesplitter import VariableSplitter


class Variables(object):
    """Represents a set of variables including both ${scalars} and @{lists}.

    Contains methods for replacing variables from list, scalars, and strings.
    On top of ${scalar} and @{list} variables these methods handle also
    %{environment} variables.
    """

    def __init__(self, identifiers=('$', '@', '%', '&', '*')):
        self._identifiers = identifiers
        self.store = VariableStore(self)

    def __setitem__(self, name, value):
        self.store.add(name, value)

    def update(self, variables):
        # TODO: Fugly!
        self.store.store.update(variables.store.store)

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
        """Replaces variables from a list of items.

        If an item in a list is a @{list} variable its value is returned.
        Possible variables from other items are replaced using 'replace_scalar'.
        Result is always a list.

        'replace_until' can be used to limit replacing arguments to certain
        index from the beginning. Used with Run Keyword variants that only
        want to resolve some of the arguments in the beginning and pass others
        to called keywords unmodified.
        """
        items = list(items or [])
        if replace_until is not None:
            return self._replace_list_until(items, replace_until)
        return self._replace_list(items)

    def _replace_list_until(self, items, replace_until):
        # @{list} variables can contain more or less arguments than needed.
        # Therefore we need to go through items one by one, and escape possible
        # extra items we got.
        replaced = []
        while len(replaced) < replace_until and items:
            replaced.extend(self._replace_list([items.pop(0)]))
        if len(replaced) > replace_until:
            replaced[replace_until:] = [utils.escape(item)
                                        for item in replaced[replace_until:]]
        return replaced + items

    def _replace_list(self, items):
        results = []
        for item in items:
            listvar = self._replace_variables_inside_possible_list_var(item)
            if listvar:
                results.extend(self[listvar])
            else:
                results.append(self.replace_scalar(item))
        return results

    def _replace_variables_inside_possible_list_var(self, item):
        if not (isinstance(item, basestring) and
                item.startswith('@{') and item.endswith('}')):
            return None
        var = VariableSplitter(item, self._identifiers)
        if not var.is_one_variable():
            return None
        return '@{%s}' % var.get_replaced_base(self)

    def replace_scalar(self, item):
        """Replaces variables from a scalar item.

        If the item is not a string it is returned as is. If it is a ${scalar}
        variable its value is returned. Otherwise variables are replaced with
        'replace_string'. Result may be any object.
        """
        if self._cannot_have_variables(item):
            return utils.unescape(item)
        var = VariableSplitter(item, self._identifiers)
        if not var.identifier:
            return utils.unescape(item)
        if var.is_one_variable():
            return self._get_variable(var)
        return self.replace_string(item, var)

    def _cannot_have_variables(self, item):
        return not (isinstance(item, basestring) and '{' in item)

    def replace_string(self, string, splitter=None, ignore_errors=False):
        """Replaces variables from a string. Result is always a string."""
        if self._cannot_have_variables(string):
            return utils.unescape(string)
        result = []
        if splitter is None:
            splitter = VariableSplitter(string, self._identifiers)
        while True:
            if splitter.identifier is None:
                result.append(utils.unescape(string))
                break
            result.append(utils.unescape(string[:splitter.start]))
            try:
                value = self._get_variable(splitter)
            except DataError:
                if not ignore_errors:
                    raise
                value = string[splitter.start:splitter.end]
            if not isinstance(value, unicode):
                value = utils.unic(value)
            result.append(value)
            string = string[splitter.end:]
            splitter = VariableSplitter(string, self._identifiers)
        return ''.join(result)

    def _get_variable(self, var):
        """'var' is an instance of a VariableSplitter"""
        # 1) Handle reserved syntax
        if var.identifier not in '$@%':
            value = '%s{%s}' % (var.identifier, var.base)
            LOGGER.warn("Syntax '%s' is reserved for future use. Please "
                        "escape it like '\\%s'." % (value, value))
            return value

        # 3) Handle ${scalar} variables and @{list} variables without index
        elif var.index is None:
            name = '%s{%s}' % (var.identifier, var.get_replaced_base(self))
            return self[name]

        # 4) Handle items from list variables e.g. @{var}[1]
        else:
            try:
                index = int(self.replace_string(var.index))
                name = '@{%s}' % var.get_replaced_base(self)
                return self[name][index]
            except (ValueError, DataError, IndexError):
                raise_not_found(var.base, self.store,
                                "Variable '@{%s}[%s]' not found."
                                % (var.base, var.index))


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
        variables = Variables(self._identifiers)
        variables.store.store = self.store.store.copy()
        return variables

    def __iter__(self):
        return iter(self.store)

    def __len__(self):
        return len(self.store)
