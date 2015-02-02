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

try:
    from java.lang.System import (getProperty as get_java_property,
                                  getProperties as get_java_properties)
except ImportError:
    get_java_property = lambda name: None
    get_java_properties = lambda: {}

from robot.errors import DataError
from robot.utils import (get_env_var, get_env_vars, get_error_message,
                         normalize, NormalizedDict)

from .notfound import raise_not_found


class StoredFinder(object):

    def __init__(self, store):
        self._store = store

    def find(self, name):
        if name[0] not in '$@&':
            raise ValueError
        return self._store.find(name[2:-1])


class NumberFinder(object):

    def find(self, name):
        if name[0] != '$':
            raise ValueError
        number = normalize(name)[2:-1]
        try:
            return self._get_int(number)
        except ValueError:
            return float(number)

    def _get_int(self, number):
        bases = {'0b': 2, '0o': 8, '0x': 16}
        if number.startswith(tuple(bases)):
            return int(number[2:], bases[number[:2]])
        return int(number)


class EmptyFinder(object):

    def find(self, name):
        return NormalizedDict({'${EMPTY}': '', '@{EMPTY}': ()})[name]


class ExtendedFinder(object):
    _extended_var_re = re.compile(r'''
    ^[\$@]{      # start of the string and "${" or "@{"
    (.+?)        # base name (group 1)
    ([^\s\w].+)  # extended part (group 2)
    }$           # "}" and end of the string
    ''', re.UNICODE|re.VERBOSE)

    def __init__(self, variables):
        self._variables = variables

    def find(self, name):
        res = self._extended_var_re.search(name)
        if res is None:
            raise ValueError
        base_name = res.group(1)
        expression = res.group(2)
        try:
            variable = self._variables['${%s}' % base_name]
        except DataError, err:
            raise DataError("Resolving variable '%s' failed: %s"
                            % (name, unicode(err)))
        try:
            return eval('_BASE_VAR_' + expression, {'_BASE_VAR_': variable})
        except:
            raise DataError("Resolving variable '%s' failed: %s"
                            % (name, get_error_message()))


class EnvironmentFinder(object):

    def find(self, name):
        if name[0] != '%':
            raise ValueError
        for getter in get_env_var, get_java_property:
            value = getter(name[2:-1])
            if value is not None:
                return value
        raise_not_found(name, self._get_candidates(),
                        "Environment variable '%s' not found." % name)

    def _get_candidates(self):
        candidates = dict(get_java_properties())
        candidates.update(get_env_vars())
        return candidates
