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

from __future__ import with_statement
from contextlib import contextmanager

from robot.errors import DataError
from robot.utils import split_from_equals, unic, DotDict

from .isvar import validate_var
from .splitter import VariableSplitter


class VariableTableSetter(object):

    def __init__(self, store):
        self._store = store

    def set(self, variables, overwrite=False):
        for name, value in VariableTableReader().read(variables):
            self._store.add(name, value, overwrite)


class VariableTableReader(object):

    def read(self, variables):
        for var in variables:
            if not var:
                continue
            try:
                yield self._get_name_and_value(var.name, var.value,
                                               var.report_invalid_syntax)
            except DataError, err:
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
        self._value = self._format_value(values)
        self._error_reporter = error_reporter
        self._resolving = False

    def _format_value(self, value):
        return value

    def resolve(self, variables):
        with self._avoid_recursion:
            return self._replace_variables(self._value, variables)

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
            self._error_reporter(unicode(error))


class ScalarVariableTableValue(VariableTableValueBase):

    def _format_value(self, value):
        if isinstance(value, basestring):
            value = [value]
            separator = ' '
        elif value and value[0].startswith('SEPARATOR='):
            separator = value[0][10:]
            value = value[1:]
        else:
            separator = ' '
        return separator, value

    def _replace_variables(self, value, variables):
        separator, items = value
        separator = variables.replace_string(separator)
        items = variables.replace_list(items)
        return separator.join(unic(item) for item in items)


class ListVariableTableValue(VariableTableValueBase):

    def _replace_variables(self, value, variables):
        return variables.replace_list(value)


class DictVariableTableValue(VariableTableValueBase):

    def _format_value(self, value):
        return list(self._yield_items(value))

    def _yield_items(self, items):
        for item in items:
            if VariableSplitter(item).is_dict_variable():
                yield item
            else:
                name, value = split_from_equals(item)
                if value is None:
                    raise DataError("Dictionary item '%s' does not contain "
                                    "'=' separator." % item)
                yield name, value

    def _replace_variables(self, value, variables):
        try:
            return DotDict(self._yield_replaced(value, variables.replace_scalar))
        except TypeError, err:
            raise DataError('Creating dictionary failed: %s' % err)

    def _yield_replaced(self, value, replace_scalar):
        for item in value:
            if isinstance(item, tuple):
                key, value = item
                yield replace_scalar(key), replace_scalar(value)
            else:
                for key, value in replace_scalar(item).items():
                    yield key, value
