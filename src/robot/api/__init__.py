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

""":mod:`robot.api` package exposes the public APIs of Robot Framework.

Unless stated otherwise, the APIs exposed in this package are considered
stable, and thus safe to use when building external tools on top of
Robot Framework. Notice that all parsing APIs were rewritten in Robot
Framework 3.2.

Currently exposed APIs are:

* :mod:`.logger` module for libraries' logging purposes.

* :mod:`.deco` module with decorators libraries can utilize.

* :mod:`.exceptions` module containing exceptions that libraries can utilize for
  reporting failures and other events. These exceptions can be imported also directly
  via :mod:`robot.api` like ``from robot.api import SkipExecution``.

* :mod:`.interfaces` module containing optional base classes that can be used
  when creating libraries and other extensions. New in Robot Framework 6.1.

* :mod:`.parsing` module exposing the parsing APIs. This module is new in Robot
  Framework 4.0. Various parsing related functions and classes were exposed
  directly via :mod:`robot.api` already in Robot Framework 3.2, but they are
  effectively deprecated and will be removed in the future.

* :class:`~robot.running.model.TestSuite` class for creating executable
  test suites programmatically and
  :class:`~robot.running.builder.builders.TestSuiteBuilder` class
  for creating such suites based on existing test data on the file system.

* :class:`~robot.model.visitor.SuiteVisitor` abstract class for processing testdata
  before execution. This can be used as a base for implementing a pre-run
  modifier that is taken into use with ``--prerunmodifier`` commandline option.

* :func:`~robot.result.resultbuilder.ExecutionResult` factory method
  for reading execution results from XML output files and
  :class:`~robot.result.visitor.ResultVisitor` abstract class to ease
  further processing the results.
  :class:`~robot.result.visitor.ResultVisitor` can also be used as a base
  for pre-Rebot modifier that is taken into use with ``--prerebotmodifier``
  commandline option.

* :class:`~robot.reporting.resultwriter.ResultWriter` class for writing
  reports, logs, XML outputs, and XUnit files. Can write results based on
  XML outputs on the file system, as well as based on the result objects
  returned by the :func:`~robot.result.resultbuilder.ExecutionResult` or
  an executed :class:`~robot.running.model.TestSuite`.

* :class:`~robot.running.arguments.typeinfo.TypeInfo` class for parsing
  type hints and converting values based on them. New in Robot Framework 7.0.

* :class:`~robot.conf.languages.Languages` and :class:`~robot.conf.languages.Language`
  classes for external tools that need to work with different translations.
  The latter is also the base class to use with custom translations.

All of the above classes can be imported like::

    from robot.api import ClassName

The public API intends to follow the `distributing type information specification
<https://typing.readthedocs.io/en/latest/spec/distributing.html#distributing-type-information>`_
originally specified in `PEP 484 <https://peps.python.org/pep-0484/>`_.

See documentations of the individual APIs for more details.

.. tip:: APIs related to the command line entry points are exposed directly
        via the :mod:`robot` root package.
"""

from robot.conf.languages import Language as Language, Languages as Languages
from robot.model import SuiteVisitor as SuiteVisitor
from robot.parsing import (
    get_init_model as get_init_model,
    get_init_tokens as get_init_tokens,
    get_model as get_model,
    get_resource_model as get_resource_model,
    get_resource_tokens as get_resource_tokens,
    get_tokens as get_tokens,
    Token as Token,
)
from robot.reporting import ResultWriter as ResultWriter
from robot.result import (
    ExecutionResult as ExecutionResult,
    ResultVisitor as ResultVisitor,
)
from robot.running import (
    TestSuite as TestSuite,
    TestSuiteBuilder as TestSuiteBuilder,
    TypeInfo as TypeInfo,
)

from .exceptions import (
    ContinuableFailure as ContinuableFailure,
    Error as Error,
    Failure as Failure,
    FatalError as FatalError,
    SkipExecution as SkipExecution,
)
