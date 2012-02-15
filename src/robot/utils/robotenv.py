#  Copyright 2008-2011 Nokia Siemens Networks Oyj
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

from .encoding import decode_from_system, encode_to_system


def get_env_var(name, default=None):
    try:
        value = os.environ[_encode(name)]
    except KeyError:
        return default
    else:
        return _decode(value)

def set_env_var(name, value):
    os.environ[_encode(name)] = _encode(value)

def del_env_var(name):
    try:
        return os.environ.pop(_encode(name))
    except KeyError:
        return None

def _encode(var):
    if isinstance(var, str):
        return var
    if isinstance(var, unicode):
        return encode_to_system(var)
    return str(var)

def _decode(var):
    return decode_from_system(var)
