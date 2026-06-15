=====================
Robot Framework 7.4.2
=====================

.. default-role:: code

`Robot Framework`_ 7.4.2 is the last planned bug fix release in the Robot Framework
7.4.x series. It contains some bug fixes as well as documentation enhancements.
The most important change is the deprecation of the `built-in Testdoc tool`_
in favor of the `external Testdoc tool`_ (`#5597`_).

.. _built-in Testdoc tool: https://robotframework.org/robotframework/7.4.2/RobotFrameworkUserGuide.html#test-data-documentation-tool-testdoc
.. _external Testdoc tool: https://marvkler.github.io/robotframework-testdoc

Questions and comments related to the release can be sent to the `#devel`
channel on `Robot Framework Slack`_ and possible bugs submitted to
the `issue tracker`_.

If you have pip_ installed, just run

::

   pip install --upgrade robotframework

to install the latest available release or use

::

   pip install robotframework==7.4.2

to install exactly this version. Alternatively you can download the package
from PyPI_ and install it manually. For more details and other installation
approaches, see the `installation instructions`_.

Robot Framework 7.4.2 was released on Tuesday March 3, 2026.

.. _Robot Framework: http://robotframework.org
.. _Robot Framework Foundation: http://robotframework.org/foundation
.. _pip: http://pip-installer.org
.. _PyPI: https://pypi.python.org/pypi/robotframework
.. _issue tracker milestone: https://github.com/robotframework/robotframework/issues?q=milestone%3Av7.4.2
.. _issue tracker: https://github.com/robotframework/robotframework/issues
.. _robotframework-users: http://groups.google.com/group/robotframework-users
.. _Slack: http://slack.robotframework.org
.. _Robot Framework Slack: Slack_
.. _installation instructions: ../../INSTALL.rst

.. contents::
   :depth: 2
   :local:

Deprecated features
===================

The `built-in Testdoc tool`_ has been deprecated and the new and enhanced
`external Testdoc tool`_ should be used instead (`#5597`_).

The built-in Testdoc tool can still be used and there are no deprecation warnings
yet. Such warnings will be emitted starting from Robot Framework 7.5 (`#5592`__),
though, the tool will be removed altogether in Robot Framework 8.0 (`#5591`__).

__ https://github.com/robotframework/robotframework/issues/5592
__ https://github.com/robotframework/robotframework/issues/5591

Acknowledgements
================

Big thanks to `Robot Framework Foundation`_ for the continued support developing
Robot Framework. Thanks also to everyone who has tested Robot Framework 7.4 and
reported issues.

| `Pekka Klärck <https://github.com/pekkaklarck>`_
| Robot Framework lead developer

Full list of fixes and enhancements
===================================

.. list-table::
    :header-rows: 1

    * - ID
      - Type
      - Priority
      - Summary
    * - `#5595`_
      - bug
      - high
      - Libdoc: Resource file documentation does not contain type documentation
    * - `#5597`_
      - feature
      - high
      - Soft-deprecate built-in Testdoc
    * - `#5601`_
      - bug
      - medium
      - Libdoc: Linking to introduction section broken
    * - `#5608`_
      - bug
      - medium
      - Libdoc: Ordered lists rendered incorrectly
    * - `#5615`_
      - bug
      - medium
      - Confusing error message when importing library using path and module name contains dots
    * - `#5590`_
      - feature
      - medium
      - Document that Telnet requires external module with Python 3.13 and newer
    * - `#5620`_
      - bug
      - low
      - Accessing variables returned by `BuiltIn.get_variables` with non-string keys fails with `AttributeError`
    * - `#5582`_
      - feature
      - low
      - Enhance documentation related to full name of user keywords in suite files
    * - `#5593`_
      - feature
      - low
      - Documentation: Clarify that `__init__.robot` files in parent directories of executed suite files/directories have no effect

Altogether 9 issues. View on the `issue tracker <https://github.com/robotframework/robotframework/issues?q=milestone%3Av7.4.2>`__.

.. _#5595: https://github.com/robotframework/robotframework/issues/5595
.. _#5597: https://github.com/robotframework/robotframework/issues/5597
.. _#5601: https://github.com/robotframework/robotframework/issues/5601
.. _#5608: https://github.com/robotframework/robotframework/issues/5608
.. _#5615: https://github.com/robotframework/robotframework/issues/5615
.. _#5590: https://github.com/robotframework/robotframework/issues/5590
.. _#5620: https://github.com/robotframework/robotframework/issues/5620
.. _#5582: https://github.com/robotframework/robotframework/issues/5582
.. _#5593: https://github.com/robotframework/robotframework/issues/5593
