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

from collections.abc import Iterable, Mapping
from collections import UserString
from io import IOBase
from os import PathLike
try:
    from types import UnionType
except ImportError:    # Python < 3.10
    UnionType = ()
from typing import Union
try:
    from typing import TypedDict
except ImportError:    # Python < 3.8
    typeddict_types = ()
else:
    typeddict_types = (type(TypedDict('Dummy', {})),)
try:
    from typing_extensions import TypedDict as ExtTypedDict
except ImportError:
    pass
else:
    typeddict_types += (type(ExtTypedDict('Dummy', {})),)

from .platform import PY_VERSION


TRUE_STRINGS = {'TRUE', 'YES', 'ON', '1'}
FALSE_STRINGS = {'FALSE', 'NO', 'OFF', '0', 'NONE', ''}


def is_integer(item):
    return isinstance(item, int)


def is_number(item):
    return isinstance(item, (int, float))


def is_bytes(item):
    return isinstance(item, (bytes, bytearray))


def is_string(item):
    return isinstance(item, str)


def is_pathlike(item):
    return isinstance(item, PathLike)


def is_list_like(item):
    if isinstance(item, (str, bytes, bytearray, UserString, IOBase)):
        return False
    return isinstance(item, Iterable)


def is_dict_like(item):
    return isinstance(item, Mapping)


def is_union(item, allow_tuple=False):
    return (isinstance(item, UnionType)
            or getattr(item, '__origin__', None) is Union
            or allow_tuple and isinstance(item, tuple))


def type_name(item, capitalize=False):
    if getattr(item, '__origin__', None):
        item = item.__origin__
    if hasattr(item, '_name') and item._name:
        # Union, Any, etc. from typing have real name in _name and __name__ is just
        # generic `SpecialForm`. Also pandas.Series has _name but it's None.
        name = item._name
    elif isinstance(item, IOBase):
        name = 'file'
    else:
        typ = type(item) if not isinstance(item, type) else item
        named_types = {str: 'string', bool: 'boolean', int: 'integer',
                       type(None): 'None', dict: 'dictionary'}
        name = named_types.get(typ, typ.__name__.strip('_'))
        # Generics from typing. With newer versions we get "real" type via __origin__.
        if PY_VERSION < (3, 7):
            if name in ('List', 'Set', 'Tuple'):
                name = name.lower()
            elif name == 'Dict':
                name = 'dictionary'
    return name.capitalize() if capitalize and name.islower() else name


def is_truthy(item):
    """Returns `True` or `False` depending is the item considered true or not.

    Validation rules:

    - If the value is a string, it is considered false if it is `'FALSE'`,
      `'NO'`, `'OFF'`, `'0'`, `'NONE'` or `''`, case-insensitively.
    - Other strings are considered true.
    - Other values are handled by using the standard `bool()` function.

    Designed to be used also by external test libraries that want to handle
    Boolean values similarly as Robot Framework itself. See also
    :func:`is_falsy`.
    """
    if is_string(item):
        return item.upper() not in FALSE_STRINGS
    return bool(item)


def is_falsy(item):
    """Opposite of :func:`is_truthy`."""
    return not is_truthy(item)
