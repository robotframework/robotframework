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

from collections import Iterable, Mapping, MutableMapping, Sequence
from UserDict import UserDict
from UserString import UserString
from types import ClassType, NoneType

try:
    from java.lang import String
except ImportError:
    String = ()

from .platform import RERAISED_EXCEPTIONS


def is_integer(item):
    return isinstance(item, (int, long))


def is_number(item):
    return isinstance(item, (int, long, float))


def is_bytes(item):
    return isinstance(item, (bytes, bytearray))


def is_string(item):
    # Returns False with `b'bytes'` on IronPython on purpose. Results of
    # `isinstance(item, basestring)` would depend on IronPython 2.7.x version.
    return isinstance(item, (str, unicode))


def is_unicode(item):
    return isinstance(item, unicode)


def is_pathlike(item):
    return False


def is_list_like(item):
    if isinstance(item, (str, unicode, bytes, bytearray, UserString, String,
                         file)):
        return False
    return isinstance(item, (Iterable, UserDict))


def is_dict_like(item):
    return isinstance(item, (Mapping, UserDict))


def type_name(item, capitalize=False):
    if isinstance(item, (type, ClassType)):
        typ = item
    elif hasattr(item, '__class__'):
        typ = item.__class__
    else:
        typ = type(item)
    named_types = {str: 'string', unicode: 'string', bool: 'boolean',
                   int: 'integer', long: 'integer', NoneType: 'None',
                   dict: 'dictionary'}
    name = named_types.get(typ, typ.__name__.strip('_'))
    return name.capitalize() if capitalize and name.islower() else name
