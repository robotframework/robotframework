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

"""Implements the core test execution logic.

The public API of this package consists of the following two classes:

* :class:`~robot.running.model.TestSuite` for creating an executable
  test suite structure programmatically.

* :class:`~robot.running.builder.TestSuiteBuilder` for creating executable
  test suites based on existing test case files and directories.

It is recommended to import both of these classes via the :mod:`robot.api`
package like in the examples below.

This package and especially all public code was rewritten in Robot Framework
2.8 to make it easier to generate and execute test suites programmatically.
Rewriting of the test execution logic will continue in future releases,
but changes to the public API ought to be relatively small.

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

We can easily parse and create an executable test suite based on the above file
using the :class:`~robot.running.builder.TestSuiteBuilder` class as follows::

    from robot.api import TestSuiteBuilder

    suite = TestSuiteBuilder().build('path/to/activate_skynet.robot')

That was easy. Let's next generate the same test suite from scratch
using the :class:`~robot.running.model.TestSuite` class::

    from robot.api import TestSuite

    suite = TestSuite('Activate Skynet')
    suite.imports.library('OperatingSystem')
    test = suite.tests.create('Should Activate Skynet', tags=['smoke'])
    test.keywords.create('Set Environment Variable', args=['SKYNET', 'activated'], type='setup')
    test.keywords.create('Environment Variable Should Be Set', args=['SKYNET'])

Not that complicated either, especially considering the flexibility. Notice
that the suite created based on the file could be edited further using
the same API.

Now that we have a test suite ready, let's
:meth:`run <robot.running.model.TestSuite.run>` it and verify that the returned
:class:`~robot.result.executionresult.Result` object contains correct
information::

    result = suite.run(critical='smoke', output='skynet.xml')

    assert result.return_code == 0
    assert result.suite.name == 'Activate Skynet'
    test = result.suite.tests[0]
    assert test.name == 'Should Activate Skynet'
    assert test.passed and test.critical
    stats = result.suite.statistics
    assert stats.critical.total == 1 and stats.critical.failed == 0

Running the suite generates a normal output XML file, unless it is disabled
by using ``output=None``. Generating log, report, and xUnit files based on
the results is possible using the
:class:`~robot.reporting.resultwriter.ResultWriter` class::

    from robot.api import ResultWriter

    # Report and xUnit files can be generated based on the result object.
    ResultWriter(result).write_results(report='skynet.html', log=None)
    # Generating log files requires processing the earlier generated output XML.
    ResultWriter('skynet.xml').write_results()

Package methods
---------------
"""

from .builder import TestSuiteBuilder
from .context import EXECUTION_CONTEXTS
from .keywords import Keyword
from .model import TestSuite, TestCase
from .testlibraries import TestLibrary
from .runkwregister import RUN_KW_REGISTER


def UserLibrary(path):
    """Create a user library instance from given resource file.

    This is used by Libdoc.
    """
    from robot.parsing import ResourceFile
    from robot import utils
    from .arguments.argumentspec import ArgumentSpec
    from .userkeyword import UserLibrary as RuntimeUserLibrary

    resource = ResourceFile(path).populate()
    ret = RuntimeUserLibrary(resource.keyword_table.keywords, path)
    for handler in ret.handlers.values():
        if handler.type != 'error':
            handler.doc = utils.unescape(handler._doc)
        else:
            handler.arguments = ArgumentSpec(handler.longname)
            handler.doc = '*Creating keyword failed: %s*' % handler.error
    ret.doc = resource.setting_table.doc.value
    return ret
