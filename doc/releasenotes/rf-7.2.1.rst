=====================
Robot Framework 7.2.1
=====================

.. default-role:: code

`Robot Framework`_ 7.2.1 is the first bug fix release in the Robot Framework 7.2.x
series. It fixes all reported regressions in `Robot Framework 7.2 <rf-7.2.rst>`_
as well as some issues affecting also earlier versions. Unfortunately the
there was a mistake in the build process that required creating an immediate
`Robot Framework 7.2.2 <rf-7.2.2.rst>`_ release.

Questions and comments related to the release can be sent to the `#devel`
channel on `Robot Framework Slack`_ and possible bugs submitted to
the `issue tracker`_.

If you have pip_ installed, just run

::

   pip install --pre --upgrade robotframework

to install the latest available release or use

::

   pip install robotframework==7.2.1

to install exactly this version. Alternatively you can download the package
from PyPI_ and install it manually. For more details and other installation
approaches, see the `installation instructions`_.

Robot Framework 7.2.1 was released on Friday February 7, 2025.
It has been superseded by `Robot Framework 7.2.2 <rf-7.2.2.rst>`_.

.. _Robot Framework: http://robotframework.org
.. _Robot Framework Foundation: http://robotframework.org/foundation
.. _pip: http://pip-installer.org
.. _PyPI: https://pypi.python.org/pypi/robotframework
.. _issue tracker milestone: https://github.com/robotframework/robotframework/issues?q=milestone%3Av7.2.1
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

Robot Framework development is sponsored by the `Robot Framework Foundation`_
and its over 70 member organizations. If your organization is using Robot Framework
and benefiting from it, consider joining the foundation to support its development
as well.

In addition to the work sponsored by the foundation, this release got a contribution
from `Mohd Maaz Usmani <https://github.com/m-usmani>`_ who fixed `Lists Should Be Equal`
when used with `ignore_case` and `ignore_order` arguments (`#5321`_).

Big thanks to the Foundation and to everyone who has submitted bug reports, debugged
problems, or otherwise helped with Robot Framework development.

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
    * - `#5326`_
      - bug
      - critical
      - Messages in test body cause crash when using templates and some iterations are skipped
    * - `#5317`_
      - bug
      - high
      - Libdoc's default language selection does not support all available languages
    * - `#5318`_
      - bug
      - high
      - Log and report generation crashes if `--removekeywords` is used with `PASSED` or `ALL` and test body contains messages
    * - `#5058`_
      - bug
      - medium
      - Elapsed time is not updated when merging results
    * - `#5321`_
      - bug
      - medium
      - `Lists Should Be Equal` does not work as expected with `ignore_case` and `ignore_order` arguments
    * - `#5331`_
      - bug
      - medium
      - `BuiltIn.set_global/suite/test/local_variable` should not log if used by listener and no keyword is started
    * - `#5325`_
      - bug
      - low
      - Elapsed time is ignored when parsing output.xml if start time is not set

Altogether 7 issues. View on the `issue tracker <https://github.com/robotframework/robotframework/issues?q=milestone%3Av7.2.1>`__.

.. _#5326: https://github.com/robotframework/robotframework/issues/5326
.. _#5317: https://github.com/robotframework/robotframework/issues/5317
.. _#5318: https://github.com/robotframework/robotframework/issues/5318
.. _#5058: https://github.com/robotframework/robotframework/issues/5058
.. _#5321: https://github.com/robotframework/robotframework/issues/5321
.. _#5331: https://github.com/robotframework/robotframework/issues/5331
.. _#5325: https://github.com/robotframework/robotframework/issues/5325
