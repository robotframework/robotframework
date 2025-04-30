#  Copyright 2008-2015 Nokia Networks
#  Copyright 2016-     Robot Framework Foundation
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

from robot.errors import DataError, VariableError
from robot.utils import (
    get_env_var, get_env_vars, get_error_message, normalize, NormalizedDict
)

from .evaluation import evaluate_expression
from .notfound import variable_not_found
from .search import search_variable, VariableMatch

NOT_FOUND = object()


class VariableFinder:

    def __init__(self, variables):
        self._finders = (
            StoredFinder(variables.store),
            NumberFinder(),
            EmptyFinder(),
            InlinePythonFinder(variables),
            EnvironmentFinder(),
            ExtendedFinder(self),
        )
        self._store = variables.store

    def find(self, variable):
        match = self._get_match(variable)
        name = match.name
        for finder in self._finders:
            if match.identifier in finder.identifiers:
                result = finder.find(name)
                if result is not NOT_FOUND:
                    return result
        variable_not_found(name, self._store.data)

    def _get_match(self, variable):
        if isinstance(variable, VariableMatch):
            return variable
        match = search_variable(variable)
        if not match.is_variable() or match.items:
            raise DataError(f"Invalid variable name '{variable}'.")
        return match


class StoredFinder:
    identifiers = "$@&"

    def __init__(self, store):
        self._store = store

    def find(self, name):
        return self._store.get(name, NOT_FOUND)


class NumberFinder:
    identifiers = "$"

    def find(self, name):
        number = normalize(name)[2:-1]
        for converter in self._get_int, float:
            try:
                return converter(number)
            except ValueError:
                pass
        return NOT_FOUND

    def _get_int(self, number):
        bases = {"0b": 2, "0o": 8, "0x": 16}
        if number.startswith(tuple(bases)):
            return int(number[2:], bases[number[:2]])
        return int(number)


class EmptyFinder:
    identifiers = "$@&"
    empty = NormalizedDict({"${EMPTY}": "", "@{EMPTY}": (), "&{EMPTY}": {}}, ignore="_")

    def find(self, name):
        return self.empty.get(name, NOT_FOUND)


class InlinePythonFinder:
    identifiers = "$@&"

    def __init__(self, variables):
        self._variables = variables

    def find(self, name):
        base = name[2:-1]
        if not base or base[0] != "{" or base[-1] != "}":
            return NOT_FOUND
        try:
            return evaluate_expression(base[1:-1].strip(), self._variables)
        except DataError as err:
            raise VariableError(f"Resolving variable '{name}' failed: {err}")


class ExtendedFinder:
    identifiers = "$@&"
    _match_extended = re.compile(
        r"""
        (.+?)          # base name (group 1)
        ([^\s\w].+)    # extended part (group 2)
        """,
        re.UNICODE | re.VERBOSE,
    ).match

    def __init__(self, finder):
        self._find_variable = finder.find

    def find(self, name):
        match = self._match_extended(name[2:-1])
        if match is None:
            return NOT_FOUND
        base_name, extended = match.groups()
        try:
            variable = self._find_variable(f"${{{base_name}}}")
        except DataError as err:
            raise VariableError(f"Resolving variable '{name}' failed: {err}")
        try:
            return eval("_BASE_VAR_" + extended, {"_BASE_VAR_": variable})
        except Exception:
            msg = get_error_message()
            raise VariableError(f"Resolving variable '{name}' failed: {msg}")


class EnvironmentFinder:
    identifiers = "%"

    def find(self, name):
        var_name, has_default, default_value = name[2:-1].partition("=")
        value = get_env_var(var_name)
        if value is not None:
            return value
        if has_default:
            return default_value
        error = f"Environment variable '{name}' not found."
        variable_not_found(name, get_env_vars(), error)
