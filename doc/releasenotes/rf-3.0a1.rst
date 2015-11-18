=====================
Robot Framework 3.0a1
=====================

.. default-role:: code

Robot Framework 3.0 alpha 1 is the first preview of the upcoming next major
version of Robot Framework. The biggest change in 3.0 will be Python 3 support,
but there are also several backwards incompatible changes. Some of these we
might still revert in later preview releases if it turns out that some of them
cause too much compatibility problems.

All issues targeted for RF 3.0 can be found from the `issue tracker
<https://github.com/robotframework/robotframework/issues?q=milestone%3A3.0>`_.

Questions and comments related to the release can be sent to the
`robotframework-users <http://groups.google.com/group/robotframework-users>`_
and possible bugs `submitted to the issue tracker
<https://github.com/robotframework/robotframework/issues>`__.

If you have `pip <http://pip-installer.org>`_ installed, just run
`pip install --upgrade --pre robotframework` to install or upgrade to the latest
version or use `pip install --pre robotframework==3.0a1` to install exactly
this version.  For more details and other installation approaches, see
`installation instructions <../../INSTALL.rst>`_.

Robot Framework 3.0a1 was released on **CHECK** Monday November 16, 2015.

.. contents::
   :depth: 2
   :local:

Most important enhancements
===========================

Python 3 support
----------------

Robot Framework 3.0 supports Python versions 2.6, 2.7, and Python 3 versions
from 3.3 up (`#1506`_). Installation on Python 3 works exactly as it does for
Python 2, and the recommended installation method is with pip:
`pip install --pre robotframework`. Note that there will be `no more Windows
installers`_.

There is no separate runner script for running Robot Framework on Python 3, but
along the usual `pybot` and `rebot` scripts, there now also a new runner script
`robot` (`#2216`_), which executes Robot Framework for the interpreter that was
used for the installation.

Note that while the standard libraries distributed with Robot Framework do work
with Python 3, most other external libraries currently do not.

Backwards incompatible changes
==============================

`OperatingSystem.Start Process` and related keywords removed
------------------------------------------------------------

Keywords related to process handling in `OperatingSystem` library were
deprecated in 2.9 in favour of the new `Process` library. Now these keywords
have been removed (`#2181`_). Please use the
`Process keywords <http://robotframework.org/robotframework/latest/libraries/Process.html>`_
instead.

Several deprecated commandline options removed
----------------------------------------------

Several command line options were deprecated in RF 2.9 and are now removed
in RF 3.0 (`#2203`_). The following table lists the options to be removed, their
replacement, possible short option, and when the replacement was added.
Notice that short options have now changed so they can be used if both old and
new versions need to be supported.

================  ================  ============  ==========================
To be removed     Replacement       Short option  When replacement was added
================  ================  ============  ==========================
--runfailed       --rerunfailed                   RF 2.8.4 (`#1641`_)
--rerunmerge      --merge                         RF 2.8.6 (`#1687`_)
--monitorcolors   --consolecolors   -C            RF 2.9 (`#2027`_)
--monitowidth     --consolewidth    -W            RF 2.9 (`#2027`_)
--monitormarkers  --consolemarkers  -K            RF 2.9 (`#2027`_)
================  ================  ============  ==========================

Listener API 1 removed
----------------------

Old listener API version 1 was deprecated in 2.9 in favour of the version 2,
which was introduced already back in Robot Framework 2.1 (`#88`_). 3.0 finally
removes the version 1 of the API (`#2206`_). From now on you will always need
to specify the API version in your listener with `ROBOT_LISTENER_API_VERSION`.

No more Windows installers
--------------------------

Earlier Robot Framework versions have been distributed also as Windows
installers, but we have decided not to continue making them in Robot Framework
3.0 (`#2218`_). The ways to install Robot Framework 3.0 are:

- Using pip online `pip install --pre robotframework`
- Using pip with local file `pip install robotframework-3.0a1.tar.gz`
- By extracting the tar file and installing manually: `python setup.py install`

Other backwards incompatible changes:
- `#2184`_ Remove `DeprecatedBuiltIn` and `DeprecatedOperatingSystem` libraries (alpha 1)
- `#2197`_ Write redirected console output using system encoding, not console encoding (alpha 1)
- `#2200`_ Changes to internal utility functions and classes (alpha 1)
- `#2202`_ Remove aliases from `robot.utils.asserts` (alpha 1)
- `#2204`_ Make it an error if same setting is used multiple times (alpha 1)
- `#2205`_ Remove old `Meta: Name` syntax for specifying test suite metadata  (alpha 1)

.. _#88: https://github.com/robotframework/robotframework/issues/88
.. _#1641: https://github.com/robotframework/robotframework/issues/1641
.. _#1687: https://github.com/robotframework/robotframework/issues/1687
.. _#2027: https://github.com/robotframework/robotframework/issues/2027

Deprecated features
===================

Deprecated synonyms for settings and table names
------------------------------------------------

Setting names `Document` and `Suite/Test Pre/Post Condition` have been
deprecated in favour of `Documentation` and `Suite/Test Setup/Teardown`
(`#2207`_) and table names `Metadata` and `User Keyword` in favour or
`Settings` and `Keywords` (`#2208`_). None of examples in the user guide or the
demo projects have used these deprecated forms, so we are assuming that they are
not widely used. If however some of these are in common use, we can still
consider removing the deprecation warning and supporting them in the future.

Acknowledgements
================

**UPDATE** based on AUTHORS.txt.

Full list of fixes and enhancements
===================================

.. list-table::
    :header-rows: 1

    * - ID
      - Type
      - Priority
      - Summary
      - Added
    * - `#1506`_
      - enhancement
      - critical
      - Python 3 support
      - alpha 1
    * - `#2188`_
      - bug
      - medium
      - `${TEST_MESSAGE}` is not updated by `Set Test Message` keyword
      - alpha 1
    * - `#2181`_
      - enhancement
      - medium
      - Remove deprecated `OperatingSystem.Start Process` and related keywords
      - alpha 1
    * - `#2184`_
      - enhancement
      - medium
      - Remove `DeprecatedBuiltIn` and `DeprecatedOperatingSystem` libraries
      - alpha 1
    * - `#2196`_
      - enhancement
      - medium
      - OperatingSystem: `Get File` and `Create File` should support native encodings
      - alpha 1
    * - `#2197`_
      - enhancement
      - medium
      - Write redirected console output using system encoding, not console encoding
      - alpha 1
    * - `#2198`_
      - enhancement
      - medium
      - Process: Allow configuring output encoding
      - alpha 1
    * - `#2216`_
      - enhancement
      - medium
      - New `robot` starter script
      - alpha 1
    * - `#2180`_
      - bug
      - low
      - Collections: Multiple dictionary keywords fail if keys are unorderable
      - alpha 1
    * - `#2200`_
      - enhancement
      - low
      - Changes to internal utility functions and classes
      - alpha 1
    * - `#2202`_
      - enhancement
      - low
      - Remove aliases from `robot.utils.asserts`
      - alpha 1
    * - `#2203`_
      - enhancement
      - low
      - Remove deprecated command line options
      - alpha 1
    * - `#2204`_
      - enhancement
      - low
      - Make it an error if same setting is used multiple times
      - alpha 1
    * - `#2205`_
      - enhancement
      - low
      - Remove old `Meta: Name` syntax for specifying test suite metadata
      - alpha 1
    * - `#2206`_
      - enhancement
      - low
      - Remove deprecated listener API version 1
      - alpha 1
    * - `#2207`_
      - enhancement
      - low
      - Deprecate `Document` and `Suite/Test Pre/Post Condition` synonym settings
      - alpha 1
    * - `#2208`_
      - enhancement
      - low
      - Deprecate `Metadata` and `User Keyword` table names
      - alpha 1

Altogether 17 issues. View on `issue tracker <https://github.com/robotframework/robotframework/issues?q=milestone%3A3.0>`__.

.. _User Guide: http://robotframework.org/robotframework/#user-guide
.. _#1506: https://github.com/robotframework/robotframework/issues/1506
.. _#2188: https://github.com/robotframework/robotframework/issues/2188
.. _#2181: https://github.com/robotframework/robotframework/issues/2181
.. _#2184: https://github.com/robotframework/robotframework/issues/2184
.. _#2196: https://github.com/robotframework/robotframework/issues/2196
.. _#2197: https://github.com/robotframework/robotframework/issues/2197
.. _#2198: https://github.com/robotframework/robotframework/issues/2198
.. _#2216: https://github.com/robotframework/robotframework/issues/2216
.. _#2180: https://github.com/robotframework/robotframework/issues/2180
.. _#2200: https://github.com/robotframework/robotframework/issues/2200
.. _#2202: https://github.com/robotframework/robotframework/issues/2202
.. _#2203: https://github.com/robotframework/robotframework/issues/2203
.. _#2204: https://github.com/robotframework/robotframework/issues/2204
.. _#2205: https://github.com/robotframework/robotframework/issues/2205
.. _#2206: https://github.com/robotframework/robotframework/issues/2206
.. _#2207: https://github.com/robotframework/robotframework/issues/2207
.. _#2208: https://github.com/robotframework/robotframework/issues/2208
.. _#2218: https://github.com/robotframework/robotframework/issues/2218
