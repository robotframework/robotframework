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

from collections import Mapping
from UserDict import UserDict
from UserString import UserString
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
