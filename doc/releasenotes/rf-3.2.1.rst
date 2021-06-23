=====================
Robot Framework 3.2.1
=====================

.. default-role:: code

`Robot Framework`_ 3.2.1 is a new minor release fixing two
high priority regressions in `Robot Framework 3.2 <rf-3.2.rst>`_.
For information about all the features and fixes in Robot Framework
3.2 see `its release notes <rf-3.2.rst>`_.

Questions and comments related to this release can be sent to the
`robotframework-users`_ mailing list or to `Robot Framework Slack`_,
and possible bugs submitted to the `issue tracker`_.

If you have pip_ installed, just run

::

   pip install --upgrade robotframework

to install the latest available release or use

::

   pip install robotframework==3.2.1

to install exactly this version. Alternatively you can download the source
distribution from PyPI_ and install it manually. For more details and other
installation approaches, see the `installation instructions`_.

Robot Framework 3.2.1 was released on Monday May 4, 2020.

.. _Robot Framework: http://robotframework.org
.. _Robot Framework Foundation: http://robotframework.org/foundation
.. _pip: http://pip-installer.org
.. _PyPI: https://pypi.python.org/pypi/robotframework
.. _issue tracker milestone: https://github.com/robotframework/robotframework/issues?q=milestone%3Av3.2.1
.. _issue tracker: https://github.com/robotframework/robotframework/issues
.. _robotframework-users: http://groups.google.com/group/robotframework-users
.. _Robot Framework Slack: https://robotframework-slack-invite.herokuapp.com
.. _installation instructions: ../../INSTALL.rst


.. contents::
   :depth: 2
   :local:

Most important enhancements
===========================

Regression with keywords methods using wrapping decorators
----------------------------------------------------------

If a keyword is implemented as a method in a class and the method is
decorated with a "wrapping decorator", keyword argument detection does
not work correctly with Robot Framework 3.2. A "wrapping decorator" is
a decorator that sets the `__wrapped__` attribute using `functools.wraps`__
or otherwise. For more details and a concrete example see issue `#3561`_.

This issue affects at least FakerLibrary__ and AppiumLibrary__.

__ https://docs.python.org/3/library/functools.html#functools.wraps
__ https://github.com/guykisel/robotframework-faker
__ https://github.com/serhatbolsu/robotframework-appiumlibrary

Execution can crash if `stdin` is closed
----------------------------------------

Robot Framework 3.2 execution crashes if the standard input stream is
closed and additionally standard output and error streams are redirected.
An exception is Windows with Python 3.6 or newer. For details see `#3565`_.

Full list of fixes and enhancements
===================================

.. list-table::
    :header-rows: 1

    * - ID
      - Type
      - Priority
      - Summary
    * - `#3561`_
      - bug
      - critical
      - Regression with keywords implemented as methods with wrapping decorator
    * - `#3565`_
      - bug
      - high
      - Execution can crash if `stdin` is closed

Altogether 2 issues. View on the `issue tracker <https://github.com/robotframework/robotframework/issues?q=milestone%3Av3.2.1>`__.

.. _#3561: https://github.com/robotframework/robotframework/issues/3561
.. _#3565: https://github.com/robotframework/robotframework/issues/3565
