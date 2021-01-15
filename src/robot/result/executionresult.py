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
from robot.model import Statistics

from .executionerrors import ExecutionErrors
from .model import TestSuite


class Result(object):
    """Test execution results.

    Can be created based on XML output files using the
    :func:`~.resultbuilder.ExecutionResult`
    factory method. Also returned by the
    :meth:`robot.running.TestSuite.run <robot.running.model.TestSuite.run>`
    method.
    """

    def __init__(self, source=None, root_suite=None, errors=None, rpa=None):
        #: Path to the XML file where results are read from.
        self.source = source
        #: Hierarchical execution results as a
        #: :class:`~.result.model.TestSuite` object.
        self.suite = root_suite or TestSuite()
        #: Execution errors as an
        #: :class:`~.executionerrors.ExecutionErrors` object.
        self.errors = errors or ExecutionErrors()
        self.generated_by_robot = True
        self._status_rc = True
        self._stat_config = {}
        self.rpa = rpa

    @property
    def statistics(self):
        """Test execution statistics.

        Statistics are an instance of
        :class:`~robot.model.statistics.Statistics` that is created based
        on the contained ``suite`` and possible
        :func:`configuration <configure>`.

        Statistics are created every time this property is accessed. Saving
        them to a variable is thus often a good idea to avoid re-creating
        them unnecessarily::

            from robot.api import ExecutionResult

            result = ExecutionResult('output.xml')
            result.configure(stat_config={'suite_stat_level': 2,
                                          'tag_stat_combine': 'tagANDanother'})
            stats = result.statistics
            print(stats.total.failed)
            print(stats.total.passed)
            print(stats.tags.combined[0].total)
        """
        return Statistics(self.suite, rpa=self.rpa, **self._stat_config)

    @property
    def return_code(self):
        """Return code (integer) of test execution.

        By default returns the number of failed tests (max 250),
        but can be :func:`configured <configure>` to always return 0.
        """
        if self._status_rc:
            return min(self.suite.statistics.failed, 250)
        return 0

    def configure(self, status_rc=True, suite_config=None, stat_config=None):
        """Configures the result object and objects it contains.

        :param status_rc: If set to ``False``, :attr:`return_code` always
            returns 0.
        :param suite_config: A dictionary of configuration options passed
            to :meth:`~.result.testsuite.TestSuite.configure` method of
            the contained ``suite``.
        :param stat_config: A dictionary of configuration options used when
            creating :attr:`statistics`.
        """
        if suite_config:
            self.suite.configure(**suite_config)
        self._status_rc = status_rc
        self._stat_config = stat_config or {}

    def save(self, path=None):
        """Save results as a new output XML file.

        :param path: Path to save results to. If omitted, overwrites the
            original file.
        """
        from robot.reporting.outputwriter import OutputWriter
        self.visit(OutputWriter(path or self.source, rpa=self.rpa))

    def visit(self, visitor):
        """An entry point to visit the whole result object.

        :param visitor: An instance of :class:`~.visitor.ResultVisitor`.

        Visitors can gather information, modify results, etc. See
        :mod:`~robot.result` package for a simple usage example.

        Notice that it is also possible to call :meth:`result.suite.visit
        <robot.result.testsuite.TestSuite.visit>` if there is no need to
        visit the contained ``statistics`` or ``errors``.
        """
        visitor.visit_result(self)

    def handle_suite_teardown_failures(self):
        """Internal usage only."""
        if self.generated_by_robot:
            self.suite.handle_suite_teardown_failures()

    def set_execution_mode(self, other):
        """Set execution mode based on other result. Internal usage only."""
        if other.rpa is None:
            pass
        elif self.rpa is None:
            self.rpa = other.rpa
        elif self.rpa is not other.rpa:
            this, that = ('task', 'test') if other.rpa else ('test', 'task')
            raise DataError("Conflicting execution modes. File '%s' has %ss "
                            "but files parsed earlier have %ss. Use '--rpa' "
                            "or '--norpa' options to set the execution mode "
                            "explicitly." % (other.source, this, that))


class CombinedResult(Result):
    """Combined results of multiple test executions."""

    def __init__(self, results=None):
        Result.__init__(self)
        for result in results or ():
            self.add_result(result)

    def add_result(self, other):
        self.set_execution_mode(other)
        self.suite.suites.append(other.suite)
        self.errors.add(other.errors)
