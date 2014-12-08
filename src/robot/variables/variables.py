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
import inspect
from functools import partial
from contextlib import contextmanager
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

from .isvar import is_var, is_scalar_var, is_list_var
from .variablesplitter import VariableSplitter


class Variables(utils.NormalizedDict):
    """Represents a set of variables including both ${scalars} and @{lists}.

    Contains methods for replacing variables from list, scalars, and strings.
    On top of ${scalar} and @{list} variables these methods handle also
    %{environment} variables.
    """

    def __init__(self, identifiers=('$', '@', '%', '&', '*')):
        utils.NormalizedDict.__init__(self, ignore='_')
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
        variable = utils.NormalizedDict.__getitem__(self, name)
        return self._solve_delayed(name, variable)

    def _raise_non_existing_variable(self, name, msg=None, env_vars=False):
        _raise_not_found(name, self.keys(), msg, env_vars=env_vars)

    def _solve_delayed(self, name, value):
        if isinstance(value, DelayedVariable):
            return value.resolve(name, self)
        return value

    def resolve_delayed(self):
        # cannot iterate over `self` here because loop changes the state.
        for var in self.keys():
            try:
                self[var]  # getting variable resolves it if needed
            except DataError:
                pass

    def _validate_var_name(self, name):
        if not is_var(name):
            msg = "Variable name '%s' is invalid." % name
            self._raise_non_existing_variable(name, msg=msg)

    def _validate_var_dict(self, dict):
        for name in dict:
            self._validate_var_name(name)

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


    def set_from_file(self, path, args=None, overwrite=False):
        LOGGER.info("Importing variable file '%s' with args %s" % (path, args))
        var_file = self._import_variable_file(path)
        try:
            variables = self._get_variables_from_var_file(var_file, args)
            self._set_from_file(variables, overwrite)
        except:
            amsg = 'with arguments %s ' % utils.seq2str2(args) if args else ''
            raise DataError("Processing variable file '%s' %sfailed: %s"
                            % (path, amsg, utils.get_error_message()))
        return variables

    # This can be used with variables got from set_from_file directly to
    # prevent importing same file multiple times
    def _set_from_file(self, variables, overwrite=False):
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

    def set_from_variable_table(self, variables, overwrite=False):
        for var in variables:
            if not var:
                continue
            try:
                name, value = self._get_var_table_name_and_value(
                    var.name, var.value, var.report_invalid_syntax)
                if overwrite or not self.contains(name):
                    self.set(name, value)
            except DataError, err:
                var.report_invalid_syntax(err)

    def _get_var_table_name_and_value(self, name, value, error_reporter):
        self._validate_var_name(name)
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
        if utils.is_dict_like(variables):
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


class DelayedVariable(object):

    def __init__(self, value, error_reporter):
        self._value = value
        self._error_reporter = error_reporter
        self._resolving = False

    def resolve(self, name, variables):
        try:
            value = self._resolve(name, variables)
        except DataError, err:
            variables.pop(name)
            self._error_reporter(unicode(err))
            msg = "Variable '%s' not found." % name
            _raise_not_found(name, variables, msg)
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
