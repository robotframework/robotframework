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

from robot.model import SuiteVisitor


class SuiteTeardownFailureHandler(SuiteVisitor):

    def end_suite(self, suite):
        teardown = suite.keywords.teardown
        # Both 'PASS' and 'NOT_RUN' (used in dry-run) statuses are OK.
        if teardown and teardown.status == 'FAIL':
            suite.suite_teardown_failed(teardown.message)

    def visit_test(self, test):
        pass

    def visit_keyword(self, keyword):
        pass


class SuiteTeardownFailed(SuiteVisitor):
    _normal_msg = 'Parent suite teardown failed:\n'
    _also_msg = '\n\nAlso parent suite teardown failed:\n'

    def __init__(self, error):
        self._normal_msg += error
        self._also_msg += error

    def visit_test(self, test):
        test.status = 'FAIL'
        test.message += self._also_msg if test.message else self._normal_msg

    def visit_keyword(self, keyword):
        pass
