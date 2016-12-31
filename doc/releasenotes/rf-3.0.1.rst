==========================
Robot Framework 3.0.1 RC 1
==========================

.. default-role:: code

Robot Framework 3.0.1 release candidate 1 is the first and only planned
preview release of the forthcoming Robot Framework 3.0.1 release. It contains
all features and fixes planned to be included in the final release. All issues
targeted for RF 3.0.1 can be found from the `issue tracker
<https://github.com/robotframework/robotframework/issues?q=milestone%3A3.0.1>`_.

Questions and comments related to the release can be sent to the
`robotframework-users <http://groups.google.com/group/robotframework-users>`_
and possible bugs `submitted to the issue tracker
<https://github.com/robotframework/robotframework/issues>`__.

If you have `pip <http://pip-installer.org>`_ installed, just run
`pip install --upgrade --pre robotframework` to install this release.
Notice that `--pre` is need when installing a preview release like this.
Alternatively you can download the source distribution from
`PyPI <https://pypi.python.org/pypi/robotframework>`_ and install it manually.
For more details and other installation approaches, see the `installation
instructions <../../INSTALL.rst>`_.

Robot Framework 3.0.1 RC 1 was released on Saturday December 31, 2016.
The final release is planned for Friday January 6, 2017.

.. contents::
   :depth: 2
   :local:

Most important enhancements
===========================

The most important new features in RF 3.0.1 are the ability to limit parsing
of test data file to a certain file type (e.g. `--extension robot`, `#2365`_)
and case-insensitivity support added to most comparison keywords in the
BuildIn library (e.g. `| Should Be Equal | ${x} | ${y} | ignore_case=True`,
`#2439`_).

There are also some high priority bug fixes in the release:

- Execution crashes if tests are run with `--output NONE` and any test or keyword has timeout (`#2326`_)
- Using HTML in failure messages is not possible in setups/teardowns or with continuable failures (`#2360`_)
- Programmatically re-running failed tests prevents subsequent Robot and Rebot usage in same process (`#2437`_)
- Copying model objects doesn't always work (`#2483`_)
- Redirecting console output with nonrepresentable characters crashes execution on Windows with Python 3.6 (`#2505`_)

Backwards incompatible changes
==============================

There should not be any.

Deprecated features
===================

This release deprecated the possibility to set a custom message to test
and keyword timeouts (`#2387`_).

Acknowledgements
================

This release has been sponsored by the `Robot Framework Foundation`__ and
would not have been possible, at least with this scope, without that. Big
thank you for all the member companies of the foundation for your support!

There have also been several great `contributions <../../CONTRIBUTING.rst>`_
by the community:

- Anton Nikitin implemented `Should (Not) Contain Any` keywords  (`#2120`_)
- Yang Qian fixed copying model objects (`#2483`_)
- Chris Callan added case-insensitivity support to various comparison keywords (`#2439`_)
- Benjamin Einaudi implemented `--rerunfailedsuites` option (`#2117`_)

__ http://robotframework.org/foundation/

Full list of fixes and enhancements
===================================

.. list-table::
    :header-rows: 1

    * - ID
      - Type
      - Priority
      - Summary
    * - `#2326`_
      - bug
      - high
      - Execution crashes if tests are run with `--output NONE` and any test or keyword has timeout
    * - `#2360`_
      - bug
      - high
      - Using HTML in failure messages is not possible in setups/teardowns or with continuable failures
    * - `#2437`_
      - bug
      - high
      - Programmatically re-running failed tests prevents subsequent Robot and Rebot usage in same process
    * - `#2483`_
      - bug
      - high
      - Copying model objects doesn't always work
    * - `#2505`_
      - bug
      - high
      - Redirecting console output with nonrepresentable characters crashes execution on Windows with Python 3.6
    * - `#2365`_
      - enhancement
      - high
      - Possibility to limit parsing of test case file to certain file type like `--extension robot`
    * - `#2439`_
      - enhancement
      - high
      - Builtin: Add case-insensitivity support to comparison keywords
    * - `#2315`_
      - bug
      - medium
      - `robot` and `rebot` scripts cannot be used with multiprocessing module
    * - `#2318`_
      - bug
      - medium
      - `Exit/Continue For Loop` does not work with continuable failures in user keywords
    * - `#2321`_
      - bug
      - medium
      - `Copy Directory` does not work with Jython on Windows
    * - `#2351`_
      - bug
      - medium
      - Telnet connections might be left open
    * - `#2373`_
      - bug
      - medium
      - Test case with template should continue if keyword timeout occurs
    * - `#2509`_
      - bug
      - medium
      - Errors in global library listener `close` method prevent log and report generation
    * - `#2117`_
      - enhancement
      - medium
      - Re-run test suite instead of tests
    * - `#2120`_
      - enhancement
      - medium
      - New `Should Contain Any` and `Should Not Contain Any` keywords
    * - `#2309`_
      - enhancement
      - medium
      - Add Robot Framework Foundation as copyright holder for 2016->
    * - `#2386`_
      - enhancement
      - medium
      - Remove deprecation for using `Create Dictionary` with individual keys and values
    * - `#2387`_
      - enhancement
      - medium
      - Deprecate setting custom timeout message
    * - `#2407`_
      - enhancement
      - medium
      - Assign `-X` short option for `--exitonfailure`
    * - `#2448`_
      - enhancement
      - medium
      - Libdoc: Add syntax highlighting support when using reStructuredText
    * - `#2496`_
      - enhancement
      - medium
      - Enhance documentation of programmatic execution entry points
    * - `#2510`_
      - enhancement
      - medium
      - Add explicit `copy` and `deepcopy` methods to model objects
    * - `#2332`_
      - bug
      - low
      - Unit tests only pass in specific order
    * - `#2363`_
      - bug
      - low
      - `Run Keyword and Expect Error` cannot catch error caused by variable assignement
    * - `#2391`_
      - bug
      - low
      - `Pass Execution` doesn't work correctly with continuable failures
    * - `#2392`_
      - bug
      - low
      - Not possible to pass tags `Pass Execution If` using a list variable
    * - `#2404`_
      - bug
      - low
      - Teardowns should stop after syntax errors
    * - `#2456`_
      - bug
      - low
      - `Should (Not) Match` does not work with bytes on Python 3
    * - `#2460`_
      - bug
      - low
      - Dialogs: Opening dialogs fails with Python on Linux if mouse button hold down
    * - `#2475`_
      - bug
      - low
      - Keywords in test case files with dots in name do not have precedence over imported keywords
    * - `#2489`_
      - bug
      - low
      - Dynamically set variables used in setups/teardowns cause failures in dry-run
    * - `#2490`_
      - bug
      - low
      - `List Should Not Contain Value` has incorrect documentation
    * - `#2501`_
      - bug
      - low
      - Generation time GMT offset in logs/reports is always in summer time
    * - `#2502`_
      - bug
      - low
      - Some unit and acceptance tests fail on Python 3.6
    * - `#2302`_
      - enhancement
      - low
      - Make setup and teardown settable in `Keywords` object
    * - `#2303`_
      - enhancement
      - low
      - Add `pop()` method to list-like model objects to ease their usage
    * - `#2405`_
      - enhancement
      - low
      - Make it explicit that `robot.running/result` model objects are part of the public API
    * - `#2455`_
      - enhancement
      - low
      - User Guide: Clarify that with module libraries imported functions become keywords
    * - `#2470`_
      - enhancement
      - low
      - Specify supported Python variants in project metadata (i.e. in `setup.py`)
    * - `#2504`_
      - enhancement
      - low
      - Allow `run_cli` and `rebot_cli` functions to return rc without exiting

Altogether 40 issues. View on `issue tracker <https://github.com/robotframework/robotframework/issues?q=milestone%3A3.0.1>`__.

.. _User Guide: http://robotframework.org/robotframework/#user-guide
.. _#2326: https://github.com/robotframework/robotframework/issues/2326
.. _#2360: https://github.com/robotframework/robotframework/issues/2360
.. _#2437: https://github.com/robotframework/robotframework/issues/2437
.. _#2483: https://github.com/robotframework/robotframework/issues/2483
.. _#2505: https://github.com/robotframework/robotframework/issues/2505
.. _#2365: https://github.com/robotframework/robotframework/issues/2365
.. _#2439: https://github.com/robotframework/robotframework/issues/2439
.. _#2315: https://github.com/robotframework/robotframework/issues/2315
.. _#2318: https://github.com/robotframework/robotframework/issues/2318
.. _#2321: https://github.com/robotframework/robotframework/issues/2321
.. _#2351: https://github.com/robotframework/robotframework/issues/2351
.. _#2373: https://github.com/robotframework/robotframework/issues/2373
.. _#2509: https://github.com/robotframework/robotframework/issues/2509
.. _#2117: https://github.com/robotframework/robotframework/issues/2117
.. _#2120: https://github.com/robotframework/robotframework/issues/2120
.. _#2309: https://github.com/robotframework/robotframework/issues/2309
.. _#2386: https://github.com/robotframework/robotframework/issues/2386
.. _#2387: https://github.com/robotframework/robotframework/issues/2387
.. _#2407: https://github.com/robotframework/robotframework/issues/2407
.. _#2448: https://github.com/robotframework/robotframework/issues/2448
.. _#2496: https://github.com/robotframework/robotframework/issues/2496
.. _#2510: https://github.com/robotframework/robotframework/issues/2510
.. _#2332: https://github.com/robotframework/robotframework/issues/2332
.. _#2363: https://github.com/robotframework/robotframework/issues/2363
.. _#2391: https://github.com/robotframework/robotframework/issues/2391
.. _#2392: https://github.com/robotframework/robotframework/issues/2392
.. _#2404: https://github.com/robotframework/robotframework/issues/2404
.. _#2456: https://github.com/robotframework/robotframework/issues/2456
.. _#2460: https://github.com/robotframework/robotframework/issues/2460
.. _#2475: https://github.com/robotframework/robotframework/issues/2475
.. _#2489: https://github.com/robotframework/robotframework/issues/2489
.. _#2490: https://github.com/robotframework/robotframework/issues/2490
.. _#2501: https://github.com/robotframework/robotframework/issues/2501
.. _#2502: https://github.com/robotframework/robotframework/issues/2502
.. _#2302: https://github.com/robotframework/robotframework/issues/2302
.. _#2303: https://github.com/robotframework/robotframework/issues/2303
.. _#2405: https://github.com/robotframework/robotframework/issues/2405
.. _#2455: https://github.com/robotframework/robotframework/issues/2455
.. _#2470: https://github.com/robotframework/robotframework/issues/2470
.. _#2504: https://github.com/robotframework/robotframework/issues/2504
