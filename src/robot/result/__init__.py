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

"""Implements parsing execution results from XML output files.

The public API of this package is the :func:`~.ExecutionResult` factory
method, which returns :class:`~.Result` objects, and :class:`~.ResultVisitor`
abstract class to ease further processing the results. It is highly
recommended to use the public API via the :mod:`robot.api` package like in
the example below.

This package is considered stable.

Example
-------

.. literalinclude:: /../../doc/api/code_examples/check_test_times.py
"""

from .executionresult import Result
from .resultbuilder import ExecutionResult
from .testsuite import TestSuite
from .visitor import ResultVisitor
