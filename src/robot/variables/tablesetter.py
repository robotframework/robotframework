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

from contextlib import contextmanager

from robot.errors import DataError
from robot.utils import DotDict, is_string, split_from_equals, unic

from .isvar import validate_var
from .splitter import VariableSplitter


class VariableTableSetter(object):

    def __init__(self, store):
        self._store = store

    def set(self, variables, overwrite=False):
        for name, value in VariableTableReader().read(variables):
            self._store.add(name, value, overwrite, decorated=False)


class VariableTableReader(object):

    def read(self, variables):
        for var in variables:
            if not var:
                continue
            try:
                yield self._get_name_and_value(var.name, var.value,
                                               var.report_invalid_syntax)
            except DataError as err:
                var.report_invalid_syntax(err)

    def _get_name_and_value(self, name, value, error_reporter):
        return name[2:-1], VariableTableValue(value, name, error_reporter)


def VariableTableValue(value, name, error_reporter=None):
    validate_var(name)
    VariableTableValue = {'$': ScalarVariableTableValue,
                          '@': ListVariableTableValue,
                          '&': DictVariableTableValue}[name[0]]
    return VariableTableValue(value, error_reporter)


class VariableTableValueBase(object):

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
            self._error_reporter(unic(error))


class ScalarVariableTableValue(VariableTableValueBase):

    def _format_values(self, values):
        separator = None
        if is_string(values):
            values = [values]
        elif values and values[0].startswith('SEPARATOR='):
            separator = values.pop(0)[10:]
        return separator, values

    def _replace_variables(self, values, variables):
        separator, values = values
        if (separator is None and len(values) == 1 and
                not VariableSplitter(values[0]).is_list_variable()):
            return variables.replace_scalar(values[0])
        if separator is None:
            separator = ' '
        separator = variables.replace_string(separator)
        values = variables.replace_list(values)
        return separator.join(unic(item) for item in values)


class ListVariableTableValue(VariableTableValueBase):

    def _replace_variables(self, values, variables):
        return variables.replace_list(values)


class DictVariableTableValue(VariableTableValueBase):

    def _format_values(self, values):
        return list(self._yield_formatted(values))

    def _yield_formatted(self, values):
        for item in values:
            if VariableSplitter(item).is_dict_variable():
                yield item
            else:
                name, value = split_from_equals(item)
                if value is None:
                    raise DataError("Dictionary item '%s' does not contain "
                                    "'=' separator." % item)
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
