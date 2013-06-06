#  Copyright 2008-2013 Nokia Siemens Networks Oyj
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

This package was rewritten for Robot Framework 2.8.

Currently, the main entry point is the :func:`~.model.TestSuite` factory
method.

Example: Creating a test suite programmatically
-----------------------------------------------

Starting from Robot Framework 2.8, it is possible to create runnable test suites
programmatically using :py:mod:`Robot Framework Public APIs <robot.api>`.

In this example, we create a basic test suite having one test case.

.. literalinclude:: /../../doc/api/code_examples/test_suite.py
   :linenos:

On line 1, we start by importing :py:class:`robot.running.model.TestSuite`,
exposed via :py:mod:`robot.api`. Please note, that no other classes
are imported via API. This is due to fact that everything related to tests
(test cases, keywords, variables, etc.) are always created via
:py:class:`robot.running.model.TestSuite`.

On line 3, we instantiate a new test suite from
:py:class:`robot.running.model.TestSuite`. When creating new test suites,
test cases or keywords, the first parameter is always the name.

On line 4, the `OperatingSystem` library is brought into use by
using :py:func:`robot.model.imports.Imports.library`. Other possible import
types are :py:func:`resource file <robot.model.imports.Imports.resource>` and
:py:func:`variable file <robot.model.imports.Imports.variables>`.

On line 5, the actual test case is created into the suite. Besides the name,
the test case is also given an additional tag as a named argument.
Multiple values can be given as a list, for example, multiple tags could be
defined by using `tags=['regression', 'slow']`.

On line 6, the test case setup is created by adding keyword
`Set Environment Variable` (from `Operating System` library) into the test case.
This keyword takes multiple arguments, hence the arguments are given as a list.
Parameter `type` with value `setup` specifies, that this keyword is defined as
the test case setup. Similarly, `type` could be `teardown` for defining the test
case teardown. If no `type` is given as parameter, the keyword is assumed to be
a normal, i.e. non-setup and non-teardown, keyword.

On line 7, another keyword `Environment Variable Should Be Set`, is added into
the test case.

On line 8, the actual test suite is ran by issuing method
:py:func:`robot.running.model.TestSuite.run`. This method returns test results
as an object which is type of :py:class:`robot.result.executionresult.Result`.


Example: Creating a test suite from source
------------------------------------------

[explanation]

.. literalinclude:: /../../doc/api/code_examples/test_suite_builder.py
"""

from .builder import TestSuiteBuilder
from .context import EXECUTION_CONTEXTS
from .keywords import Keyword
from .model import TestSuite, TestCase
from .testlibraries import TestLibrary
from .runkwregister import RUN_KW_REGISTER


def UserLibrary(path):
    """Create a user library instance from given resource file.

    This is used at least by libdoc.py."""
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

