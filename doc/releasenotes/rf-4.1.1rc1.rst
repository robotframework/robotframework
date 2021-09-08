=========================================
Robot Framework 4.1.1 release candidate 1
=========================================

.. default-role:: code

`Robot Framework`_ 4.1.1 is mostly a bug fix release but it also brings
official Python 3.10 support. This release candidate contains all issues
targeted to the final release.

Questions and comments related to the release can be sent to the
`robotframework-users`_ mailing list or to `Robot Framework Slack`_,
and possible bugs submitted to the `issue tracker`_.

If you have pip_ installed, just run

::

   pip install --pre --upgrade robotframework

to install the latest available release or use

::

   pip install robotframework==4.1.1rc1

to install exactly this version. Alternatively you can download the source
distribution from PyPI_ and install it manually. For more details and other
installation approaches, see the `installation instructions`_.

Robot Framework 4.1.1 rc 1 was released on Wednesday September 1, 2021.
It was followed by `Robot Framework 4.1.1 <rf-4.1.1.rst>`_ final release
on Wednesday September 8, 2021.

.. _Robot Framework: http://robotframework.org
.. _Robot Framework Foundation: http://robotframework.org/foundation
.. _pip: http://pip-installer.org
.. _PyPI: https://pypi.python.org/pypi/robotframework
.. _issue tracker milestone: https://github.com/robotframework/robotframework/issues?q=milestone%3Av4.1.1
.. _issue tracker: https://github.com/robotframework/robotframework/issues
.. _robotframework-users: http://groups.google.com/group/robotframework-users
.. _Robot Framework Slack: https://robotframework-slack-invite.herokuapp.com
.. _installation instructions: ../../INSTALL.rst

.. contents::
   :depth: 2
   :local:

Most important enhancements
===========================

Python 3.10 support
-------------------

Robot Framework 4.1.1 adds official support for the forthcoming `Python 3.10`__
release. Also older Robot Framework releases work with Python 3.10, but there
may be warnings due to those versions using nowadays deprecated APIs.

In addition to supporting Python 3.10 in general, Robot Framework 4.1.1 adds
support for writing unions in type hints in keyword arguments like `arg: X | Y`
(`#4075`_, `PEP 604`__).

__ https://docs.python.org/3.10/whatsnew/3.10.html
__ https://www.python.org/dev/peps/pep-0604

Fixes to rare crashes
---------------------

Robot Framework 4.1.1 fixes several problems resulting to execution crashing.
Crashes are always severe, but luckily all these cases occurred only in pretty rare
circumstances:

- SKIP in combination with continuable failures containing HTML error messages (`#4062`_)
- Non-existing variable used as teardown (`#4061`_)
- Strange functions without `__annotations__` (`#4059`_)
- `--removekeywords WUKS` when listener has logged messages and the WUKS keyword is
  otherwise empty (`#4063`_)

Acknowledgements
================

Robot Framework 4.1.1 development has been sponsored by the `Robot Framework Foundation`_
and its `close to 50 member organizations <https://robotframework.org/foundation/#members>`_.
Big thanks for the foundation for its continued support!

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
    * - `#4073`_
      - enhancement
      - critical
      - Python 3.10 support
      - rc 1
    * - `#4061`_
      - bug
      - high
      - Non-existing variable used as teardown causes crash
      - rc 1
    * - `#4062`_
      - bug
      - high
      - SKIP in conbination with continuable failures containing HTML error messages causes crash
      - rc 1
    * - `#4075`_
      - enhancement
      - high
      - Support `arg: X | Y` syntax in type conversion
      - rc 1
    * - `#4044`_
      - bug
      - medium
      - Unable to run dry mode since 4.1 if "Set Tags" keyword contains variables defined on runtime
      - rc 1
    * - `#4047`_
      - bug
      - medium
      - Variables in unexecuted FOR loops overwrite local variables
      - rc 1
    * - `#4057`_
      - bug
      - medium
      - Log: "Link to this keyword" functionality doesn't work correctly if parent has also messages
      - rc 1
    * - `#4059`_
      - bug
      - medium
      - Strange functions without `__annotations__` cause error
      - rc 1
    * - `#4063`_
      - bug
      - medium
      - `--removekeywords WUKS` causes crash if WUKS contains only messages
      - rc 1
    * - `#4071`_
      - bug
      - medium
      - Creating failure message with HTML fails if message contains exception type
      - rc 1
    * - `#3952`_
      - enhancement
      - low
      - Enhance `Set Test Variable` docs to explain it cannot be used outside test
      - rc 1

Altogether 11 issues. View on the `issue tracker <https://github.com/robotframework/robotframework/issues?q=milestone%3Av4.1.1>`__.

.. _#4073: https://github.com/robotframework/robotframework/issues/4073
.. _#4061: https://github.com/robotframework/robotframework/issues/4061
.. _#4062: https://github.com/robotframework/robotframework/issues/4062
.. _#4075: https://github.com/robotframework/robotframework/issues/4075
.. _#4044: https://github.com/robotframework/robotframework/issues/4044
.. _#4047: https://github.com/robotframework/robotframework/issues/4047
.. _#4057: https://github.com/robotframework/robotframework/issues/4057
.. _#4059: https://github.com/robotframework/robotframework/issues/4059
.. _#4063: https://github.com/robotframework/robotframework/issues/4063
.. _#4071: https://github.com/robotframework/robotframework/issues/4071
.. _#3952: https://github.com/robotframework/robotframework/issues/3952
