===========================
Robot Framework 3.2 alpha 1
===========================


.. default-role:: code


`Robot Framework`_ 3.2

All issues targeted for Robot Framework v3.2 can be found
from the `issue tracker milestone`_.

Questions and comments related to the release can be sent to the
`robotframework-users`_ mailing list or to `Robot Framework Slack`_,
and possible bugs submitted to the `issue tracker`_.

If you have pip_ installed, just run

::

   pip install --pre --upgrade robotframework

to install the latest available release or use

::

   pip install robotframework==3.2a1

to install exactly this version. Alternatively you can download the source
distribution from PyPI_ and install it manually. For more details and other
installation approaches, see the `installation instructions`_.

Robot Framework 3.2a1 was released on ???.

.. _Robot Framework: http://robotframework.org
.. _pip: http://pip-installer.org
.. _PyPI: https://pypi.python.org/pypi/robotframework
.. _issue tracker milestone: https://github.com/robotframework/robotframework/issues?q=milestone%3Av3.1
.. _issue tracker: https://github.com/robotframework/robotframework/issues
.. _robotframework-users: http://groups.google.com/group/robotframework-users
.. _Robot Framework Slack: https://robotframework-slack-invite.herokuapp.com
.. _installation instructions: ../../INSTALL.rst


.. contents::
   :depth: 2
   :local:

Most important enhancements
===========================


Backwards incompatible changes
==============================


Full list of fixes and enhancements
===================================

.. list-table::
    :header-rows: 1

    * - ID
      - Type
      - Priority
      - Summary
      - Added
    * - `#3209`_
      - enhancement
      - normal
      - Add `strict:` switch to `retry_interval` in keyword `Wait Until Keyword Succeeds` to ensure a fixed execution frequency of the keyword, instead of adding `retry_interval` as a static wait time.
      - alpha 1


Altogether 1 issues. View on the `issue tracker <https://github.com/robotframework/robotframework/issues?q=milestone%3Av3.2>`__.
