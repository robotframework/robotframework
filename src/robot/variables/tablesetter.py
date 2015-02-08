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
from robot.utils import split_from_equals, DotDict

from .isvar import validate_var
from .notfound import raise_not_found
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
        return name[2:-1], VariableTableValue(name, value, error_reporter)


def VariableTableValue(name, value, error_reporter=None):
    VariableTableValue = {'$': ScalarVariableTableValue,
                          '@': ListVariableTableValue,
                          '&': DictVariableTableValue}[name[0]]
    return VariableTableValue(name, value, error_reporter)


class VariableTableValueBase(object):

    def __init__(self, name, value, error_reporter=None):
        self._name = name
        self._value = self._format_value(value, name)
        self._error_reporter = error_reporter
        self._resolving = False

    def _format_value(self, value, name):
        return value

    def resolve(self, variables, name=None):
        if not name:
            name = self._name
        try:
            with self._avoid_recursion:
                return self._replace_variables(self._value, variables)
        except DataError, err:
            # Recursive resolving may have already removed variable.
            if name in variables.store:
                variables.store.remove(name)
                if self._error_reporter:
                    self._error_reporter(unicode(err))
            raise_not_found('${%s}' % name, variables.store.data,
                            "Variable '${%s}' not found." % name)

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


class ScalarVariableTableValue(VariableTableValueBase):

    def _format_value(self, value, name):
        if isinstance(value, basestring):
            return value
        # TODO: Should we catenate values in RF 2.9 instead?
        if len(value) == 1:
            return value[0]
        raise DataError("Creating a scalar variable with a list value in "
                        "the Variable table is no longer possible. "
                        "Create a list variable '@%s' and use it as a "
                        "scalar variable '%s' instead." % (name[1:], name))

    def _replace_variables(self, value, variables):
        return variables.replace_scalar(value)


class ListVariableTableValue(VariableTableValueBase):

    def _replace_variables(self, value, variables):
        return variables.replace_list(value)


class DictVariableTableValue(VariableTableValueBase):

    def _format_value(self, value, name):
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
            return DotDict(self._yield_replaced(value,variables.replace_scalar))
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
