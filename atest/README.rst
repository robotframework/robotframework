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

run.py
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

Robot Framework's acceptance tests are run using `<run.py>`__. See its
documentation our run it with ``--help`` to see the usage. To run all the
acceptance tests, execute the ``atest/robot`` folder entirely::

    python atest/run.py python atest/robot

The command above will execute all tests, but often you may want to skip
for example `telnet tests`_ and tests requiring manual interaction. These
tests are marked with the ``no-ci`` tag and can be excluded from the test run::

    python atest/run.py python --exclude no-ci atest/robot

A sub test suite can be executed simply by running the folder or file
containing it. On modern machines running all acceptance tests ought to
take less than ten minutes with Python, but with Jython the execution time
is considerably longer. This is due to Jython being somewhat slower than
Python in general, but the main reason is that the JVM is started by
acceptance dozens of times and it always takes few seconds.

When acceptance tests are run, Python, Jython, and IronPython interpreters
should be used to verify interoperability with all supported interpreters.
Tests can (and should) also be run using different interpreter versions and
on different operating systems.

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

Test tags
---------

The tests on the running side (``atest/robot``) contains tags that are used
to include or exclude them based on the platform and required dependencies.
Selecting tests based on the platform is done automatically by the `<run.py>`__
script, but additional selection can be done by the user to avoid running
tests that require dependencies that are not available.

``manual``
  Require manual interaction from user. Used with Dialogs library tests.

``telnet``
  Require a telnet server with test account running at localhost. See
  `Telnet tests`_ for details.

``screenshot``
  Tests for the screenshot library. May require extra modules depending
  on the platform.

``no-ci``
  Tests which are not executed at continuous integration. Contains all tests
  tagged with ``manual`` or ``telnet``.

``require-jython``
  Require the interpreter to be Jython. Mainly used with tests related to
  Java integration.

``require-windows``
  Require the operating system to be Windows.

``require-yaml``, ``require-docutils``, ``require-lxml``
  Require lxml, docutils or PyYAML module to be installed, respectively.
  See `Required modules`_ for details.

``require-et13``
  Require ElementTree version 1.3. Automatically excluded when running with
  Python 2.6 or IronPython.

``no-windows``, ``no-osx``, ``no-jython``, ``no-ipy``,  ...
  Tests to be excluded on different operating systems or Python interpreter
  versions. Set automatically.

Examples::

    # Exclude tests requiring manual interaction or running telnet server.
    python atest/run.py python --exclude no-ci atest/robot

    # Same as the above but also exclude tests requiring docutils.
    python atest/run.py python -e no-ci -e require-docutils atest/robot

    # Run only tests related to Java integration. This is considerably faster
    # than running all tests on Jython.
    python atest/run.py jython --include require-jython atest/robot

Required modules
----------------

Certain Robot Framework features require optional external modules to be
installed, and naturally tests related to these features require same modules
as well:

- `docutils <http://docutils.sourceforge.net/>`_ is needed with tests related
  to parsing test data in reStructuredText format.
- `PyYAML <http://pyyaml.org/>`__ is required with tests related to YAML
   variable files.
- `lxml <http://lxml.de/>`__ is needed with XML library tests.

All of the above modules can be installed using ``pip``. It is possible to
install them individually or in a one go by using the provided
`<requirements.txt>`__ file::

    # Install individually
    pip install 'docutils>=0.9'
    pip install pyyaml
    pip install lxml

    # Install using requirements.txt
    pip install -r atest/requirements.txt

Notice that the lxml module requires compilation on Linux. You can also install
it using a system package manager like ``apt-get install python-lxml``.
Additionally lxml is not compatible with Jython or IronPython.

If a required module is not installed, it is possible to exclude tests
from the execution by using tags as explained in the `Test tags`_ section.
The lxml related tests are excluded with Jython and IronPython automatically.

Telnet tests
------------

Running telnet tests requires some extra setup. Instructions how to run them
can be found from `<testdata/standard_libraries/telnet/README.rst>`_.
If you don't want to run an unprotected telnet server on your machine, you can
always skip these tests by excluding tests with a tag ``telnet`` or ``no-ci``.
