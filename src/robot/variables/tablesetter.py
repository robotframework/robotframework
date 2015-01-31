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

from .isvar import is_list_var, is_scalar_var, validate_var
from .notfound import raise_not_found


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
        validate_var(name)
        if not isinstance(value, basestring):
            value = [self._unescape_spaces(cell) for cell in value]
            if is_scalar_var(name):
                value = self._get_scalar_value(name, value)
        return name[2:-1], DelayedVariable(value, error_reporter)

    def _unescape_spaces(self, item):
        # TODO: Is this still needed? Why here?
        if item.endswith(' \\'):
            item = item[:-1]
        if item.startswith('\\ '):
            item = item[1:]
        return item

    def _get_scalar_value(self, name, value):
        # TODO: Should we catenate values in RF 2.9 instead?
        if len(value) == 1:
            return value[0]
        raise DataError("Creating a scalar variable with a list value in "
                        "the Variable table is no longer possible. "
                        "Create a list variable '@%s' and use it as a "
                        "scalar variable '%s' instead." % (name[1:], name))


class DelayedVariable(object):

    def __init__(self, value, error_reporter):
        self._value = value
        self._error_reporter = error_reporter
        self._resolving = False

    def resolve(self, name, variables):
        try:
            return self._resolve(variables)
        except DataError, err:
            # Recursive resolving may have already removed variable.
            if name in variables.store:
                variables.store.remove(name)
                self._error_reporter(unicode(err))
            raise_not_found('${%s}' % name, variables.store.store,
                            "Variable '${%s}' not found." % name)

    def _resolve(self, variables):
        with self._avoid_recursion:
            if isinstance(self._value, basestring):
                return variables.replace_scalar(self._value)
            return variables.replace_list(self._value)

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
