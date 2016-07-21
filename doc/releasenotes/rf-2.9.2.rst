=====================
Robot Framework 2.9.2
=====================

.. default-role:: code

Robot Framework 2.9.2 is a new release that fixes broken AutoItLibrary
support, adds IronPython support to the Dialogs library, and contains
several other fixes and enhancements.

Questions and comments related to the release can be sent to the
`robotframework-users <http://groups.google.com/group/robotframework-users>`_
and possible bugs `submitted to the issue tracker
<https://github.com/robotframework/robotframework/issues>`__.

If you have `pip <http://pip-installer.org>`_ installed, just run
`pip install --upgrade robotframework` to install or upgrade to the latest
version or use `pip install robotframework==2.9.2` to install exactly
this version.  For more details and other installation approaches, see
`installation instructions <../../INSTALL.rst>`_.

Robot Framework 2.9.2 was released on Friday October 09, 2015.

.. contents::
   :depth: 2
   :local:

Most important enhancements
===========================

The most important new enhancement is the support for the Dialogs library on
IronPython (`#1235`_). Robot Framework 2.9.2 also fixes the AutoItLibrary
compatibility that was broken in 2.9.1 (`#2147`_) and invalid list and dict
variables no longer crash the whole test execution (`#2131`_).

Backwards incompatible changes
==============================

It used to be possible to access file objects as Robot Framework lists:

.. code:: robotframework

    *** Test Cases ***
    Example
        ${file} =    Evaluate    open('foo.txt')
        Log many    @{file}    # logs each row of file

This was never intentional and is now removed in 2.9.2 (`#2162`_). It is 
still possible to access all lines of a file object using extended variable
syntax:

.. code:: robotframework

    *** Test Cases ***
    Example
        ${file} =    Evaluate    open('foo.txt')
        Log many    @{file.readlines()}    # logs each row of file

Deprecated features
===================

All keywords operating with started processes in the OperatingSystem library,
have been deprecated (`#2158`_). Previously only `Start Process` keyword itself
was deprecated. The Process library should be used instead.

Acknowledgements
================

Many thanks to Tim Orling for implementing the support for Dialogs library on
IronPython (`#1235`_) and to Vinicius K. Ruoso for allowing control over
connection timeout in Telnet library (`#2079`_) and suppressing docutils
warnings when using the reStructuredText format (`#2093`_).

Full list of fixes and enhancements
===================================

.. list-table::
    :header-rows: 1

    * - ID
      - Type
      - Priority
      - Summary
    * - `#2147`_
      - bug
      - critical
      - AutoItLibrary not compatible with RF 2.9.1
    * - `#2131`_
      - bug
      - high
      - Invalid list and dict variables not handled correctly, in worst case causing crashes
    * - `#1235`_
      - enhancement
      - high
      - IronPython support for `Dialogs` library
    * - `#1996`_
      - bug
      - medium
      - DateTime library does not support dates in distant past (hard limit 1900, on Windows 1970)
    * - `#2130`_
      - bug
      - medium
      - DateTime: `Convert Date` changes time part when close to DTS boundary
    * - `#2133`_
      - bug
      - medium
      - rebot discards warning messages in merge mode
    * - `#2146`_
      - bug
      - medium
      - XML: Parsing XML with processing instructions fails with lxml
    * - `#2153`_
      - bug
      - medium
      - `Copy/Move File` fails if source and destination are same
    * - `#2156`_
      - bug
      - medium
      - `Get Library Instance` doesn't work if library has space in name
    * - `#2162`_
      - bug
      - medium
      - Variables containing file objects should not be considered list-like
    * - `#2077`_
      - enhancement
      - medium
      - Optional parameter to choose screenshot module.
    * - `#2079`_
      - enhancement
      - medium
      - Telnet Library: Allowing control over connection timeout
    * - `#2091`_
      - enhancement
      - medium
      - Cleanup acceptance tests
    * - `#2093`_
      - enhancement
      - medium
      - Suppress docutils errors/warnings with reST format
    * - `#2141`_
      - enhancement
      - medium
      - Small XML library enhancements
    * - `#2143`_
      - enhancement
      - medium
      - Add PyYAML to standalone jar
    * - `#2148`_
      - enhancement
      - medium
      - Take screenshot on OSX using `screencapture` tool when using Python
    * - `#2160`_
      - enhancement
      - medium
      - Keywords to split and join command line arguments
    * - `#2163`_
      - enhancement
      - medium
      - `Pop From Dictionary` keyword to `Collections`
    * - `#2170`_
      - enhancement
      - medium
      - BuiltIn: Possibility to get all library instances
    * - `#2129`_
      - bug
      - low
      - `Builtin.set_suite_(documentation|metadata)` raises `AttributeError` instead of `RobotNotRunningError`
    * - `#2151`_
      - bug
      - low
      - Libdoc: Creating documentation fails if library has multiple keywords with same name
    * - `#2158`_
      - enhancement
      - low
      - OperatingSystem: Deprecate all keywords related to `Start Process`
    * - `#2164`_
      - enhancement
      - low
      - Possibility to show internal traces when keywords fail
    * - `#2167`_
      - enhancement
      - low
      - `Copy/Move File` should return destination path
    * - `#2168`_
      - enhancement
      - low
      - `ROBOT_OPTIONS` and `REBOT_OPTIONS` should allow spaces in values when surrounded by quotes

Altogether 26 issues. View on `issue tracker <https://github.com/robotframework/robotframework/issues?q=milestone%3A2.9.2>`__.

.. _User Guide: http://robotframework.org/robotframework/#user-guide
.. _#2147: https://github.com/robotframework/robotframework/issues/2147
.. _#2131: https://github.com/robotframework/robotframework/issues/2131
.. _#1235: https://github.com/robotframework/robotframework/issues/1235
.. _#1996: https://github.com/robotframework/robotframework/issues/1996
.. _#2130: https://github.com/robotframework/robotframework/issues/2130
.. _#2133: https://github.com/robotframework/robotframework/issues/2133
.. _#2146: https://github.com/robotframework/robotframework/issues/2146
.. _#2153: https://github.com/robotframework/robotframework/issues/2153
.. _#2156: https://github.com/robotframework/robotframework/issues/2156
.. _#2162: https://github.com/robotframework/robotframework/issues/2162
.. _#2077: https://github.com/robotframework/robotframework/issues/2077
.. _#2079: https://github.com/robotframework/robotframework/issues/2079
.. _#2091: https://github.com/robotframework/robotframework/issues/2091
.. _#2093: https://github.com/robotframework/robotframework/issues/2093
.. _#2141: https://github.com/robotframework/robotframework/issues/2141
.. _#2143: https://github.com/robotframework/robotframework/issues/2143
.. _#2148: https://github.com/robotframework/robotframework/issues/2148
.. _#2160: https://github.com/robotframework/robotframework/issues/2160
.. _#2163: https://github.com/robotframework/robotframework/issues/2163
.. _#2170: https://github.com/robotframework/robotframework/issues/2170
.. _#2129: https://github.com/robotframework/robotframework/issues/2129
.. _#2151: https://github.com/robotframework/robotframework/issues/2151
.. _#2158: https://github.com/robotframework/robotframework/issues/2158
.. _#2164: https://github.com/robotframework/robotframework/issues/2164
.. _#2167: https://github.com/robotframework/robotframework/issues/2167
.. _#2168: https://github.com/robotframework/robotframework/issues/2168
