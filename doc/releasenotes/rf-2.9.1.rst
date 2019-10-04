=====================
Robot Framework 2.9.1
=====================

.. default-role:: code

Robot Framework 2.9.1 is a bug fix release that fixes few high priority bugs in
`Robot Framework 2.9 <rf-2.9.rst>`_. Most important fixes are explained below
and all issues listed in the table at the end.

Questions and comments related to the release can be sent to the
`robotframework-users <http://groups.google.com/group/robotframework-users>`_
and possible bugs `submitted to the issue tracker
<https://github.com/robotframework/robotframework/issues>`__.

Robot Framework 2.9.1 was released on Friday August 28, 2015.

.. contents::
   :depth: 2
   :local:

Installation
============

Source distribution and Windows installers are available at `PyPI
<https://pypi.python.org/pypi/robotframework/2.9.1>`_ and the standalone JAR
with Jython 2.7 at `Maven central
<http://search.maven.org/#search%7Cga%7C1%7Ca%3Arobotframework>`_.

If you have `pip <http://pip-installer.org>`_ installed, just run
`pip install --upgrade robotframework` to install or upgrade to the latest
version or use `pip install robotframework==2.9.1` to install exactly
this version.

For more details and other installation approaches, see the
`full installation instructions <../../INSTALL.rst>`_.

Most important fixes
====================

Embedded arguments fixes
------------------------

There was a regression in embedded arguments handling, which caused keywords
with same name, but different regular expression to fail (`#2095`_). The same
issue also prevented creating keywords with a name that matched the name of
an earlier embedded arguments keyword (`#2098`_).

Another bug prevented using library keyword with embedded arguments when the
library was imported with a custom name (`#2105`_).

Java integration fixes
----------------------

There was a bug in the Robot Framework Java API that manifested itself with
Jython 2.7 and caused problems with Maven (`#2088`_). This bug has prevented
creating RF 2.9 compatible `Maven plugin
<https://github.com/robotframework/MavenPlugin>`__.

`Run Keyword If Test Failed/Passed` and ignored failures
--------------------------------------------------------

There was a bug which caused ignored errors to be considered test failures
with `Run Keyword If Test Failed/Passed` keywords (`#2108`_). For example,
the test below would fail with a message `Test should have passed`:

.. code:: robotframework

    *** Test Cases ***
    Example
        No Operation
        [Teardown]    Teardown bug

    *** Keywords ***
    Teardown bug
        Run Keyword And Ignore Error
        ...    Fail    This error should be ignored
        Run Keyword If Test Failed
        ...    Fail    Test should have passed

Backwards incompatible changes
==============================

Creating keywords with same name in test libraries fails
--------------------------------------------------------

Earlier it has been possible that a test library contains multiple functions
that create keywords with same name (e.g. `example_keyword` and
`exampleKeyword`) and it was ambiguous which implementation was actually used.
Nowadays such usage causes errors and trying to use the keyword fails
(`#2097`_).

Full list of fixes and enhancements
===================================

.. list-table::
    :header-rows: 1

    * - ID
      - Type
      - Priority
      - Summary
    * - `#2088`_
      - bug
      - high
      - Cleanup Jython Interpreter after executing Robot Framework though Java API
    * - `#2095`_
      - bug
      - high
      - Embedded arguments do not work anymore if keyword name is same but regexp is different
    * - `#2098`_
      - bug
      - high
      - Creating keyword with name matching earlier embedded arguments keyword fails
    * - `#2105`_
      - bug
      - high
      - Keywords with embedded arguments broken if library imported with custom name
    * - `#2108`_
      - bug
      - high
      - `Run Keyword If Test Failed/Passed` do not handle earlier ignored failures correctly
    * - `#2097`_
      - bug
      - medium
      - No error if test library has multiple functions resulting same keyword
    * - `#2110`_
      - bug
      - medium
      - Libdoc HTML - Shortcuts/links to keywords (having spaces) are not working with Internet Explorer (11 and others).
    * - `#2113`_
      - bug
      - medium
      - `OperatingSystem`: Path looking like glob pattern not always handled correctly
    * - `#2074`_
      - enhancement
      - medium
      - Release notes should be in code repository
    * - `#2089`_
      - enhancement
      - medium
      - `Should Be Equal` should show better multiline diffs
    * - `#2096`_
      - bug
      - low
      - Explicitly given library keyword name should not be altered
    * - `#2109`_
      - enhancement
      - low
      - Explicitly state that shell shouldn't be used in Process library documentation

Altogether 12 issues. View on `issue tracker <https://github.com/robotframework/robotframework/issues?q=milestone%3A2.9.1>`__.

.. _User Guide: http://robotframework.org/robotframework/#user-guide
.. _#2088: https://github.com/robotframework/robotframework/issues/2088
.. _#2095: https://github.com/robotframework/robotframework/issues/2095
.. _#2098: https://github.com/robotframework/robotframework/issues/2098
.. _#2105: https://github.com/robotframework/robotframework/issues/2105
.. _#2108: https://github.com/robotframework/robotframework/issues/2108
.. _#2097: https://github.com/robotframework/robotframework/issues/2097
.. _#2110: https://github.com/robotframework/robotframework/issues/2110
.. _#2074: https://github.com/robotframework/robotframework/issues/2074
.. _#2089: https://github.com/robotframework/robotframework/issues/2089
.. _#2096: https://github.com/robotframework/robotframework/issues/2096
.. _#2113: https://github.com/robotframework/robotframework/issues/2113
.. _#2109: https://github.com/robotframework/robotframework/issues/2109
