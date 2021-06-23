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
        teardown = suite.teardown
        # Both 'PASS' and 'NOT RUN' statuses are OK.
        if teardown and teardown.status == teardown.FAIL:
            suite.suite_teardown_failed(teardown.message)
        if teardown and teardown.status == teardown.SKIP:
            suite.suite_teardown_skipped(teardown.message)

    def visit_test(self, test):
        pass

    def visit_keyword(self, keyword):
        pass


class SuiteTeardownFailed(SuiteVisitor):
    _normal_msg = 'Parent suite teardown failed:\n%s'
    _also_msg = '\n\nAlso parent suite teardown failed:\n%s'
    _normal_skip_msg = 'Skipped in parent suite teardown:\n%s'
    _also_skip_msg = 'Skipped in parent suite teardown:\n%s\n\nEarlier message:\n%s'

    def __init__(self, message, skipped=False):
        self.message = message
        self.skipped = skipped

    def visit_test(self, test):
        if not self.skipped:
            self._suite_teardown_failed(test)
        else:
            self._suite_teardown_skipped(test)

    def _suite_teardown_failed(self, test):
        if not test.skipped:
            test.status = test.FAIL
        prefix = self._also_msg if test.message else self._normal_msg
        test.message += prefix % self.message

    def _suite_teardown_skipped(self, test):
        test.status = test.SKIP
        if test.message:
            test.message = self._also_skip_msg % (self.message, test.message)
        else:
            test.message = self._normal_skip_msg % self.message

    def visit_keyword(self, keyword):
        pass
