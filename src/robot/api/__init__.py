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

"""This package exposes the public APIs of Robot Framework.

Unless stated otherwise, the APIs exposed in this module are considered stable,
and thus safe to use when building external tools on top of Robot Framework.

Currently exposed APIs are:

  * :py:mod:`.logger` for test libraries' logging purposes.

  * :py:func:`~robot.result.resultbuilder.ExecutionResult` for reading
    execution results from XML output files.

  * :py:class:`~robot.parsing.model.TestCaseFile`,
    :py:class:`~robot.parsing.model.TestDataDirectory`, and
    :py:class:`~robot.parsing.model.ResourceFile` for parsing data files.
    In addition, a convenience factory function
    :py:func:`~robot.parsing.model.TestData` creates either
    :py:class:`~robot.parsing.model.TestCaseFile` or
    :py:class:`~robot.parsing.model.TestDataDirectory` based on the input.

  * :py:func:`~robot.running.model.TestSuite` for creating a
    test suite that can be executed. This API is going to change in
    Robot Framework 2.8.

These names can be imported like this:

.. code-block:: python

    from robot.api import <name>

See documentations of the individual APIs for more details.
"""

from robot.parsing import TestCaseFile, TestDataDirectory, ResourceFile, TestData
from robot.result import ExecutionResult
from robot.running import TestSuite
