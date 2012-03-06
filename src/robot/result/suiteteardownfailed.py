#  Copyright 2008-2012 Nokia Siemens Networks Oyj
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

from robot.model import SuiteVisitor


class SuiteTeardownFailureHandler(SuiteVisitor):

    def __init__(self, suite_generator):
        self._should_handle = suite_generator == 'ROBOT'

    def start_suite(self, suite):
        if not self._should_handle:
            return False
        if self._suite_teardown_failed(suite.keywords.teardown):
            suite.visit(SuiteTeardownFailed())

    def _suite_teardown_failed(self, teardown):
        return bool(teardown and not teardown.passed)

    def start_test(self, test):
        return False

    def start_keyword(self, keyword):
        return False


class SuiteTeardownFailed(SuiteVisitor):
    _normal_msg = 'Teardown of the parent suite failed.'
    _also_msg = '\n\nAlso teardown of the parent suite failed.'

    def __init__(self):
        self._top_level_visited = False

    def start_suite(self, suite):
        if self._top_level_visited:
            self._set_message(suite)
        self._top_level_visited = True

    def visit_test(self, test):
        test.status = 'FAIL'
        self._set_message(test)

    def _set_message(self, item):
        item.message += self._also_msg if item.message else self._normal_msg

    def visit_keyword(self, keyword):
        pass
