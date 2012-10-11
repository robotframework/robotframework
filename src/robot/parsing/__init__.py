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

"""Implements parsing of test data files.

Classes :class:`~.model.TestCaseFile`, :class:`~.model.TestDataDirectory` and
:class:`~.model.ResourceFile` represented parsed test data. These can be
modified and saved back to disk. In addition, a convenience factory function
:func:`~.model.TestData` can be used to parse file or directory to a
corresponding object.

This package is considered stable.

Example
-------

.. code-block:: python

    from robot.parsing import TestCaseFile

    suite = TestCaseFile(source='path/to/tests.html').populate()
    print 'Suite: ', suite.name
    for test in suite.testcase_table:
        print test.name
"""

from .model import TestData, TestCaseFile, TestDataDirectory, ResourceFile
from . import populators

VALID_EXTENSIONS = tuple(populators.READERS)

def disable_curdir_processing(method):
    """Decorator to disable processing `${CURDIR}` variable."""
    def decorated(*args, **kwargs):
        original = populators.PROCESS_CURDIR
        populators.PROCESS_CURDIR = False
        try:
            return method(*args, **kwargs)
        finally:
            populators.PROCESS_CURDIR = original
    return decorated
