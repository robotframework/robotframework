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

from .isvar import is_list_var, is_scalar_var, validate_var


class VariableTableSetter(object):

    def __init__(self, table):
        self.table = table

    def update(self, store, overwrite=False):
        for var in self.table:
            if not var:
                continue
            try:
                name, value = self._get_var_table_name_and_value(
                    var.name, var.value, var.report_invalid_syntax)
                if overwrite or name not in store:
                    store[name] = value
            except DataError, err:
                var.report_invalid_syntax(err)

    def _get_var_table_name_and_value(self, name, value, error_reporter):
        validate_var(name)
        if is_scalar_var(name) and isinstance(value, basestring):
            value = [value]
        else:
            self._validate_var_is_not_scalar_list(name, value)
        value = [self._unescape_leading_trailing_spaces(cell) for cell in value]
        return name, DelayedVariable(value, error_reporter)

    def _unescape_leading_trailing_spaces(self, item):
        if item.endswith(' \\'):
            item = item[:-1]
        if item.startswith('\\ '):
            item = item[1:]
        return item

    def _validate_var_is_not_scalar_list(self, name, value):
        if is_scalar_var(name) and len(value) > 1:
            raise DataError("Creating a scalar variable with a list value in "
                            "the Variable table is no longer possible. "
                            "Create a list variable '@%s' and use it as a "
                            "scalar variable '%s' instead." % (name[1:], name))


class DelayedVariable(object):

    def __init__(self, value, error_reporter):
        self._value = value
        self._error_reporter = error_reporter
        self._resolving = False

    def resolve(self, name, variables, error_reporter):
        # TODO: Move error reported to importable util
        try:
            value = self._resolve(name, variables)
        except DataError, err:
            variables.pop(name)
            self._error_reporter(unicode(err))
            msg = "Variable '%s' not found." % name
            error_reporter(name, variables, msg)
        variables[name] = value
        return value

    def _resolve(self, name, variables):
        with self._avoid_recursion:
            if is_list_var(name):
                return variables.replace_list(self._value)
            return variables.replace_scalar(self._value[0])

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
