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

from functools import partial
from contextlib import contextmanager
import inspect
try:
    from java.util import Map
except ImportError:
    class Map(object): pass

from robot.errors import DataError
from robot.output import LOGGER
from robot.utils import (get_error_message, is_dict_like, is_list_like,
                         seq2str2, unic, Importer)

from .isvar import is_list_var, is_scalar_var, validate_var


class VariableFileReader(object):

    def __init__(self, path_or_variables, args=None):
        importer = Importer('variable file').import_class_or_module_by_path
        self._import_variable_file = partial(importer, instantiate_with_args=())
        if isinstance(path_or_variables, basestring):
            self.variables = self._import_file(path_or_variables, args)
        else:
            self.variables = path_or_variables

    def _import_file(self, path, args):
        LOGGER.info("Importing variable file '%s' with args %s" % (path, args))
        var_file = self._import_variable_file(path)
        try:
            return self._get_variables(var_file, args)
        except:
            amsg = 'with arguments %s ' % seq2str2(args) if args else ''
            raise DataError("Processing variable file '%s' %sfailed: %s"
                            % (path, amsg, get_error_message()))

    def _get_variables(self, var_file, args):
        variables = self._get_dynamical_variables(var_file, args or ())
        if variables is None:
            names = self._get_static_variable_names(var_file)
            variables = self._get_static_variables(var_file, names)
        self._validate_variables(variables)
        return variables

    def _get_dynamical_variables(self, var_file, args):
        get_variables = getattr(var_file, 'get_variables', None)
        if not get_variables:
            get_variables = getattr(var_file, 'getVariables', None)
        if not get_variables:
            return None
        variables = get_variables(*args)
        if is_dict_like(variables):
            return variables.items()
        if isinstance(variables, Map):
            return [(entry.key, entry.value) for entry in variables.entrySet()]
        raise DataError("Expected mapping but %s returned %s."
                        % (get_variables.__name__, type(variables).__name__))

    def _get_static_variable_names(self, var_file):
        names = [attr for attr in dir(var_file) if not attr.startswith('_')]
        if hasattr(var_file, '__all__'):
            names = [name for name in names if name in var_file.__all__]
        return names

    def _get_static_variables(self, var_file, names):
        variables = [(name, getattr(var_file, name)) for name in names]
        if not inspect.ismodule(var_file):
            variables = [var for var in variables if not callable(var[1])]
        return variables

    def _validate_variables(self, variables):
        for name, value in variables:
            if name.startswith('LIST__') and not is_list_like(value):
                name = '@{%s}' % name[len('LIST__'):]
                raise DataError("List variable '%s' cannot get a non-list "
                                "value '%s'" % (name, unic(value)))

    def update(self, store, overwrite=False):
        for name, value in self.variables:
            if name.startswith('LIST__'):
                name = '@{%s}' % name[len('LIST__'):]
                value = list(value)
            else:
                name = '${%s}' % name
            if overwrite or name not in store:
                store[name] = value


class VariableTableReader(object):

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
