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

from __future__ import with_statement

from robot.model import Statistics
from robot.reporting.outputwriter import OutputWriter

from .executionerrors import ExecutionErrors
from .configurer import SuiteConfigurer
from .testsuite import TestSuite


class Result(object):
    """Contains results of test execution.

    :ivar source: Path to the xml file where results are read from.
    :ivar suite: Hierarchical :class:`~.testsuite.TestSuite` results.
    :ivar errors: Execution :class:`~.executionerrors.ExecutionErrors`.
    """

    def __init__(self, source=None, root_suite=None, errors=None):
        self.source = source
        self.suite = root_suite or TestSuite()
        self.errors = errors or ExecutionErrors()
        self.generator = None
        self._status_rc = True
        self._stat_config = {}

    @property
    def statistics(self):
        """Test execution :class:`~robot.model.statistics.Statistics`."""
        return Statistics(self.suite, **self._stat_config)

    @property
    def return_code(self):
        """Return code (integer) of test execution."""
        if self._status_rc:
            return min(self.suite.statistics.critical.failed, 250)
        return 0

    def configure(self, status_rc=True, suite_config={}, stat_config={}):
        SuiteConfigurer(**suite_config).configure(self.suite)
        self._status_rc = status_rc
        self._stat_config = stat_config

    def visit(self, visitor):
        visitor.visit_result(self)

    def save(self, path=None):
        self.visit(OutputWriter(path or self.source))


class CombinedResult(Result):

    def __init__(self, others):
        Result.__init__(self)
        for other in others:
            self.add_result(other)

    def add_result(self, other):
        self.suite.suites.append(other.suite)
        self.errors.add(other.errors)
