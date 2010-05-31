#  Copyright 2008-2010 Nokia Siemens Networks Oyj
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

import os
import re
from UserDict import UserDict


_WHITESPACE_REGEXP = re.compile('\s+')
if os.sep == '\\':
    _CASE_INSENSITIVE_FILESYSTEM = True
else:
    try:
        _CASE_INSENSITIVE_FILESYSTEM = os.listdir('/tmp') == os.listdir('/TMP')
    except OSError:
        _CASE_INSENSITIVE_FILESYSTEM = False


def normalize(string, ignore=[], caseless=True, spaceless=True):
    if spaceless:
        string = _WHITESPACE_REGEXP.sub('', string)
    if caseless:
        string = string.lower()
        ignore = [ ign.lower() for ign in ignore ]
    for ign in ignore:
        string = string.replace(ign, '')
    return string


def normalize_tags(tags):
    """Removes duplicates (normalized) and empty tags and sorts tags"""
    ret = []
    dupes = NormalizedDict({'': 1})
    for tag in tags:
        if not dupes.has_key(tag):
            ret.append(tag)
            dupes[tag] = 1
    ret.sort(lambda x, y: cmp(normalize(x), normalize(y)))
    return ret


def normpath(path, normcase=True):
    """Returns path in normalized and absolute format.

    On case-insensitive file systems the path is also casenormalized
    (if normcase is True).
    """
    path = _abspath(path)
    if normcase and _CASE_INSENSITIVE_FILESYSTEM:
        path = path.lower()
    return path

def _abspath(path):
    pathlen = len(path)
    # Return 'x:\' both when the given path is 'x:\' and 'x:'. Notice that
    # os.path.abspath('x:') returns the current dir (we don't want that) and
    # with Jython os.path.abspath('x:\') returns 'x:' (don't want that either)
    if os.sep == '\\' and pathlen > 1 and path[1] == ':':
        if pathlen == 2:
            return path + '\\'
        if pathlen == 3:
            return path
    return os.path.abspath(path)


class NormalizedDict(UserDict):

    def __init__(self, initial={}, ignore=[], caseless=True, spaceless=True):
        UserDict.__init__(self)
        self._keys = {}
        self._normalize = lambda s: normalize(s, ignore, caseless, spaceless)
        for key, value in initial.items():
            self[key] = value

    def __setitem__(self, key, value):
        nkey = self._normalize(key)
        self._keys.setdefault(nkey, key)
        self.data[nkey] = value

    set = __setitem__

    def __getitem__(self, key):
        return self.data[self._normalize(key)]

    def __delitem__(self, key):
        nkey = self._normalize(key)
        del self.data[nkey]
        del self._keys[nkey]

    def get(self, key, default=None):
        try:
            return self.__getitem__(key)
        except KeyError:
            return default

    def has_key(self, key):
        return self.data.has_key(self._normalize(key))

    __contains__ = has_key

    def keys(self):
        return self._keys.values()

    def items(self):
        return [ (key, self[key]) for key in self.keys() ]

    def copy(self):
        copy = UserDict.copy(self)
        copy._keys = self._keys.copy()
        return copy

    def __str__(self):
        return str(dict(self.items()))
