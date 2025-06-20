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

from typing import Any, Callable, Sequence, TYPE_CHECKING

from robot.errors import DataError
from robot.utils import DotDict, split_from_equals, type_name
from robot.utils.secret import Secret
from robot.utils.unic import safe_str

from .resolvable import Resolvable
from .search import is_dict_variable, is_list_variable, search_variable, VariableMatch

if TYPE_CHECKING:
    from robot.running import Var, Variable

    from .store import VariableStore


class VariableTableSetter:

    def __init__(self, store: "VariableStore"):
        self.store = store

    def set(self, variables: "Sequence[Variable]", overwrite: bool = False):
        for var in variables:
            try:
                resolver = VariableResolver.from_variable(var)
                self.store.add(resolver.name, resolver, overwrite)
            except DataError as err:
                var.report_error(str(err))


class VariableResolver(Resolvable):

    def __init__(
        self,
        value: Sequence[str],
        name: "str|None" = None,
        type: "str|None" = None,
        error_reporter: "Callable[[str], None]|None" = None,
    ):
        self.value = tuple(value)
        self.name = name
        self.type = type
        self.error_reporter = error_reporter
        self.resolving = False
        self.resolved = False

    @classmethod
    def from_name_and_value(
        cls,
        name: str,
        value: "str|Sequence[str]",
        separator: "str|None" = None,
        error_reporter: "Callable[[str], None]|None" = None,
    ) -> "VariableResolver":
        match = search_variable(name, parse_type=True)
        if not match.is_assign(allow_nested=True):
            raise DataError(f"Invalid variable name '{name}'.")
        if match.identifier == "$":
            return ScalarVariableResolver(
                value,
                separator,
                match.name,
                match.type,
                error_reporter,
            )
        if separator is not None:
            raise DataError("Only scalar variables support separators.")
        klass = {"@": ListVariableResolver, "&": DictVariableResolver}[match.identifier]
        return klass(value, match.name, match.type, error_reporter)

    @classmethod
    def from_variable(cls, var: "Var|Variable") -> "VariableResolver":
        if var.error:
            raise DataError(var.error)
        return cls.from_name_and_value(
            var.name,
            var.value,
            var.separator,
            getattr(var, "report_error", None),
        )

    def resolve(self, variables) -> Any:
        if self.resolving:
            raise DataError("Recursive variable definition.")
        if not self.resolved:
            self.resolving = True
            try:
                value = self._replace_variables(variables)
            finally:
                self.resolving = False
            self.value = self._convert(value, self.type) if self.type else value
            if self.name:
                base = variables.replace_string(self.name[2:-1])
                self.name = self.name[:2] + base + "}"
            self.resolved = True
        return self.value

    def _replace_variables(self, variables) -> Any:
        raise NotImplementedError

    def _handle_secrets(self, value, replace_scalar, typ=None):
        typ = typ or self.type
        if not typ or typ.title() != "Secret":
            return value
        match = search_variable(value, identifiers="$%")
        if not match:
            self._raise_secret_not_found(value)
        if match.is_variable():
            return self._wrap_secret(replace_scalar, match)
        values = []
        secret_seen = False
        while match:
            values.append(match.before)
            try:
                values.append(self._wrap_secret(replace_scalar, match).value)
            except DataError:
                values.append(replace_scalar(match.match))
            else:
                secret_seen = True
            match = search_variable(match.after, identifiers="$%")
        values.append(match.before)
        if not secret_seen:
            self._raise_secret_not_found(value, values)
        return Secret("".join(safe_str(v) for v in values))

    def _raise_secret_not_found(self, value, values=None):
        if not values:
            typ = type_name(value)
            raise DataError(f"Value '{value}' must have type 'Secret', got {typ}.")
        typ = [f"'{type_name(v)}'" for v in values]
        typ = ", ".join(typ)
        raise DataError(
            f"Value '{value}' has types: {typ}, but does not have 'Secret' type."
        )

    def _wrap_secret(self, replace_scalar, match: VariableMatch) -> "Secret|Any":
        secret = replace_scalar(match.match)
        if match.identifier == "%":
            return Secret(secret)
        if isinstance(secret, Secret):
            return secret
        self._raise_secret_not_found(secret)

    def _convert(self, value, type_):
        from robot.running import TypeInfo

        info = TypeInfo.from_type_hint(type_)
        try:
            return info.convert(value, kind="Value")
        except (ValueError, TypeError) as err:
            raise DataError(str(err))

    def report_error(self, error):
        if self.error_reporter:
            self.error_reporter(error)
        else:
            raise DataError(f"Error reporter not set. Reported error was: {error}")


class ScalarVariableResolver(VariableResolver):

    def __init__(
        self,
        value: "str|Sequence[str]",
        separator: "str|None" = None,
        name=None,
        type=None,
        error_reporter=None,
    ):
        value, separator = self._get_value_and_separator(value, separator)
        super().__init__(value, name, type, error_reporter)
        self.separator = separator

    def _get_value_and_separator(self, value, separator):
        if isinstance(value, str):
            value = [value]
        elif separator is None and value and value[0].startswith("SEPARATOR="):
            separator = value[0][10:]
            value = value[1:]
        return value, separator

    def _replace_variables(self, variables):
        value, separator = self.value, self.separator
        if self._is_single_value(value, separator):
            replace_scalar = variables.replace_scalar
            value = self._handle_secrets(value[0], replace_scalar)
            return replace_scalar(value)
        if separator is None:
            separator = " "
        else:
            separator = variables.replace_string(separator)
        value = variables.replace_list(value)
        return separator.join(str(item) for item in value)

    def _is_single_value(self, value, separator):
        return separator is None and len(value) == 1 and not is_list_variable(value[0])


class ListVariableResolver(VariableResolver):

    def _replace_variables(self, variables):
        replace_scalar = variables.replace_scalar
        value = [self._handle_secrets(value, replace_scalar) for value in self.value]
        self.value = tuple(value)
        return variables.replace_list(self.value)

    def _convert(self, value, type_):
        return super()._convert(value, f"list[{type_}]")


class DictVariableResolver(VariableResolver):

    def __init__(self, value: Sequence[str], name=None, type=None, error_reporter=None):
        super().__init__(tuple(self._yield_items(value)), name, type, error_reporter)

    def _yield_items(self, values):
        for item in values:
            if is_dict_variable(item):
                yield item
            else:
                name, value = split_from_equals(item)
                if value is None:
                    raise DataError(
                        f"Invalid dictionary variable item '{item}'. Items must use "
                        f"'name=value' syntax or be dictionary variables themselves."
                    )
                yield name, value

    def _replace_variables(self, variables):
        try:
            return DotDict(self._yield_replaced(self.value, variables.replace_scalar))
        except TypeError as err:
            raise DataError(f"Creating dictionary variable failed: {err}")

    def _yield_replaced(self, values, replace_scalar):
        if not self.type:
            k_type = v_type = None
        elif "=" in self.type:
            k_type, v_type = self.type.split("=", 1)
        else:
            k_type, v_type = "Any", self.type
        for item in values:
            if isinstance(item, tuple):
                key, value = item
                yield (
                    replace_scalar(self._handle_secrets(key, replace_scalar, k_type)),
                    replace_scalar(self._handle_secrets(value, replace_scalar, v_type)),
                )
            else:
                yield from replace_scalar(item).items()

    def _convert(self, value, type_):
        k_type, v_type = type_.split("=", 1) if "=" in type_ else ("Any", type_)
        return super()._convert(value, f"dict[{k_type}, {v_type}]")
