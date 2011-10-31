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

from visitor import Visitor


class SuiteTeardownFailureHandler(Visitor):

    def __init__(self, suite_generator):
        self._should_handle = suite_generator == 'ROBOT'

    def visit_suite(self, suite):
        if self._should_handle:
            self.start_suite(suite)

    def start_suite(self, suite):
        if self._suite_teardown_failed(suite.keywords.teardown):
            suite.visit(SuiteTeardownFailed())

    def _suite_teardown_failed(self, teardown):
        return teardown and teardown.status == 'FAIL'

    def start_test(self, test):
        return False

    def start_keyword(self, keyword):
        return False


class SuiteTeardownFailed(Visitor):
    _normal_msg = 'Teardown of the parent suite failed.'
    _also_msg = '\n\nAlso teardown of the parent suite failed.'

    def start_test(self, test):
        test.status = 'FAIL'
        test.message += self._also_msg if test.message else self._normal_msg
        return False

    def start_keyword(self, keyword):
        return False
