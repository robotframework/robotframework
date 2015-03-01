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
import sys
from collections import Mapping
from six.moves import UserDict


_WHITESPACE_REGEXP = re.compile('\s+')


def normalize(string, ignore=(), caseless=True, spaceless=True):
    """Normalizes given string according to given spec.

    By default string is turned to lower case and all whitespace is removed.
    Additional characters can be removed by giving them in `ignore` list.
    """
    if spaceless:
        string = _WHITESPACE_REGEXP.sub('', string)
    if caseless:
        string = lower(string)
        ignore = [lower(i) for i in ignore]
    for ign in ignore:
        if ign in string:  # performance optimization
            string = string.replace(ign, '')
    return string


# http://ironpython.codeplex.com/workitem/33133
if sys.platform == 'cli' and sys.version_info < (2, 7, 5):
    def lower(string):
        return ('A' + string).lower()[1:]
else:
    def lower(string):
        return string.lower()


class NormalizedDict(UserDict):
    """Custom dictionary implementation automatically normalizing keys."""

    def __init__(self, initial=None, ignore=(), caseless=True, spaceless=True):
        """Initializes with possible initial value and normalizing spec.

        Initial values can be either a dictionary or an iterable of name/value
        pairs. In the latter case items are added in the given order.

        Normalizing spec has exact same semantics as with `normalize` method.
        """
        UserDict.__init__(self)
        self._keys = {}
        self._normalize = lambda s: normalize(s, ignore, caseless, spaceless)
        if initial:
            self._add_initial(initial)

    def _add_initial(self, items):
        if hasattr(items, 'items'):
            items = items.items()
        for key, value in items:
            self[key] = value

    def update(self, dict=None, **kwargs):
        if dict:
            for key in dict:
                self[key] = dict[key]
        if kwargs:
            self.update(kwargs)

    def _add_key(self, key):
        nkey = self._normalize(key)
        self._keys.setdefault(nkey, key)
        return nkey

    def __setitem__(self, key, value):
        nkey = self._add_key(key)
        self.data[nkey] = value

    def get(self, key, default=None):
        if key in self:
            return self[key]
        return default

    def __getitem__(self, key):
        return self.data[self._normalize(key)]

    def pop(self, key, *default):
        nkey = self._normalize(key)
        self._keys.pop(nkey, *default)
        return self.data.pop(nkey, *default)

    __delitem__ = pop

    def clear(self):
        UserDict.clear(self)
        self._keys.clear()

    def has_key(self, key):
        return self._normalize(key) in self.data

    __contains__ = has_key

    def __iter__(self):
        return (self._keys[norm_key] for norm_key in sorted(self._keys))

    def keys(self):
        return list(self)

    def iterkeys(self):
        return iter(self)

    def values(self):
        return list(self.itervalues())

    def itervalues(self):
        return (self[key] for key in self)

    def items(self):
        return list(self.iteritems())

    def iteritems(self):
        return ((key, self[key]) for key in self)

    def popitem(self):
        if not self:
            raise KeyError('dictionary is empty')
        key = next(self.iterkeys())
        return key, self.pop(key)

    def copy(self):
        copy = UserDict.copy(self)
        copy._keys = self._keys.copy()
        return copy

    def __str__(self):
        return str(dict(self.items()))

    def __cmp__(self, other):
        if (isinstance(other, (Mapping, UserDict)) and
                not isinstance(other, NormalizedDict)):
            other = NormalizedDict(other)
        return UserDict.__cmp__(self, other)

    def __eq__(self, other):
        if (isinstance(other, (Mapping, UserDict)) and
                not isinstance(other, NormalizedDict)):
            other = NormalizedDict(other).data
        return self.data == other
