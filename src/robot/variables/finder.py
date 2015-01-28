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

import re

from robot.errors import DataError
from robot.utils import get_error_message, is_list_like, normalize

from .isvar import is_list_var, is_scalar_var, validate_var
from .notfound import raise_not_found


class VariableFinder(object):

    def __init__(self, variables):
        self._variables = variables

    def find(self, name):
        validate_var(name)
        try:
            return self._variables.store.find(name, self._variables)
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
                            raise_not_found(name, self._variables.store.keys())

    def _find_variable(self, name):
        return self._variables.store.find(name, self._variables)

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
        if not is_list_like(value):
            raise DataError("Using scalar variable '%s' as list variable '@%s' "
                            "requires its value to be list or list-like."
                            % (name, name[1:]))
        return value

    def _get_extended_var(self, name):
        # TODO: Should be able to use self, not self._variables here.
        return ExtendedVariableFinder(self._variables).find(name)

    def _get_number_var(self, name):
        if name[0] != '$':
            raise ValueError
        number = normalize(name)[2:-1]
        try:
            return self._get_int_var(number)
        except ValueError:
            return float(number)

    def _get_int_var(self, number):
        bases = {'0b': 2, '0o': 8, '0x': 16}
        if number.startswith(tuple(bases)):
            return int(number[2:], bases[number[:2]])
        return int(number)


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
                            % (name, get_error_message()))
