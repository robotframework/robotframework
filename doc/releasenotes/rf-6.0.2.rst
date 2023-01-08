=====================
Robot Framework 6.0.2
=====================

.. default-role:: code

`Robot Framework`_ 6.0.2 is the second and also the last maintenance release in
the `RF 6.0 <rf-6.0.rst>`_ series. It does not contain any high priority fixes
or enhancements and was released mainly to make it possible to fully concentrate
on Robot Framework 6.1.

Questions and comments related to the release can be sent to the
`robotframework-users`_ mailing list or to `Robot Framework Slack`_,
and possible bugs submitted to the `issue tracker`_.

If you have pip_ installed, just run

::

   pip install --pre --upgrade robotframework

to install the latest available release or use

::

   pip install robotframework==6.0.2

to install exactly this version. Alternatively you can download the source
distribution from PyPI_ and install it manually. For more details and other
installation approaches, see the `installation instructions`_.

Robot Framework 6.0.2 was released on Sunday January 8, 2023.

.. _Robot Framework: http://robotframework.org
.. _Robot Framework Foundation: http://robotframework.org/foundation
.. _pip: http://pip-installer.org
.. _PyPI: https://pypi.python.org/pypi/robotframework
.. _issue tracker milestone: https://github.com/robotframework/robotframework/issues?q=milestone%3Av6.0.2
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

Thanks for `Robot Framework Foundation`_ for sponsoring the development and
for Jerzy Głowacki for providing Polish translations for Boolean words (`#4528`_).

| `Pekka Klärck <https://github.com/pekkaklarck>`__
| Robot Framework Creator

Full list of fixes and enhancements
===================================

.. list-table::
    :header-rows: 1

    * - ID
      - Type
      - Priority
      - Summary
    * - `#4527`_
      - bug
      - medium
      - Using settings valid in Settings section with tests or keywords (e.g. `[Metadata]`) causes confusing error message
    * - `#4528`_
      - enhancement
      - medium
      - Polish translations for Boolean words
    * - `#4533`_
      - bug
      - low
      - IF and WHILE execution time does not include time taken for evaluating condition
    * - `#4557`_
      - bug
      - low
      - Bug in `--reportbackgroundcolor` documentation in the User Guide
    * - `#4587`_
      - bug
      - low
      - Wrong version number in deprecation warning

Altogether 5 issues. View on the `issue tracker <https://github.com/robotframework/robotframework/issues?q=milestone%3Av6.0.2>`__.

.. _#4527: https://github.com/robotframework/robotframework/issues/4527
.. _#4528: https://github.com/robotframework/robotframework/issues/4528
.. _#4533: https://github.com/robotframework/robotframework/issues/4533
.. _#4557: https://github.com/robotframework/robotframework/issues/4557
.. _#4587: https://github.com/robotframework/robotframework/issues/4587
