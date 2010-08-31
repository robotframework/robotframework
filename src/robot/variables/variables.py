#  Copyright 2008-2010 Nokia Siemens Networks Oyj
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
import os
from UserDict import UserDict
if os.name == 'java':
    from java.util import Map
else:
    class Map: pass

from robot import utils
from robot.errors import DataError
from robot.output import LOGGER

from isvar import is_var, is_scalar_var


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
    ''', re.VERBOSE)

    def __init__(self, identifiers=['$','@','%','&','*']):
        utils.NormalizedDict.__init__(self, ignore=['_'])
        self._identifiers = identifiers

    def __setitem__(self, name, value, path=None, depr_warning=True):
        if not is_var(name):
            raise DataError("Invalid variable name '%s'." % name)
        if depr_warning:
            self._deprecation_warning_if_basename_already_used(name, path)
        utils.NormalizedDict.__setitem__(self, name, value)

    def _deprecation_warning_if_basename_already_used(self, name, path):
        other = ('@' if name[0] == '$' else '$') + name[1:]
        if utils.NormalizedDict.__contains__(self, other):
            self._log_warning_when_basename_already_used(name, other, path)

    def _log_warning_when_basename_already_used(self, name, other, path):
        msg = ("Using same base name with scalar and list variables is "
               "deprecated. Please change either '%s' or '%s'") % (name, other)
        if path:
            msg += " in file '%s'" % path
        msg += " before Robot Framework 2.6."
        # If path is not known we are executing keywords and can log message
        LOGGER.warn(msg, log=not path)

    def __getitem__(self, name):
        if not is_var(name):
            raise DataError("Invalid variable name '%s'." % name)
        try: return utils.NormalizedDict.__getitem__(self, name)
        except KeyError:
            try: return self._get_number_var(name)
            except ValueError:
                try: return self._get_extended_var(name)
                except ValueError:
                    try: return self._get_list_var_as_scalar(name)
                    except ValueError:
                        raise DataError("Non-existing variable '%s'." % name)

    def _get_list_var_as_scalar(self, name):
        if is_scalar_var(name):
            try:
                return self['@'+name[1:]]
            except DataError:
                pass
        raise ValueError

    def _get_extended_var(self, name):
        res = self._extended_var_re.search(name)
        if res is None:
            raise ValueError
        base_name = res.group(1)
        expression = res.group(2)
        try:
            variable = self['${%s}' % base_name]
        except DataError:
            raise ValueError
        try:
            return eval('_BASE_VAR_' + expression, {'_BASE_VAR_': variable})
        except:
            raise DataError("Resolving variable '%s' failed: %s"
                            % (name, utils.get_error_message()))

    def _get_number_var(self, name):
        if name[0] != '$':
            raise ValueError
        base = self._normalize(name)[2:-1]
        try:
            return long(base)
        except ValueError:
            return float(base)

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
        if not (isinstance(item, basestring) 
                and item.startswith('@{') and item.endswith('}')):
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
        if var.identifier and var.base and \
               var.start == 0 and var.end == len(item):
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
            if not isinstance(value, basestring):
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

        # 2) Handle environment variables
        elif var.identifier == '%':
            try:
                name = var.get_replaced_base(self).strip()
                if name != '':
                    return os.environ[name]
                else:
                    return '%%{%s}' % var.base
            except KeyError:
                raise DataError("Environment variable '%s' does not exist"
                                % name)

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

    def set_from_file(self, path, args, overwrite=False):
        LOGGER.info("Importing varible file '%s' with args %s" % (path, args))
        args = args or []
        try:
            module = utils.simple_import(path)
            variables = self._get_variables_from_module(module, args)
            self._set_from_file(variables, overwrite, path)
        except:
            amsg = args and 'with arguments %s ' % utils.seq2str2(args) or ''
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
            if overwrite or not utils.NormalizedDict.has_key(self, name):
                self.__setitem__(name, value, path)

    def set_from_variable_table(self, variable_table):
        for variable in variable_table:
            try:
                name, value = self._get_var_table_name_and_value(variable.name,
                                                                 variable.value, 
                                                                 variable_table.source)
                # self.has_key would also match if name matches extended syntax
                if not utils.NormalizedDict.has_key(self, name):
                    self.__setitem__(name, value, variable_table.source)
            except DataError, err:
                variable_table.report_invalid_syntax("Setting variable '%s' failed: %s"
                                                     % (variable.name, unicode(err)))

    def _get_var_table_name_and_value(self, name, value, path=None):
        if not is_var(name):
            raise DataError("Invalid variable name.")
        value = [ self._unescape_leading_trailing_spaces(cell) for cell in value ]
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
               "Robot Framework 2.6. Create a list variable '@%s' and use "
               "it as a scalar variable '%s' instead" % (name[1:], name))
        if path:
            msg += " in file '%s'" % path
        LOGGER.warn(msg + '.')
        return self.replace_list(value)

    def _get_variables_from_module(self, module, args):
        variables = self._get_dynamical_variables(module, args)
        if variables is not None:
            return variables
        names = [ attr for attr in dir(module) if not attr.startswith('_') ]
        try:
            names = [ name for name in names if name in module.__all__ ]
        except AttributeError:
            pass
        return [ (name, getattr(module, name)) for name in names ]

    def _get_dynamical_variables(self, module, args):
        try:
            try:
                get_variables = getattr(module, 'get_variables')
            except AttributeError:
                get_variables = getattr(module, 'getVariables')
        except AttributeError:
            return None
        variables = get_variables(*args)
        if isinstance(variables, (dict, UserDict)):
            return variables.items()
        if isinstance(variables, Map):
            return [(entry.key, entry.value) for entry in variables.entrySet()]
        raise DataError("Expected mapping but %s returned %s."
                         % (get_variables.__name__, type(variables).__name__))

    def has_key(self, key):
        try:
            self[key]
        except DataError:
            return False
        else:
            return True

    __contains__ = has_key


class VariableSplitter:

    def __init__(self, string, identifiers):
        self.identifier = None
        self.base = None
        self.index = None
        self.start = -1
        self.end = -1
        self._identifiers = identifiers
        self._may_have_internal_variables = False
        if self._split(string):
            self._finalize()

    def get_replaced_base(self, variables):
        if self._may_have_internal_variables:
            return variables.replace_string(self.base)
        return self.base

    def _finalize(self):
        self.identifier = self._variable_chars[0]
        self.base = ''.join(self._variable_chars[2:-1])
        self.end = self.start + len(self._variable_chars)
        if self._index_chars and self._index_chars[-1] == ']':
            self.index = ''.join(self._index_chars[1:-1])
            self.end += len(self._index_chars)

    def _split(self, string):
        start_index, max_index = self._find_variable(string)
        if start_index < 0:
            return False
        self.start = start_index
        self._started_vars = 1
        self._state_handler = self._variable_state_handler
        self._variable_chars = [ string[start_index], '{' ]
        self._index_chars = []
        start_index += 2
        for index, char in enumerate(string[start_index:]):
            try:
                self._state_handler(char)
            except StopIteration:
                break
            if self._state_handler not in [ self._waiting_index_state_handler,
                  self._index_state_handler ] and start_index+index > max_index:
                break
        return True

    def _find_variable(self, string):
        max_index = string.rfind('}')
        if max_index == -1:
            return -1, -1
        start_index = self._find_start_index(string, 1, max_index)
        if start_index == -1:
            return -1, -2
        return start_index, max_index

    def _find_start_index(self, string, start, end):
        index = string.find('{', start, end) - 1
        if index < 0:
            return -1
        elif self._start_index_is_ok(string, index):
            return index
        else:
            return self._find_start_index(string, index+2, end)

    def _start_index_is_ok(self, string, index):
        if string[index] not in self._identifiers:
            return False
        backslash_count = 0
        while index - backslash_count > 0:
            if string[index - backslash_count - 1] == '\\':
                backslash_count += 1
            else:
                break
        return backslash_count % 2 == 0

    def _variable_state_handler(self, char):
        self._variable_chars.append(char)
        if char == '}':
            self._started_vars -= 1
            if self._started_vars == 0:
                if self._variable_chars[0] == '@':
                    self._state_handler = self._waiting_index_state_handler
                else:
                    raise StopIteration
        elif char in self._identifiers:
            self._state_handler = self._internal_variable_start_state_handler

    def _internal_variable_start_state_handler(self, char):
        self._state_handler = self._variable_state_handler
        if char == '{':
            self._variable_chars.append(char)
            self._started_vars += 1
            self._may_have_internal_variables = True
        else:
            self._variable_state_handler(char)

    def _waiting_index_state_handler(self, char):
        if char == '[':
            self._index_chars.append(char)
            self._state_handler = self._index_state_handler
        else:
            raise StopIteration

    def _index_state_handler(self, char):
        self._index_chars.append(char)
        if char == ']':
            raise StopIteration
