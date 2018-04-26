=====================
Robot Framework 3.0.4
=====================

.. default-role:: code


`Robot Framework`_ 3.0.4 is a new minor release fixing regressions in
Robot Framework 3.0.3 related to using dictionary variables.

Questions and comments related to the release can be sent to the
`robotframework-users`_ mailing list or to `Robot Framework Slack`_,
and possible bugs submitted to the `issue tracker`_.

If you have pip_ installed, just run

::

   pip install --upgrade robotframework

to install the latest available release or use

::

   pip install robotframework==3.0.4

to install exactly this version. Alternatively you can download the source
distribution from PyPI_ and install it manually. For more details and other
installation approaches, see the `installation instructions`_.

Robot Framework 3.0.4 was released on Wednesday April 25, 2018.

.. _Robot Framework: http://robotframework.org
.. _pip: http://pip-installer.org
.. _PyPI: https://pypi.python.org/pypi/robotframework
.. _issue tracker milestone: https://github.com/robotframework/robotframework/issues?q=milestone%3Av3.0.4
.. _issue tracker: https://github.com/robotframework/robotframework/issues
.. _robotframework-users: http://groups.google.com/group/robotframework-users
.. _Robot Framework Slack: https://robotframework-slack-invite.herokuapp.com
.. _installation instructions: ../../INSTALL.rst

List of fixed issues
====================

.. list-table::
    :header-rows: 1

    * - ID
      - Type
      - Priority
      - Summary
    * - `#2814`_
      - bug
      - high
      - Iterable objects (incl. ElementTree objects) converted to lists when added to dictionary variables in RF 3.0.3
    * - `#2813`_
      - bug
      - medium
      - Modifying lists and dictionaries used as dictionary variable values stopped working in RF 3.0.3

Altogether 2 issues. View on the `issue tracker <https://github.com/robotframework/robotframework/issues?q=milestone%3Av3.0.4>`__.

.. _#2814: https://github.com/robotframework/robotframework/issues/2814
.. _#2813: https://github.com/robotframework/robotframework/issues/2813
