#  Copyright 2008-2014 Nokia Solutions and Networks
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
if sys.platform.startswith('java'):
    from java.lang import String
    from java.util import Map
else:
    String = Map = ()
try:
    from collections import Mapping
except ImportError:  # New in 2.6
    Mapping = dict
from UserDict import UserDict
from UserString import UserString


def is_str_like(item, allow_java=False):
    return (isinstance(item, (basestring, UserString)) or
            allow_java and isinstance(item, String))


def is_list_like(item):
    if is_str_like(item, allow_java=True) or is_dict_like(item, allow_java=True):
        return False
    try:
        iter(item)
    except TypeError:
        return False
    else:
        return True


def is_dict_like(item, allow_java=False):
    # TODO: allow_java is meaningless since Jython 2.7b4 because java.util.Map
    # implement collections.Mapping. Can remove that in RF 2.9.
    return (isinstance(item, (Mapping, UserDict)) or
            allow_java and isinstance(item, Map))
