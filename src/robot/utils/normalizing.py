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
from collections.abc import Iterable, Iterator, Mapping, Sequence
from typing import MutableMapping, TypeVar

V = TypeVar("V")
Self = TypeVar("Self", bound="NormalizedDict")


def normalize(
    string: str,
    ignore: "Sequence[str]" = (),
    caseless: bool = True,
    spaceless: bool = True,
) -> str:
    """Normalize the ``string`` according to the given spec.

    By default, string is turned to lower case (actually case-folded) and all
    whitespace is removed. Additional characters can be removed by giving them
    in ``ignore`` list.
    """
    if spaceless:
        string = "".join(string.split())
    if caseless:
        string = string.casefold()
        ignore = [i.casefold() for i in ignore]
    # both if statements below enhance performance a little
    if ignore:
        for ign in ignore:
            if ign in string:
                string = string.replace(ign, "")
    return string


def normalize_whitespace(string):
    return re.sub(r"\s", " ", string, flags=re.UNICODE)


class NormalizedDict(MutableMapping[str, V]):
    """Custom dictionary implementation automatically normalizing keys."""

    def __init__(
        self,
        initial: "Mapping[str, V]|Iterable[tuple[str, V]]|None" = None,
        ignore: "Sequence[str]" = (),
        caseless: bool = True,
        spaceless: bool = True,
    ):
        """Initialized with possible initial value and normalizing spec.

        Initial values can be either a dictionary or an iterable of name/value
        pairs.

        Normalizing spec has exact same semantics as with the :func:`normalize`
        function.
        """
        self._data: "dict[str, V]" = {}
        self._keys: "dict[str, str]" = {}
        self._normalize = lambda s: normalize(s, ignore, caseless, spaceless)
        if initial:
            self.update(initial)

    @property
    def normalized_keys(self) -> "tuple[str, ...]":
        return tuple(self._keys)

    def __getitem__(self, key: str) -> V:
        return self._data[self._normalize(key)]

    def __setitem__(self, key: str, value: V):
        norm_key = self._normalize(key)
        self._data[norm_key] = value
        self._keys.setdefault(norm_key, key)

    def __delitem__(self, key: str):
        norm_key = self._normalize(key)
        del self._data[norm_key]
        del self._keys[norm_key]

    def __iter__(self) -> "Iterator[str]":
        return (self._keys[norm_key] for norm_key in sorted(self._keys))

    def __len__(self) -> int:
        return len(self._data)

    def __str__(self) -> str:
        items = ", ".join(f"{key!r}: {self[key]!r}" for key in self)
        return f"{{{items}}}"

    def __repr__(self) -> str:
        name = type(self).__name__
        params = str(self) if self else ""
        return f"{name}({params})"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Mapping):
            return False
        if not isinstance(other, NormalizedDict):
            other = NormalizedDict(other)
        return self._data == other._data

    def copy(self: Self) -> Self:
        copy = type(self)()
        copy._data = self._data.copy()
        copy._keys = self._keys.copy()
        copy._normalize = self._normalize
        return copy

    # Speed-ups. Following methods are faster than default implementations.

    def __contains__(self, key: str) -> bool:
        return self._normalize(key) in self._data

    def clear(self):
        self._data.clear()
        self._keys.clear()
