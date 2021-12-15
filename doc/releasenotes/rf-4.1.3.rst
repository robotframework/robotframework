=====================
Robot Framework 4.1.3
=====================

.. default-role:: code

`Robot Framework`_ 4.1.3 contains a fix to a regression related to parsing
`reStructuredText <https://en.wikipedia.org/wiki/ReStructuredText>`_ files
(`#4124`_) that was introduced in `Robot Framework 4.1.2`_.

Questions and comments related to the release can be sent to the
`robotframework-users`_ mailing list or to `Robot Framework Slack`_,
and possible bugs submitted to the `issue tracker`_.

If you have pip_ installed, just run

::

   pip install --pre --upgrade robotframework

to install the latest available release or use

::

   pip install robotframework==4.1.3

to install exactly this version. Alternatively you can download the source
distribution from PyPI_ and install it manually. For more details and other
installation approaches, see the `installation instructions`_.

Robot Framework 4.1.3 was released on Wednesday December 15, 2021.

.. _Robot Framework 4.1.2: https://github.com/robotframework/robotframework/blob/master/doc/releasenotes/rf-4.1.2.rst
.. _Robot Framework: http://robotframework.org
.. _Robot Framework Foundation: http://robotframework.org/foundation
.. _pip: http://pip-installer.org
.. _PyPI: https://pypi.python.org/pypi/robotframework
.. _issue tracker milestone: https://github.com/robotframework/robotframework/issues?q=milestone%3Av4.1.3
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
    * - `#4124`_
      - bug
      - medium
      - Errors emitted for unrecognized reST directives outside the robotframework code block, introduced in v4.1.2

Altogether 1 issue. View on the `issue tracker <https://github.com/robotframework/robotframework/issues?q=milestone%3Av4.1.3>`__.

.. _#4124: https://github.com/robotframework/robotframework/issues/4124
