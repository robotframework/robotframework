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

from collections import Mapping, UserString
from io import IOBase

from .platform import RERAISED_EXCEPTIONS


def is_integer(item):
    return isinstance(item, int)


def is_number(item):
    return isinstance(item, (int, float))


def is_bytes(item):
    return isinstance(item, (bytes, bytearray))


def is_string(item):
    return isinstance(item, str)


def is_unicode(item):
    return isinstance(item, str)


def is_list_like(item):
    if isinstance(item, (str, bytes, bytearray, UserString, IOBase)):
        return False
    try:
        iter(item)
    except RERAISED_EXCEPTIONS:
        raise
    except:
        return False
    else:
        return True


def is_dict_like(item):
    return isinstance(item, Mapping)


def type_name(item):
    if isinstance(item, IOBase):
        return 'file'
    cls = item.__class__ if hasattr(item, '__class__') else type(item)
    named_types = {str: 'string', bool: 'boolean', int: 'integer',
                   type(None): 'None', dict: 'dictionary', type: 'class'}
    return named_types.get(cls, cls.__name__)
