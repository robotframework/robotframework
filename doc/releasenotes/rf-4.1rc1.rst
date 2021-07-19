=======================================
Robot Framework 4.1 release candidate 1
=======================================

.. default-role:: code

`Robot Framework`_ 4.1 is a feature release with several nice enhancements,
for example, to the continue-on-failure mode and argument conversion,
as well as some bug fixes. This release candidate contains all planned changes.

Questions and comments related to the release can be sent to the
`robotframework-users`_ mailing list or to `Robot Framework Slack`_,
and possible bugs submitted to the `issue tracker`_.

If you have pip_ installed, just run

::

   pip install --pre --upgrade robotframework

to install the latest available release or use

::

   pip install robotframework==4.1rc1

to install exactly this version. Alternatively you can download the source
distribution from PyPI_ and install it manually. For more details and other
installation approaches, see the `installation instructions`_.

Robot Framework 4.1 rc 1 was released on Friday July 9, 2021. The final release
is planned for Monday July 19, 2021.

.. _Robot Framework: http://robotframework.org
.. _Robot Framework Foundation: http://robotframework.org/foundation
.. _pip: http://pip-installer.org
.. _PyPI: https://pypi.python.org/pypi/robotframework
.. _issue tracker milestone: https://github.com/robotframework/robotframework/issues?q=milestone%3Av4.1
.. _issue tracker: https://github.com/robotframework/robotframework/issues
.. _robotframework-users: http://groups.google.com/group/robotframework-users
.. _Robot Framework Slack: https://robotframework-slack-invite.herokuapp.com
.. _installation instructions: ../../INSTALL.rst


.. contents::
   :depth: 2
   :local:

Most important enhancements
===========================

Continue-on-failure mode can be controlled using tags
-----------------------------------------------------

Robot Framework has for long time had so called "continuable failures" that fail
the test case but allow execution to continue after the failure. Earlier this
functionality could only be enabled by library keywords using special exceptions
and by using BuiltIn keyword `Run Keyword And Continue On Failure`.

Robot Framework 4.1 eases using the continue-on-failure mode considerably by
allowing tests and keywords to use special tags to initiate it. The new
`robot:continue-on-failure` tag enables the mode so that if any of the executed
keywords fail, the next keyword is nevertheless run. This mode does not
propagate to lower level keywords, though, so in them execution stops
immediately and is resumed only on the test or keyword with the special tag.
If recursive usage is desired, it is possible to use another new tag
`robot:recursive-continue-on-failure`. (`#2285`_)

Argument conversion enhancements
--------------------------------

Automatic argument conversion has been improved in few different ways:

- `Derived enumerations`__ `IntEnum` and `IntFlag` are not supported. With both
  of them the value that is used can be a member name, like with other
  enumerations, or the integer value of a member. (`#3910`_)

- Number conversions (`int`, `float` and `Decimal`) support spaces and
  underscores as number separators like `2 000 000`. (`#4026`_)

- Integer conversion supports hexadecimal, octal and binary values using
  `0x`, `Oo` and `0b` prefixes, respectively. For example, `0xAA`, `0o252`,
  and `0b 1010 1010` are alternative ways to specify integer `170`. (`#3909`_)

__ https://docs.python.org/3/library/enum.html#derived-enumerations

Backwards incompatible changes
==============================

Robot Framework 4.1 is mostly backwards compatible with Robot Framework 4.0.
There are, however, few changes that may affect some users:

- If `--doc` or `--metadata` gets a value that points to an existing file,
  the actual value is read from that file, but in earlier releases the value is
  the path itself. It is rather unlikely that anyone has used this kind of
  documentation, but with metadata paths are possible. If a path to an existing
  file should be used as the actual value, the value should get some extra
  content to avoid the path to be recognized. Even a single space like
  `--metadata "Example: file.txt"` is enough. (`#4008`_)

- String library methods `should_be_uppercase` and `should_be_lowercase` have
  been renamed to `should_be_upper_case` and `should_be_lower_case`, respectively.
  Due to Robot Framework's keyword matching being underscore insensitive, this
  change does not affect normal usage of these keywords. If someone has used
  these methods programmatically, they need to update their code. (`#3890`_)

In addition to the changes explained above, any change to the code may
`affect someones workflow`__. It is thus a good idea to test new versions
before using them in production.

__ https://xkcd.com/1172/

Deprecated features
===================

Python 2 support
----------------

Robot Framework 4.1 is the last release supporting Python 2. Its possible bug
fix releases will still support Python 2 as well, but Robot Framework 5.0 will
require Python 3.6 or newer. (`#3457`__)

This unfortunately means also Jython__ and IronPython__ support is deprecated.
Support can be added again if these projects get Python 3.6+ compatible versions
released.

__ https://github.com/robotframework/robotframework/issues/3457
__ https://jython.org
__ https://ironpython.net

Built-in Tidy
-------------

The built-in Tidy tool has been deprecated in favor of the externally developed
and much more powerful RoboTidy__ tool. The built-in Tidy will be removed altogether
in Robot Framework 5.0. (`#4004`_)

__ https://robotidy.readthedocs.io

Acknowledgements
================

Robot Framework 4.1 development has been sponsored by the `Robot Framework Foundation`_
and its `close to 50 member organizations <https://robotframework.org/foundation/#members>`_.
In addition to that, we have got great contributions by the open source community:

- `Oliver Boehmer <https://github.com/oboehmer>`_ added support to control
  the continue-on-failure mode using test and keyword tags (`#2285`_).

- `Oliver Schwaneberg <https://github.com/Schwaneberg>`_ enhanced
  `Wait Until Keyword Succeeds` to support strict retry interval (`#3209`_).

- `Sergey Tupikov <https://github.com/vokiput>`_ added support to collapse
  whitespace with `Should Be Equal` and other comparison keywords (`#3884`_).

- `Mikhail Tuev <https://github.com/miktuy>`_ fixed using `--removekeywords` when
  test contains IF structure (`#4009`_) and renamed String library methods for
  consistency (`#3890`_).

- `Vinay Vennela <https://github.com/vinayvennela>`_ enhanced the dry-run mode
  to allow modifying tags using `Set Tags` and `Remove Tags` keywords (`#3985`_).

- `@asonkeri <https://github.com/asonkeri>`_ fixed keyword documentation
  scrollbar issues in Libdoc HTML output (`#4012`_).

Huge thanks to all sponsors, contributors and to everyone else who has reported
problems, participated in discussions on various forums, or otherwise helped to make
Robot Framework and its community and ecosystem better.

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
    * - `#4009`_
      - bug
      - high
      - Rebot generates invalid output.xml when using `--removekeywords` and there's IF on test case level
      - rc 1
    * - `#4036`_
      - bug
      - high
      - Log generation fails if using `--expandkeywords` and test contains `ELSE` branch
      - rc 1
    * - `#2285`_
      - enhancement
      - high
      - Support controlling continue-on-failure mode using test and keyword tags
      - rc 1
    * - `#3910`_
      - enhancement
      - high
      - Support `IntEnum` and `IntFlag` in automatic argument conversion
      - rc 1
    * - `#3798`_
      - bug
      - medium
      - Screenshot library prevents graceful termination of execution if wxPython is installed
      - rc 1
    * - `#3973`_
      - bug
      - medium
      - `--exitonfailure` mode is not initiated if test is failed by listener
      - rc 1
    * - `#3985`_
      - bug
      - medium
      - Tags set using keywords don't appear in dryrun logs
      - rc 1
    * - `#3994`_
      - bug
      - medium
      - Skipped tests will have fail status if suite teardown fails
      - rc 1
    * - `#3996`_
      - bug
      - medium
      - `--exitonfailure` incorrectly initiated if test skipped in teardown
      - rc 1
    * - `#4012`_
      - bug
      - medium
      - Keyword documentation scrollbar issues in a small browser window
      - rc 1
    * - `#4030`_
      - bug
      - medium
      - Libdoc stores data type documentation with extra indentation
      - rc 1
    * - `#4034`_
      - bug
      - medium
      - `@{varargs}` with default value in user keyword arguments not reported as error correctly
      - rc 1
    * - `#3209`_
      - enhancement
      - medium
      - `Wait Until Keyword Succeeds`: Support retry time with strict interval
      - rc 1
    * - `#3398`_
      - enhancement
      - medium
      - Execution in teardown should continue after keyword timeout
      - rc 1
    * - `#3818`_
      - enhancement
      - medium
      - Rebot should not take into account SKIP status when merging results
      - rc 1
    * - `#3884`_
      - enhancement
      - medium
      - BuiltIn: Support collapsing whitespaces with `Should Be Equal` and other comparison keywords
      - rc 1
    * - `#3909`_
      - enhancement
      - medium
      - Support binary, octal and hex values in argument conversion with `int` type
      - rc 1
    * - `#3934`_
      - enhancement
      - medium
      - Remote: Support Unicode characters in range 0-255, not only 0-127, in binary conversion
      - rc 1
    * - `#3946`_
      - enhancement
      - medium
      - Parser should detect invalid arguments in user keyword definition
      - rc 1
    * - `#4004`_
      - enhancement
      - medium
      - Deprecate built-in Tidy tool in favor of external Robotidy
      - rc 1
    * - `#4008`_
      - enhancement
      - medium
      - Support reading `--doc` and `--metadata` from file
      - rc 1
    * - `#4026`_
      - enhancement
      - medium
      - Support space and underscore as number separators in argument conversion
      - rc 1
    * - `#4037`_
      - enhancement
      - medium
      - Support `${var}[key]` syntax with lists that allow also key access
      - rc 1
    * - `#4027`_
      - bug
      - low
      - Wrong error message when test fails in teardown and skip-on-failure is active
      - rc 1
    * - `#4035`_
      - bug
      - low
      - Log not expanded correctly if all tests are skipped
      - rc 1
    * - `#3890`_
      - enhancement
      - low
      - String: Rename `should_be_uppercase` to `should_be_upper_case` (and same with `lower`)
      - rc 1
    * - `#3991`_
      - enhancement
      - low
      - Officially remove support for using using colon (`:`) in Settings section
      - rc 1
    * - `#4003`_
      - enhancement
      - low
      - Remove outdated information from installation instructions
      - rc 1

Altogether 28 issues. View on the `issue tracker <https://github.com/robotframework/robotframework/issues?q=milestone%3Av4.1>`__.

.. _#4009: https://github.com/robotframework/robotframework/issues/4009
.. _#4036: https://github.com/robotframework/robotframework/issues/4036
.. _#2285: https://github.com/robotframework/robotframework/issues/2285
.. _#3910: https://github.com/robotframework/robotframework/issues/3910
.. _#3798: https://github.com/robotframework/robotframework/issues/3798
.. _#3973: https://github.com/robotframework/robotframework/issues/3973
.. _#3985: https://github.com/robotframework/robotframework/issues/3985
.. _#3994: https://github.com/robotframework/robotframework/issues/3994
.. _#3996: https://github.com/robotframework/robotframework/issues/3996
.. _#4012: https://github.com/robotframework/robotframework/issues/4012
.. _#4030: https://github.com/robotframework/robotframework/issues/4030
.. _#4034: https://github.com/robotframework/robotframework/issues/4034
.. _#3209: https://github.com/robotframework/robotframework/issues/3209
.. _#3398: https://github.com/robotframework/robotframework/issues/3398
.. _#3818: https://github.com/robotframework/robotframework/issues/3818
.. _#3884: https://github.com/robotframework/robotframework/issues/3884
.. _#3909: https://github.com/robotframework/robotframework/issues/3909
.. _#3934: https://github.com/robotframework/robotframework/issues/3934
.. _#3946: https://github.com/robotframework/robotframework/issues/3946
.. _#4004: https://github.com/robotframework/robotframework/issues/4004
.. _#4008: https://github.com/robotframework/robotframework/issues/4008
.. _#4026: https://github.com/robotframework/robotframework/issues/4026
.. _#4037: https://github.com/robotframework/robotframework/issues/4037
.. _#4027: https://github.com/robotframework/robotframework/issues/4027
.. _#4035: https://github.com/robotframework/robotframework/issues/4035
.. _#3890: https://github.com/robotframework/robotframework/issues/3890
.. _#3991: https://github.com/robotframework/robotframework/issues/3991
.. _#4003: https://github.com/robotframework/robotframework/issues/4003
