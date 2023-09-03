=====================
Robot Framework 6.0.1
=====================

.. default-role:: code

`Robot Framework`_ 6.0.1 is the first bug fix release in the `RF 6.0 <rf-6.0.rst>`_
series. It mainly fixes a bug in using `localized <rf-6.0.rst#localization>`_
BDD prefixes consisting of more than one word (`#4515`_) as well as a regression
related to the library search order (`#4516`_).

Questions and comments related to the release can be sent to the
`robotframework-users`_ mailing list or to `Robot Framework Slack`_,
and possible bugs submitted to the `issue tracker`_.

If you have pip_ installed, just run

::

   pip install --pre --upgrade robotframework

to install the latest available release or use

::

   pip install robotframework==6.0.1

to install exactly this version. Alternatively you can download the source
distribution from PyPI_ and install it manually. For more details and other
installation approaches, see the `installation instructions`_.

Robot Framework 6.0.1 was released on Thursday November 3, 2022.
It was superseded by `Robot Framework 6.0.2 <rf-6.0.2.rst>`_

.. _Robot Framework: http://robotframework.org
.. _Robot Framework Foundation: http://robotframework.org/foundation
.. _pip: http://pip-installer.org
.. _PyPI: https://pypi.python.org/pypi/robotframework
.. _issue tracker milestone: https://github.com/robotframework/robotframework/issues?q=milestone%3Av6.0.1
.. _issue tracker: https://github.com/robotframework/robotframework/issues
.. _robotframework-users: http://groups.google.com/group/robotframework-users
.. _Slack: http://slack.robotframework.org
.. _Robot Framework Slack: Slack_
.. _installation instructions: ../../INSTALL.rst

Full list of fixes and enhancements
===================================

.. list-table::
    :header-rows: 1

    * - ID
      - Type
      - Priority
      - Summary
    * - `#4515`_
      - bug
      - high
      - Localized BDD prefixes consisting of more than one word don't work
    * - `#4516`_
      - bug
      - high
      - `Set Library Search Order` doesn't work if there are two matches and one is from standard libraries
    * - `#4519`_
      - bug
      - medium
      - Libdoc's `DocumentationBuilder` doesn't anymore work with resource files with `.robot` extension
    * - `#4520`_
      - enhancement
      - medium
      - Document Libdoc's public API better
    * - `#4521`_
      - enhancement
      - medium
      - Enhance `robot.utils.timestr_to_secs` so that it works with `timedelta` objects
    * - `#4523`_
      - bug
      - low
      - Unit test `test_parse_time_with_now_and_utc` fails around DST change
    * - `#4525`_
      - bug
      - low
      - Wrong version numbers used in the User Guide and in a deprecation warning

Altogether 7 issues. View on the `issue tracker <https://github.com/robotframework/robotframework/issues?q=milestone%3Av6.0.1>`__.

.. _#4515: https://github.com/robotframework/robotframework/issues/4515
.. _#4516: https://github.com/robotframework/robotframework/issues/4516
.. _#4519: https://github.com/robotframework/robotframework/issues/4519
.. _#4520: https://github.com/robotframework/robotframework/issues/4520
.. _#4521: https://github.com/robotframework/robotframework/issues/4521
.. _#4523: https://github.com/robotframework/robotframework/issues/4523
.. _#4525: https://github.com/robotframework/robotframework/issues/4525
