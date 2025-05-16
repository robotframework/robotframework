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
from functools import partial
from typing import Iterator, Sequence

from robot.errors import VariableError


def search_variable(
    string: str,
    identifiers: Sequence[str] = "$@&%*",
    parse_type: bool = False,
    ignore_errors: bool = False,
) -> "VariableMatch":
    if not (isinstance(string, str) and "{" in string):
        return VariableMatch(string)
    return _search_variable(string, identifiers, parse_type, ignore_errors)


def contains_variable(string: str, identifiers: Sequence[str] = "$@&") -> bool:
    match = search_variable(string, identifiers, ignore_errors=True)
    return bool(match)


def is_variable(string: str, identifiers: Sequence[str] = "$@&") -> bool:
    match = search_variable(string, identifiers, ignore_errors=True)
    return match.is_variable()


def is_scalar_variable(string: str) -> bool:
    return is_variable(string, "$")


def is_list_variable(string: str) -> bool:
    return is_variable(string, "@")


def is_dict_variable(string: str) -> bool:
    return is_variable(string, "&")


def is_assign(
    string: str,
    identifiers: Sequence[str] = "$@&",
    allow_assign_mark: bool = False,
    allow_nested: bool = False,
    allow_items: bool = False,
) -> bool:
    match = search_variable(string, identifiers, ignore_errors=True)
    return match.is_assign(allow_assign_mark, allow_nested, allow_items)


def is_scalar_assign(
    string: str,
    allow_assign_mark: bool = False,
    allow_nested: bool = False,
    allow_items: bool = False,
) -> bool:
    return is_assign(string, "$", allow_assign_mark, allow_nested, allow_items)


def is_list_assign(
    string: str,
    allow_assign_mark: bool = False,
    allow_nested: bool = False,
    allow_items: bool = False,
) -> bool:
    return is_assign(string, "@", allow_assign_mark, allow_nested, allow_items)


def is_dict_assign(
    string: str,
    allow_assign_mark: bool = False,
    allow_nested: bool = False,
    allow_items: bool = False,
) -> bool:
    return is_assign(string, "&", allow_assign_mark, allow_nested, allow_items)


class VariableMatch:

    def __init__(
        self,
        string: str,
        identifier: "str|None" = None,
        base: "str|None" = None,
        type: "str|None" = None,
        items: "tuple[str, ...]" = (),
        start: int = -1,
        end: int = -1,
    ):
        self.string = string
        self.identifier = identifier
        self.base = base
        self.type = type
        self.items = items
        self.start = start
        self.end = end

    def resolve_base(self, variables, ignore_errors=False):
        if self.identifier:
            internal = search_variable(self.base)
            self.base = variables.replace_string(
                internal,
                custom_unescaper=unescape_variable_syntax,
                ignore_errors=ignore_errors,
            )

    @property
    def name(self) -> "str|None":
        return f"{self.identifier}{{{self.base}}}" if self.identifier else None

    @property
    def before(self) -> str:
        return self.string[: self.start] if self.identifier else self.string

    @property
    def match(self) -> "str|None":
        return self.string[self.start : self.end] if self.identifier else None

    @property
    def after(self) -> str:
        return self.string[self.end :] if self.identifier else ""

    def is_variable(self) -> bool:
        return bool(
            self.identifier
            and self.base
            and self.start == 0
            and self.end == len(self.string)
        )

    def is_scalar_variable(self) -> bool:
        return self.identifier == "$" and self.is_variable()

    def is_list_variable(self) -> bool:
        return self.identifier == "@" and self.is_variable()

    def is_dict_variable(self) -> bool:
        return self.identifier == "&" and self.is_variable()

    def is_assign(
        self,
        allow_assign_mark: bool = False,
        allow_nested: bool = False,
        allow_items: bool = False,
    ) -> bool:
        if allow_assign_mark and self.string.endswith("="):
            match = search_variable(self.string[:-1].rstrip(), ignore_errors=True)
            return match.is_assign(allow_nested=allow_nested, allow_items=allow_items)
        return (
            self.is_variable()
            and self.identifier in "$@&"
            and (allow_items or not self.items)
            and (allow_nested or not search_variable(self.base))
        )

    def is_scalar_assign(
        self,
        allow_assign_mark: bool = False,
        allow_nested: bool = False,
    ) -> bool:
        return self.identifier == "$" and self.is_assign(
            allow_assign_mark, allow_nested
        )

    def is_list_assign(
        self,
        allow_assign_mark: bool = False,
        allow_nested: bool = False,
    ) -> bool:
        return self.identifier == "@" and self.is_assign(
            allow_assign_mark, allow_nested
        )

    def is_dict_assign(
        self,
        allow_assign_mark: bool = False,
        allow_nested: bool = False,
    ) -> bool:
        return self.identifier == "&" and self.is_assign(
            allow_assign_mark, allow_nested
        )

    def __bool__(self) -> bool:
        return self.identifier is not None

    def __str__(self) -> str:
        if not self:
            return "<no match>"
        type = f": {self.type}" if self.type else ""
        items = "".join([f"[{i}]" for i in self.items]) if self.items else ""
        return f"{self.identifier}{{{self.base}{type}}}{items}"


def _search_variable(
    string: str,
    identifiers: Sequence[str],
    parse_type: bool = False,
    ignore_errors: bool = False,
) -> VariableMatch:
    start = _find_variable_start(string, identifiers)
    if start < 0:
        return VariableMatch(string)

    match = VariableMatch(string, identifier=string[start], start=start)
    left_brace, right_brace = "{", "}"
    open_braces = 1
    escaped = False
    items = []
    indices_and_chars = enumerate(string[start + 2 :], start=start + 2)

    for index, char in indices_and_chars:
        if char == right_brace and not escaped:
            open_braces -= 1
            if open_braces == 0:
                _, next_char = next(indices_and_chars, (-1, None))
                # Parsing name.
                if left_brace == "{":
                    match.base = string[start + 2 : index]
                    if next_char != "[" or match.identifier not in "$@&":
                        match.end = index + 1
                        break
                    left_brace, right_brace = "[", "]"
                # Parsing items.
                else:
                    items.append(string[start + 1 : index])
                    if next_char != "[":
                        match.end = index + 1
                        match.items = tuple(items)
                        break
                start = index + 1  # Start of the next item.
                open_braces = 1
        elif char == left_brace and not escaped:
            open_braces += 1
        else:
            escaped = False if char != "\\" else not escaped

    if open_braces:
        if ignore_errors:
            return VariableMatch(string)
        incomplete = string[match.start :]
        if left_brace == "{":
            raise VariableError(f"Variable '{incomplete}' was not closed properly.")
        raise VariableError(f"Variable item '{incomplete}' was not closed properly.")

    if parse_type and ": " in match.base:
        match.base, match.type = match.base.rsplit(": ", 1)

    return match


def _find_variable_start(string, identifiers):
    index = 1
    while True:
        index = string.find("{", index) - 1
        if index < 0:
            return -1
        if string[index] in identifiers and _not_escaped(string, index):
            return index
        index += 2


def _not_escaped(string, index):
    escaped = False
    while index > 0 and string[index - 1] == "\\":
        index -= 1
        escaped = not escaped
    return not escaped


def unescape_variable_syntax(item):

    def handle_escapes(match):
        escapes, text = match.groups()
        if len(escapes) % 2 == 1 and starts_with_variable_or_curly(text):
            return escapes[1:]
        return escapes

    def starts_with_variable_or_curly(text):
        if text[0] in "{}":
            return True
        match = search_variable(text, ignore_errors=True)
        return match and match.start == 0

    return re.sub(r"(\\+)(?=(.+))", handle_escapes, item)


class VariableMatches:

    def __init__(
        self,
        string: str,
        identifiers: Sequence[str] = "$@&%",
        parse_type: bool = False,
        ignore_errors: bool = False,
    ):
        self.string = string
        self.search_variable = partial(
            search_variable,
            identifiers=identifiers,
            parse_type=parse_type,
            ignore_errors=ignore_errors,
        )

    def __iter__(self) -> Iterator[VariableMatch]:
        remaining = self.string
        while True:
            match = self.search_variable(remaining)
            if not match:
                break
            remaining = match.after
            yield match

    def __len__(self) -> int:
        return sum(1 for _ in self)

    def __bool__(self) -> bool:
        return bool(self.search_variable(self.string))
