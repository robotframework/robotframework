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

import inspect

from robot.utils import normalize, unic


def LibraryScope(libcode, library):
    scope = _get_scope(libcode)
    if scope == 'global':
        return GlobalScope(library)
    if scope == 'testsuite':
        return TestSuiteScope(library)
    return TestCaseScope(library)


def _get_scope(libcode):
    if inspect.ismodule(libcode):
        return 'global'
    scope = getattr(libcode, 'ROBOT_LIBRARY_SCOPE', '')
    return normalize(unic(scope), ignore='_')


class GlobalScope(object):
    is_global = True

    def __init__(self, library):
        self._register_listeners = library.register_listeners
        self._unregister_listeners = library.unregister_listeners

    def start_suite(self):
        self._register_listeners()

    def end_suite(self):
        self._unregister_listeners()

    def start_test(self):
        pass

    def end_test(self):
        pass

    def __str__(self):
        return 'global'


class TestSuiteScope(GlobalScope):
    is_global = False

    def __init__(self, library):
        GlobalScope.__init__(self, library)
        self._reset_instance = library.reset_instance
        self._instance_cache = []

    @property
    def is_global(self):
        return False

    def start_suite(self):
        prev = self._reset_instance()
        self._instance_cache.append(prev)
        self._register_listeners()

    def end_suite(self):
        self._unregister_listeners(close=True)
        prev = self._instance_cache.pop()
        self._reset_instance(prev)

    def __str__(self):
        return 'test suite'


class TestCaseScope(TestSuiteScope):

    def start_test(self):
        self._unregister_listeners()
        prev = self._reset_instance()
        self._instance_cache.append(prev)
        self._register_listeners()

    def end_test(self):
        self._unregister_listeners(close=True)
        prev = self._instance_cache.pop()
        self._reset_instance(prev)
        self._register_listeners()

    def __str__(self):
        return 'test case'
