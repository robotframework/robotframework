=====================
Robot Framework 7.3.2
=====================

.. default-role:: code

`Robot Framework`_ 7.3.2 is the second and the last planned bug fix release
in the Robot Framework 7.3.x series. It fixes few regressions in earlier
RF 7.3.x releases as well as some issues affecting also earlier releases.

Questions and comments related to the release can be sent to the `#devel`
channel on `Robot Framework Slack`_ and possible bugs submitted to
the `issue tracker`_.

If you have pip_ installed, just run

::

   pip install --upgrade robotframework

to install the latest available release or use

::

   pip install robotframework==7.3.2

to install exactly this version. Alternatively you can download the package
from PyPI_ and install it manually. For more details and other installation
approaches, see the `installation instructions`_.

Robot Framework 7.3.2 was released on Friday July 4, 2025.

.. _Robot Framework: http://robotframework.org
.. _Robot Framework Foundation: http://robotframework.org/foundation
.. _pip: http://pip-installer.org
.. _PyPI: https://pypi.python.org/pypi/robotframework
.. _issue tracker milestone: https://github.com/robotframework/robotframework/issues?q=milestone%3Av7.3.2
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

Robot Framework is developed with support from the Robot Framework Foundation
and its 80+ member organizations. Join the journey — support the project by
`joining the Foundation <Robot Framework Foundation_>`_.

Big thanks to the Foundation and to everyone who has submitted bug reports, debugged
problems, or otherwise helped with Robot Framework development.

| `Pekka Klärck <https://github.com/pekkaklarck>`_
| Robot Framework lead developer

Full list of fixes
==================

.. list-table::
    :header-rows: 1

    * - ID
      - Type
      - Priority
      - Summary
    * - `#5455`_
      - bug
      - high
      - Embedded arguments matching only after replacing variables do not work with `Run Keyword` or setup/teardown (regression in RF 7.3.1)
    * - `#5456`_
      - bug
      - high
      - French `Étant donné`, `Et` and `Mais` BDD prefixes don't work with keyword names starting with `que` or `qu'` (regression in RF 7.3)
    * - `#5463`_
      - bug
      - high
      - Messages and keywords by listener `end_test` method override original body when using JSON outputs if test has teardown
    * - `#5464`_
      - bug
      - high
      - `--flattenkeywords` doesn't work with JSON outputs
    * - `#5466`_
      - bug
      - medium
      - `--flattenkeywords` doesn't remove GROUP, VAR or RETURN
    * - `#5467`_
      - bug
      - medium
      - `ExecutionResult` ignores `include_keywords` argument with JSON outputs
    * - `#5468`_
      - bug
      - medium
      - Suite teardown failures are not handled properly with JSON outputs

Altogether 7 issues. View on the `issue tracker <https://github.com/robotframework/robotframework/issues?q=milestone%3Av7.3.2>`__.

.. _#5455: https://github.com/robotframework/robotframework/issues/5455
.. _#5464: https://github.com/robotframework/robotframework/issues/5464
.. _#5463: https://github.com/robotframework/robotframework/issues/5463
.. _#5456: https://github.com/robotframework/robotframework/issues/5456
.. _#5466: https://github.com/robotframework/robotframework/issues/5466
.. _#5467: https://github.com/robotframework/robotframework/issues/5467
.. _#5468: https://github.com/robotframework/robotframework/issues/5468
