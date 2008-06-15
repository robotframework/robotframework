#  Copyright 2008 Nokia Siemens Networks Oyj
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
import sys
import re
from UserDict import UserDict
if os.name == 'java':
    import java.io

import misc


_WHITESPACE_REGEXP = re.compile('\s+')
if os.sep == '\\':
    _CASE_INSENSITIVE_FILESYSTEM = True
else:
    try:
        _CASE_INSENSITIVE_FILESYSTEM = os.listdir('/tmp') == os.listdir('/TMP')
    except:
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


def normalize_list(list, ignore=[], caseless=True, spaceless=True):
    """Normalize list (w/ default values), sort it and remove empty values"""
    d = NormalizedDict(ignore=ignore, caseless=caseless, spaceless=spaceless)
    for item in list:
        d[item] = 1
    ret = [ k for k in d.keys() if k != '' ]
    ret.sort()
    return ret
    

def normpath(path, normcase=True):
    """Returns path in normalized and absolute format.
    
    On case-insensitive file systems the path is also casenormalized
    (if normcase is True).
    """ 
    if misc.is_url(path):
        return path
    path = _absnorm(path)
    if normcase and _CASE_INSENSITIVE_FILESYSTEM:
        path = path.lower()
    if os.sep == '\\' and len(path) == 2 and path[1] == ':':
        path += '\\'
    return path

def _absnorm(path):
    if os.sep == '\\' and len(path) == 2 and path[1] == ':':
        return path + '\\'
    # Jython (at least 2.2b1) may raise IOException if path invalid because it
    # uses java.io.File.getCanonicalPath. java.io.File.getAbsolutePath is safe.
    try:
        path = os.path.abspath(path)
    except:
        path = java.io.File(path).getAbsolutePath()
    return os.path.normpath(path)

def _is_case_insensitive_filesystem():
    return os.sep == '\\' or 'cygwin' in sys.platform or \
                    'darwin' in sys.platform


class NormalizedDict(UserDict):
    
    def __init__(self, initial={}, ignore=[], caseless=True, spaceless=True):
        UserDict.__init__(self)
        self._ignore = ignore
        self._caseless = caseless
        self._spaceless = spaceless
        for key, value in initial.items():
            self.__setitem__(key, value)
    
    def __setitem__(self, key, value):
        self.data[self._normalize(key)] = value

    set = __setitem__

    def __getitem__(self, key):
        return self.data[self._normalize(key)]    
    
    def get(self, key, default=None):
        try:
            return self.__getitem__(key)
        except KeyError:
            return default

    def has_key(self, key):
        return self.data.has_key(self._normalize(key))
    
    __contains__ = has_key

    def _normalize(self, item):
        return normalize(item, self._ignore, self._caseless, self._spaceless) 
