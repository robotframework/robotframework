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

from itertools import chain

from robot.errors import DataError
from robot.utils import NormalizedDict, seq2str

from .usererrorhandler import UserErrorHandler


class HandlerStore:

    def __init__(self):
        self._normal = NormalizedDict(ignore='_')
        self._embedded = []

    def add(self, handler, embedded=False):
        if embedded:
            self._embedded.append(handler)
        elif handler.name not in self._normal:
            self._normal[handler.name] = handler
        else:
            error = DataError('Keyword with same name defined multiple times.')
            self._normal[handler.name] = UserErrorHandler(error, handler.name,
                                                          handler.libname)
            raise error

    def __iter__(self):
        return chain(self._normal.values(), self._embedded)

    def __len__(self):
        return len(self._normal) + len(self._embedded)

    def __contains__(self, name):
        if name in self._normal:
            return True
        if not self._embedded:
            return False
        return any(template.matches(name) for template in self._embedded)

    def __getitem__(self, name):
        handlers = self.get_handlers(name)
        if len(handlers) == 1:
            return handlers[0]
        if not handlers:
            raise ValueError(f"No handler with name '{name}' found.")
        names = seq2str([handler.name for handler in handlers])
        raise ValueError(f"Multiple handlers matching name '{name}' found: {names}")

    def get_handlers(self, name):
        if name in self._normal:
            return [self._normal[name]]
        return [template for template in self._embedded if template.matches(name)]
