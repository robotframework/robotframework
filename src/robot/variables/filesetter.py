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

from six import string_types

import inspect
try:
    from java.util import Map
except ImportError:
    class Map(object): pass

from robot.errors import DataError
from robot.output import LOGGER
from robot.utils import (get_error_message, is_dict_like, is_list_like,
                         seq2str2, type_name, Importer)


class VariableFileSetter(object):

    def __init__(self, store):
        self._store = store

    def set(self, path_or_variables, args=None, overwrite=False):
        variables = self._import_if_needed(path_or_variables, args)
        self._set(variables, overwrite)
        return variables

    def _import_if_needed(self, path_or_variables, args=None):
        if not isinstance(path_or_variables, string_types):
            return path_or_variables
        return VariableFileImporter().import_variables(path_or_variables, args)

    def _set(self, variables, overwrite=False):
        for name, value in variables:
            self._store.add(name, value, overwrite)


class VariableFileImporter(object):

    def import_variables(self, path, args=None):
        LOGGER.info("Importing variable file '%s' with args %s" % (path, args))
        importer = Importer('variable file').import_class_or_module_by_path
        var_file = importer(path, instantiate_with_args=())
        try:
            return self._get_variables(var_file, args)
        except:
            args = 'with arguments %s ' % seq2str2(args) if args else ''
            raise DataError("Processing variable file '%s' %sfailed: %s"
                            % (path, args, get_error_message()))

    def _get_variables(self, var_file, args):
        if self._is_dynamic(var_file):
            variables = self._get_dynamic(var_file, args)
        else:
            variables = self._get_static(var_file)
        return list(self._decorate_and_validate(variables))

    def _is_dynamic(self, var_file):
        return (hasattr(var_file, 'get_variables') or
                hasattr(var_file, 'getVariables'))

    def _get_dynamic(self, var_file, args):
        get_variables = (getattr(var_file, 'get_variables', None) or
                         getattr(var_file, 'getVariables'))
        variables = get_variables(*args)
        if is_dict_like(variables):
            return variables.items()
        raise DataError("Expected '%s' to return dict-like value, got %s."
                        % (get_variables.__name__, type_name(variables)))

    def _get_static(self, var_file):
        names = [attr for attr in dir(var_file) if not attr.startswith('_')]
        if hasattr(var_file, '__all__'):
            names = [name for name in names if name in var_file.__all__]
        variables = [(name, getattr(var_file, name)) for name in names]
        if not inspect.ismodule(var_file):
            variables = [(n, v) for n, v in variables if not callable(v)]
        return variables

    def _decorate_and_validate(self, variables):
        for name, value in variables:
            name = self._decorate(name)
            self._validate(name, value)
            yield name, value

    def _decorate(self, name):
        if name.startswith('LIST__'):
            return '@{%s}' % name[6:]
        if name.startswith('DICT__'):
            return '&{%s}' % name[6:]
        return '${%s}' % name

    def _validate(self, name, value):
        if name[0] == '@' and not is_list_like(value):
            raise DataError("Invalid variable '%s': Expected list-like value, "
                            "got %s." % (name, type_name(value)))
        if name[0] == '&' and not is_dict_like(value):
            raise DataError("Invalid variable '%s': Expected dict-like value, "
                            "got %s." % (name, type_name(value)))
