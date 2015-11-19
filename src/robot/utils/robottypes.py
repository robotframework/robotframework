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

from .platform import PY2


if PY2:
    from .robottypes2 import (is_bytes, is_dict_like, is_integer, is_list_like,
                              is_number, is_string, is_unicode, type_name)

else:
    from .robottypes3 import (is_bytes, is_dict_like, is_integer, is_list_like,
                              is_number, is_string, is_unicode, type_name)


def is_truthy(item):
    if is_string(item):
        return item.upper() not in ('FALSE', 'NO', '')
    return bool(item)


def is_falsy(item):
    return not is_truthy(item)
