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

import numbers
from collections.abc import Mapping, Sequence
from operator import eq, ge, gt, le, lt
from typing import Any

from .robottypes import type_name


def safe_sort_key(item: Any) -> "tuple[str, Any]":
    """Return a key for sorting objects that may not be comparable.

    The key is a two-tuple containing a type name and a normalized value.
    The type name makes objects of different types comparable and the
    normalized value is used to sort objects of the same type. Values are
    normalized recursively for mappings, sequences and sets.

    This function never fails. For natively sortable values the resulting
    order is the same as when using ``sorted`` without a key function.
    """
    if item is None:
        return "NoneType", 0
    if isinstance(item, numbers.Complex) and not isinstance(item, numbers.Real):
        return "numbers.Complex", (item.real, item.imag)
    if isinstance(item, numbers.Number):
        return "numbers.Number", item
    if isinstance(item, Mapping):
        return "collections.abc.Mapping", tuple(
            sorted(
                (
                    (safe_sort_key(key), safe_sort_key(value))
                    for key, value in item.items()
                ),
                key=lambda pair: pair[0],
            )
        )
    if isinstance(item, str):
        return "builtins.str", item
    if isinstance(item, (bytes, bytearray)):
        return "builtins.bytes", bytes(item)
    type_ = f"{type(item).__module__}.{type(item).__qualname__}"
    if isinstance(item, Sequence):
        return type_, tuple(safe_sort_key(value) for value in item)
    if isinstance(item, (set, frozenset)):
        return type_, tuple(sorted(safe_sort_key(value) for value in item))
    try:
        lt(item, item)
    except Exception:
        try:
            item = repr(item)
        except Exception:
            item = ""
    return type_, item


class Sortable:
    """Base class for sorting based self._sort_key"""

    _sort_key = NotImplemented

    def __test(self, operator, other, require_sortable=True):
        if isinstance(other, Sortable):
            return operator(self._sort_key, other._sort_key)
        if not require_sortable:
            return False
        raise TypeError(f"Cannot sort '{type_name(self)}' and '{type_name(other)}'.")

    def __eq__(self, other):
        return self.__test(eq, other, require_sortable=False)

    def __lt__(self, other):
        return self.__test(lt, other)

    def __le__(self, other):
        return self.__test(le, other)

    def __gt__(self, other):
        return self.__test(gt, other)

    def __ge__(self, other):
        return self.__test(ge, other)

    def __hash__(self):
        return hash(self._sort_key)
