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

from six import PY3, string_types, text_type as unicode
if PY3:
    long = int

from collections import Mapping
from six.moves import UserDict, UserString
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
    return isinstance(item, string_types + (UserString, String))


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
