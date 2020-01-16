Robot Framework acceptance tests
================================

Acceptance tests for Robot Framework are naturally created using Robot
Framework itself. This folder contains all those acceptance tests and other
test data they need.

.. contents::
   :local:

Directory contents
------------------

run.py
    A script for running acceptance tests. See `Running acceptance tests`_
    for further instructions.

robot/
    Contains actual acceptance test cases. See `Test data`_ section for details.

resources/
    Resources needed by acceptance tests in the ``robot`` folder.

testdata/
    Contains test cases that are run by actual acceptance tests in the
    ``robot`` folder. See `Test data`_ section for details.

testresources/
    Contains resources needed by test cases in the ``testdata`` folder.
    Some of these resources are also used by `unit tests <../utest/README.rst>`_.

results/
    The place for test execution results. This directory is generated when
    acceptance tests are executed. It is in ``.gitignore`` and can be safely
    deleted any time.

genrunner.py
    Script to generate acceptance test runners (i.e. files under the ``robot``
    directory) based on the test data files (i.e. files under the ``testdata``
    directory). Mainly useful if there is one-to-one mapping between tests in
    the ``testdata`` and ``robot`` directories.

    Usage:  ``atest/genrunner.py atest/testdata/path/data.robot [atest/robot/path/runner.robot]``

Running acceptance tests
------------------------

Robot Framework's acceptance tests are executed using the `<run.py>`__
script. It has two mandatory arguments, the Python interpreter to use
when running tests and path to tests to be executed, and it accepts also
all same options as Robot Framework. The script itself should always be
executed with Python 3.6 or newer. Run it with ``--help`` or see
documentation in its `source code <run.py>`__ for more information.

To run all the acceptance tests, execute the ``atest/robot`` folder
entirely using the selected interpreter::

    atest/run.py python atest/robot
    atest/run.py jython atest/robot

The commands above will execute all tests, but you typically want to skip
`Telnet tests`_ and tests requiring manual interaction. These tests are marked
with the ``no-ci`` tag and can be easily excluded::

    atest/run.py python --exclude no-ci atest/robot

A sub test suite can be executed simply by running the folder or file
containing it. On modern machines running all acceptance tests ought to
take less than ten minutes with Python, but with Jython the execution time
is considerably longer. This is due to Jython being somewhat slower than
Python in general, but the main reason is that the JVM is started by
acceptance tests dozens of times and that always takes a few seconds.

Before a release tests should be executed separately using Python, Jython,
IronPython and PyPy to verify interoperability with all supported interpreters.
Tests should also be run using different interpreter versions (when applicable)
and on different operating systems.

The results of the test execution are written into an interpreter specific
directory under the ``atest/results`` directory. Temporary outputs created
during the execution are created under the system temporary directory.

Test data
---------

The test data is divided into two, test data part (``atest/testdata`` folder) and
running part (``atest/robot`` folder). Test data side contains test cases for
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

Test tags
---------

The tests on the running side (``atest/robot``) contain tags that are used
to include or exclude them based on the platform and required dependencies.
Selecting tests based on the platform is done automatically by the `<run.py>`__
script, but additional selection can be done by the user to avoid running
tests with `preconditions`_ that are not met.

manual
  Require manual interaction from user. Used with Dialogs library tests.

telnet
  Require a telnet server with test account running at localhost. See
  `Telnet tests`_ for details.

no-ci
  Tests which are not executed at continuous integration. Contains all tests
  tagged with ``manual`` or ``telnet``.

require-yaml, require-enum, require-docutils, require-pygments, require-lxml, require-screenshot, require-tools.jar
  Require specified Python module or some other external tool to be installed.
  See `Preconditions`_ for details and exclude like ``--exclude require-lxml``
  if needed.

require-windows, require-jython, require-py2, require-py3, ...
  Tests that require certain operating system or Python interpreter.
  Excluded automatically outside these platforms.

no-windows, no-osx, no-jython, no-ipy, ...
  Tests to be excluded on certain operating systems or Python interpreters.
  Excluded automatically on these platforms.

Examples:

.. code:: bash

    # Exclude tests requiring manual interaction or running telnet server.
    atest/run.py python --exclude no-ci atest/robot

    # Same as the above but also exclude tests requiring docutils and lxml
    atest/run.py python -e no-ci -e require-docutils -e require-lxml atest/robot

    # Run only tests related to Java integration. This is considerably faster
    # than running all tests on Jython.
    atest/run.py jython --include require-jython atest/robot

Preconditions
-------------

Certain Robot Framework features require optional external modules or tools
to be installed, and naturally tests related to these features require same
modules/tools as well. This section lists what preconditions are needed to
run all tests successfully. See `Test tags`_ for instructions how to avoid
running certain tests if all preconditions are not met.

Required Python modules
~~~~~~~~~~~~~~~~~~~~~~~

These Python modules need to be installed:

- `docutils <http://docutils.sourceforge.net/>`_ is needed with tests related
  to parsing test data in reStructuredText format and with Libdoc tests
  for documentation in reST format. `Not compatible with IronPython
  <https://github.com/IronLanguages/ironpython2/issues/113>`__.
- `Pygments <http://pygments.org/>`_ is needed by Libdoc tests for syntax
  highlighting.
- `PyYAML <http://pyyaml.org/>`__ is required with tests related to YAML
  variable files.
- `enum34 <https://pypi.org/project/enum34/>`__ (or older
  `enum <https://pypi.org/project/enum/>`__) by enum conversion tests.
  This module is included by default in Python 3.4 and newer.
- `lxml <http://lxml.de/>`__ is needed with XML library tests. Not compatible
  with Jython or IronPython.

It is possible to install the above modules using ``pip`` either
individually or by using the provided `<requirements.txt>`__ file:

.. code:: bash

    # Install individually
    pip install 'docutils>=0.9'
    pip install pygments
    pip install pyyaml
    pip install enum34    # Needed only with Python 2.
    pip install lxml

    # Install using requirements.txt
    pip install -r atest/requirements.txt

Notice that the lxml module may require compilation on Linux, which in turn
may require installing development headers of lxml dependencies. Alternatively
lxml can be installed using a system package manager with a command like
``sudo apt-get install python-lxml``.

Because lxml is not compatible with Jython or IronPython, tests requiring it
are excluded automatically when using these interpreters.

Screenshot module or tool
~~~~~~~~~~~~~~~~~~~~~~~~~

Screenshot library tests require a platform dependent module or tool that can
take screenshots. See `Screenshot library documentation`__ for details.

__ http://robotframework.org/robotframework/latest/libraries/Screenshot.html

``tools.jar``
~~~~~~~~~~~~~

When using Java 8 or earlier, Libdoc requires ``tools.jar``, which is part
of the standard JDK installation, to be in ``CLASSPATH`` when reading library
documentation from Java source files. In addition to setting ``CLASSPATH``
explicitly, it is possible to put ``tools.jar`` into the ``ext-lib``
directory in the project root and ``CLASSPATH`` is set automatically.

Telnet tests
------------

Running telnet tests requires some extra setup. Instructions how to run them
can be found from `<testdata/standard_libraries/telnet/README.rst>`_.
If you don't want to run an unprotected telnet server on your machine, you can
always skip these tests by excluding tests with a tag ``telnet`` or ``no-ci``.

License and copyright
---------------------

All content in the ``atest`` folder is under the following copyright::

    Copyright 2008-2015 Nokia Networks
    Copyright 2016-     Robot Framework Foundation

    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at

        http://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.
