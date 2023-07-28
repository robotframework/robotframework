=====================
Robot Framework 6.1.1
=====================

.. default-role:: code

`Robot Framework`_ 6.1.1 is the first bug fix release in the `Robot Framework
6.1 <rf-6.1.rst>`_ series.

Questions and comments related to the release can be sent to the
`robotframework-users`_ mailing list or to `Robot Framework Slack`_,
and possible bugs submitted to the `issue tracker`_.

If you have pip_ installed, just run

::

   pip install --pre --upgrade robotframework

to install the latest available release or use

::

   pip install robotframework==6.1.1

to install exactly this version. Alternatively you can download the source
distribution from PyPI_ and install it manually. For more details and other
installation approaches, see the `installation instructions`_.

Robot Framework 6.1.1 was released on Friday July 28, 2023.

.. _Robot Framework: http://robotframework.org
.. _Robot Framework Foundation: http://robotframework.org/foundation
.. _pip: http://pip-installer.org
.. _PyPI: https://pypi.python.org/pypi/robotframework
.. _issue tracker milestone: https://github.com/robotframework/robotframework/issues?q=milestone%3Av6.1.1
.. _issue tracker: https://github.com/robotframework/robotframework/issues
.. _robotframework-users: http://groups.google.com/group/robotframework-users
.. _Slack: http://slack.robotframework.org
.. _Robot Framework Slack: Slack_
.. _installation instructions: ../../INSTALL.rst

.. contents::
   :depth: 2
   :local:

Most important enhancements
===========================

- Robot Framework 6.1 added shortcuts for the buttons in the dialogs used by
  the Dialogs__ library. Shortcuts work well otherwise, but `o` and `c` were
  bound for the `Ok` and `Cancel` buttons also when typing text with the
  `Get Value From User` keyword. This is now fixed and it is possible to input
  `o` and `c` characters again. (`#4812`_)

- Execution mode (test execution vs. RPA) is checked only after selecting which
  test or tasks are actually run. This fixes a regression when using the `--suite`
  option for selecting which suites to run and is an enhancement with `--include`,
  `--exclude`, `--test` or `--task`. (`#4807`_)

- Argument conversion does not anymore unnecessarily convert containers
  with nested items when using parameterized types like `list[str]` and items
  have correct types. Most importantly, this fixes a bug when using such types
  in an union with `str` like `str | list[str]`. (`#4809`_)

- A library using `@classmethod` and `@property` together does not anymore
  crash the whole execution. (`#4802`_)

__ https://robotframework.org/robotframework/latest/libraries/Dialogs.html

Full list of fixes and enhancements
===================================

.. list-table::
    :header-rows: 1

    * - ID
      - Type
      - Priority
      - Summary
    * - `#4812`_
      - bug
      - critical
      - Dialogs: Cannot type `o` or `c` to input dialog due to they being registered as shortcuts
    * - `#4802`_
      - bug
      - high
      - Library using `@classmethod` and `@property` together crashes execution and fails with Libdoc
    * - `#4809`_
      - bug
      - high
      - Parameterized types are not converted when used in union with `str` like `str | list[str]`
    * - `#4807`_
      - enhancement
      - high
      - Execution mode should be checked only after selecting which test/tasks are run
    * - `#4820`_
      - bug
      - medium
      - Libdoc does not show inits having only named-only arguments
    * - `#4829`_
      - bug
      - medium
      - Test cases with tag 'robot:skip' will fail when whole suite is skipped
    * - `#4831`_
      - bug
      - medium
      - Argument conversion fails if `tuple` has unrecognized parameter
    * - `#4833`_
      - bug
      - medium
      - Execution fails with PyPy if language configuration is invalid
    * - `#4816`_
      - bug
      - low
      - User Guide: Forthcoming `-tag` syntax will be added in RF 7.0, not in RF 6.1
    * - `#4800`_
      - enhancement
      - low
      - Update Polish translations to use title case

Altogether 10 issues. View on the `issue tracker <https://github.com/robotframework/robotframework/issues?q=milestone%3Av6.1.1>`__.

.. _#4812: https://github.com/robotframework/robotframework/issues/4812
.. _#4802: https://github.com/robotframework/robotframework/issues/4802
.. _#4809: https://github.com/robotframework/robotframework/issues/4809
.. _#4807: https://github.com/robotframework/robotframework/issues/4807
.. _#4820: https://github.com/robotframework/robotframework/issues/4820
.. _#4829: https://github.com/robotframework/robotframework/issues/4829
.. _#4831: https://github.com/robotframework/robotframework/issues/4831
.. _#4833: https://github.com/robotframework/robotframework/issues/4833
.. _#4816: https://github.com/robotframework/robotframework/issues/4816
.. _#4800: https://github.com/robotframework/robotframework/issues/4800
