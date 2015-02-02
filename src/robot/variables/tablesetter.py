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

from .isvar import is_dict_var, is_scalar_var, validate_var
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
        DelayedVariable = {'$': DelayedScalarVariable,
                           '@': DelayedListVariable,
                           '&': DelayedDictVariable}[name[0]]
        return name[2:-1], DelayedVariable(value, name, error_reporter)


class DelayedVariable(object):

    def __init__(self, value, name, error_reporter):
        self._value = self._format_value(value, name)
        self._error_reporter = error_reporter
        self._resolving = False

    def _format_value(self, value, name):
        return value

    def resolve(self, name, variables):
        try:
            with self._avoid_recursion:
                return self._replace_variables(self._value, variables)
        except DataError, err:
            # Recursive resolving may have already removed variable.
            if name in variables.store:
                variables.store.remove(name)
                self._error_reporter(unicode(err))
            raise_not_found('${%s}' % name, variables.store.store,
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


class DelayedScalarVariable(DelayedVariable):

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


class DelayedListVariable(DelayedVariable):

    def _replace_variables(self, value, variables):
        return variables.replace_list(value)


class DelayedDictVariable(DelayedVariable):

    def _format_value(self, value, name):
        return list(self._yield_items(value))

    def _yield_items(self, value):
        for item in value:
            if is_dict_var(item):
                yield item
            else:
                yield self._split_item(item)

    def _split_item(self, item):
        try:
            index = self._get_split_index(item)
        except ValueError:
            raise DataError("Dictionary item '%s' does not contain '=' "
                            "separator." % item)
        return item[:index], item[index+1:]

    def _get_split_index(self, item):
        index = 0
        while True:
            index += item[index:].index('=')
            if self._not_escaping(item[:index]):
                return index
            index += 1

    def _not_escaping(self, name):
        backslashes = len(name) - len(name.rstrip('\\'))
        return backslashes % 2 == 0

    def _replace_variables(self, value, variables):
        try:
            return dict(self._yield_replaced(value, variables.replace_scalar))
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
