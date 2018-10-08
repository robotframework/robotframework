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
from robot.output import LOGGER
from robot.utils import (escape, is_dict_like, is_list_like, is_string,
                         type_name, unescape, unic)

from .splitter import VariableSplitter


class VariableReplacer(object):

    def __init__(self, variables):
        self._variables = variables

    def replace_list(self, items, replace_until=None, ignore_errors=False):
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
            return self._replace_list_until(items, replace_until, ignore_errors)
        return list(self._replace_list(items, ignore_errors))

    def _replace_list_until(self, items, replace_until, ignore_errors):
        # @{list} variables can contain more or less arguments than needed.
        # Therefore we need to go through items one by one, and escape possible
        # extra items we got.
        replaced = []
        while len(replaced) < replace_until and items:
            replaced.extend(self._replace_list([items.pop(0)], ignore_errors))
        if len(replaced) > replace_until:
            replaced[replace_until:] = [escape(item)
                                        for item in replaced[replace_until:]]
        return replaced + items

    def _replace_list(self, items, ignore_errors):
        for item in items:
            if self._cannot_have_variables(item):
                yield unescape(item)
            else:
                for value in self._replace_list_item(item, ignore_errors):
                    yield value

    def _replace_list_item(self, item, ignore_errors):
        splitter = VariableSplitter(item)
        try:
            value = self._replace_scalar(item, splitter)
        except DataError:
            if ignore_errors:
                return [item]
            raise
        if splitter.is_list_variable():
            return value
        return [value]

    def replace_scalar(self, item, ignore_errors=False):
        """Replaces variables from a scalar item.

        If the item is not a string it is returned as is. If it is a ${scalar}
        variable its value is returned. Otherwise variables are replaced with
        'replace_string'. Result may be any object.
        """
        if self._cannot_have_variables(item):
            return unescape(item)
        return self._replace_scalar(item, ignore_errors=ignore_errors)

    def _replace_scalar(self, item, splitter=None, ignore_errors=False):
        if not splitter:
            splitter = VariableSplitter(item)
        if not splitter.identifier:
            return unescape(item)
        if not splitter.is_variable():
            return self._replace_string(item, splitter, ignore_errors)
        try:
            return self._get_variable(splitter)
        except DataError:
            if ignore_errors:
                return item
            raise

    def _cannot_have_variables(self, item):
        return not (is_string(item) and '{' in item)

    def replace_string(self, string, ignore_errors=False):
        """Replaces variables from a string. Result is always a string."""
        if not is_string(string):
            return unic(string)
        if self._cannot_have_variables(string):
            return unescape(string)
        return self._replace_string(string, ignore_errors=ignore_errors)

    def _replace_string(self, string, splitter=None, ignore_errors=False):
        if not splitter:
            splitter = VariableSplitter(string)
        return ''.join(self._yield_replaced(string, splitter, ignore_errors))

    def _yield_replaced(self, string, splitter, ignore_errors=False):
        while splitter.identifier:
            yield unescape(string[:splitter.start])
            try:
                value = self._get_variable(splitter)
            except DataError:
                if not ignore_errors:
                    raise
                value = string[splitter.start:splitter.end]
            yield unic(value)
            string = string[splitter.end:]
            splitter = VariableSplitter(string)
        yield unescape(string)

    def _get_variable(self, splitter):
        if splitter.identifier not in '$@&%':
            return self._get_reserved_variable(splitter)
        name = splitter.get_replaced_variable(self)
        variable = self._variables[name]
        for item in splitter.items:
            variable = self._get_variable_item(name, variable, item)
            name = '%s[%s]' % (name, item)
        return variable

    def _get_variable_item(self, name, variable, item):
        if is_dict_like(variable):
            return self._get_dict_variable_item(name, variable, item)
        if is_list_like(variable):
            return self._get_list_variable_item(name, variable, item)
        raise VariableError("Variable '%s' is %s, not list or dictionary, "
                            "and thus accessing item '%s' from it is not "
                            "possible."
                            % (name, type_name(variable), item))

    def _get_reserved_variable(self, splitter):
        value = splitter.get_replaced_variable(self)
        LOGGER.warn("Syntax '%s' is reserved for future use. Please "
                    "escape it like '\\%s'." % (value, value))
        return value

    def _get_list_variable_item(self, name, variable, index):
        index = self.replace_string(index)
        try:
            index = self._parse_list_variable_index(index, name[0] == '$')
        except ValueError:
            raise VariableError("List '%s' used with invalid index '%s'."
                                % (name, index))
        try:
            return variable[index]
        except IndexError:
            raise VariableError("List '%s' has no item in index %d."
                                % (name, index))

    def _parse_list_variable_index(self, index, support_slice=True):
        if ':' not in index:
            return int(index)
        if index.count(':') > 2 or not support_slice:
            raise ValueError
        return slice(*[int(i) if i else None for i in index.split(':')])

    def _get_dict_variable_item(self, name, variable, key):
        key = self.replace_scalar(key)
        try:
            return variable[key]
        except KeyError:
            raise VariableError("Dictionary '%s' has no key '%s'."
                                % (name, key))
        except TypeError as err:
            raise VariableError("Dictionary '%s' used with invalid key: %s"
                                % (name, err))
