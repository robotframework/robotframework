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


class VariableStore(NormalizedDict):

    def __init__(self):
        NormalizedDict.__init__(self, ignore='_')

    def resolve_delayed(self, variables):
        for name, value in self.items():
            try:
                self._resolve_delayed(name, value, variables)
            except DataError:
                pass

    def _resolve_delayed(self, name, value, variables):
        if not isinstance(value, DelayedVariable):
            return value
        self[name] = value.resolve(name, variables)
        return self[name]

    def find(self, name, variables):
        return self._resolve_delayed(name, self[name], variables)
