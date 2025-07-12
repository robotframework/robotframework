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
from collections.abc import MutableSequence

from robot.errors import (
    DataError, ExecutionStatus, HandlerExecutionFailed, VariableError
)
from robot.utils import (
    DotDict, ErrorDetails, format_assign_message, get_error_message, is_dict_like,
    is_list_like, prepr, type_name
)

from .search import search_variable


class VariableAssignment:

    def __init__(self, assignment):
        validator = AssignmentValidator()
        self.assignment = validator.validate(assignment)
        self.errors = tuple(dict.fromkeys(validator.errors))  # remove duplicates

    def __iter__(self):
        return iter(self.assignment)

    def __len__(self):
        return len(self.assignment)

    def validate_assignment(self):
        if self.errors:
            if len(self.errors) == 1:
                error = self.errors[0]
            else:
                error = "\n- ".join(["Multiple errors:", *self.errors])
            raise DataError(error, syntax=True)

    def assigner(self, context):
        self.validate_assignment()
        return VariableAssigner(self.assignment, context)


class AssignmentValidator:

    def __init__(self):
        self.seen_list = False
        self.seen_dict = False
        self.seen_any = False
        self.seen_mark = False
        self.errors = []

    def validate(self, assignment):
        return [self._validate(var) for var in assignment]

    def _validate(self, variable):
        variable = self._validate_assign_mark(variable)
        self._validate_state(is_list=variable[0] == "@", is_dict=variable[0] == "&")
        return variable

    def _validate_assign_mark(self, variable):
        if self.seen_mark:
            self.errors.append(
                "Assign mark '=' can be used only with the last variable.",
            )
        if variable[-1] == "=":
            self.seen_mark = True
            return variable[:-1].rstrip()
        return variable

    def _validate_state(self, is_list, is_dict):
        if is_list and self.seen_list:
            self.errors.append(
                "Assignment can contain only one list variable.",
            )
        if self.seen_dict or is_dict and self.seen_any:
            self.errors.append(
                "Dictionary variable cannot be assigned with other variables.",
            )
        self.seen_list += is_list
        self.seen_dict += is_dict
        self.seen_any = True


class VariableAssigner:
    _valid_extended_attr = re.compile(r"^[_a-zA-Z]\w*$")

    def __init__(self, assignment, context):
        self._assignment = assignment
        self._context = context

    def __enter__(self):
        return self

    def __exit__(self, etype, error, tb):
        if error is None:
            return
        if not isinstance(error, ExecutionStatus):
            error = HandlerExecutionFailed(ErrorDetails(error))
        if error.can_continue(self._context):
            self.assign(error.return_value)

    def assign(self, return_value):
        context = self._context
        context.output.trace(
            lambda: f"Return: {prepr(return_value)}", write_if_flat=False
        )
        resolver = ReturnValueResolver.from_assignment(self._assignment)
        for name, items, value in resolver.resolve(return_value):
            if items:
                value = self._item_assign(name, items, value, context.variables)
            elif not self._extended_assign(name, value, context.variables):
                value = self._normal_assign(name, value, context.variables)
            context.info(format_assign_message(name, value, items))

    def _extended_assign(self, name, value, variables):
        if "." not in name or name in variables:
            return False
        base, attr = [token.strip() for token in name[2:-1].rsplit(".", 1)]
        try:
            var = variables.replace_scalar(f"${{{base}}}")
        except VariableError:
            return False
        if not (
            self._variable_supports_extended_assign(var)
            and self._is_valid_extended_attribute(attr)
        ):
            return False
        try:
            setattr(var, attr, self._handle_list_and_dict(value, name[0]))
        except Exception:
            raise VariableError(f"Setting '{name}' failed: {get_error_message()}")
        return True

    def _variable_supports_extended_assign(self, var):
        return not isinstance(var, (str, int, float))

    def _is_valid_extended_attribute(self, attr):
        return self._valid_extended_attr.match(attr) is not None

    def _parse_sequence_index(self, index):
        if isinstance(index, (int, slice)):
            return index
        if not isinstance(index, str):
            raise ValueError
        if ":" not in index:
            return int(index)
        if index.count(":") > 2:
            raise ValueError
        return slice(*[int(i) if i else None for i in index.split(":")])

    def _variable_type_supports_item_assign(self, var):
        return hasattr(var, "__setitem__") and callable(var.__setitem__)

    def _raise_cannot_set_type(self, value, expected):
        value_type = type_name(value)
        raise VariableError(f"Expected {expected}-like value, got {value_type}.")

    def _handle_list_and_dict(self, value, identifier):
        if identifier == "@":
            if not is_list_like(value):
                self._raise_cannot_set_type(value, "list")
            value = list(value)
        if identifier == "&":
            if not is_dict_like(value):
                self._raise_cannot_set_type(value, "dictionary")
            value = DotDict(value)
        return value

    def _item_assign(self, name, items, value, variables):
        *nested, item = items
        decorated_nested_items = "".join(f"[{item}]" for item in nested)
        var = variables.replace_scalar(f"${name[1:]}{decorated_nested_items}")
        if not self._variable_type_supports_item_assign(var):
            raise VariableError(
                f"Variable '{name}{decorated_nested_items}' is {type_name(var)} "
                f"and does not support item assignment."
            )
        selector = variables.replace_scalar(item)
        if isinstance(var, MutableSequence):
            try:
                selector = self._parse_sequence_index(selector)
            except ValueError:
                pass
        try:
            var[selector] = self._handle_list_and_dict(value, name[0])
        except (IndexError, TypeError, Exception):
            raise VariableError(
                f"Setting value to {type_name(var)} variable "
                f"'{name}{decorated_nested_items}' at index [{item}] failed: "
                f"{get_error_message()}"
            )
        return value

    def _normal_assign(self, name, value, variables):
        try:
            variables[name] = value
        except DataError as err:
            raise VariableError(f"Setting variable '{name}' failed: {err}")
        # Always return the actually assigned value.
        return value if name[0] == "$" else variables[name]


class ReturnValueResolver:

    @classmethod
    def from_assignment(cls, assignment):
        if not assignment:
            return NoReturnValueResolver()
        if len(assignment) == 1:
            return OneReturnValueResolver(assignment[0])
        if any(a[0] == "@" for a in assignment):
            return ScalarsAndListReturnValueResolver(assignment)
        return ScalarsOnlyReturnValueResolver(assignment)

    def resolve(self, return_value):
        raise NotImplementedError

    def _split_assignment(self, assignment):
        from robot.running import TypeInfo

        match = search_variable(assignment, parse_type=True)
        info = TypeInfo.from_variable(match) if match.type else None
        return match.name, info, match.items

    def _convert(self, return_value, type_info):
        if not type_info:
            return return_value
        return type_info.convert(return_value, kind="Return value")


class NoReturnValueResolver(ReturnValueResolver):

    def resolve(self, return_value):
        return []


class OneReturnValueResolver(ReturnValueResolver):

    def __init__(self, assignment):
        self._name, self._type, self._items = self._split_assignment(assignment)

    def resolve(self, return_value):
        if return_value is None:
            identifier = self._name[0]
            return_value = {"$": None, "@": [], "&": {}}[identifier]
        return_value = self._convert(return_value, self._type)
        return [(self._name, self._items, return_value)]


class MultiReturnValueResolver(ReturnValueResolver):

    def __init__(self, assignments):
        self._names = []
        self._types = []
        self._items = []
        for assign in assignments:
            name, type_, items = self._split_assignment(assign)
            self._names.append(name)
            self._types.append(type_)
            self._items.append(items)
        self._minimum = len(assignments)

    def resolve(self, return_value):
        return_value = self._convert_to_list(return_value)
        self._validate(len(return_value))
        return self._resolve(return_value)

    def _convert_to_list(self, return_value):
        if return_value is None:
            return [None] * self._minimum
        if isinstance(return_value, str):
            self._raise_expected_list(return_value)
        try:
            return list(return_value)
        except TypeError:
            self._raise_expected_list(return_value)

    def _raise_expected_list(self, ret):
        self._raise(f"Expected list-like value, got {type_name(ret)}.")

    def _raise(self, error):
        raise VariableError(f"Cannot set variables: {error}")

    def _validate(self, return_count):
        raise NotImplementedError

    def _resolve(self, return_value):
        raise NotImplementedError


class ScalarsOnlyReturnValueResolver(MultiReturnValueResolver):

    def _validate(self, return_count):
        if return_count != self._minimum:
            self._raise(f"Expected {self._minimum} return values, got {return_count}.")

    def _resolve(self, return_value):
        return_value = [
            self._convert(rv, t) for rv, t in zip(return_value, self._types)
        ]
        return list(zip(self._names, self._items, return_value))


class ScalarsAndListReturnValueResolver(MultiReturnValueResolver):

    def __init__(self, assignments):
        super().__init__(assignments)
        self._minimum -= 1

    def _validate(self, return_count):
        if return_count < self._minimum:
            self._raise(
                f"Expected {self._minimum} or more return values, got {return_count}."
            )

    def _resolve(self, return_value):
        list_index = [a[0] for a in self._names].index("@")
        list_len = len(return_value) - len(self._names) + 1
        items_before_list = zip(
            self._names[:list_index],
            self._items[:list_index],
            return_value[:list_index],
        )
        list_items = (
            self._names[list_index],
            self._items[list_index],
            return_value[list_index : list_index + list_len],
        )
        items_after_list = zip(
            self._names[list_index + 1 :],
            self._items[list_index + 1 :],
            return_value[list_index + list_len :],
        )
        all_items = [*items_before_list, list_items, *items_after_list]
        return [
            (name, items, self._convert(value, info))
            for (name, items, value), info in zip(all_items, self._types)
        ]
