#  Copyright 2008-2012 Nokia Siemens Networks Oyj
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

import re
import inspect
from functools import partial
from UserDict import UserDict
try:
    from java.lang.System import getProperty as getJavaSystemProperty
    from java.util import Map
except ImportError:
    getJavaSystemProperty = lambda name: None
    class Map: pass

from robot import utils
from robot.errors import DataError
from robot.output import LOGGER

from .isvar import is_var, is_scalar_var
from .variablesplitter import VariableSplitter


class Variables(utils.NormalizedDict):
    """Represents a set of variables including both ${scalars} and @{lists}.

    Contains methods for replacing variables from list, scalars, and strings.
    On top of ${scalar} and @{list} variables these methods handle also
    %{environment} variables.
    """

    _extended_var_re = re.compile(r'''
    ^\${         # start of the string and "${"
    (.+?)        # base name (group 1)
    ([^\s\w].+)  # extended part (group 2)
    }$           # "}" and end of the string
    ''', re.UNICODE|re.VERBOSE)

    def __init__(self, identifiers=('$','@','%','&','*')):
        utils.NormalizedDict.__init__(self, ignore=['_'])
        self._identifiers = identifiers
        importer = utils.Importer('variable file').import_class_or_module_by_path
        self._import_variable_file = partial(importer, instantiate_with_args=())

    def __setitem__(self, name, value):
        self._validate_var_name(name)
        utils.NormalizedDict.__setitem__(self, name, value)

    def update(self, dict=None, **kwargs):
        if dict:
            self._validate_var_dict(dict)
            UserDict.update(self, dict)
            for key in dict:
                self._add_key(key)
        if kwargs:
            self.update(kwargs)

    def __getitem__(self, name):
        self._validate_var_name(name)
        try: return utils.NormalizedDict.__getitem__(self, name)
        except KeyError:
            try: return self._get_number_var(name)
            except ValueError:
                try: return self._get_list_var_as_scalar(name)
                except ValueError:
                    try: return self._get_extended_var(name)
                    except ValueError:
                        raise DataError("Non-existing variable '%s'." % name)

    def _validate_var_name(self, name):
        if not is_var(name):
            raise DataError("Invalid variable name '%s'." % name)

    def _validate_var_dict(self, dict):
        for name in dict:
            self._validate_var_name(name)

    def _get_list_var_as_scalar(self, name):
        if is_scalar_var(name):
            try:
                return self['@'+name[1:]]
            except DataError:
                pass
        raise ValueError

    def _get_extended_var(self, name):
        err_pre = "Resolving variable '%s' failed: " % name
        res = self._extended_var_re.search(name)
        if res is None:
            raise ValueError
        base_name = res.group(1)
        expression = res.group(2)
        try:
            variable = self['${%s}' % base_name]
        except DataError, err:
            raise DataError(err_pre + unicode(err))
        try:
            return eval('_BASE_VAR_' + expression, {'_BASE_VAR_': variable})
        except:
            raise DataError(err_pre + utils.get_error_message())

    def _get_number_var(self, name):
        if name[0] != '$':
            raise ValueError
        number = self._normalize(name)[2:-1]
        try:
            return self._get_int_var(number)
        except ValueError:
            return float(number)

    def _get_int_var(self, number):
        bases = {'0b': 2, '0o': 8, '0x': 16}
        if number.startswith(tuple(bases)):
            return int(number[2:], bases[number[:2]])
        return int(number)

    def replace_list(self, items):
        """Replaces variables from a list of items.

        If an item in a list is a @{list} variable its value is returned.
        Possible variables from other items are replaced using 'replace_scalar'.
        Result is always a list.
        """
        results = []
        for item in items or []:
            listvar = self._replace_variables_inside_possible_list_var(item)
            if listvar:
                results.extend(self[listvar])
            else:
                results.append(self.replace_scalar(item))
        return results

    def _replace_variables_inside_possible_list_var(self, item):
        if not (isinstance(item, basestring) and
                item.startswith('@{') and item.endswith('}')):
            return None
        var = VariableSplitter(item, self._identifiers)
        if var.start != 0 or var.end != len(item):
            return None
        return '@{%s}' % var.get_replaced_base(self)

    def replace_scalar(self, item):
        """Replaces variables from a scalar item.

        If the item is not a string it is returned as is. If it is a ${scalar}
        variable its value is returned. Otherwise variables are replaced with
        'replace_string'. Result may be any object.
        """
        if self._cannot_have_variables(item):
            return utils.unescape(item)
        var = VariableSplitter(item, self._identifiers)
        if var.identifier and var.base and var.start == 0 and var.end == len(item):
            return self._get_variable(var)
        return self.replace_string(item, var)

    def _cannot_have_variables(self, item):
        return (not isinstance(item, basestring)) or '{' not in item

    def replace_string(self, string, splitted=None, ignore_errors=False):
        """Replaces variables from a string. Result is always a string."""
        if self._cannot_have_variables(string):
            return utils.unescape(string)
        result = []
        if splitted is None:
            splitted = VariableSplitter(string, self._identifiers)
        while True:
            if splitted.identifier is None:
                result.append(utils.unescape(string))
                break
            result.append(utils.unescape(string[:splitted.start]))
            try:
                value = self._get_variable(splitted)
            except DataError:
                if not ignore_errors:
                    raise
                value = string[splitted.start:splitted.end]
            if not isinstance(value, unicode):
                value = utils.unic(value)
            result.append(value)
            string = string[splitted.end:]
            splitted = VariableSplitter(string, self._identifiers)
        result = ''.join(result)
        return result

    def _get_variable(self, var):
        """'var' is an instance of a VariableSplitter"""
        # 1) Handle reserved syntax
        if var.identifier not in ['$','@','%']:
            value = '%s{%s}' % (var.identifier, var.base)
            LOGGER.warn("Syntax '%s' is reserved for future use. Please "
                        "escape it like '\\%s'." % (value, value))
            return value

        # 2) Handle environment variables and Java system properties
        elif var.identifier == '%':
            name = var.get_replaced_base(self).strip()
            if not name:
                return '%%{%s}' % var.base
            value = utils.get_env_var(name)
            if value is not None:
                return value
            value = getJavaSystemProperty(name)
            if value is not None:
                return value
            raise DataError("Environment variable '%s' does not exist" % name)

        # 3) Handle ${scalar} variables and @{list} variables without index
        elif var.index is None:
            name = '%s{%s}' % (var.identifier, var.get_replaced_base(self))
            return self[name]

        # 4) Handle items from list variables e.g. @{var}[1]
        else:
            try:
                index = int(self.replace_string(var.index))
                name = '@{%s}' % var.get_replaced_base(self)
                return self[name][index]
            except (ValueError, DataError, IndexError):
                raise DataError("Non-existing variable '@{%s}[%s]'"
                                % (var.base, var.index))

    def set_from_file(self, path, args=None, overwrite=False):
        LOGGER.info("Importing variable file '%s' with args %s" % (path, args))
        var_file = self._import_variable_file(path)
        try:
            variables = self._get_variables_from_var_file(var_file, args)
            self._set_from_file(variables, overwrite, path)
        except:
            amsg = 'with arguments %s ' % utils.seq2str2(args) if args else ''
            raise DataError("Processing variable file '%s' %sfailed: %s"
                            % (path, amsg, utils.get_error_message()))
        return variables

    # This can be used with variables got from set_from_file directly to
    # prevent importing same file multiple times
    def _set_from_file(self, variables, overwrite, path):
        list_prefix = 'LIST__'
        for name, value in variables:
            if name.startswith(list_prefix):
                name = '@{%s}' % name[len(list_prefix):]
                try:
                    if isinstance(value, basestring):
                        raise TypeError
                    value = list(value)
                except TypeError:
                    raise DataError("List variable '%s' cannot get a non-list "
                                    "value '%s'" % (name, utils.unic(value)))
            else:
                name = '${%s}' % name
            if overwrite or not self.contains(name):
                self.set(name, value)

    def set_from_variable_table(self, variable_table, overwrite=False):
        for variable in variable_table:
            if not variable.has_data():
                continue
            try:
                name, value = self._get_var_table_name_and_value(
                    variable.name, variable.value, variable_table.source)
                if overwrite or not self.contains(name):
                    self.set(name, value)
            except DataError, err:
                variable_table.report_invalid_syntax("Setting variable '%s' failed: %s"
                                                     % (variable.name, unicode(err)))

    def _get_var_table_name_and_value(self, name, value, path=None):
        self._validate_var_name(name)
        value = [self._unescape_leading_trailing_spaces(cell) for cell in value]
        if name[0] == '@':
            return name, self.replace_list(value)
        return name, self._get_var_table_scalar_value(name, value, path)

    def _unescape_leading_trailing_spaces(self, item):
        if item.endswith(' \\'):
            item = item[:-1]
        if item.startswith('\\ '):
            item = item[1:]
        return item

    def _get_var_table_scalar_value(self, name, value, path=None):
        if len(value) == 1:
            return self.replace_scalar(value[0])
        msg = ("Creating a scalar variable with a list value in the Variable "
               "table is deprecated and this functionality will be removed in "
               "Robot Framework 2.7. Create a list variable '@%s' and use "
               "it as a scalar variable '%s' instead" % (name[1:], name))
        if path:
            msg += " in file '%s'" % path
        LOGGER.warn(msg + '.')
        return self.replace_list(value)

    def _get_variables_from_var_file(self, var_file, args):
        variables = self._get_dynamical_variables(var_file, args or ())
        if variables is not None:
            return variables
        names = self._get_static_variable_names(var_file)
        return self._get_static_variables(var_file, names)

    def _get_dynamical_variables(self, var_file, args):
        get_variables = getattr(var_file, 'get_variables', None)
        if not get_variables:
            get_variables = getattr(var_file, 'getVariables', None)
        if not get_variables:
            return None
        variables = get_variables(*args)
        if isinstance(variables, (dict, UserDict)):
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

    def has_key(self, variable):
        try:
            self[variable]
        except DataError:
            return False
        else:
            return True

    __contains__ = has_key

    def contains(self, variable, extended=False):
        if extended:
            return self.has_key(variable)
        return utils.NormalizedDict.has_key(self, variable)
