#  Copyright 2008-2014 Nokia Solutions and Networks
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
import re
from functools import partial
try:
    from java.lang.System import getProperty as getJavaSystemProperty
except ImportError:
    getJavaSystemProperty = lambda name: None

from robot import utils
from robot.errors import DataError
from robot.output import LOGGER

from .filesetter import VariableFileSetter
from .isvar import is_scalar_var, is_list_var, validate_var
from .store import VariableStore
from .tablesetter import VariableTableSetter, DelayedVariable
from .variablesplitter import VariableSplitter


class Variables(object):
    """Represents a set of variables including both ${scalars} and @{lists}.

    Contains methods for replacing variables from list, scalars, and strings.
    On top of ${scalar} and @{list} variables these methods handle also
    %{environment} variables.
    """

    def __init__(self, identifiers=('$', '@', '%', '&', '*')):
        self._identifiers = identifiers
        self._store = VariableStore()

    def __setitem__(self, name, value):
        validate_var(name)
        self._store[name] = value

    def update(self, dict=None, **kwargs):
        for name in list(dict or []) + list(kwargs):
            validate_var(name)
        self._store.update(dict, **kwargs)

    def __getitem__(self, name):
        validate_var(name)
        try:
            return self._find_variable(name)
        except KeyError:
            try:
                return self._get_number_var(name)
            except ValueError:
                try:
                    return self._get_list_var_as_scalar(name)
                except ValueError:
                    try:
                        return self._get_scalar_var_as_list(name)
                    except ValueError:
                        try:
                            return self._get_extended_var(name)
                        except ValueError:
                            self._raise_non_existing_variable(name)

    def _find_variable(self, name):
        variable = self._store[name]
        return self._solve_delayed(name, variable)

    def _raise_non_existing_variable(self, name, msg=None, env_vars=False):
        _raise_not_found(name, self._store.keys(), msg, env_vars=env_vars)

    def _solve_delayed(self, name, value):
        if isinstance(value, DelayedVariable):
            return value.resolve(name, self, _raise_not_found)
        return value

    def resolve_delayed(self):
        # cannot iterate over `self` here because loop changes the state.
        for var in self._store.keys():
            try:
                self[var]  # getting variable resolves it if needed
            except DataError:
                pass

    def _get_list_var_as_scalar(self, name):
        if not is_scalar_var(name):
            raise ValueError
        name = '@'+name[1:]
        try:
            return self._find_variable(name)
        except KeyError:
            return self._get_extended_var(name)

    def _get_scalar_var_as_list(self, name):
        if not is_list_var(name):
            raise ValueError
        name = '$'+name[1:]
        try:
            value = self._find_variable(name)
        except KeyError:
            value = self._get_extended_var(name)
        if not utils.is_list_like(value):
            raise DataError("Using scalar variable '%s' as list variable '@%s' "
                            "requires its value to be list or list-like."
                            % (name, name[1:]))
        return value

    def _get_extended_var(self, name):
        return ExtendedVariableFinder(self).find(name)

    def _get_number_var(self, name):
        if name[0] != '$':
            raise ValueError
        number = utils.normalize(name)[2:-1]
        try:
            return self._get_int_var(number)
        except ValueError:
            return float(number)

    def _get_int_var(self, number):
        bases = {'0b': 2, '0o': 8, '0x': 16}
        if number.startswith(tuple(bases)):
            return int(number[2:], bases[number[:2]])
        return int(number)

    def replace_list(self, items, replace_until=None):
        """Replaces variables from a list of items.

        If an item in a list is a @{list} variable its value is returned.
        Possible variables from other items are replaced using 'replace_scalar'.
        Result is always a list.

        'replace_until' can be used to limit replacing arguments to certain
        index from the beginning. Used with Run Keyword variants that only
        want to resolve some of the arguments in the beginning and pass others
        to called keywords unmodified.
        """
        items = list(items or [])
        if replace_until is not None:
            return self._replace_list_until(items, replace_until)
        return self._replace_list(items)

    def _replace_list_until(self, items, replace_until):
        # @{list} variables can contain more or less arguments than needed.
        # Therefore we need to go through arguments one by one.
        processed = []
        while len(processed) < replace_until and items:
            processed.extend(self._replace_list([items.pop(0)]))
        # If @{list} variable is opened, arguments going further must be
        # escaped to prevent them being un-escaped twice.
        if len(processed) > replace_until:
            processed[replace_until:] = [self._escape(item)
                                         for item in processed[replace_until:]]
        return processed + items

    def _escape(self, item):
        item = utils.escape(item)
        # Escape also special syntax used by Run Kw If and Run Kws.
        if item in ('ELSE', 'ELSE IF', 'AND'):
            item = '\\' + item
        return item

    def _replace_list(self, items):
        results = []
        for item in items:
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
        return not (isinstance(item, basestring) and '{' in item)

    def replace_string(self, string, splitter=None, ignore_errors=False):
        """Replaces variables from a string. Result is always a string."""
        if self._cannot_have_variables(string):
            return utils.unescape(string)
        result = []
        if splitter is None:
            splitter = VariableSplitter(string, self._identifiers)
        while True:
            if splitter.identifier is None:
                result.append(utils.unescape(string))
                break
            result.append(utils.unescape(string[:splitter.start]))
            try:
                value = self._get_variable(splitter)
            except DataError:
                if not ignore_errors:
                    raise
                value = string[splitter.start:splitter.end]
            if not isinstance(value, unicode):
                value = utils.unic(value)
            result.append(value)
            string = string[splitter.end:]
            splitter = VariableSplitter(string, self._identifiers)
        result = ''.join(result)
        return result

    def _get_variable(self, var):
        """'var' is an instance of a VariableSplitter"""
        # 1) Handle reserved syntax
        if var.identifier not in '$@%':
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
            msg = "Environment variable '%%{%s}' not found." % name
            self._raise_non_existing_variable('%%{%s}' % name, msg,
                                              env_vars=True)

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
                msg = ("Variable '@{%s}[%s]' not found."
                       % (var.base, var.index))
                self._raise_non_existing_variable(var.base, msg)


    def set_from_file(self, path_or_variables, args=None, overwrite=False):
        setter = VariableFileSetter(self._store)
        return setter.set(path_or_variables, args, overwrite)

    def set_from_variable_table(self, variables, overwrite=False):
        setter = VariableTableSetter(self._store)
        setter.set(variables, overwrite)

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
            return variable in self
        return variable in self._store

    def clear(self):
        self._store.clear()

    def keys(self):
        return self._store.keys()

    def items(self):
        return self._store.items()

    def copy(self):
        variables = Variables(self._identifiers)
        variables._store = self._store.copy()
        return variables

    def __iter__(self):
        return iter(self._store)

    def __len__(self):
        return len(self._store)

    def pop(self, key=None, *default):
        return self._store.pop(key, *default)


class ExtendedVariableFinder(object):
    _extended_var_re = re.compile(r'''
    ^\${         # start of the string and "${"
    (.+?)        # base name (group 1)
    ([^\s\w].+)  # extended part (group 2)
    }$           # "}" and end of the string
    ''', re.UNICODE|re.VERBOSE)

    def __init__(self, variables):
        self.variables = variables

    def find(self, name):
        res = self._extended_var_re.search(name)
        if res is None:
            raise ValueError
        base_name = res.group(1)
        expression = res.group(2)
        try:
            variable = self.variables['${%s}' % base_name]
        except DataError, err:
            raise DataError("Resolving variable '%s' failed: %s"
                            % (name, unicode(err)))
        try:
            return eval('_BASE_VAR_' + expression, {'_BASE_VAR_': variable})
        except:
            raise DataError("Resolving variable '%s' failed: %s"
                            % (name, utils.get_error_message()))


def _raise_not_found(name, candidates, msg=None, env_vars=False):
    """Raise DataError for missing variable name.

    Return recommendations for similar variable names if any are found.
    """
    if msg is None:
        msg = "Variable '%s' not found." % name
    if env_vars:
        candidates += ['%%{%s}' % var for var in
                       utils.get_env_vars()]
    normalizer = partial(utils.normalize, ignore='$@%&*{}_', caseless=True,
                         spaceless=True)
    finder = utils.RecommendationFinder(normalizer)
    recommendations = finder.find_recommendations(name, candidates)
    msg = finder.format_recommendations(msg, recommendations)
    raise DataError(msg)
