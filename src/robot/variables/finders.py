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
                         is_dict_like, is_list_like, normalize, DotDict,
                         NormalizedDict)

from .isvar import validate_var
from .notfound import raise_not_found


class VariableFinder(object):

    def __init__(self, variable_store):
        self._finders = (StoredFinder(variable_store),
                         NumberFinder(),
                         EmptyFinder(),
                         EnvironmentFinder(),
                         ExtendedFinder(self))
        self._store = variable_store

    def find(self, name):
        validate_var(name, '$@&%')
        identifier = name[0]
        for finder in self._finders:
            if identifier in finder.identifiers:
                try:
                    value = finder.find(name)
                except (KeyError, ValueError):
                    continue
                return self._validate_value(value, identifier, name)
        raise_not_found(name, self._store.data)

    def _validate_value(self, value, identifier, name):
        if identifier == '@':
            if not is_list_like(value):
                raise DataError("Value of variable '%s' is not list or "
                                "list-like." % name)
            return list(value)
        if identifier == '&':
            if not is_dict_like(value):
                raise DataError("Value of variable '%s' is not dictionary "
                                "or dictionary-like." % name)
            return DotDict(value)
        return value


class StoredFinder(object):
    identifiers = '$@&'

    def __init__(self, store):
        self._store = store

    def find(self, name):
        return self._store[name[2:-1]]


class NumberFinder(object):
    identifiers = '$'

    def find(self, name):
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
    identifiers = '$@&'
    find = NormalizedDict({'${EMPTY}': '', '@{EMPTY}': (), '&{EMPTY}': {}},
                          ignore='_').__getitem__


class ExtendedFinder(object):
    identifiers = '$@&'
    _match_extended = re.compile(r'''
        (.+?)          # base name (group 1)
        ([^\s\w].+)    # extended part (group 2)
    ''', re.UNICODE|re.VERBOSE).match

    def __init__(self, finder):
        self._find_variable = finder.find

    def find(self, name):
        match = self._match_extended(name[2:-1])
        if match is None:
            raise ValueError
        base_name, extended = match.groups()
        try:
            variable = self._find_variable('${%s}' % base_name)
        except DataError as err:
            raise DataError("Resolving variable '%s' failed: %s"
                            % (name, unicode(err)))
        try:
            return eval('_BASE_VAR_' + extended, {'_BASE_VAR_': variable})
        except:
            raise DataError("Resolving variable '%s' failed: %s"
                            % (name, get_error_message()))


class EnvironmentFinder(object):
    identifiers = '%'

    def find(self, name):
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
