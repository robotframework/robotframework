Robot Framework acceptance tests
================================

Introduction
------------

Acceptance tests for Robot Framework are naturally created using Robot
Framework itself. This folder contains all those acceptance tests and other
test data they need.

License and copyright
---------------------

All the content in ``atest`` folder is the under following copyright::

    Copyright 2008-2015 Nokia Solutions and Networks

    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at

        http://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.

Directory contents
------------------

run_atests.py
    A script for running acceptance tests. See below for further instructions.

genrunner.py
    Script to generate atest runners based on plain text data files.

    Usage:  genrunner.py testdata/path/data.robot [robot/path/runner.robot]

robot/
    Contains actual acceptance test cases.

resources/
    Resources needed by acceptance tests in ``robot`` folder.

testdata/
    Contains test data used by acceptance tests. This test data consists
    mainly of test cases that are run by actual acceptance tests in
    the ``robot`` folder.

testresources/
    Contains resources needed by test cases in ``testdata`` folder.
    Some of these resources are also used by unit tests.

results/
    The place for test execution results like reports, logs and outputs.
    This directory is generated when acceptance tests are executed. It
    is in ``.gitignore`` and can be safely deleted any time.

Running acceptance tests
------------------------

Robot Framework's acceptance tests are run using `<run_atests.py>`__. Its
usage is displayed with ``--help`` and also shown below::

    A script for running Robot Framework's acceptance tests.

    Usage:  run_atests.py interpreter [options] datasource(s)

    Data sources are paths to directories or files under `robot` folder.

    Available options are the same that can be used with Robot Framework.
    See its help (e.g. `pybot --help`) for more information.

    The specified interpreter is used by acceptance tests under `robot` to
    run test cases under `testdata`. It can be simply `python` or `jython`
    (if they are in PATH) or to a path a selected interpreter (e.g.
    `/usr/bin/python26`). Note that this script itself must always be
    executed with Python 2.6 or newer.

    Examples:
    $ atest/run_atests.py python --test example atest/robot
    $ atest/run_atests.py /usr/bin/jython25 atest/robot/tags/tag_doc.txt

To run all the acceptance tests, execute the ``atest/robot`` folder entirely::

    python atest/run_atests.py python atest/robot

A sub test suite can be executed simply by running the folder or file
containing it. On modern machines running all acceptance tests ought to
take less than ten minutes with Python, but with Jython the execution time
is considerably longer. This is due to Jython being somewhat slower than
Python in general, but the main reason is that the JVM is started by
acceptance dozens of times and it always takes few seconds.

When acceptance tests are run, both Python and Jython interpreter should be
used to verify interoperability with both supported interpreters. Tests
can (and should) also be run using different Python and Jython versions and
on different operating systems. Since running tests on Jython takes quite a
lot time, it is sometimes a good idea to run only those tests that are not
executed with Python with it::

    python atest/run_atests.py jython --exclude pybot atest/robot

The results of the test execution are written to ``results`` folder. The
directory contains output, log and report files of the execution as
well as a separate directory for other outputs.

Test data
---------

The test data is divided to two, test data part (``testdata`` folder) and
running part (``robot`` folder). Test data side contains test cases for
different features. Running side contains the actual acceptance test cases
that run the test cases on the test data side and verify their results.

The basic mechanism to verify that a test case in the test data side is
executed as expected is setting the expected status and possible error
message in its documentation. By default tests are expected to pass, but
having ``FAIL`` (this and subsequent markers are case sensitive) in the
documentation changes the expectation. The text after the ``FAIL`` marker
is the expected error message, which, by default, must match the actual
error exactly. If the error message starts with ``REGEXP:``, ``GLOB:`` or
``STARTS:``, the expected error is considered to be a regexp or glob pattern
matching the actual error, or to contain the beginning of the error. All
other details can be tested also, but that logic is in the running side.

These acceptance tests are in general *not* good examples of
well-written test cases. This is mainly due to us learning how to
write good test cases with Robot Framework while developing it, and so
far there has not been time for refactoring them. With better tools
refactoring is getting easier and hopefully we can do something for
these tests in the future. The first step would be reorganizing the
structure of ``robot`` and ``testdata`` folders. Their current structure
follows Robot Framework's old internal module structure and it is far
from ideal nowadays.

Additional modules
------------------

Tests related to YAML variable files require `PyYAML <http://pyyaml.org/>`_
module. You should be able to install it with ``pip install pyyaml``.
The Python version of the module is enough so it is not a problem if
installing the C version fails due to a missing compiler or otherwise.

XML library tests verifying using `lxml <http://lxml.de/>`_ module naturally
require having that module installed. Because installing it is not always
trivial, these tests are not considered critical if it is not installed.

Tests related to parsing reStructuredText test data files require
`docutils <http://docutils.sourceforge.net/>`_ module. You can install it
with ``pip install docutils``, but also these tests are non-critical if
the module is not installed.

Telnet tests
------------

Telnet test are not critical by default and running them requires some
extra setup. Instructions how to run them can be found from
`<testdata/standard_libraries/telnet/README.rst>`_.
