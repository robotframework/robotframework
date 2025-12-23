=====================
Robot Framework 7.4.1
=====================

.. default-role:: code

`Robot Framework`_ 7.4.1 is the first bug fix release in the Robot Framework 7.4.x
series. It fixes all reported regressions in `Robot Framework 7.4 <rf-7.4.rst>`_.

Questions and comments related to the release can be sent to the `#devel`
channel on `Robot Framework Slack`_ and possible bugs submitted to
the `issue tracker`_.

If you have pip_ installed, just run

::

   pip install --upgrade robotframework

to install the latest available release or use

::

   pip install robotframework==7.4.1

to install exactly this version. Alternatively you can download the package
from PyPI_ and install it manually. For more details and other installation
approaches, see the `installation instructions`_.

Robot Framework 7.4.1 was released on Tuesday December 23, 2025.

.. _Robot Framework: http://robotframework.org
.. _Robot Framework Foundation: http://robotframework.org/foundation
.. _pip: http://pip-installer.org
.. _PyPI: https://pypi.python.org/pypi/robotframework
.. _issue tracker milestone: https://github.com/robotframework/robotframework/issues?q=milestone%3Av7.4.1
.. _issue tracker: https://github.com/robotframework/robotframework/issues
.. _robotframework-users: http://groups.google.com/group/robotframework-users
.. _Slack: http://slack.robotframework.org
.. _Robot Framework Slack: Slack_
.. _installation instructions: ../../INSTALL.rst

.. contents::
   :depth: 2
   :local:

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
    * - `#5577`_
      - bug
      - high
      - Using `VAR` to set falsy value to non-local variable emits incorrect deprecation warning
    * - `#5580`_
      - bug
      - high
      - Some BuiltIn keywords cannot anymore be programmatically used like `name=value`
    * - `#5578`_
      - bug
      - medium
      - `typing_extensions.Literal` does not work with Python 3.8 or 3.9

Altogether 3 issues. View on the `issue tracker <https://github.com/robotframework/robotframework/issues?q=milestone%3Av7.4.1>`__.

.. _#5577: https://github.com/robotframework/robotframework/issues/5577
.. _#5580: https://github.com/robotframework/robotframework/issues/5580
.. _#5578: https://github.com/robotframework/robotframework/issues/5578
