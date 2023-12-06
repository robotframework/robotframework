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

from enum import auto, Enum
from typing import TYPE_CHECKING

from robot.errors import DataError

from .context import EXECUTION_CONTEXTS

if TYPE_CHECKING:
    from .testlibraries import TestLibrary


class Scope(Enum):
    GLOBAL = auto()
    SUITE = auto()
    TEST = auto()


class ScopeManager:

    def __init__(self, library: 'TestLibrary'):
        self.library = library

    @classmethod
    def for_library(cls, library):
        manager = {Scope.GLOBAL: GlobalScopeManager,
                   Scope.SUITE: SuiteScopeManager,
                   Scope.TEST: TestScopeManager}[library.scope]
        return manager(library)

    def start_suite(self):
        pass

    def end_suite(self):
        pass

    def start_test(self):
        pass

    def end_test(self):
        pass

    def close_global_listeners(self):
        pass

    def register_listeners(self):
        if self.library.listeners:
            try:
                listeners = EXECUTION_CONTEXTS.current.output.library_listeners
                listeners.register(self.library)
            except DataError as err:
                self.library._has_listeners = False
                self.library.report_error(f"Registering listeners failed: {err}")

    def unregister_listeners(self, close=False):
        if self.library.listeners:
            listeners = EXECUTION_CONTEXTS.current.output.library_listeners
            listeners.unregister(self.library, close)


class GlobalScopeManager(ScopeManager):

    def start_suite(self):
        self.register_listeners()

    def end_suite(self):
        self.unregister_listeners()

    def close_global_listeners(self):
        self.register_listeners()
        self.unregister_listeners(close=True)


class SuiteScopeManager(ScopeManager):

    def __init__(self, library):
        super().__init__(library)
        self.instance_cache = []

    def start_suite(self):
        self.instance_cache.append(self.library._instance)
        self.library.instance = None
        self.register_listeners()

    def end_suite(self):
        self.unregister_listeners(close=True)
        self.library.instance = self.instance_cache.pop()


class TestScopeManager(SuiteScopeManager):

    def start_test(self):
        self.unregister_listeners()
        self.instance_cache.append(self.library._instance)
        self.library.instance = None
        self.register_listeners()

    def end_test(self):
        self.unregister_listeners(close=True)
        self.library.instance = self.instance_cache.pop()
        self.register_listeners()
