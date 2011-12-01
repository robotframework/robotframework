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

from robot.model.statistics import Statistics

from .configurer import SuiteConfigurer
from .testsuite import TestSuite
from .executionerrors import ExecutionErrors


class ExecutionResult(object):

    def __init__(self, root_suite=None, errors=None):
        self.suite = root_suite or TestSuite()
        self.errors = errors or ExecutionErrors()
        self.generator = None
        self._status_rc = True
        self._stat_config = {}

    @property
    def statistics(self):
        return Statistics(self.suite, **self._stat_config)

    @property
    def return_code(self):
        if self._status_rc:
            return min(self.suite.statistics.critical.failed, 250)
        return 0

    def configure(self, status_rc=True, suite_config={}, stat_config={}):
        SuiteConfigurer(**suite_config).configure(self.suite)
        self._status_rc = status_rc
        self._stat_config = stat_config

    def visit(self, visitor):
        visitor.visit_result(self)


class CombinedExecutionResult(ExecutionResult):

    def __init__(self, *others):
        ExecutionResult.__init__(self)
        for other in others:
            self.add_result(other)

    def add_result(self, other):
        self.suite.suites.append(other.suite)
        self.errors.add(other.errors)
