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

"""Implements the core test execution logic.

The public API of this module consists of the following objects:

* :class:`~robot.running.model.TestSuite` for creating an executable
  test suite structure programmatically.

* :class:`~robot.running.builder.builders.TestSuiteBuilder` for creating
  executable test suites based on data on a file system.
  Instead of using this class directly, it is possible to use the
  :meth:`TestSuite.from_file_system <robot.running.model.TestSuite.from_file_system>`
  classmethod that uses it internally.

* Classes used by :class:`~robot.running.model.TestSuite`, such as
  :class:`~robot.running.model.TestCase`, :class:`~robot.running.model.Keyword`
  and :class:`~robot.running.model.If` that are defined in the
  :mod:`robot.running.model` module. These classes are typically only needed
  in type hints.

* Keyword implementation related classes :class:`~robot.running.resourcemodel.UserKeyword`,
  :class:`~robot.running.librarykeyword.LibraryKeyword`,
  :class:`~robot.running.invalidkeyword.InvalidKeyword` and their common base class
  :class:`~robot.running.keywordimplementation.KeywordImplementation`. Also these
  classes are mainly needed in type hints.

* :class:`~robot.running.builder.settings.TestDefaults` that is part of the
  `external parsing API`__ and also typically needed only in type hints.

__ http://robotframework.org/robotframework/latest/RobotFrameworkUserGuide.html#parser-interface

:class:`~robot.running.model.TestSuite` and
:class:`~robot.running.builder.builders.TestSuiteBuilder` can be imported also via
the :mod:`robot.api` package.

.. note:: Prior to Robot Framework 6.1, only some classes in
          :mod:`robot.running.model` were exposed via :mod:`robot.running`.
          Keyword implementation related classes are new in Robot Framework 7.0.

Examples
--------

First, let's assume we have the following test suite in file
``activate_skynet.robot``::

    *** Settings ***
    Library    OperatingSystem

    *** Test Cases ***
    Should Activate Skynet
        [Tags]    smoke
        [Setup]    Set Environment Variable    SKYNET    activated
        Environment Variable Should Be Set    SKYNET

We can easily create an executable test suite based on the above file::

    from robot.api import TestSuite

    suite = TestSuite.from_file_system('path/to/activate_skynet.robot')

That was easy. Let's next generate the same test suite from scratch::

    from robot.api import TestSuite

    suite = TestSuite('Activate Skynet')
    suite.resource.imports.library('OperatingSystem')
    test = suite.tests.create('Should Activate Skynet', tags=['smoke'])
    test.setup.config(name='Set Environment Variable', args=['SKYNET', 'activated'])
    test.body.create_keyword('Environment Variable Should Be Set', args=['SKYNET'])

Not that complicated either, especially considering the flexibility. Notice
that the suite created based on the file could also be edited further using
the same API.

Now that we have a test suite ready, let's :meth:`execute it
<robot.running.model.TestSuite.run>` and verify that the returned
:class:`~robot.result.executionresult.Result` object contains correct
information::

    result = suite.run(output='skynet.xml')

    assert result.return_code == 0
    assert result.suite.name == 'Activate Skynet'
    test = result.suite.tests[0]
    assert test.name == 'Should Activate Skynet'
    assert test.passed
    stats = result.suite.statistics
    assert stats.total == 1 and stats.passed == 1 and stats.failed == 0

Running the suite generates a normal output XML file, unless it is disabled
by using ``output=None``. Generating log, report, and xUnit files based on
the results is possible using the
:class:`~robot.reporting.resultwriter.ResultWriter` class::

    from robot.api import ResultWriter

    # Report and xUnit files can be generated based on the result object.
    ResultWriter(result).write_results(report='skynet.html', log=None)
    # Generating log files requires processing the earlier generated output XML.
    ResultWriter('skynet.xml').write_results()
"""

from .arguments import (
    ArgInfo as ArgInfo,
    ArgumentSpec as ArgumentSpec,
    TypeConverter as TypeConverter,
    TypeInfo as TypeInfo,
)
from .builder import (
    ResourceFileBuilder as ResourceFileBuilder,
    TestDefaults as TestDefaults,
    TestSuiteBuilder as TestSuiteBuilder,
)
from .context import EXECUTION_CONTEXTS as EXECUTION_CONTEXTS
from .invalidkeyword import InvalidKeyword as InvalidKeyword
from .keywordimplementation import KeywordImplementation as KeywordImplementation
from .librarykeyword import LibraryKeyword as LibraryKeyword
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
    Return as Return,
    TestCase as TestCase,
    TestSuite as TestSuite,
    Try as Try,
    TryBranch as TryBranch,
    Var as Var,
    While as While,
    WhileIteration as WhileIteration,
)
from .resourcemodel import (
    Import as Import,
    ResourceFile as ResourceFile,
    UserKeyword as UserKeyword,
    Variable as Variable,
)
from .runkwregister import RUN_KW_REGISTER as RUN_KW_REGISTER
from .testlibraries import TestLibrary as TestLibrary
