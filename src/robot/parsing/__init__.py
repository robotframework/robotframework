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

# FIXME misleading maybe??
"""Implements test data parsing.

Classes :class:`~.model.TestCaseFile`, :class:`~.model.TestDataDirectory`
and :class:`~.model.ResourceFile` represented parsed test data. Objects
of these classes can be modified and saved back to disk. In addition,
a convenience factory function :func:`~.model.TestData` can be used to
parse a test case file or directory to a corresponding object.

Aforementioned classes and functions are part of the public API. It is
recommended that they are imported through the :mod:`robot.api` package
like in the example below.

This package is likely to change radically in Robot Framework 2.9. The main
motivation for the planned changes is making the data easier to use for
external tools that use these modules.

Example
-------

::

    import sys
    from robot.api import TestData

    def print_suite(suite):
        print 'Suite:', suite.name
        for test in suite.testcase_table:
            print '-', test.name
        for child in suite.children:
            print_suite(child)

    suite = TestData(source=sys.argv[1])
    print_suite(suite)
"""

from robot.errors import DataError

from .lexer import TestCaseFileLexer, ResourceFileLexer
from .nodes import TestCaseSection
from .parser import RobotFrameworkParser
from .lexerwrapper import LexerWrapper
from .model import Model
from . import lexerwrapper


def get_test_case_file_ast(source):
    return RobotFrameworkParser(TestCaseFileLexer()).parse(source)


def get_resource_file_ast(source):
    ast = RobotFrameworkParser(ResourceFileLexer()).parse(source)
    if any(isinstance(s, TestCaseSection) for s in ast.sections):
        raise DataError("Resource file '%s' cannot contain tests or tasks." % source)
    return ast


def disable_curdir_processing(method):
    """Decorator to disable processing `${CURDIR}` variable."""
    def decorated(*args, **kwargs):
        original = lexerwrapper.PROCESS_CURDIR
        lexerwrapper.PROCESS_CURDIR = False
        try:
            return method(*args, **kwargs)
        finally:
            lexerwrapper.PROCESS_CURDIR = original
    return decorated
