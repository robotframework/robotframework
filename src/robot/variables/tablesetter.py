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
from robot.utils import DotDict, split_from_equals

from .resolvable import Resolvable
from .search import is_assign, is_list_variable, is_dict_variable

if TYPE_CHECKING:
    from robot.running.model import Var, Variable
    from .store import VariableStore


class VariableTableSetter:

    def __init__(self, store: 'VariableStore'):
        self.store = store

    def set(self, variables: 'Sequence[Variable]', overwrite: bool = False):
        for var in variables:
            try:
                value = VariableResolver.from_variable(var)
                self.store.add(var.name, value, overwrite)
            except DataError as err:
                var.report_error(str(err))


class VariableResolver(Resolvable):

    def __init__(self, value: Sequence[str], error_reporter=None):
        self.value = tuple(value)
        self.error_reporter = error_reporter
        self._resolving = False

    @classmethod
    def from_name_and_value(cls, name: str, value: 'str|Sequence[str]',
                            separator: 'str|None' = None,
                            error_reporter=None) -> 'VariableResolver':
        if not is_assign(name, allow_nested=True):
            raise DataError(f"Invalid variable name '{name}'.")
        if name[0] == '$':
            return ScalarVariableResolver(value, separator, error_reporter)
        if separator is not None:
            raise DataError('Only scalar variables support separators.')
        klass = {'@': ListVariableResolver,
                 '&': DictVariableResolver}[name[0]]
        return klass(value, error_reporter)

    @classmethod
    def from_variable(cls, var: 'Var|Variable') -> 'VariableResolver':
        if var.error:
            raise DataError(var.error)
        return cls.from_name_and_value(var.name, var.value, var.separator,
                                       getattr(var, 'report_error', None))

    def resolve(self, variables):
        with self._avoid_recursion:
            return self._replace_variables(variables)

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

    def _replace_variables(self, variables):
        raise NotImplementedError

    def report_error(self, error):
        if self.error_reporter:
            self.error_reporter(error)
        else:
            raise DataError(f'Error reporter not set. Reported error was: {error}')


class ScalarVariableResolver(VariableResolver):

    def __init__(self, value: 'str|Sequence[str]', separator: 'str|None' = None,
                 error_reporter=None):
        value, separator = self._get_value_and_separator(value, separator)
        super().__init__(value, error_reporter)
        self.separator = separator

    def _get_value_and_separator(self, value, separator):
        if isinstance(value, str):
            value = [value]
        elif separator is None and value and value[0].startswith('SEPARATOR='):
            separator = value[0][10:]
            value = value[1:]
        return value, separator

    def _replace_variables(self, variables):
        value, separator = self.value, self.separator
        if self._is_single_value(value, separator):
            return variables.replace_scalar(value[0])
        if separator is None:
            separator = ' '
        else:
            separator = variables.replace_string(separator)
        value = variables.replace_list(value)
        return separator.join(str(item) for item in value)

    def _is_single_value(self, value, separator):
        return separator is None and len(value) == 1 and not is_list_variable(value[0])


class ListVariableResolver(VariableResolver):

    def _replace_variables(self, variables):
        return variables.replace_list(self.value)


class DictVariableResolver(VariableResolver):

    def __init__(self, value: Sequence[str], error_reporter=None):
        super().__init__(tuple(self._yield_formatted(value)), error_reporter)

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

    def _replace_variables(self, variables):
        try:
            return DotDict(self._yield_replaced(self.value, variables.replace_scalar))
        except TypeError as err:
            raise DataError(f'Creating dictionary variable failed: {err}')

    def _yield_replaced(self, values, replace_scalar):
        for item in values:
            if isinstance(item, tuple):
                key, values = item
                yield replace_scalar(key), replace_scalar(values)
            else:
                yield from replace_scalar(item).items()
