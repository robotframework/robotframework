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
from collections.abc import Mapping, MutableMapping, Sequence
from typing import overload


@overload
def normalize(string: str, ignore: 'Sequence[str]' = (), caseless: bool = True,
              spaceless: bool = True) -> str:
    ...

@overload
def normalize(string: bytes, ignore: 'Sequence[bytes]' = (), caseless: bool = True,
              spaceless: bool = True) -> bytes:
    ...

def normalize(string, ignore=(), caseless=True, spaceless=True):
    """Normalizes given string according to given spec.

    By default string is turned to lower case and all whitespace is removed.
    Additional characters can be removed by giving them in ``ignore`` list.
    """
    empty = '' if isinstance(string, str) else b''
    if isinstance(ignore, bytes):
        # Iterating bytes in Python3 yields integers.
        ignore = [bytes([i]) for i in ignore]
    if spaceless:
        string = empty.join(string.split())
    if caseless:
        string = string.lower()
        ignore = [i.lower() for i in ignore]
    # both if statements below enhance performance a little
    if ignore:
        for ign in ignore:
            if ign in string:
                string = string.replace(ign, empty)
    return string


def normalize_whitespace(string):
    return re.sub(r'\s', ' ', string, flags=re.UNICODE)


class NormalizedDict(MutableMapping):
    """Custom dictionary implementation automatically normalizing keys."""

    def __init__(self, initial=None, ignore=(), caseless=True, spaceless=True):
        """Initialized with possible initial value and normalizing spec.

        Initial values can be either a dictionary or an iterable of name/value
        pairs. In the latter case items are added in the given order.

        Normalizing spec has exact same semantics as with the :func:`normalize`
        function.
        """
        self._data = {}
        self._keys = {}
        self._normalize = lambda s: normalize(s, ignore, caseless, spaceless)
        if initial:
            items = initial.items() if hasattr(initial, 'items') else initial
            for key, value in items:
                self[key] = value

    @property
    def normalized_keys(self):
        return self._keys

    def __getitem__(self, key):
        return self._data[self._normalize(key)]

    def __setitem__(self, key, value):
        norm_key = self._normalize(key)
        self._data[norm_key] = value
        self._keys.setdefault(norm_key, key)

    def __delitem__(self, key):
        norm_key = self._normalize(key)
        del self._data[norm_key]
        del self._keys[norm_key]

    def __iter__(self):
        return (self._keys[norm_key] for norm_key in sorted(self._keys))

    def __len__(self):
        return len(self._data)

    def __str__(self):
        items = ', '.join(f'{key!r}: {self[key]!r}' for key in self)
        return f'{{{items}}}'

    def __repr__(self):
        name = type(self).__name__
        params = str(self) if self else ''
        return f'{name}({params})'

    def __eq__(self, other):
        if not isinstance(other, Mapping):
            return False
        if not isinstance(other, NormalizedDict):
            other = NormalizedDict(other)
        return self._data == other._data

    def copy(self):
        copy = NormalizedDict()
        copy._data = self._data.copy()
        copy._keys = self._keys.copy()
        copy._normalize = self._normalize
        return copy

    # Speed-ups. Following methods are faster than default implementations.

    def __contains__(self, key):
        return self._normalize(key) in self._data

    def clear(self):
        self._data.clear()
        self._keys.clear()
