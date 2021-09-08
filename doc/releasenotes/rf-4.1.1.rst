=====================
Robot Framework 4.1.1
=====================

.. default-role:: code

`Robot Framework`_ 4.1.1 is mostly a bug fix release but it also brings
official `Python 3.10 <https://docs.python.org/3.10/whatsnew/3.10.html>`_
support.

Questions and comments related to the release can be sent to the
`robotframework-users`_ mailing list or to `Robot Framework Slack`_,
and possible bugs submitted to the `issue tracker`_.

If you have pip_ installed, just run

::

   pip install --upgrade robotframework

to install the latest available release or use

::

   pip install robotframework==4.1.1

to install exactly this version. Alternatively you can download the source
distribution from PyPI_ and install it manually. For more details and other
installation approaches, see the `installation instructions`_.

Robot Framework 4.1.1 was released on Wednesday September 8, 2021.

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

Robot Framework 4.1.1 adds official support for the forthcoming `Python 3.10`_
release. Also older Robot Framework releases work with Python 3.10, but there
are warnings due to those versions using nowadays deprecated Python APIs.

In addition to supporting Python 3.10 in general, Robot Framework 4.1.1 adds
support for writing unions in type hints like `arg: X | Y`. (`#4075`_, `PEP 604`__).
As the example below demonstrates, this syntax is quite a bit more convenient
in cases where an argument has multiple possible types:

.. code:: python

    # Old way, need to import and use Union.

    from typing import Union


    def example(arg: Union[int, float]):
        ...

.. code:: python

    # New way, no imports needed. Requires Python 3.10 and RF 4.1.1 or newer.

    def example(arg: int | float):
        ...

__ https://www.python.org/dev/peps/pep-0604

Fixes to rare crashes
---------------------

Robot Framework 4.1.1 fixes several problems resulting to fatal crashes during
execution. Crashes are always severe, but luckily all these crashes occurred
only in rather rare circumstances:

- SKIP in combination with continuable failures containing HTML error messages (`#4062`_)
- Non-existing variable used as teardown (`#4061`_)
- Strange functions without `__annotations__` (`#4059`_)
- `--removekeywords WUKS` when listener has logged messages and `Wait Until Keyword
  Succeeds` keyword itself is otherwise empty (`#4063`_)

Acknowledgements
================

Robot Framework 4.1.1 development has been sponsored by the `Robot Framework Foundation`_
and its `close to 50 member organizations <https://robotframework.org/foundation/#members>`_.
Big thanks for the foundation for its continued support! If your organization is using
Robot Framework and finds it useful, consider joining the foundation to make make
sure it is maintained and developed further also in the future.

Robot Framework 4.1.1 was a pretty small release and there was only one pull request
by the wider open source community. Thanks `@chriscallan <https://github.com/chriscallan>`__
for enhancing documentation related to `Set Test Variable` (`#3952`_) and also to everyone
else who has submitted bug reports, helped debugging problems, or otherwise helped with
this release.

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
    * - `#4073`_
      - enhancement
      - critical
      - Python 3.10 support
    * - `#4061`_
      - bug
      - high
      - Non-existing variable used as teardown causes crash
    * - `#4062`_
      - bug
      - high
      - SKIP in combination with continuable failures containing HTML error messages causes crash
    * - `#4075`_
      - enhancement
      - high
      - Support `arg: X | Y` syntax in type conversion
    * - `#4044`_
      - bug
      - medium
      - Unable to run dry mode since 4.1 if "Set Tags" keyword contains variables defined on runtime
    * - `#4047`_
      - bug
      - medium
      - Variables in unexecuted FOR loops overwrite local variables
    * - `#4057`_
      - bug
      - medium
      - Log: "Link to this keyword" functionality doesn't work correctly if parent has also messages
    * - `#4059`_
      - bug
      - medium
      - Strange functions without `__annotations__` cause error
    * - `#4063`_
      - bug
      - medium
      - `--removekeywords WUKS` can cause crash
    * - `#4071`_
      - bug
      - medium
      - Creating failure message with HTML fails if message contains exception type
    * - `#3952`_
      - enhancement
      - low
      - Enhance `Set Test Variable` docs to explain it cannot be used outside test

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
