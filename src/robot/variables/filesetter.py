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

import inspect
try:
    from java.util import Map
except ImportError:
    class Map(object): pass

from robot.errors import DataError
from robot.output import LOGGER
from robot.utils import (get_error_message, is_dict_like, is_list_like,
                         seq2str2, unic, Importer)


class VariableFileSetter(object):

    def __init__(self, store):
        self._store = store

    def set(self, path_or_variables, args=None, overwrite=False):
        variables = self._import_if_needed(path_or_variables, args)
        self._set(variables, overwrite)
        return variables

    def _import_if_needed(self, path_or_variables, args=None):
        if isinstance(path_or_variables, basestring):
            importer = VariableFileImporter()
            return importer.import_variables(path_or_variables, args)
        return path_or_variables

    def _set(self, variables, overwrite=False):
        for name, value in variables:
            if name.startswith('LIST__'):
                name = name[len('LIST__'):]
            self._store.add(name, value, overwrite)


class VariableFileImporter(object):

    def import_variables(self, path, args=None):
        LOGGER.info("Importing variable file '%s' with args %s" % (path, args))
        importer = Importer('variable file').import_class_or_module_by_path
        var_file = importer(path, instantiate_with_args=())
        try:
            return self._get_variables(var_file, args)
        except:
            amsg = 'with arguments %s ' % seq2str2(args) if args else ''
            raise DataError("Processing variable file '%s' %sfailed: %s"
                            % (path, amsg, get_error_message()))

    def _get_variables(self, var_file, args=None):
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
        # TODO: This shouldn't be needed after Jython 2.7 beta 4
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
                # TODO: what to do with this error
                name = '@{%s}' % name[len('LIST__'):]
                raise DataError("List variable '%s' cannot get a non-list "
                                "value '%s'" % (name, unic(value)))
