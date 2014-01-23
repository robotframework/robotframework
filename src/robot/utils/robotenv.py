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

import os
import sys

from .encoding import decode_from_system, encode_to_system
from .unic import unic


def get_env_var(name, default=None):
    value = _get_env_var_from_java(name)
    if value is not None:
        return value
    try:
        value = os.environ[_encode(name)]
    except KeyError:
        return default
    else:
        return _decode(value)

def set_env_var(name, value):
    os.environ[_encode(name)] = _encode(value)

def del_env_var(name):
    # cannot use os.environ.pop() due to http://bugs.python.org/issue1287
    value = get_env_var(name)
    if value is not None:
        del os.environ[_encode(name)]
    return value

def get_env_vars(upper=os.sep != '/'):
    # by default, name is upper-cased on Windows regardless interpreter
    return dict((name if not upper else name.upper(), get_env_var(name))
                for name in (_decode(name) for name in os.environ))


def _encode(var):
    if isinstance(var, str):
        return var
    if isinstance(var, unicode):
        return encode_to_system(var)
    return str(var)

def _decode(var):
    return decode_from_system(var, can_be_from_java=False)

# Jython hack below needed due to http://bugs.jython.org/issue1841
if not sys.platform.startswith('java'):
    def _get_env_var_from_java(name):
        return None

else:
    from java.lang import String, System

    def _get_env_var_from_java(name):
        name = name if isinstance(name, basestring) else unic(name)
        value_set_before_execution = System.getenv(name)
        if value_set_before_execution is None:
            return None
        current_value = String(os.environ[name]).toString()
        if value_set_before_execution != current_value:
            return None
        return value_set_before_execution
