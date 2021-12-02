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

from contextlib import contextmanager

from robot.errors import DataError
from robot.utils import DotDict, is_string, split_from_equals

from .search import is_assign, is_list_variable, is_dict_variable


class VariableTableSetter:

    def __init__(self, store):
        self._store = store

    def set(self, variables, overwrite=False):
        for name, value in self._get_items(variables):
            self._store.add(name, value, overwrite, decorated=False)

    def _get_items(self, variables):
        for var in variables:
            if var.error:
                var.report_invalid_syntax(var.error)
                continue
            try:
                value = VariableTableValue(var.value, var.name,
                                           var.report_invalid_syntax)
            except DataError as err:
                var.report_invalid_syntax(err)
            else:
                yield var.name[2:-1], value


def VariableTableValue(value, name, error_reporter=None):
    if not is_assign(name):
        raise DataError("Invalid variable name '%s'." % name)
    VariableTableValue = {'$': ScalarVariableTableValue,
                          '@': ListVariableTableValue,
                          '&': DictVariableTableValue}[name[0]]
    return VariableTableValue(value, error_reporter)


class VariableTableValueBase:

    def __init__(self, values, error_reporter=None):
        self._values = self._format_values(values)
        self._error_reporter = error_reporter
        self._resolving = False

    def _format_values(self, values):
        return values

    def resolve(self, variables):
        with self._avoid_recursion:
            return self._replace_variables(self._values, variables)

    @property
    @contextmanager
    def _avoid_recursion(self):
        if self._resolving:
            raise DataError('Recursive variable definition.')
        self._resolving = True
        try:
            yield
        finally:
            self._resolving = False

    def _replace_variables(self, value, variables):
        raise NotImplementedError

    def report_error(self, error):
        if self._error_reporter:
            self._error_reporter(str(error))


class ScalarVariableTableValue(VariableTableValueBase):

    def _format_values(self, values):
        separator = None
        if is_string(values):
            values = [values]
        elif values and values[0].startswith('SEPARATOR='):
            separator = values[0][10:]
            values = values[1:]
        return separator, values

    def _replace_variables(self, values, variables):
        separator, values = values
        # Avoid converting single value to string.
        if self._is_single_value(separator, values):
            return variables.replace_scalar(values[0])
        if separator is None:
            separator = ' '
        separator = variables.replace_string(separator)
        values = variables.replace_list(values)
        return separator.join(str(item) for item in values)

    def _is_single_value(self, separator, values):
        return (separator is None and len(values) == 1 and
                not is_list_variable(values[0]))


class ListVariableTableValue(VariableTableValueBase):

    def _replace_variables(self, values, variables):
        return variables.replace_list(values)


class DictVariableTableValue(VariableTableValueBase):

    def _format_values(self, values):
        return list(self._yield_formatted(values))

    def _yield_formatted(self, values):
        for item in values:
            if is_dict_variable(item):
                yield item
            else:
                name, value = split_from_equals(item)
                if value is None:
                    raise DataError(
                        "Invalid dictionary variable item '%s'. "
                        "Items must use 'name=value' syntax or be dictionary "
                        "variables themselves." % item
                    )
                yield name, value

    def _replace_variables(self, values, variables):
        try:
            return DotDict(self._yield_replaced(values,
                                                variables.replace_scalar))
        except TypeError as err:
            raise DataError('Creating dictionary failed: %s' % err)

    def _yield_replaced(self, values, replace_scalar):
        for item in values:
            if isinstance(item, tuple):
                key, values = item
                yield replace_scalar(key), replace_scalar(values)
            else:
                for key, values in replace_scalar(item).items():
                    yield key, values
