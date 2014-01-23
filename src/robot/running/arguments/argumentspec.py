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


class ArgumentSpec(object):

    def __init__(self, name, type='Keyword', positional=None, defaults=None,
                 varargs=None, kwargs=None, supports_named=True):
        self.name = name
        self.type = type
        self.positional = positional or []
        self.defaults = defaults or []
        self.varargs = varargs
        self.kwargs = kwargs
        self.supports_named = supports_named

    @property
    def minargs(self):
        return len(self.positional) - len(self.defaults)

    @property
    def maxargs(self):
        return len(self.positional) if not self.varargs else sys.maxint
