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
the results. It is recommended to import these public entry-points via the
:mod:`robot.api` package like in the example below.

The model objects defined in the :mod:`robot.result.model` module are also
part of the public API. They are used inside the :class:`~.Result` object,
and they can also be inspected and modified as part of the normal test
execution by using `pre-Rebot modifiers`__ and `listeners`__. These model
objects are not exposed via :mod:`robot.api`, but they can be imported
from :mod:`robot.result` if needed.

Example
-------

.. literalinclude:: /../../doc/api/code_examples/check_test_times.py

__ http://robotframework.org/robotframework/latest/RobotFrameworkUserGuide.html#programmatic-modification-of-results
__ http://robotframework.org/robotframework/latest/RobotFrameworkUserGuide.html#listener-interface
"""

from .executionresult import Result as Result
from .model import (
    Break as Break,
    Continue as Continue,
    Error as Error,
    For as For,
    ForIteration as ForIteration,
    Group as Group,
    If as If,
    IfBranch as IfBranch,
    Keyword as Keyword,
    Message as Message,
    Return as Return,
    TestCase as TestCase,
    TestSuite as TestSuite,
    Try as Try,
    TryBranch as TryBranch,
    Var as Var,
    While as While,
    WhileIteration as WhileIteration,
)
from .resultbuilder import (
    ExecutionResult as ExecutionResult,
    ExecutionResultBuilder as ExecutionResultBuilder,
)
from .visitor import ResultVisitor as ResultVisitor
