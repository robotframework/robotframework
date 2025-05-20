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

from robot.errors import DataError
from robot.model import SuiteVisitor
from robot.result import ExecutionResult
from robot.utils import get_error_message, glob_escape


class GatherFailedTests(SuiteVisitor):

    def __init__(self):
        self.tests = []

    def visit_test(self, test):
        if test.failed:
            self.tests.append(glob_escape(test.full_name))

    def visit_keyword(self, kw):
        pass


class GatherFailedSuites(SuiteVisitor):

    def __init__(self):
        self.suites = []

    def start_suite(self, suite):
        if any(test.failed for test in suite.tests):
            self.suites.append(glob_escape(suite.full_name))

    def visit_test(self, test):
        pass

    def visit_keyword(self, kw):
        pass


def gather_failed_tests(output, empty_suite_ok=False):
    if output is None:
        return None
    gatherer = GatherFailedTests()
    kind = "tests or tasks"
    try:
        suite = ExecutionResult(output, include_keywords=False).suite
        suite.visit(gatherer)
        kind = "tests" if not suite.rpa else "tasks"
        if not gatherer.tests and not empty_suite_ok:
            raise DataError(f"All {kind} passed.")
    except Exception:
        raise DataError(
            f"Collecting failed {kind} from '{output}' failed: {get_error_message()}"
        )
    return gatherer.tests


def gather_failed_suites(output, empty_suite_ok=False):
    if output is None:
        return None
    gatherer = GatherFailedSuites()
    try:
        ExecutionResult(output, include_keywords=False).suite.visit(gatherer)
        if not gatherer.suites and not empty_suite_ok:
            raise DataError("All suites passed.")
    except Exception:
        raise DataError(
            f"Collecting failed suites from '{output}' failed: {get_error_message()}"
        )
    return gatherer.suites
