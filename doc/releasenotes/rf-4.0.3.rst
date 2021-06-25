=====================
Robot Framework 4.0.3
=====================

.. default-role:: code

`Robot Framework`_ 4.0.3 fixes few regressions, including a critical regression
using `TypedDict` in type hints introduced by earlier RF 4.0.x releases.

Questions and comments related to the release can be sent to the
`robotframework-users`_ mailing list or to `Robot Framework Slack`_,
and possible bugs submitted to the `issue tracker`_.

If you have pip_ installed, just run

::

   pip install --pre --upgrade robotframework

to install the latest available release or use

::

   pip install robotframework==4.0.3

to install exactly this version. Alternatively you can download the source
distribution from PyPI_ and install it manually. For more details and other
installation approaches, see the `installation instructions`_.

Robot Framework 4.0.3 was released on Tuesday May 25, 2021.
For information about all new features in the Robot Framework 4.0.x series,
see the `Robot Framework 4.0`__ release notes.

__ https://github.com/robotframework/robotframework/blob/master/doc/releasenotes/rf-4.0.rst

.. _Robot Framework: http://robotframework.org
.. _Robot Framework Foundation: http://robotframework.org/foundation
.. _pip: http://pip-installer.org
.. _PyPI: https://pypi.python.org/pypi/robotframework
.. _issue tracker milestone: https://github.com/robotframework/robotframework/issues?q=milestone%3Av4.0.3
.. _issue tracker: https://github.com/robotframework/robotframework/issues
.. _robotframework-users: http://groups.google.com/group/robotframework-users
.. _Robot Framework Slack: https://robotframework-slack-invite.herokuapp.com
.. _installation instructions: ../../INSTALL.rst

.. contents::
   :depth: 2
   :local:

Most important enhancements
===========================

Regression using `TypedDict` as type hint
-----------------------------------------

Robot Framework 4.0.1 changed how `Union` used as a type hint works (`#3897`__).
The change itself was valid, but it unfortunately introduced a regression making
it impossible to use `Union` containing `TypedDict` or subscribed generics
(e.g. `List[int]`) as a type hint. The latter problem with generics was fixed in
Robot Framework 4.0.2 (`#3931`__), but that change very unfortunately made the
problem with `TypedDict` even worse and made it impossible to use them as type
hints at all.

Robot Framework 4.0.3 fixes the problem with `TypedDict` with and without `Union`
(`#3969`_). The fix is generic and should prevent this kind of problems occurring
also with other types. Hopefully the saga with `Union` as type hint now finally ends.

__ https://github.com/robotframework/robotframework/issues/3897
__ https://github.com/robotframework/robotframework/issues/3931

Acknowledgements
================

Robot Framework 4.0.3 development has been sponsored by the `Robot Framework Foundation`_
and its `close to 50 member organizations <https://robotframework.org/foundation/#members>`_.
Thanks for your continued support!

| `Pekka Klärck <https://github.com/pekkaklarck>`__
| Robot Framework Lead Developer

Full list of fixes and enhancements
===================================

.. list-table::
    :header-rows: 1

    * - ID
      - Type
      - Priority
      - Summary
    * - `#3969`_
      - bug
      - critical
      - Regression using `TypedDict` as type hint
    * - `#3965`_
      - bug
      - medium
      - Nested extended variable assignment doesn't work if parent uses item access
    * - `#3970`_
      - bug
      - medium
      - `--flattenkeywords` doesn't flatten IF/ELSE blocks

Altogether 3 issues. View on the `issue tracker <https://github.com/robotframework/robotframework/issues?q=milestone%3Av4.0.3>`__.

.. _#3969: https://github.com/robotframework/robotframework/issues/3969
.. _#3965: https://github.com/robotframework/robotframework/issues/3965
.. _#3970: https://github.com/robotframework/robotframework/issues/3970
