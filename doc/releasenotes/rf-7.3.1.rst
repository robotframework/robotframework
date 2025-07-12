=====================
Robot Framework 7.3.1
=====================

.. default-role:: code

`Robot Framework`_ 7.3.1 is the first bug fix release in the Robot Framework 7.3.x
series. It fixes all reported regressions in `Robot Framework 7.3 <rf-7.3.rst>`_.

Questions and comments related to the release can be sent to the `#devel`
channel on `Robot Framework Slack`_ and possible bugs submitted to
the `issue tracker`_.

If you have pip_ installed, just run

::

   pip install --upgrade robotframework

to install the latest available stable release or use

::

   pip install robotframework==7.3.1

to install exactly this version. Alternatively you can download the package
from PyPI_ and install it manually. For more details and other installation
approaches, see the `installation instructions`_.

Robot Framework 7.3.1 was released on Monday June 16, 2025.

.. _Robot Framework: http://robotframework.org
.. _Robot Framework Foundation: http://robotframework.org/foundation
.. _pip: http://pip-installer.org
.. _PyPI: https://pypi.python.org/pypi/robotframework
.. _issue tracker milestone: https://github.com/robotframework/robotframework/issues?q=milestone%3Av7.3.1
.. _issue tracker: https://github.com/robotframework/robotframework/issues
.. _robotframework-users: http://groups.google.com/group/robotframework-users
.. _Slack: http://slack.robotframework.org
.. _Robot Framework Slack: Slack_
.. _installation instructions: ../../INSTALL.rst

.. contents::
   :depth: 2
   :local:

Most important enhancements
===========================

Parsing crashes if user keyword has invalid argument specification with type information
----------------------------------------------------------------------------------------

For example, this keyword caused parsing to crash so that the whole execution was
prevented (`#5443`_):

.. sourcecode:: robotframework

    *** Keywords ***
    Argument without default value after default values
        [Arguments]    ${a: int}=1    ${b: str}
        No Operation

This kind of invalid data is unlikely to be common, but the whole execution crashing
is nevertheless severe. This bug also affected IDEs using Robot's parsing modules
and caused annoying problems when the user had not finished writing the data.

Keyword resolution change when using variable in setup/teardown keyword name
----------------------------------------------------------------------------

Earlier variables in setup/teardown keyword names were resolved before matching
the name to available keywords. To support keywords accepting embedded arguments
better, this was changed in Robot Framework 7.3 so that the initial name with
variables was matched first  (`#5367`__). That change made sense in general,
but in the uncommon case that a keyword matched both a normal keyword and
a keyword accepting embedded arguments, the latter now had a precedence.

This behavioral change in Robot Framework 7.3 was not intended and the resulting
behavior was also inconsistent with how precedence rules work normally. That part
of the earlier change has now been reverted and nowadays keywords matching exactly
after variables have been resolved again have priority over embedded matches
(`#5444`_).

__ https://github.com/robotframework/robotframework/issues/5367

Acknowledgements
================

Robot Framework is developed with support from the Robot Framework Foundation
and its 80+ member organizations. Join the journey — support the project by
`joining the Foundation <Robot Framework Foundation_>`_.

In addition to the work sponsored by the foundation, this release got a contribution
from `Pasi Saikkonen <https://github.com/psaikkonen>`_ who fixed the toggle icon in
the log file when toggling a failed or skipped test (`#5322`_).

Big thanks to the Foundation and to everyone who has submitted bug reports, debugged
problems, or otherwise helped with Robot Framework development.

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
    * - `#5443`_
      - bug
      - critical
      - Parsing crashes if user keyword has invalid argument specification with type information
    * - `#5444`_
      - bug
      - high
      - Keyword matching exactly after replacing variables is not used with setup/teardown or with `Run Keyword` (regression)
    * - `#5441`_
      - enhancement
      - high
      - Update contribution guidelines
    * - `#5322`_
      - bug
      - low
      - Log: Toggle icon is stuck to `[+]` after toggling failed or skipped test
    * - `#5447`_
      - enhancement
      - low
      - Memory usage enhancement to `FileReader.readlines`

Altogether 5 issues. View on the `issue tracker <https://github.com/robotframework/robotframework/issues?q=milestone%3Av7.3.1>`__.

.. _#5443: https://github.com/robotframework/robotframework/issues/5443
.. _#5444: https://github.com/robotframework/robotframework/issues/5444
.. _#5441: https://github.com/robotframework/robotframework/issues/5441
.. _#5322: https://github.com/robotframework/robotframework/issues/5322
.. _#5447: https://github.com/robotframework/robotframework/issues/5447
