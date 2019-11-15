===================
Robot Framework 3.0
===================

.. default-role:: code

Robot Framework 3.0 is a new major release with Python 3 support and a new
powerful listener interface that allows modifying executed tests as well as
execution results. Also start-up scripts have been enhanced and it is now
possible to run tests with new `robot` command and like `python -m robot`.

Questions and comments related to the release can be sent to the
`robotframework-users <http://groups.google.com/group/robotframework-users>`_
and possible bugs `submitted to the issue tracker
<https://github.com/robotframework/robotframework/issues>`__.

Robot Framework 3.0 was released on Thursday December 31, 2015.

.. contents::
   :depth: 2
   :local:

Installation
============

The easiest way to install or upgrade to the latest version is using
`pip <http://pip-installer.org>`_::

    pip install --upgrade robotframework

Alternatively you can download the source distribution from `PyPI
<https://pypi.python.org/pypi/robotframework>`_, extract it, and install it
by running::

    python setup.py install

For more details, including installing Python, Jython and IronPython, see
the `installation instructions <../../INSTALL.rst>`_.

The standalone JAR distribution with Jython 2.7 is available at `Maven central
<http://search.maven.org/#search%7Cga%7C1%7Ca%3Arobotframework>`_.
Separate Windows installers `are not created anymore <#2218_>`_.

Upgrading from earlier versions
-------------------------------

As usual with new major releases, there are some `backwards incompatible
changes`_ and `deprecated features`_ that should be taken into account
especially when upgrading larger amount of tests or bigger test infrastructure
to Robot Framework 3.0.

Some of the removed features were deprecated only in `Robot Framework 2.9
<rf-2.9.rst>`_. If you encounter lot of errors when upgrading from RF 2.8
or earlier, it might be a good idea to upgrade first to `RF 2.9.2
<rf-2.9.2.rst>`_ to get deprecation warnings about features that have now
be removed altogether.

Most important enhancements
===========================

Python 3 support
----------------

Robot Framework 3.0 adds support for Python 3 (`#1506`_). More precisely, the
currently supported Python versions are 2.6, 2.7, and 3.3 and newer.
Installation on Python 3 works exactly as it does for Python 2, and
the recommended installation method is with pip::

    pip3 install robotframework
    python3 -m pip install robotframework

Note that while the standard libraries distributed with Robot Framework do work
with Python 3, most other external libraries and tools currently do not.

New listener interface that can modify executed tests and results
-----------------------------------------------------------------

New listener API version that receives actual data and result model objects
Robot Framework itself uses as arguments has been added (`#1208`_).
It is possible to query information from these objects more fluently
than when using the old listener API, but more importantly these objects
can be modified so that the executed tests and/or created results are affected.

For more information about the new listener API, including interesting
usage examples, see the `Listener interface`__ section from Robot
Framework User Guide.

__ http://robotframework.org/robotframework/latest/RobotFrameworkUserGuide.html#listener-interface

New `robot` start-up script
---------------------------

New generic `robot` start-up script has been introduced to allow running tests
like `robot tests.robot` regardless the Python interpreter (`#2216`_).
Old interpreter specific `pybot`, `jybot` and `ipybot` scripts still work as
earlier, but the plan is to deprecate and remove them in the future major
releases.

The old `rebot` script has also been made generic and is installed with all
Python interpreters. Old `jyrebot` and `ipyrebot` scripts work for now.

Possibility to run tests with `python -m robot`
-----------------------------------------------

Earlier it has been possible to run tests with `python -m robot.run`
but now also shorter version `python -m robot` is supported (`#2223`_).
Using this approach is especially useful if Robot Framework is used with
multiple Python interpreters like, for example,  `python3 -m robot`,
`/opt/jython27/jython -m robot` or `ipy -m robot`.

A limitation of the `python -m robot` approach is that it does not work with
Python 2.6. The old `python -m robot.run` version can be used instead.

The same enhancement that made `python -m robot` possible also made it possible
to execute the `robot` installation directory like `python path/to/robot`.
This works the same way as `python path/to/robot/run.py` that works also
with the earlier versions.

Listeners no longer slow down execution
---------------------------------------

Listeners used to slow down execution considerably, especially when keyword
arguments or return values were objects with a long string presentation
(`#2241`_). As part of the speedup fix for this issue, listeners no longer get
log messages below the active log level (`#2242`_).

Backwards incompatible changes
==============================

No more GUI installers for Windows
----------------------------------

Earlier Robot Framework versions have been distributed also as Windows
installers, but we have decided not to continue making them in Robot Framework
3.0 (`#2218`_). The ways to install Robot Framework 3.0 are:

1. Using pip online::

     pip install robotframework

2. Downloading the source distribution from PyPI_ and installing it using
   pip locally::

      pip install robotframework-3.0.tar.gz

3. Extracting the aforementioned source distribution, navigating to the created
   directory on the command line, and installing manually::

      python setup.py install

`OperatingSystem.Start Process` and related keywords removed
------------------------------------------------------------

Keywords related to starting processes in the `OperatingSystem` library were
deprecated in RF 2.9 in favour of better keywords in the `Process  library
<http://robotframework.org/robotframework/latest/libraries/Process.html>`_.
These keywords have been removed in RF 3.0 (`#2181`_) and the aforementioned
Process library must be used instead.

Several deprecated commandline options removed
----------------------------------------------

Several command line options were deprecated in RF 2.9 and are now removed
in RF 3.0 (`#2203`_). The following table lists the removed options, their
replacement, possible short option, and when the replacement was added.
Notice that short options have not changed, and they can thus be used if
both RF 2.8 and RF 3.0 need to be supported.

================  ================  ==============  ====================
    Removed         Replacement      Short option    Replacement added
================  ================  ==============  ====================
--runfailed       --rerunfailed                     RF 2.8.4 (`#1641`_)
--rerunmerge      --merge                           RF 2.8.6 (`#1687`_)
--monitorcolors   --consolecolors   -C              RF 2.9 (`#2027`_)
--monitowidth     --consolewidth    -W              RF 2.9 (`#2027`_)
--monitormarkers  --consolemarkers  -K              RF 2.9 (`#2027`_)
================  ================  ==============  ====================

.. _#1641: https://github.com/robotframework/robotframework/issues/1641
.. _#1687: https://github.com/robotframework/robotframework/issues/1687
.. _#2027: https://github.com/robotframework/robotframework/issues/2027

Listener API 1 removed
----------------------

Old listener API version 1 was deprecated in RF 2.9 in favour of the listener
version 2 which was introduced already back in Robot Framework 2.1 (`#88`_).
RF 3.0 finally removed the support for the listener API version 1 (`#2206`_).
From now on you will always need to specify the API version in your listener
with `ROBOT_LISTENER_API_VERSION`.

.. _#88: https://github.com/robotframework/robotframework/issues/88

Listeners no longer get log message below the active log level
--------------------------------------------------------------

Listeners used to get all log messages to `log_message` regardless of their
log level. This meant that taking a listener into use would cause a considerable
amount of `TRACE` level messages to be generated internally even if the active
log level was for example `INFO`. Now `log_message` will only be called for
messages that would be logged by the current active log level (`#2242`_). If
this change breaks some reasonable use case for listeners, we can consider
making it possible for listeners to set their own custom log level.

Keyword type passed to listeners has changed
--------------------------------------------

Keyword type passed to listeners was totally messed up with for loops and
keyword teardowns. Fixing the problem required changing how types are reported
in general. For more information about the new types and the original problem
see issue `#2248`_.

Other backwards incompatible changes
------------------------------------

- `DeprecatedBuiltIn` and `DeprecatedOperatingSystem` libraries have been removed (`#2184`_).
- Using same setting multiple times is an error (`#2204`_).
- Old `Meta: Name` syntax for specifying test suite metadata has been removed (`#2205`_).
- Test and keyword timeouts are written to output.xml as a separate `<timeout/>` element,
  not as an attribute for the `<kw>` element (`#2092`_).
- Executor's local variables can not be used in keyword timeouts (`#2092`_)
- Console output redirected to a file is written using system encoding, not console encoding (`#2197`_).
- Aliases from `robot.utils.asserts` module have been removed (`#2202`_).
- Changes to internal utility functions and classes (`#2200`_).
- `RunnerFactory` Java API has changed (`#2090`_).

Deprecated features
===================

Synonyms for settings
---------------------

Setting names `Document` and `Suite/Test Pre/Post Condition` have been
deprecated in favour of `Documentation` and `Suite/Test Setup/Teardown`,
respectively (`#2207`_). The motivation is to make the overall syntax
supported by Robot Framework simpler for users and for external tools.
None of examples in the Robot Framework User Guide or in the demo projects
have used these deprecated forms, and we assume that they are not widely used.
If, however, some of them are in common use, we can still consider removing
the deprecation warning and supporting them in the future.

Synonyms for tables
-------------------

Table names `Metadata` and `User Keyword` have been deprecated in favour of
`Settings` and `Keywords`, respectively (`#2208`_). Similarly as with
`deprecated synonyms for settings`_, the motivation is making the syntax
simpler, we do not expect them to be used too wildly, and we can consider
reverting the deprecation if our expectation is wrong.

Python 2.6 support
------------------

Robot Framework 3.0 still supports Python 2.6, but that support can be
considered deprecated. The plan is to drop Python 2.6 support in RF 3.1
(`#2276`_).

.. _#2276: https://github.com/robotframework/robotframework/issues/2276

Other deprecated features
-------------------------

- Using the `WITH NAME` syntax case-insensitively is deprecated. Only the
  all uppercase form will be supported in the future (`#2263`_).
- Importing libraries with extra spaces in the name like `Operating System`
  is deprecated (`#2264`_).
- Semi public API to register "run keyword variants" has been deprecated
  in order to be able to redesign it fully in the future (`#2265`_).
- Using `robot.running.TestSuite.(imports|variables|user_keywords)` properties
  programmatically is deprecated more loudly (`#2219`_).

Acknowledgements
================

Many thanks to Jozef Behran for fixing `${TEST_MESSAGE}` to reflect current test
message (`#2188`_), Michael Walle for `Strip String` keyword (`#2213`_), and
Joong-Hee Lee for adding timeout support for `Repeat keyword` (`#2245`_).

Full list of fixes and enhancements
===================================

.. list-table::
    :header-rows: 1

    * - ID
      - Type
      - Priority
      - Summary
    * - `#1208`_
      - enhancement
      - critical
      - New listener API that gets real suite/test objects as arguments and can modify them
    * - `#1506`_
      - enhancement
      - critical
      - Python 3 support
    * - `#2241`_
      - bug
      - high
      - Listeners slow down execution, especially when keyword arguments or return values are big
    * - `#2216`_
      - enhancement
      - high
      - New `robot` start-up script to replace `pybot`, `jybot` and `ipybot`
    * - `#2218`_
      - enhancement
      - high
      - No more binary installers for Windows
    * - `#2223`_
      - enhancement
      - high
      - Support executing tests with `python -m robot`
    * - `#2188`_
      - bug
      - medium
      - `${TEST_MESSAGE}` is not updated by `Set Test Message` keyword
    * - `#2192`_
      - bug
      - medium
      - `BuiltIn.Import Resource` does not work on standalone jar when no directories in `sys.path`
    * - `#2217`_
      - bug
      - medium
      - Error about non-existing variable in keyword return value cannot be caught
    * - `#2231`_
      - bug
      - medium
      - Parsing massive test case file takes lot of time
    * - `#2248`_
      - bug
      - medium
      - Keyword type passed to listeners is wrong with for loops and keyword teardowns
    * - `#2090`_
      - enhancement
      - medium
      - Cleanup `RunnerFactory` code in Java API
    * - `#2092`_
      - enhancement
      - medium
      - Possibility to specify keyword timeout using variable provided as argument
    * - `#2177`_
      - enhancement
      - medium
      - Show critical and non-critical patterns in statistics automatically
    * - `#2181`_
      - enhancement
      - medium
      - Remove deprecated `OperatingSystem.Start Process` and related keywords
    * - `#2184`_
      - enhancement
      - medium
      - Remove `DeprecatedBuiltIn` and `DeprecatedOperatingSystem` libraries
    * - `#2196`_
      - enhancement
      - medium
      - OperatingSystem: `Get File` and `Create File` should support native encodings
    * - `#2197`_
      - enhancement
      - medium
      - Write redirected console output using system encoding, not console encoding
    * - `#2198`_
      - enhancement
      - medium
      - Process: Allow configuring output encoding
    * - `#2213`_
      - enhancement
      - medium
      - String: New `Strip String` keyword
    * - `#2229`_
      - enhancement
      - medium
      - Screenshot: Support taking screenshot using `scrot` on Linux
    * - `#2238`_
      - enhancement
      - medium
      - Officially support imports from `sys.path` with `Import Library/Resource/Variables` keywords
    * - `#2242`_
      - enhancement
      - medium
      - Listeners should not get log messages below the active log level
    * - `#2245`_
      - enhancement
      - medium
      - BuiltIn: Support also timeout with `Repeat Keyword`
    * - `#2257`_
      - enhancement
      - medium
      - Allow using previous arguments in user keyword default values
    * - `#2271`_
      - enhancement
      - medium
      - Wrap lines from the specified console width when using dotted output
    * - `#2275`_
      - enhancement
      - medium
      - API docs have general module documentation after submodules
    * - `#2279`_
      - enhancement
      - medium
      - Enhance public API documentation related to parts exposed to model modifiers and listeners
    * - `#2180`_
      - bug
      - low
      - Collections: Multiple dictionary keywords fail if keys are unorderable
    * - `#2185`_
      - bug
      - low
      - Bad error if dynamic or hybrid library returns invalid keyword names
    * - `#2243`_
      - bug
      - low
      - Using list variable as user keyword argument default value does not work
    * - `#2256`_
      - bug
      - low
      - Error about non-existing variable in for loop values cannot be caught
    * - `#2266`_
      - bug
      - low
      - Embedded user keyword arguments are not trace logged
    * - `#2267`_
      - bug
      - low
      - Dialogs: Closing PASS/FAIL dialog should not be considered same as pressing FAIL
    * - `#2268`_
      - bug
      - low
      - `Convert To Number` ignores precision if it is `${0}`
    * - `#2269`_
      - bug
      - low
      - User keyword tags cannot contain list variables
    * - `#2121`_
      - enhancement
      - low
      - Clarify documentation related to dictionaries originating from YAML variable files
    * - `#2200`_
      - enhancement
      - low
      - Changes to internal utility functions and classes
    * - `#2202`_
      - enhancement
      - low
      - Remove aliases from `robot.utils.asserts`
    * - `#2203`_
      - enhancement
      - low
      - Remove deprecated command line options
    * - `#2204`_
      - enhancement
      - low
      - Make it an error if same setting is used multiple times
    * - `#2205`_
      - enhancement
      - low
      - Remove old `Meta: Name` syntax for specifying test suite metadata
    * - `#2206`_
      - enhancement
      - low
      - Remove deprecated listener API version 1
    * - `#2207`_
      - enhancement
      - low
      - Deprecate `Document` and `Suite/Test Pre/Post Condition` synonym settings
    * - `#2208`_
      - enhancement
      - low
      - Deprecate `Metadata` and `User Keyword` table names
    * - `#2219`_
      - enhancement
      - low
      - Loudly deprecate `robot.running.TestSuite.(imports|variables|user_keywords)` properties
    * - `#2259`_
      - enhancement
      - low
      - Add keyword tags to `start/end_keyword` listener methods
    * - `#2263`_
      - enhancement
      - low
      - Deprecate using `WITH NAME` case-insensitively
    * - `#2264`_
      - enhancement
      - low
      - Deprecate importing library with extra spaces in name
    * - `#2265`_
      - enhancement
      - low
      - Deprecate semi-public API to register "run keyword variants" and to disable variable resolving in arguments

Altogether 50 issues. View on `issue tracker <https://github.com/robotframework/robotframework/issues?q=milestone%3A3.0>`__.

.. _User Guide: http://robotframework.org/robotframework/#user-guide
.. _#1208: https://github.com/robotframework/robotframework/issues/1208
.. _#1506: https://github.com/robotframework/robotframework/issues/1506
.. _#2241: https://github.com/robotframework/robotframework/issues/2241
.. _#2216: https://github.com/robotframework/robotframework/issues/2216
.. _#2218: https://github.com/robotframework/robotframework/issues/2218
.. _#2223: https://github.com/robotframework/robotframework/issues/2223
.. _#2188: https://github.com/robotframework/robotframework/issues/2188
.. _#2192: https://github.com/robotframework/robotframework/issues/2192
.. _#2217: https://github.com/robotframework/robotframework/issues/2217
.. _#2231: https://github.com/robotframework/robotframework/issues/2231
.. _#2248: https://github.com/robotframework/robotframework/issues/2248
.. _#2090: https://github.com/robotframework/robotframework/issues/2090
.. _#2092: https://github.com/robotframework/robotframework/issues/2092
.. _#2177: https://github.com/robotframework/robotframework/issues/2177
.. _#2181: https://github.com/robotframework/robotframework/issues/2181
.. _#2184: https://github.com/robotframework/robotframework/issues/2184
.. _#2196: https://github.com/robotframework/robotframework/issues/2196
.. _#2197: https://github.com/robotframework/robotframework/issues/2197
.. _#2198: https://github.com/robotframework/robotframework/issues/2198
.. _#2213: https://github.com/robotframework/robotframework/issues/2213
.. _#2229: https://github.com/robotframework/robotframework/issues/2229
.. _#2238: https://github.com/robotframework/robotframework/issues/2238
.. _#2242: https://github.com/robotframework/robotframework/issues/2242
.. _#2245: https://github.com/robotframework/robotframework/issues/2245
.. _#2257: https://github.com/robotframework/robotframework/issues/2257
.. _#2271: https://github.com/robotframework/robotframework/issues/2271
.. _#2275: https://github.com/robotframework/robotframework/issues/2275
.. _#2279: https://github.com/robotframework/robotframework/issues/2279
.. _#2180: https://github.com/robotframework/robotframework/issues/2180
.. _#2185: https://github.com/robotframework/robotframework/issues/2185
.. _#2243: https://github.com/robotframework/robotframework/issues/2243
.. _#2256: https://github.com/robotframework/robotframework/issues/2256
.. _#2266: https://github.com/robotframework/robotframework/issues/2266
.. _#2267: https://github.com/robotframework/robotframework/issues/2267
.. _#2268: https://github.com/robotframework/robotframework/issues/2268
.. _#2269: https://github.com/robotframework/robotframework/issues/2269
.. _#2121: https://github.com/robotframework/robotframework/issues/2121
.. _#2200: https://github.com/robotframework/robotframework/issues/2200
.. _#2202: https://github.com/robotframework/robotframework/issues/2202
.. _#2203: https://github.com/robotframework/robotframework/issues/2203
.. _#2204: https://github.com/robotframework/robotframework/issues/2204
.. _#2205: https://github.com/robotframework/robotframework/issues/2205
.. _#2206: https://github.com/robotframework/robotframework/issues/2206
.. _#2207: https://github.com/robotframework/robotframework/issues/2207
.. _#2208: https://github.com/robotframework/robotframework/issues/2208
.. _#2219: https://github.com/robotframework/robotframework/issues/2219
.. _#2259: https://github.com/robotframework/robotframework/issues/2259
.. _#2263: https://github.com/robotframework/robotframework/issues/2263
.. _#2264: https://github.com/robotframework/robotframework/issues/2264
.. _#2265: https://github.com/robotframework/robotframework/issues/2265
