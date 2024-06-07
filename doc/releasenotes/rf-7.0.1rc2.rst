=========================================
Robot Framework 7.0.1 release candidate 2
=========================================

.. default-role:: code

`Robot Framework`_ 7.0.1 is the first and the only planned bug fix release in
the Robot Framework 7.0.x series. It fixes all reported regressions as well as
some issues affecting also earlier versions. The only bigger enhancement it
contains is the new Japanese localization__ (`#5069`_).

__ https://robotframework.org/robotframework/latest/RobotFrameworkUserGuide.html#localization

Questions and comments related to the release can be sent to the `#devel`
channel on `Robot Framework Slack`_ and possible bugs submitted to
the `issue tracker`_.

If you have pip_ installed, just run

::

   pip install --pre --upgrade robotframework

to install the latest available release or use

::

   pip install robotframework==7.0.1rc2

to install exactly this version. Alternatively you can download the package
from PyPI_ and install it manually. For more details and other installation
approaches, see the `installation instructions`_.

Robot Framework 7.0.1 release candidate 2 was released on Friday June 7, 2024.
It is especially targeted for users who have reported issues so that they can
verify that fixes work properly. The final Robot Framework 7.0 version is
planned to be released on Monday June 10, 2024.

.. _Robot Framework: http://robotframework.org
.. _Robot Framework Foundation: http://robotframework.org/foundation
.. _pip: http://pip-installer.org
.. _PyPI: https://pypi.python.org/pypi/robotframework
.. _issue tracker: https://github.com/robotframework/robotframework/issues
.. _robotframework-users: http://groups.google.com/group/robotframework-users
.. _Slack: http://slack.robotframework.org
.. _Robot Framework Slack: Slack_
.. _installation instructions: ../../INSTALL.rst

.. contents::
   :depth: 2
   :local:

Backwards incompatible changes
==============================

`--test` and `--include` options are non-cumulative again
---------------------------------------------------------

Robot Framework 7.0 changed the behavior of the `--test` and `--include` options
so that a test (or a task) is selected if it matches either of these options when
earlier it needed to match both of them (`#4721`__). This behavior was considered
more useful back then, but it turned out to cause problems with the `--rerun-failed`
option and with the Pabot__ tool. In the end the benefits of the new behavior were
not considered important enough compared to the problems, and the behavior was
changed back to what it was earlier in Robot Framework 7.0.1 (`#5023`_).

__ https://github.com/robotframework/robotframework/issues/4721
__ https://pabot.org/

Changes to passing named arguments with non-string values programmatically
--------------------------------------------------------------------------

Robot Framework 7.0 attempted to provide a convenient API for creating keywords
programmatically, and the key feature was the possibility to use named arguments
with non-string values (`#5000`__). The selected approach unfortunately caused
backwards incompatibility problems and needed to be reverted (`#5031`_).

Because using named arguments with non-string values is important, for example,
to the DataDriver__ tool, a new semi-private API for exactly that purpose was
added as part of the issue `#5031`_. That API has some limitations, though, and
the plan is to add a better public API in Robot Framework 7.1 (`#5143`__).

__ https://github.com/robotframework/robotframework/issues/5000
__ https://github.com/Snooz82/robotframework-datadriver
__ https://github.com/robotframework/robotframework/issues/5143

Acknowledgements
================

Robot Framework development is sponsored by the `Robot Framework Foundation`_
and its over 60 member organizations. If your organization is using Robot Framework
and benefiting from it, consider joining the foundation to support its
development as well.

The community has also done some great contributions:

- `Yas <https://github.com/5003>`__ provided Japanese localization (`#5069`_).
- `Lukas Rolf <https://github.com/lfighter>`__ fixed a crash occurring with the Dialogs
  library (`#4993`_).
- `Many Kasiriha <https://github.com/manykarim>`__ implemented a better theme for
  the `API docs <https://robot-framework.readthedocs.io/>`__ (`#5039`_).
- `Federico Pellegrin <https://github.com/fedepell>`__ fixed unit tests under
  the forthcoming `Python 3.13`__ (`#5035`_). Official support for Python 3.13
  is planned for Robot Framework 7.1 (`#5091`__).
- `@sunday2 <https://github.com/sunday2>`__ fixed a problem with acceptance tests
  when a directory path contains spaces (`#5100`_).

__ https://docs.python.org/3.13/whatsnew/3.13.html
__ https://github.com/robotframework/robotframework/issues/5091

Big thanks to Robot Framework Foundation, to the community members listed above,
and to everyone else who has submitted bug reports, debugged problems, or otherwise
helped with Robot Framework 7.0.1 development.

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
      - Added
    * - `#5012`_
      - bug
      - high
      - `--legacy-output` does not work with Rebot when combining, merging or filtering results
      - rc 1
    * - `#5023`_
      - bug
      - high
      - Make `--test` and `--include` non-cumulative again due to backwards incompatibility problems
      - rc 1
    * - `#5031`_
      - bug
      - high
      - Problems with non-string arguments when using `BuildIn.run_keyword`
      - rc 2
    * - `#5063`_
      - bug
      - high
      - Robot Framework does not run outside Windows if `signal.setitimer` is not available (affects e.g. Pyodide)
      - rc 1
    * - `#5069`_
      - enhancement
      - high
      - Japanese localization
      - rc 1
    * - `#5120`_
      - bug
      - high
      - Incorrect syntax in for loop crashes RF and html reports are not generated.
      - rc 1
    * - `#4993`_
      - bug
      - medium
      - Dialogs: Problems closing dialogs on Linux
      - rc 1
    * - `#5017`_
      - bug
      - medium
      - `start/end_body_item` listener v3 methods missing from documentation in User Guide
      - rc 1
    * - `#5051`_
      - bug
      - medium
      - Logging unexecuted keyword has unnecessary overhead if keywords are not found
      - rc 1
    * - `#5114`_
      - bug
      - medium
      - Dictionaries are not accepted as-is in argument conversion with unions containing TypedDicts
      - rc 1
    * - `#5115`_
      - bug
      - medium
      - `NotRequired` and `Required` not properly handled with Python < 3.11 in `TypedDict` conversion
      - rc 1
    * - `#5128`_
      - bug
      - medium
      - Named-only arguments are not trace logged with user keywords
      - rc 1
    * - `#5039`_
      - enhancement
      - medium
      - Use better theme with API docs at Read The Docs
      - rc 1
    * - `#5032`_
      - bug
      - low
      - Collections: No default value shown in documentation for `Get/Pop From Dictionary`
      - rc 1
    * - `#5035`_
      - bug
      - low
      - Unit test fails under Python 3.13
      - rc 1
    * - `#5070`_
      - bug
      - low
      - Typo in listener interface documentation in the User Guide
      - rc 1
    * - `#5100`_
      - bug
      - low
      - Acceptance tests fail if directory path contains spaces
      - rc 1
    * - `#5130`_
      - bug
      - low
      - Collections: Value of `ignore_case` argument accidentally logged
      - rc 1

Altogether 18 issues. View on the `issue tracker <https://github.com/robotframework/robotframework/issues?q=milestone%3Av7.0.1>`__.

.. _#5012: https://github.com/robotframework/robotframework/issues/5012
.. _#5023: https://github.com/robotframework/robotframework/issues/5023
.. _#5031: https://github.com/robotframework/robotframework/issues/5031
.. _#5063: https://github.com/robotframework/robotframework/issues/5063
.. _#5120: https://github.com/robotframework/robotframework/issues/5120
.. _#4993: https://github.com/robotframework/robotframework/issues/4993
.. _#5017: https://github.com/robotframework/robotframework/issues/5017
.. _#5051: https://github.com/robotframework/robotframework/issues/5051
.. _#5114: https://github.com/robotframework/robotframework/issues/5114
.. _#5115: https://github.com/robotframework/robotframework/issues/5115
.. _#5128: https://github.com/robotframework/robotframework/issues/5128
.. _#5039: https://github.com/robotframework/robotframework/issues/5039
.. _#5069: https://github.com/robotframework/robotframework/issues/5069
.. _#5032: https://github.com/robotframework/robotframework/issues/5032
.. _#5035: https://github.com/robotframework/robotframework/issues/5035
.. _#5070: https://github.com/robotframework/robotframework/issues/5070
.. _#5100: https://github.com/robotframework/robotframework/issues/5100
.. _#5130: https://github.com/robotframework/robotframework/issues/5130
