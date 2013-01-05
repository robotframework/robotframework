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

    def end_suite(self, suite):
        teardown = suite.keywords.teardown
        if teardown and not teardown.passed:
            suite.visit(SuiteTeardownFailed(teardown.message))

    def visit_test(self, test):
        pass

    def visit_keyword(self, keyword):
        pass


class SuiteTeardownFailed(SuiteVisitor):
    _normal_msg = 'Teardown of the parent suite failed:\n'
    _also_msg = '\n\nAlso teardown of the parent suite failed:\n'

    def __init__(self, error):
        self._normal_msg += error
        self._also_msg += error

    def visit_test(self, test):
        test.status = 'FAIL'
        test.message += self._also_msg if test.message else self._normal_msg

    def visit_keyword(self, keyword):
        pass
