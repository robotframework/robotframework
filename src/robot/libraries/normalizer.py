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
from collections.abc import Mapping, Sequence
from typing import Any, Literal, Union

IgnoreCase = Union[Literal["KEY", "KEYS", "VALUE", "VALUES"], bool]
StripSpaces = Union[Literal["LEADING", "TRAILING"], bool]


class Normalizer:

    def __init__(
        self,
        ignore_case: IgnoreCase = False,
        strip_spaces: StripSpaces = False,
        collapse_spaces: bool = False,
        ignore_order: bool = False,
        ignore_keys: "Sequence | None" = None,
    ):
        self.ignore_case = bool(ignore_case)
        if isinstance(ignore_case, str):
            self.ignore_key_case = ignore_case.upper() not in ("VALUE", "VALUES")
            self.ignore_value_case = ignore_case.upper() not in ("KEY", "KEYS")
        else:
            self.ignore_key_case = self.ignore_value_case = self.ignore_case
        if isinstance(strip_spaces, str):
            self.strip_leading_spaces = strip_spaces.upper() != "TRAILING"
            self.strip_trailing_spaces = strip_spaces.upper() != "LEADING"
        else:
            self.strip_leading_spaces = self.strip_trailing_spaces = bool(strip_spaces)
        self.collapse_spaces = collapse_spaces
        self.ignore_order = ignore_order
        self.ignore_keys = self._parse_ignored_keys(ignore_keys)

    def _parse_ignored_keys(self, ignore_keys: "Sequence | None") -> set:
        if not ignore_keys:
            return set()
        return {self.normalize_key(k) for k in ignore_keys}

    def normalize(self, value: Any, mapping_to_list: bool = False) -> Any:
        if not self:
            return value
        if isinstance(value, str):
            return self.normalize_string(value)
        if isinstance(value, (bytes, bytearray)):
            return self.normalize_bytes(value)
        if isinstance(value, Mapping):
            if mapping_to_list:
                return self.normalize_list(list(value))
            return self.normalize_dict(value)
        if isinstance(value, Sequence):
            return self.normalize_list(value)
        return value

    def normalize_string(self, value: str) -> str:
        if self.ignore_case:
            value = value.casefold()
        if self.strip_leading_spaces:
            value = value.lstrip()
        if self.strip_trailing_spaces:
            value = value.rstrip()
        if self.collapse_spaces:
            value = re.sub(r"\s+", " ", value)
        return value

    def normalize_bytes(self, value: "bytes | bytearray") -> "bytes | bytearray":
        if self.ignore_case:
            value = value.lower()
        if self.strip_leading_spaces:
            value = value.lstrip()
        if self.strip_trailing_spaces:
            value = value.rstrip()
        if self.collapse_spaces:
            value = re.sub(rb"\s+", b" ", value)
        return value

    def normalize_list(self, value: Sequence) -> Sequence:
        cls = type(value)
        value_list = [self.normalize(v) for v in value]
        if self.ignore_order:
            value_list = sorted(value_list)
        return self._try_to_preserve_type(value_list, cls)

    def _try_to_preserve_type(self, value: Any, cls: type) -> Any:
        # Try to preserve original type. Most importantly, preserve tuples to
        # allow using them as dictionary keys.
        try:
            return cls(value)
        except TypeError:
            return value

    def normalize_dict(self, value: Mapping) -> Mapping:
        cls = type(value)
        result = {}
        for key in value:
            normalized = self.normalize_key(key)
            if normalized in self.ignore_keys:
                continue
            if normalized in result:
                raise AssertionError(
                    f"Dictionary {value} contains multiple keys that are normalized "
                    f"to '{normalized}'. Try normalizing only dictionary values like "
                    f"'ignore_case=values'."
                )
            result[normalized] = self.normalize_value(value[key])
        return self._try_to_preserve_type(result, cls)

    def normalize_key(self, key: object) -> object:
        ignore_case, self.ignore_case = self.ignore_case, self.ignore_key_case
        try:
            return self.normalize(key)
        finally:
            self.ignore_case = ignore_case

    def normalize_value(self, value: object) -> object:
        ignore_case, self.ignore_case = self.ignore_case, self.ignore_value_case
        try:
            return self.normalize(value)
        finally:
            self.ignore_case = ignore_case

    def __bool__(self) -> bool:
        return bool(
            self.ignore_case
            or self.strip_leading_spaces
            or self.strip_trailing_spaces
            or self.collapse_spaces
            or self.ignore_order
            or getattr(self, "ignore_keys", False)
        )
