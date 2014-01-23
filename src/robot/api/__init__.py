#  Copyright 2008-2014 Nokia Solutions and Networks
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

""":mod:`robot.api` package exposes the public APIs of Robot Framework.

Unless stated otherwise, the APIs exposed in this package are considered stable,
and thus safe to use when building external tools on top of Robot Framework.

Currently exposed APIs are:

* :mod:`.logger` module for test libraries' logging purposes.

* :class:`~robot.parsing.model.TestCaseFile`,
  :class:`~robot.parsing.model.TestDataDirectory`, and
  :class:`~robot.parsing.model.ResourceFile` classes for parsing test
  data files and directories.
  In addition, a convenience factory method
  :func:`~robot.parsing.model.TestData` creates either
  :class:`~robot.parsing.model.TestCaseFile` or
  :class:`~robot.parsing.model.TestDataDirectory` objects based on the input.
  **Note:** Test data parsing may be rewritten in Robot Framework 2.9 or later.

* :class:`~robot.running.model.TestSuite` class for creating executable
  test suites programmatically and
  :class:`~robot.running.builder.TestSuiteBuilder` class
  for creating such suites based on existing test data on the file system.

* :func:`~robot.result.resultbuilder.ExecutionResult` factory method
  for reading execution results from XML output files and
  :class:`~robot.result.visitor.ResultVisitor` abstract class to ease
  further processing the results.

* :class:`~robot.reporting.resultwriter.ResultWriter` class for writing
  reports, logs, XML outputs, and XUnit files. Can write results based on
  XML outputs on the file system, as well as based on the result objects
  returned by the :func:`~robot.result.resultbuilder.ExecutionResult` or
  an executed :class:`~robot.running.model.TestSuite`.


All of the above names can be imported like::

    from robot.api import ApiName

See documentations of the individual APIs for more details.

.. tip:: APIs related to the command line entry points are exposed directly
        via the :mod:`robot` root package.
"""

from robot.parsing import TestCaseFile, TestDataDirectory, ResourceFile, TestData
from robot.reporting import ResultWriter
from robot.result import ExecutionResult, ResultVisitor
from robot.running import TestSuite, TestSuiteBuilder
