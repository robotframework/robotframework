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
from robot.model import SuiteVisitor
from robot.result import ExecutionResult
from robot.utils import get_error_message


class GatherFailedTests(SuiteVisitor):

    def __init__(self):
        self.tests = []

    def visit_test(self, test):
        if not test.passed:
            self.tests.append(test.longname)

    def visit_keyword(self, kw):
        pass


def gather_failed_tests(output):
    if output.upper() == 'NONE':
        return []
    gatherer = GatherFailedTests()
    try:
        ExecutionResult(output, include_keywords=False).suite.visit(gatherer)
        if not gatherer.tests:
            raise DataError('All tests passed.')
    except:
        raise DataError("Collecting failed tests from '%s' failed: %s"
                        % (output, get_error_message()))
    return gatherer.tests
