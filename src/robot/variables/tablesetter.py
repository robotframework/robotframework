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
from typing import Sequence, TYPE_CHECKING

from robot.errors import DataError
from robot.utils import DotDict, is_string, split_from_equals

from .resolvable import Resolvable
from .search import is_assign, is_list_variable, is_dict_variable

if TYPE_CHECKING:
    from robot.running.model import Variable


class VariableTableSetter:

    def __init__(self, store):
        self._store = store

    def set(self, variables: 'Sequence[Variable]', overwrite: bool = False):
        for name, value in self._get_items(variables):
            self._store.add(name, value, overwrite, decorated=False)

    def _get_items(self, variables: 'Sequence[Variable]'):
        for var in variables:
            try:
                value = VariableResolver.from_variable(var)
            except DataError as err:
                var.report_error(str(err))
            else:
                yield var.name[2:-1], value


class VariableResolver(Resolvable):

    def __init__(self, value: 'str|Sequence[str]', error_reporter=None):
        self.value = self._format_value(value)
        self.error_reporter = error_reporter
        self._resolving = False

    def _format_value(self, value):
        return value

    @classmethod
    def from_name_and_value(cls, name: str, value: 'str|Sequence[str]',
                            error_reporter=None) -> 'VariableResolver':
        if not is_assign(name):
            raise DataError(f"Invalid variable name '{name}'.")
        klass = {'$': ScalarVariableResolver,
                 '@': ListVariableResolver,
                 '&': DictVariableResolver}[name[0]]
        return klass(value, error_reporter)

    @classmethod
    def from_variable(cls, var: 'Variable') -> 'VariableResolver':
        if var.error:
            raise DataError(var.error)
        return cls.from_name_and_value(var.name, var.value, var.report_error)

    def resolve(self, variables):
        with self._avoid_recursion:
            return self._replace_variables(self.value, variables)

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
        if self.error_reporter:
            self.error_reporter(error)
        else:
            raise DataError(f'Error reported not set. Reported error was: {error}')


class ScalarVariableResolver(VariableResolver):

    def _format_value(self, values):
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


class ListVariableResolver(VariableResolver):

    def _replace_variables(self, values, variables):
        return variables.replace_list(values)


class DictVariableResolver(VariableResolver):

    def _format_value(self, values):
        return list(self._yield_formatted(values))

    def _yield_formatted(self, values):
        for item in values:
            if is_dict_variable(item):
                yield item
            else:
                name, value = split_from_equals(item)
                if value is None:
                    raise DataError(
                        f"Invalid dictionary variable item '{item}'. Items must use "
                        f"'name=value' syntax or be dictionary variables themselves."
                    )
                yield name, value

    def _replace_variables(self, values, variables):
        try:
            return DotDict(self._yield_replaced(values, variables.replace_scalar))
        except TypeError as err:
            raise DataError(f'Creating dictionary failed: {err}')

    def _yield_replaced(self, values, replace_scalar):
        for item in values:
            if isinstance(item, tuple):
                key, values = item
                yield replace_scalar(key), replace_scalar(values)
            else:
                for key, values in replace_scalar(item).items():
                    yield key, values
