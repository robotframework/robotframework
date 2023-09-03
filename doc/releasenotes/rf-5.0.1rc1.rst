=========================================
Robot Framework 5.0.1 release candidate 1
=========================================

.. default-role:: code

`Robot Framework`_ 5.0.1 is the first and also the last planned bug fix
release in the Robot Framework 5.0.x series. This release candidate contains
all issues targeted to the final release.

Questions and comments related to the release can be sent to the
`robotframework-users`_ mailing list or to `Robot Framework Slack`_,
and possible bugs submitted to the `issue tracker`_.

If you have pip_ installed, just run

::

   pip install --pre --upgrade robotframework

to install the latest available release or use

::

   pip install robotframework==5.0.1rc1

to install exactly this version. Alternatively you can download the source
distribution from PyPI_ and install it manually. For more details and other
installation approaches, see the `installation instructions`_.

Robot Framework 5.0.1 rc 1 was released on Monday May 9, 2022.
The plan is to get the final release out on Monday May 16, just before the
`RoboCon 2022 <https://robocon.io>`_ conference.

.. _Robot Framework: http://robotframework.org
.. _Robot Framework Foundation: http://robotframework.org/foundation
.. _pip: http://pip-installer.org
.. _PyPI: https://pypi.python.org/pypi/robotframework
.. _issue tracker milestone: https://github.com/robotframework/robotframework/issues?q=milestone%3Av5.0.1
.. _issue tracker: https://github.com/robotframework/robotframework/issues
.. _robotframework-users: http://groups.google.com/group/robotframework-users
.. _Robot Framework Slack: https://robotframework-slack-invite.herokuapp.com
.. _installation instructions: ../../INSTALL.rst

.. contents::
   :depth: 2
   :local:

Most important fixes and enhancements
=====================================

Fix crash when using `partialmethod` in library
-----------------------------------------------

Using `partialmethod` in a library crashed the whole execution (`#4318`_).
As part of the fix, support to create keyword using both `partialmethod` and
`partial` as added.

Libdoc JSON schema has been updated
-----------------------------------

There were some changes to Libdoc's spec files in Robot Framework 5.0.
The schema for XML spec files was updated already then, but the JSON schema
was updated only now as part of Robot Framework 5.0.1 development (`#4281`_).
All schema files, including the output.xml schema, can be found at
https://github.com/robotframework/robotframework/tree/master/doc/schema/.

Acknowledgements
================

Robot Framework 5.0.1 development has been sponsored by the `Robot Framework Foundation`_
and its close to 50 member organizations. Big thanks for the foundation for its continued
support!

Thanks also to all community members who have submitted bug reports, helped debugging
problems, or otherwise helped with the release.

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
      - Added
    * - `#4318`_
      - bug
      - high
      - Support creating functions using `partial` and `partialmethod` (earlier the latter caused a crash)
      - rc 1
    * - `#4281`_
      - enhancement
      - high
      - Update Libdoc's JSON schema
      - rc 1
    * - `#3862`_
      - bug
      - medium
      - `--runemptysuite` should work with `--rerunfailed` when there are no failed tests
      - rc 1
    * - `#4175`_
      - bug
      - medium
      - `Get Variable Value` fails if variable name contains another variable and resolving it fails
      - rc 1
    * - `#4204`_
      - bug
      - medium
      - Using `Set Test Variable` in suite setup or teardown should be a normal error, not a syntax error
      - rc 1
    * - `#4305`_
      - bug
      - medium
      - Functions named `__init__` are exposed as keywords with name `__init__`, not `Init`
      - rc 1
    * - `#4315`_
      - bug
      - medium
      - `BuiltIn.Log`: Using invalid log level should be a normal error, not a syntax error
      - rc 1
    * - `#4324`_
      - bug
      - medium
      - Programmatic execution API doesn't support `pathlib.Path` objects
      - rc 1
    * - `#4331`_
      - bug
      - medium
      - Example in API documentation uses an out-of-date API
      - rc 1
    * - `#4336`_
      - bug
      - medium
      - `Get Variable Value` doesn't support accessing list/dict variable items like `${var}[0]` or `${var}[key]`
      - rc 1
    * - `#4292`_
      - bug
      - low
      - Process library test related to sending signals fails on Guix
      - rc 1
    * - `#4314`_
      - bug
      - low
      - Document that `EXCEPT` does not catch syntax errors
      - rc 1
    * - `#4322`_
      - enhancement
      - low
      - DateTime: Enhance documentation related to the epoch time format
      - rc 1

Altogether 13 issues. View on the `issue tracker <https://github.com/robotframework/robotframework/issues?q=milestone%3Av5.0.1>`__.

.. _#4318: https://github.com/robotframework/robotframework/issues/4318
.. _#4281: https://github.com/robotframework/robotframework/issues/4281
.. _#3862: https://github.com/robotframework/robotframework/issues/3862
.. _#4175: https://github.com/robotframework/robotframework/issues/4175
.. _#4204: https://github.com/robotframework/robotframework/issues/4204
.. _#4305: https://github.com/robotframework/robotframework/issues/4305
.. _#4315: https://github.com/robotframework/robotframework/issues/4315
.. _#4324: https://github.com/robotframework/robotframework/issues/4324
.. _#4331: https://github.com/robotframework/robotframework/issues/4331
.. _#4336: https://github.com/robotframework/robotframework/issues/4336
.. _#4292: https://github.com/robotframework/robotframework/issues/4292
.. _#4314: https://github.com/robotframework/robotframework/issues/4314
.. _#4322: https://github.com/robotframework/robotframework/issues/4322
