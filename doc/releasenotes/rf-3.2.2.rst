=====================
Robot Framework 3.2.2
=====================

.. default-role:: code

`Robot Framework`_ 3.2.2 is a new minor release with some bug fixes, Libdoc enhancements and
official Python 3.9 support. This is the last planned Robot Framework 3.2.x release. See
the `project milestones`__ for information about future releases.

Questions and comments related to the release can be sent to the
`robotframework-users`_ mailing list or to `Robot Framework Slack`_,
and possible bugs submitted to the `issue tracker`_.

To install the latest available release using pip_, just run

::

   pip install --upgrade robotframework

or to install exactly this version use

::

   pip install robotframework==3.2.2

Alternatively you can download the source distribution from PyPI_ and install it manually.
For more details and other installation approaches, see the `installation instructions`_.

Robot Framework 3.2.2 was released on Tuesday September 1, 2020.

__ https://github.com/robotframework/robotframework/milestones
.. _Robot Framework: http://robotframework.org
.. _Robot Framework Foundation: http://robotframework.org/foundation
.. _pip: http://pip-installer.org
.. _PyPI: https://pypi.python.org/pypi/robotframework
.. _issue tracker milestone: https://github.com/robotframework/robotframework/issues?q=milestone%3Av3.2.2
.. _issue tracker: https://github.com/robotframework/robotframework/issues
.. _robotframework-users: http://groups.google.com/group/robotframework-users
.. _Robot Framework Slack: https://robotframework-slack-invite.herokuapp.com
.. _installation instructions: ../../INSTALL.rst


.. contents::
   :depth: 2
   :local:

Most important enhancements
===========================

Libdoc enhancements
-------------------

Libdoc's HTML output has been enhanced in several ways:

- Keyword arguments are split to separate lines to make them easier to read especially when there are
  lot of arguments or arguments have type information or default values. (`#3639`_)

- If argument type is an enumeration__, its members are shown automatically in arguments. This
  helps, for example, with the Browser__ library that uses enumerations extensively. (`#3637`_)

- Shortcuts to keywords can be shown in expanded list in addition to the old compact style.
  (`#3635`_)

- Libdoc once again works if the original source of the keyword cannot be found. (`#3587`_)

To see actual examples of the enhancements, see the documentation for Browser__ and
SeleniumLibrary__.

__ https://docs.python.org/3/library/enum.html
__ https://github.com/MarketSquare/robotframework-browser
__ https://marketsquare.github.io/robotframework-browser/Browser.html#Shortcuts
__ https://robotframework.org/SeleniumLibrary/SeleniumLibrary.html#Shortcuts

Python 3.9 support
------------------

Although `Python 3.9`__ has not yet been officially released, Robot Framework 3.2.2 was tested using
its beta releases. Bugs affecting the XML library (`#3627`_) and line number detection of imported
libraries (`#3628`_) were fixed and Python 3.9 was also added to our CI. (`#3629`_)

__ https://docs.python.org/3.9/whatsnew/3.9.html

Acknowledgements
================

Robot Framework 3.2.2 development has been sponsored by the `Robot Framework Foundation`_.
Big thanks to all the `40+ member organizations <https://robotframework.org/foundation/#members>`_
for your continued support!

We have also had several great contributions by the open source community:

- `willemvanoort <https://github.com/willemvanoort>`__ enhanced type conversions with enums
  to work with normalized member names (`#3611`_)

- `Rudolf-AT <https://github.com/Rudolf-AT>`__ proposed enhancing Libdoc to allow switching between
  compact and expanded list of shortcuts and also implemented the functionality (`#3635`_)

- `Kerkko Pelttari <https://github.com/xylix>`__ changed Libdoc to show arguments on own lines (`#3639`_)

- `Dirk Richter <https://github.com/DirkRichter>`__ fixed problems with `--expandkeywords` (`#3585`_)

- `Jeroen <https://github.com/jeroen1602>`__ updated documentation to use the new `FOR/END` loop
  style instead of the old `:FOR` style (`#3596`_)

- `Mikhail Kulinich <https://github.com/tysonite>`__ added Python 3.9 to CI (`#3629`_)

Huge thanks to all sponsors, contributors and to everyone else who has reported problems,
participated in discussions on various forums, or otherwise helped to make Robot Framework and its community
and ecosystem better.

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
    * - `#3629`_
      - enhancement
      - high
      - Python 3.9 support
    * - `#3584`_
      - bug
      - medium
      - `--exitonfailure` option ignores dynamic changes to criticality
    * - `#3585`_
      - bug
      - medium
      - `--expandkeywords` fails in some cases
    * - `#3587`_
      - bug
      - medium
      - Libdoc: Generating documentation fails if getting keyword source file is not possible
    * - `#3618`_
      - bug
      - medium
      - Tidy adds trailing whitespace in multi-paragraph `Documentation`
    * - `#3626`_
      - bug
      - medium
      - Screenshot: Newer scrot versions don't overwrite images when they should
    * - `#3627`_
      - bug
      - medium
      - XML: `Remove Element(s)` does not work with Python 3.9
    * - `#3611`_
      - enhancement
      - medium
      - Argument conversion with enums should work with normalized names
    * - `#3635`_
      - enhancement
      - medium
      - Libdoc: Allow switching between compact and expanded list of shortcuts and tags
    * - `#3637`_
      - enhancement
      - medium
      - Show members of enum argument types in Libdoc HTML
    * - `#3639`_
      - enhancement
      - medium
      - Libdoc: Split arguments and tags in keyword table to own lines
    * - `#3596`_
      - bug
      - low
      - `:FOR` still used in BuiltIn library docs
    * - `#3598`_
      - bug
      - low
      -  Libdoc: Shortcuts are messed up on Firefox after search
    * - `#3621`_
      - bug
      - low
      - Bug in User Guide example related to `**kwargs`
    * - `#3628`_
      - bug
      - low
      - Line number reported by test libraries using class decorators is different in Python 3.9 than earlier
    * - `#3643`_
      - bug
      - low
      - Error running RobotFramework in a Windows console with PyTest

Altogether 16 issues. View on the `issue tracker <https://github.com/robotframework/robotframework/issues?q=milestone%3Av3.2.2>`__.

.. _#3629: https://github.com/robotframework/robotframework/issues/3629
.. _#3584: https://github.com/robotframework/robotframework/issues/3584
.. _#3585: https://github.com/robotframework/robotframework/issues/3585
.. _#3587: https://github.com/robotframework/robotframework/issues/3587
.. _#3618: https://github.com/robotframework/robotframework/issues/3618
.. _#3626: https://github.com/robotframework/robotframework/issues/3626
.. _#3627: https://github.com/robotframework/robotframework/issues/3627
.. _#3611: https://github.com/robotframework/robotframework/issues/3611
.. _#3635: https://github.com/robotframework/robotframework/issues/3635
.. _#3637: https://github.com/robotframework/robotframework/issues/3637
.. _#3639: https://github.com/robotframework/robotframework/issues/3639
.. _#3596: https://github.com/robotframework/robotframework/issues/3596
.. _#3598: https://github.com/robotframework/robotframework/issues/3598
.. _#3621: https://github.com/robotframework/robotframework/issues/3621
.. _#3628: https://github.com/robotframework/robotframework/issues/3628
.. _#3643: https://github.com/robotframework/robotframework/issues/3643
