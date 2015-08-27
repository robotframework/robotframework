=====================
Robot Framework 2.9.1
=====================

.. default-role:: code

Robot Framework 2.9.1 is a new release with bug fixes to embedded arguments handling 
(#2095, #2098, #2105), `Run Keyword If Test Failed/Passed` and ignored failures (#2108), 
and java integration (#2088). It was released on Thursday August 27, 2015.
All issues targeted for RF 2.9.1 can be found from the `issue tracker
<https://github.com/robotframework/robotframework/issues?q=milestone%3A2.9.1>`_.

Questions and comments related to the release can be sent to the
`robotframework-users <http://groups.google.com/group/robotframework-users>`_
and possible bugs `submitted to the issue tracker
<https://github.com/robotframework/robotframework/issues>`__.

If you have `pip <http://pip-installer.org>`_ installed, just run
`pip install --upgrade robotframework` to install or upgrade to the latest
version or use `pip install robotframework==2.9.1` to install exactly
this version.  For more details and other installation approaches, see
`installation instructions <../../INSTALL.rst>`_.

Robot Framework 2.9.1 was released on Friday August 28, 2015.

.. contents::
   :depth: 2
   :local:

Most important enhancements
===========================

Embedded arguments fixes
------------------------

There was a regression in embedded arguments handling, which caused keywords with same name, 
but different regular expression to fail (#2095). The same issue also prevented creating keywords
with a name that matched the name of an earlier embedded arguments keyword (#2098).

There was also a bug which prevented using library keyword with embedded arguments when a library was imported with a
custom name (#2105).

Java integration cleanup
------------------------

There was a bug in the Robot Framework Java API which sometimes caused stack traces to be printed
on standard output (#2088).

`Run Keyword If Test Failed/Passed` and ignored failures
--------------------------------------------------------

There was a bug which caused ignored errors to show as a
test failure with `Run Keyword If Test Failed/Passed` (#2108)

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

Warning if test library has multiple functions resulting same keyword
---------------------------------------------------------------------

There is now a warning if a library has multiple functions result in the same keyword (#2097).

Full list of fixes and enhancements
===================================

.. list-table::
    :header-rows: 1

    * - ID
      - Type
      - Priority
      - Summary
    * - #2088
      - bug
      - high
      - Cleanup Jython Interpreter when executing Robot Framework though Java API
    * - #2095
      - bug
      - high
      - Embedded arguments do not work anymore if keyword name is same but regexp is different
    * - #2098
      - bug
      - high
      - Creating keyword with name matching earlier embedded arguments keyword fails
    * - #2105
      - bug
      - high
      - Keywords with embedded arguments broken if library imported with custom name
    * - #2108
      - bug
      - high
      - `Run Keyword If Test Failed/Passed` do not handle earlier ignored failures correctly
    * - #2097
      - bug
      - medium
      - No warning if test library has multiple functions resulting same keyword
    * - #2110
      - bug
      - medium
      - Libdoc HTML - Shortcuts/links to keywords (having spaces) are not working with Internet Explorer (11 and others). 
    * - #2074
      - enhancement
      - medium
      - Release notes should be in code repository
    * - #2089
      - enhancement
      - medium
      - `Should Be Equal` should show better multiline diffs
    * - #2096
      - bug
      - low
      - Explicitly given library keyword name should not be altered
    * - #2113
      - bug
      - low
      - `OperatingSystem`: Path looking like glob pattern not always handled correctly
    * - #2109
      - enhancement
      - low
      - Explicitly state that shell shouldn't be used in Process library documentation

Altogether 12 issues. View on `issue tracker <https://github.com/robotframework/robotframework/issues?q=milestone%3A2.9.1>`__.
