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

from .platform import PY2


if PY2:
    from .robottypes2 import (is_bytes, is_dict_like, is_integer, is_list_like,
                              is_number, is_string, is_unicode, type_name)

else:
    from .robottypes3 import (is_bytes, is_dict_like, is_integer, is_list_like,
                              is_number, is_string, is_unicode, type_name)


def is_truthy(item):
    """Returns `True` or `False` depending is the item considered true or not.

    Validation rules:

    - If the value is a string, it is considered `True` if it is not `FALSE`,
      `NO` or and empty string, case-insensitively.
    - Other values are handled by using the standard `bool()` function.

    Designed to be used also by external test libraries that want to handle
    Boolean values similarly as Robot Framework itself. See also
    :func:`is_falsy` and :func:`is_noney`.
    """
    if is_string(item):
        return item.upper() not in ('FALSE', 'NO', '')
    return bool(item)


def is_falsy(item):
    """Opposite of :func:`is_truthy`."""
    return not is_truthy(item)


def is_noney(item):
    """Returns `True` or `False` depending is the item considered `None` or not.

    Validation rules:

    - If the value is a string, it is considered `None` if it is equal to
      `NONE`, case-insensitively.
    - Otherwise the value is considerd `None` only if it is the actual `None`.

    Designed to be used also by external test libraries that want to handle
    `NONE` similarly as Robot Framework itself. New in Robot Framework 3.0.3.
    See also :func:`is_truthy` and :func:`is_falsy`.
    """
    return item is None or is_string(item) and item.upper() == 'NONE'
