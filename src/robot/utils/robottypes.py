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

import sys

PY3 = sys.version_info[0] == 3

from .platform import IRONPYTHON
from collections import Mapping
if PY3:
    from collections import UserList, UserDict, UserString
else:
    from UserList import UserList
    from UserDict import UserDict
    from UserString import UserString, MutableString
if PY3:
    long = int
    bytes = bytes
    unicode = str
else:
    long = long
    bytes = str if not IRONPYTHON else bytes
    unicode = unicode
try:
    from java.lang import String
except ImportError:
    String = ()


def type_name(item):
    cls = item.__class__ if hasattr(item, '__class__') else type(item)
    named_types = {str: 'string', unicode: 'string', bool: 'boolean',
                   int: 'integer', long: 'integer', type(None): 'None',
                   dict: 'dictionary'}
    return named_types.get(cls, cls.__name__)


def is_str_like(item):
    return isinstance(item, (basestring, UserString, String))


if PY3:
    _integer = int
    _number = int, float
    _bytes = bytes
    _bytes_like = bytes, bytearray
    _string = str
    _string_like = str, UserString
else:
    _integer = int, long
    _number = int, long, float
    _bytes = str
    _bytes_like = str, bytearray, UserString, MutableString, String
    _string = basestring
    _string_like = basestring, UserString, MutableString, String


def is_integer(item):
    return isinstance(item, _integer)

def is_number(item):
    return isinstance(item, _number)

def is_bytes(item):
    return isinstance(item, _bytes)

def is_bytes_like(item):
    return isinstance(item, _bytes_like)

def is_string(item):
    return isinstance(item, _string)

def is_string_like(item):
    return isinstance(item, _string_like)

if PY3:
    is_unicode = is_string
    is_unicode_like = is_string_like
else:
    def is_unicode(item):
        return isinstance(item, unicode)

    is_unicode_like = is_unicode


def is_list_like(item):
    if is_str_like(item):
        return False
    try:
        iter(item)
    except TypeError:
        return False
    else:
        return True


def is_dict_like(item):
    return isinstance(item, (Mapping, UserDict))


def is_truthy(item):
    if isinstance(item, basestring):
        return item.upper() not in ('FALSE', 'NO', '')
    return bool(item)


def is_falsy(item):
    return not is_truthy(item)
