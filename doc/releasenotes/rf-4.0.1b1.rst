============================
Robot Framework 4.0.1 beta 1
============================

.. default-role:: code

`Robot Framework`_ 4.0.1 is the first bug fix release in the Robot Framework
4.0.x series. This beta release contains fixes to all issues that have been
reported so far, but if more problems are encountered they can still be fixed
before the final Robot Framework 4.0.1 release.

Questions and comments related to the release can be sent to the
`robotframework-users`_ mailing list or to `Robot Framework Slack`_,
and possible bugs submitted to the `issue tracker`_.

If you have pip_ installed, just run

::

   pip install --pre --upgrade robotframework

to install the latest available release or use

::

   pip install robotframework==4.0.1b1

to install exactly this version. Alternatively you can download the source
distribution from PyPI_ and install it manually. For more details and other
installation approaches, see the `installation instructions`_.

Robot Framework 4.0.1 beta 1 was released on Thursday April 1, 2021.
The final Robot Framework 4.0.1 release is planned for Thursday April 8, 2021.

.. _Robot Framework: http://robotframework.org
.. _Robot Framework Foundation: http://robotframework.org/foundation
.. _pip: http://pip-installer.org
.. _PyPI: https://pypi.python.org/pypi/robotframework
.. _issue tracker milestone: https://github.com/robotframework/robotframework/issues?q=milestone%3Av4.0.1
.. _issue tracker: https://github.com/robotframework/robotframework/issues
.. _robotframework-users: http://groups.google.com/group/robotframework-users
.. _Robot Framework Slack: https://robotframework-slack-invite.herokuapp.com
.. _installation instructions: ../../INSTALL.rst

.. contents::
   :depth: 2
   :local:

Most important fixes
====================

Fix running keywords in `start/end_suite` listener method
---------------------------------------------------------

Listeners can execute keywords by using `BuiltIn().run_keyword`. Using it in
listener `start/end_suite` methods created output.xml that Robot Framework
itself could not parse. (`#3893`_)

This problem affected, for example, DataDriver__, but that project was luckily
able to workaround it in their latest release.

__ https://github.com/Snooz82/robotframework-datadriver

Fix skipping tests in suite teardown if suite setup has been failed or skipped
------------------------------------------------------------------------------

Using the new `Skip` keyword or some other skipping approach in suite teardown
crashed the whole test execution to crash if suite setup had either been skipped
or failed. (`#3896`_)

Avoid argument conversion if given argument has one of the accepted types
-------------------------------------------------------------------------

Argument conversion with `multiple possible types`__ is a new feature in
Robot Framework 4.0. It worked fine otherwise, but arguments that already
had one of the accepted types could be unnecessarily converted to other types
(`#3897`_). For example, if an argument had type information like
`arg: Union[int, float]` and it was called with a float `1.5`, the value
was converted to an integer even though also float would be accepted.
In addition to that, this functionality broke using `${None}` when an argument
had `None` as a default value if it had a type hint (`#3908`_).

__ https://github.com/robotframework/robotframework/issues/3738

Backwards incompatible changes
==============================

The aforementioned change to argument conversion logic when an argument has
multiple possible types (`#3897`_) is backwards incompatible compared to how
conversion worked in Robot Framework 4.0. For example, if an argument has type
information like `arg: Union[int, str]` and it is called with a string
`42`, the value is converted to an integer in Robot Framework 4.0, but in
Robot Framework 4.0.1 it is passed in as a string.

Because the original functionality did not work properly in all cases, there
was no other solution than changing it. Luckily this feature is brand new, and
the change mainly affects cases where `str` is one of the accepted types, so
it is unlikely that many users are affected.

Acknowledgements
================

Robot Framework 4.0.1 development has been sponsored by the `Robot Framework Foundation`_
and its `close to 50 member organizations <https://robotframework.org/foundation/#members>`_.
In addition to that we got these great contributions by the open source community:

- `KotlinIsland <https://github.com/KotlinIsland>`__ fixed argument conversion with
  multiple types (`#3897`_). This also fixed the regression with converting `${None}`
  to a string even if argument default value is `None` (`#3908`_).

- `mhwaage <https://github.com/mhwaage>`__ fixed using `pathlib.Path` when saving
  programmatically modified results to disk (`#3904`_).

Big thanks to sponsors, contributors and to everyone else who has reported problems or
otherwise helped to make Robot Framework better!

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
      - Added
    * - `#3893`_
      - bug
      - critical
      - Using `BuiltIn().run_keyword` in listener `start/end_suite` method creates invalid output.xml
      - beta 1
    * - `#3896`_
      - bug
      - high
      - Skipping suite teardown causes a crash if suite setup has been failed or skipped
      - beta 1
    * - `#3897`_
      - bug
      - high
      - Argument should not be converted if its type is one of the accepted types
      - beta 1
    * - `#3882`_
      - bug
      - medium
      - Passing `--noncritical` or `--skiponfailure` using `robot.run` API as a string is broken
      - beta 1
    * - `#3908`_
      - bug
      - medium
      - `${None}` converted to string even if argument default value is `None`
      - beta 1
    * - `#3911`_
      - bug
      - medium
      - Expanding keywords recursively in log.html is broken
      - beta 1
    * - `#3912`_
      - bug
      - medium
      - Deprecating `--critical` does not work correctly
      - beta 1
    * - `#3913`_
      - bug
      - medium
      - `Run Keyword If Test Failed` is executed when test is skipped
      - beta 1
    * - `#3915`_
      - bug
      - medium
      - robot.tidy removes indent within IF/ELSE IF/ELSE blocks
      - beta 1
    * - `#3903`_
      - bug
      - low
      - FORs and IFs aren't omitted when generating only report based on output.xml
      - beta 1
    * - `#3904`_
      - bug
      - low
      - Using `pathlib.Path` when saving programmatically modified results does not work
      - beta 1
    * - `#3889`_
      - enhancement
      - low
      - Enhance documentation of programmatically modifying setups and teardowns
      - beta 1

Altogether 12 issues. View on the `issue tracker <https://github.com/robotframework/robotframework/issues?q=milestone%3Av4.0.1>`__.

.. _#3893: https://github.com/robotframework/robotframework/issues/3893
.. _#3896: https://github.com/robotframework/robotframework/issues/3896
.. _#3897: https://github.com/robotframework/robotframework/issues/3897
.. _#3882: https://github.com/robotframework/robotframework/issues/3882
.. _#3908: https://github.com/robotframework/robotframework/issues/3908
.. _#3911: https://github.com/robotframework/robotframework/issues/3911
.. _#3912: https://github.com/robotframework/robotframework/issues/3912
.. _#3913: https://github.com/robotframework/robotframework/issues/3913
.. _#3915: https://github.com/robotframework/robotframework/issues/3915
.. _#3903: https://github.com/robotframework/robotframework/issues/3903
.. _#3904: https://github.com/robotframework/robotframework/issues/3904
.. _#3889: https://github.com/robotframework/robotframework/issues/3889
