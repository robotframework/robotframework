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

"""Implements the core test execution logic.

Currently, the main entry points are classes
:py:class:`~robot.running.model.TestSuite` for creating test suites
programmatically, and
:py:class:`~robot.running.builder.TestSuiteBuilder` for creating test suites
from existing test case files.

This package was rewritten for Robot Framework 2.8.

Examples
--------

1) Creating test cases programmatically


.. literalinclude:: /../../doc/api/code_examples/test_suite.py

2) Creating test cases from source files


.. literalinclude:: /../../doc/api/code_examples/test_suite_from_file.py

And here is the test case file:

.. literalinclude:: /../../doc/api/code_examples/my_tests.txt
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

