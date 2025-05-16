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

from robot.errors import DataError, VariableError
from robot.output import librarylogger as logger
from robot.utils import (
    DotDict, escape, get_error_message, is_dict_like, is_list_like, safe_str, type_name,
    unescape
)

from .finders import VariableFinder
from .search import search_variable, VariableMatch


class VariableReplacer:

    def __init__(self, variables):
        self._finder = VariableFinder(variables)

    def replace_list(self, items, replace_until=None, ignore_errors=False):
        """Replaces variables from a list of items.

        If an item in a list is a @{list} variable its value is returned.
        Possible variables from other items are replaced using 'replace_scalar'.
        Result is always a list.

        'replace_until' can be used to limit replacing arguments to certain
        index from the beginning. Used with Run Keyword variants that only
        want to resolve some arguments in the beginning and pass others
        to called keywords unmodified.
        """
        items = list(items or [])
        if replace_until is not None:
            return self._replace_list_until(items, replace_until, ignore_errors)
        return self._replace_list(items, ignore_errors)

    def _replace_list_until(self, items, limit, ignore_errors):
        # @{list} variables can contain more or less arguments than needed.
        # Therefore, we need to go through items one by one, and escape
        # possible extra items we got.
        replaced = []
        while len(replaced) < limit and items:
            replaced.extend(self._replace_list([items.pop(0)], ignore_errors))
        if len(replaced) > limit:
            replaced[limit:] = [escape(item) for item in replaced[limit:]]
        return replaced + items

    def _replace_list(self, items, ignore_errors):
        result = []
        for item in items:
            match = search_variable(item, ignore_errors=ignore_errors)
            value = self._replace(match, ignore_errors)
            if match.is_list_variable() and is_list_like(value):
                result.extend(value)
            else:
                result.append(value)
        return result

    def replace_scalar(self, item, ignore_errors=False):
        """Replaces variables from a scalar item.

        If the item is not a string it is returned as is. If it is a variable,
        its value is returned. Otherwise, possible variables are replaced with
        'replace_string'. Result may be any object.
        """
        if isinstance(item, VariableMatch):
            match = item
        else:
            match = search_variable(item, ignore_errors=ignore_errors)
        return self._replace(match, ignore_errors)

    def replace_string(self, item, custom_unescaper=None, ignore_errors=False):
        """Replaces variables from a string. Result is always a string.

        Input can also be an already found VariableMatch.
        """
        if isinstance(item, VariableMatch):
            match = item
        else:
            match = search_variable(item, ignore_errors=ignore_errors)
        result = self._replace(match, ignore_errors, custom_unescaper or unescape)
        return safe_str(result)

    def _replace(self, match, ignore_errors, unescaper=unescape):
        if not match:
            return unescaper(match.string)
        if match.is_variable():
            return self._get_variable_value(match, ignore_errors)
        parts = []
        while match:
            if match.before:
                parts.append(unescaper(match.before))
            parts.append(self._get_variable_value(match, ignore_errors))
            match = search_variable(match.after, ignore_errors=ignore_errors)
        if match.string:
            parts.append(unescaper(match.string))
        if all(isinstance(p, (bytes, bytearray)) for p in parts):
            return b"".join(parts)
        return "".join(safe_str(p) for p in parts)

    def _get_variable_value(self, match, ignore_errors):
        match.resolve_base(self, ignore_errors)
        # TODO: Do we anymore need to reserve `*{var}` syntax for anything?
        if match.identifier == "*":
            logger.warn(
                rf"Syntax '{match}' is reserved for future use. "
                rf"Please escape it like '\{match}'."
            )
            return str(match)
        try:
            value = self._finder.find(match)
            if match.items:
                value = self._get_variable_item(match, value)
            try:
                return self._validate_value(match, value)
            except VariableError:
                raise
            except Exception:
                error = get_error_message()
                raise VariableError(f"Resolving variable '{match}' failed: {error}")
        except DataError:
            if ignore_errors:
                return unescape(match.match)
            raise

    def _get_variable_item(self, match, value):
        name = match.name
        for item in match.items:
            if is_dict_like(value):
                value = self._get_dict_variable_item(name, value, item)
            elif hasattr(value, "__getitem__"):
                value = self._get_sequence_variable_item(name, value, item)
            else:
                raise VariableError(
                    f"Variable '{name}' is {type_name(value)}, which is not "
                    f"subscriptable, and thus accessing item '{item}' from it "
                    f"is not possible. To use '[{item}]' as a literal value, "
                    f"it needs to be escaped like '\\[{item}]'."
                )
            name = f"{name}[{item}]"
        return value

    def _get_sequence_variable_item(self, name, variable, index):
        index = self.replace_scalar(index)
        try:
            index = self._parse_sequence_variable_index(index)
        except ValueError:
            try:
                return variable[index]
            except TypeError:
                var_type = type_name(variable, capitalize=True)
                raise VariableError(
                    f"{var_type} '{name}' used with invalid index '{index}'. "
                    f"To use '[{index}]' as a literal value, it needs to be "
                    f"escaped like '\\[{index}]'."
                )
            except Exception:
                error = get_error_message()
                raise VariableError(f"Accessing '{name}[{index}]' failed: {error}")
        try:
            return variable[index]
        except IndexError:
            var_type = type_name(variable, capitalize=True)
            raise VariableError(f"{var_type} '{name}' has no item in index {index}.")

    def _parse_sequence_variable_index(self, index):
        if isinstance(index, (int, slice)):
            return index
        if not isinstance(index, str):
            raise ValueError
        if ":" not in index:
            return int(index)
        if index.count(":") > 2:
            raise ValueError
        return slice(*[int(i) if i else None for i in index.split(":")])

    def _get_dict_variable_item(self, name, variable, key):
        key = self.replace_scalar(key)
        try:
            return variable[key]
        except KeyError:
            raise VariableError(f"Dictionary '{name}' has no key '{key}'.")
        except TypeError as err:
            raise VariableError(f"Dictionary '{name}' used with invalid key: {err}")

    def _validate_value(self, match, value):
        if match.identifier == "@":
            if not is_list_like(value):
                raise VariableError(
                    f"Value of variable '{match}' is not list or list-like."
                )
            return list(value)
        if match.identifier == "&":
            if not is_dict_like(value):
                raise VariableError(
                    f"Value of variable '{match}' is not dictionary or dictionary-like."
                )
            return DotDict(value)
        return value
