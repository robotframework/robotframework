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

from robot.errors import DataError
from robot.utils import NormalizedDict

from .tablesetter import DelayedVariable


class VariableStore(object):

    def __init__(self, variables):
        self.store = NormalizedDict(ignore='_')
        self._variables = variables

    def resolve_delayed(self):
        for name, value in self.store.items():
            try:
                self._resolve_delayed(name, value)
            except DataError:
                pass

    def _resolve_delayed(self, name, value):
        if not isinstance(value, DelayedVariable):
            return value
        self.store[name] = value.resolve(name, self._variables)
        return self.store[name]

    def find(self, name):
        return self._resolve_delayed(name, self.store[name])

    def clear(self):
        self.store.clear()

    def add(self, name, value, overwrite=True):
        if overwrite or name not in self.store:
            self.store[name] = value

    def remove(self, name):
        if name in self.store:
            self.store.pop(name)

    def __len__(self):
        return len(self.store)

    def __iter__(self):
        return iter(self.store)

    def __contains__(self, name):
        return name in self.store
