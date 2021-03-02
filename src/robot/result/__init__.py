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

"""Implements parsing execution results from XML output files.

The main public API of this package consists of the :func:`~.ExecutionResult`
factory method, that returns :class:`~.Result` objects, and of the
:class:`~.ResultVisitor` abstract class, that eases further processing
the results.

The model objects in the :mod:`~.model` module can also be considered to be
part of the public API, because they can be found inside the :class:`~.Result`
object. They can also be inspected and modified as part of the normal test
execution by `pre-Rebot modifiers`__ and `listeners`__.

It is highly recommended to import the public entry-points via the
:mod:`robot.api` package like in the example below. In those rare cases
where the aforementioned model objects are needed directly, they can be
imported from this package.

This package is considered stable.

Example
-------

.. literalinclude:: /../../doc/api/code_examples/check_test_times.py

__ http://robotframework.org/robotframework/latest/RobotFrameworkUserGuide.html#programmatic-modification-of-results
__ http://robotframework.org/robotframework/latest/RobotFrameworkUserGuide.html#listener-interface
"""

from .executionresult import Result
from .model import For, If, IfBranch, ForIteration, Keyword, Message, TestCase, TestSuite
from .resultbuilder import ExecutionResult, ExecutionResultBuilder
from .visitor import ResultVisitor
