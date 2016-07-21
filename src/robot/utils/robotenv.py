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

import os

from .encoding import system_decode as decode, system_encode as encode


def get_env_var(name, default=None):
    try:
        value = os.environ[encode(name)]
    except KeyError:
        return default
    else:
        return decode(value)


def set_env_var(name, value):
    os.environ[encode(name)] = encode(value)


def del_env_var(name):
    value = get_env_var(name)
    if value is not None:
        del os.environ[encode(name)]
    return value


def get_env_vars(upper=os.sep != '/'):
    # by default, name is upper-cased on Windows regardless interpreter
    return dict((name if not upper else name.upper(), get_env_var(name))
                for name in (decode(name) for name in os.environ))
