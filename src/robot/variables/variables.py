#  Copyright 2008 Nokia Siemens Networks Oyj
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
from types import DictionaryType

from robot import utils
from robot.errors import DataError
from robot.output import LOGGER

from isvar import is_var, is_scalar_var, is_list_var


class Variables(utils.NormalizedDict):
    
    """Represents a set of variables including both ${scalars} and @{lists}.
    
    Contains methods for replacing variables from list, scalars, and strings.
    On top of ${scalar} and @{list} variables these methods handle also
    %{environment} variables.
    """

    _extended_var_re = re.compile(r'''
    ^\${         # start of the string and "${" 
    (.+?)        # base name (group 1)
    ([^\s\w].+)  # extended part (any non-alphanum or space)ast once) (group 2)
    }$           # "}" and end of the string
    ''', re.VERBOSE)
    
    def __init__(self, identifiers=['$','@','%','&','*']):
        utils.NormalizedDict.__init__(self, ignore=['_'])
        self._identifiers = identifiers

    def __setitem__(self, name, value):
        if not is_var(name):
            raise DataError("Invalid variable name '%s'" % name)
        utils.NormalizedDict.__setitem__(self, name, value)
        
    def __getitem__(self, name):
        if not is_var(name):
            raise DataError("Invalid variable name '%s'" % name)
        try: return utils.NormalizedDict.__getitem__(self, name)
        except KeyError:
            try: return self._get_number_var(name)
            except ValueError:
                try: return self._get_extended_var(name)
                except ValueError:
                    try: return self._get_list_var_as_scalar(name)
                    except ValueError:
                        raise DataError("Non-existing variable '%s'" % name)

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
        for item in utils.to_list(items):
            if is_list_var(item):
                results.extend(self[item])
            else:
                results.append(self.replace_scalar(item))
        return results
        
    def replace_scalar(self, item):
        """Replaces variables from a scalar item.
        
        If the item is not a string it is returned as is. If it is a ${scalar}
        variable its value is returned. Otherwise variables are replaced with
        'replace_string'. Result may be any object.
        """
        if not utils.is_str(item):
            return item
        var = _VariableSplitter(item, self._identifiers)
        if var.identifier and var.base and \
               var.start == 0 and var.end == len(item):
            return self._get_variable(var)
        return self.replace_string(item, var)
        
    def replace_string(self, string, splitted=None):
        """Replaces variables from a string. Result is always a string."""
        result = []
        if splitted is None:
            splitted = _VariableSplitter(string, self._identifiers)
        while True:
            if splitted.identifier is None:
                result.append(utils.unescape(string))
                break
            result.append(utils.unescape(string[:splitted.start]))
            value = self._get_variable(splitted)
            if not utils.is_str(value):
                value = utils.unic(value)
            result.append(value)
            string = string[splitted.end:]
            splitted = _VariableSplitter(string, self._identifiers)
        result = ''.join(result)
        return result
        
    def _get_variable(self, var):
        """'var' is an instance of a _VariableSplitter"""
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
        args = utils.to_list(args)
        try:
            module = utils.simple_import(path)
            variables = self._get_variables_from_module(module, args)
            self._set_from_file(variables, overwrite)
        except:
            amsg = args and 'with arguments %s ' % utils.seq2str2(args) or ''
            raise DataError("Processing variable file '%s' %sfailed: %s"
                            % (path, amsg, utils.get_error_message()))
        return variables
                
    # This can be used with variables got from set_from_file directly to 
    # prevent importing same file multiple times
    def _set_from_file(self, variables, overwrite):
        list_prefix = 'LIST__'
        for name, value in variables:
            if name.startswith(list_prefix):
                name = '@{%s}' % name[len(list_prefix):]
                if not utils.is_list(value):
                    raise DataError("List variable '%s' cannot get a non-list "
                                    "value '%s'" % (name, utils.unic(value)))
            else:
                name = '${%s}' % name
            if overwrite or not utils.NormalizedDict.has_key(self, name):
                self[name] = value

    def set_from_variable_table(self, raw_variables):
        for rawvar in raw_variables:
            try:
                name, value = self._get_var_table_name_and_value(rawvar)
                # self.has_key would also match if name matches extended syntax
                if not utils.NormalizedDict.has_key(self, name):
                    self[name] = value
            except:
                rawvar.report_invalid_syntax("Setting variable '%s' failed: %s"
                                             % (rawvar.name,
                                                utils.get_error_message()))

    def _get_var_table_name_and_value(self, rawvar):
        name = self._normalize(rawvar.name)
        if not name:
            raise DataError('No variable name given')
        if name.endswith('=') and is_var(name[:-1]):
            name = name[:-1]
        elif not is_var(name):
            raise DataError("Invalid variable name '%s'" % rawvar.name)
        value = self._unescape_leading_trailing_spaces_from_var_table_value(rawvar.value)
        if name[0] == '$':
            if len(value) == 1:
                value = self.replace_scalar(value[0])
            elif len(value) == 0:
                value = ''
            else:
                value = self.replace_list(value)
        else:
            value = self.replace_list(value)
        return name, value
        
    def _unescape_leading_trailing_spaces_from_var_table_value(self, value):
        ret = []
        for item in value:
            if utils.is_str(item):
                if item.endswith(' \\'):
                    item = item[:-1]
                if item.startswith('\\ '):
                    item = item[1:]
            ret.append(item)
        return ret
        
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
        if type(variables) != DictionaryType:
            raise DataError("%s returned '%s', expected a dictionary" 
                            % (get_variables.__name__,
                               utils.type_as_str(variables)))
        return variables.items()

    def has_key(self, key):
        try:
            self[key]
        except DataError:
            return False
        else:
            return True

    __contains__ = has_key


class _VariableSplitter:
    
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
