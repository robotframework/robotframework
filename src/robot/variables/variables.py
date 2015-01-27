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

from __future__ import with_statement
try:
    from java.lang.System import getProperty as getJavaSystemProperty
except ImportError:
    getJavaSystemProperty = lambda name: None

from robot import utils
from robot.errors import DataError
from robot.output import LOGGER

from .filesetter import VariableFileSetter
from .finder import VariableFinder
from .isvar import validate_var
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
        self.store = VariableStore()

    def __setitem__(self, name, value):
        validate_var(name)
        self.store[name] = value

    def update(self, dict=None, **kwargs):
        for name in list(dict or []) + list(kwargs):
            validate_var(name)
        self.store.update(dict, **kwargs)

    def __getitem__(self, name):
        return VariableFinder(self).find(name)

    def resolve_delayed(self):
        # cannot iterate over `self.store` here because loop changes its state.
        # TODO: This belongs to store
        for var in self.store.keys():
            try:
                self[var]  # getting variable resolves it if needed
            except DataError:
                pass

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
        # Therefore we need to go through arguments one by one.
        processed = []
        while len(processed) < replace_until and items:
            processed.extend(self._replace_list([items.pop(0)]))
        # If @{list} variable is opened, arguments going further must be
        # escaped to prevent them being un-escaped twice.
        if len(processed) > replace_until:
            processed[replace_until:] = [self._escape(item)
                                         for item in processed[replace_until:]]
        return processed + items

    def _escape(self, item):
        item = utils.escape(item)
        # Escape also special syntax used by Run Kw If and Run Kws.
        # TODO: Move to utils.escape. Can be configurable if needed.
        if item in ('ELSE', 'ELSE IF', 'AND'):
            item = '\\' + item
        return item

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
        if var.start != 0 or var.end != len(item):
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
        if var.identifier and var.base and var.start == 0 and var.end == len(item):
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
        result = ''.join(result)
        return result

    def _get_variable(self, var):
        """'var' is an instance of a VariableSplitter"""
        # 1) Handle reserved syntax
        if var.identifier not in '$@%':
            value = '%s{%s}' % (var.identifier, var.base)
            LOGGER.warn("Syntax '%s' is reserved for future use. Please "
                        "escape it like '\\%s'." % (value, value))
            return value

        # 2) Handle environment variables and Java system properties
        elif var.identifier == '%':
            name = var.get_replaced_base(self).strip()
            if not name:
                return '%%{%s}' % var.base
            value = utils.get_env_var(name)
            if value is not None:
                return value
            value = getJavaSystemProperty(name)
            if value is not None:
                return value
            raise_not_found('%%{%s}' % name, self.store.keys(),
                            "Environment variable '%%{%s}' not found." % name,
                            env_vars=True)

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
                raise_not_found(var.base, self.store.keys(),
                                "Variable '@{%s}[%s]' not found."
                                % (var.base, var.index))


    def set_from_file(self, path_or_variables, args=None, overwrite=False):
        setter = VariableFileSetter(self.store)
        return setter.set(path_or_variables, args, overwrite)

    def set_from_variable_table(self, variables, overwrite=False):
        setter = VariableTableSetter(self.store)
        setter.set(variables, overwrite)

    def has_key(self, variable):
        try:
            self[variable]
        except DataError:
            return False
        else:
            return True

    __contains__ = has_key

    def contains(self, variable, extended=False):
        if extended:
            return variable in self
        return variable in self.store

    def clear(self):
        self.store.clear()

    def keys(self):
        return self.store.keys()

    def items(self):
        return self.store.items()

    def copy(self):
        variables = Variables(self._identifiers)
        variables.store = self.store.copy()
        return variables

    def __iter__(self):
        return iter(self.store)

    def __len__(self):
        return len(self.store)

    def pop(self, key=None, *default):
        return self.store.pop(key, *default)
