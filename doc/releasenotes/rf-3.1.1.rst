=====================
Robot Framework 3.1.1
=====================

.. default-role:: code

`Robot Framework`_ 3.1.1 contains fixes for few regressions in the recent
`Robot Framework 3.1 major release <rf-3.1.rst>`_. These reported and fixed
problems were all pretty severe but luckily occurred only in somewhat special
cases.

Questions and comments related to the release can be sent to the
`robotframework-users`_ mailing list or to `Robot Framework Slack`_,
and possible bugs submitted to the `issue tracker`_.

If you have pip_ installed, just run

::

   pip install --upgrade robotframework

to install the latest available stable release or use

::

   pip install robotframework==3.1.1

to install exactly this version. Alternatively you can download the source
distribution from PyPI_ and install it manually. For more details and other
installation approaches, see the `installation instructions`_.

Robot Framework 3.1.1 was released on Tuesday January 8, 2019.

.. _Robot Framework: http://robotframework.org
.. _pip: http://pip-installer.org
.. _PyPI: https://pypi.python.org/pypi/robotframework
.. _issue tracker milestone: https://github.com/robotframework/robotframework/issues?q=milestone%3Av3.1.1
.. _issue tracker: https://github.com/robotframework/robotframework/issues
.. _robotframework-users: http://groups.google.com/group/robotframework-users
.. _Robot Framework Slack: https://robotframework-slack-invite.herokuapp.com
.. _installation instructions: ../../INSTALL.rst

Full list of fixes and enhancements
===================================

.. list-table::
    :header-rows: 1

    * - ID
      - Type
      - Priority
      - Summary
    * - `#3029`_
      - bug
      - critical
      - Regression using `--suite` when executing multiple data sources or `--name` option (affects Pabot)
    * - `#3024`_
      - bug
      - high
      - Regression with Python 3.5+ when keyword is decorated and decorator uses `functools.wraps`
    * - `#3025`_
      - bug
      - high
      - Regression when using `BuiltIn.run_keyword` internally in keyword with timeouts

Altogether 3 issues. View on the `issue tracker <https://github.com/robotframework/robotframework/issues?q=milestone%3Av3.1.1>`__.

.. _#3029: https://github.com/robotframework/robotframework/issues/3029
.. _#3024: https://github.com/robotframework/robotframework/issues/3024
.. _#3025: https://github.com/robotframework/robotframework/issues/3025
