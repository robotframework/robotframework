=====================
Robot Framework 3.1.2
=====================

.. default-role:: code


`Robot Framework`_ 3.1.2 is a new minor release with few important bug fixes
and some nice enhancements. It also contains several minor deprecations related
to the test data syntax that pave the way towards Robot Framework 3.2 which will
contain a new test data parser.

Questions and comments related to the release can be sent to the
`robotframework-users`_ mailing list or to `Robot Framework Slack`_,
and possible bugs submitted to the `issue tracker`_.

If you have pip_ installed, just run

::

   pip install --upgrade robotframework

to install the latest available release or use

::

   pip install robotframework==3.1.2

to install exactly this version. Alternatively you can download the source
distribution from PyPI_ and install it manually. For more details and other
installation approaches, see the `installation instructions`_.

Robot Framework 3.1.2 was released on Friday May 24, 2019.

.. _Robot Framework: http://robotframework.org
.. _pip: http://pip-installer.org
.. _PyPI: https://pypi.python.org/pypi/robotframework
.. _issue tracker milestone: https://github.com/robotframework/robotframework/issues?q=milestone%3Av3.1.2
.. _issue tracker: https://github.com/robotframework/robotframework/issues
.. _robotframework-users: http://groups.google.com/group/robotframework-users
.. _Robot Framework Slack: https://robotframework-slack-invite.herokuapp.com
.. _installation instructions: ../../INSTALL.rst
.. _#3076: https://github.com/robotframework/robotframework/issues/3076

.. contents::
   :depth: 2
   :local:

Most important bug fixes
========================

- Creating scalar variables in resource files with custom separator
  (`SEPARATOR=<sep>`) has been fixed. (`#3102`_)

- Using keywords accepting embedded arguments when library is imported multiple
  times using the `WITH NAME` syntax has been fixed. (`#3181`_)

- The Tidy tool both handles new style for loops (`FOR ... END`) correctly and
  converts old style loops (`:FOR ... \ ...`) to new style loops automatically.
  (`#3064`_)

Deprecated features
===================

Robot Framework 3.1.2 deprecates some strange features in the test data syntax
that were found while developing the new test data parser for Robot Framework
3.2 (`#3076`_). A decision was made that features that make no sense in general,
or would unnecessarily complicate implementation of the new parser, are
deprecated and will not be supported anymore in the future. That includes
these features:

- Omitting lines with only `...` or `... ​ # comment`. (`#3107`_)
- Converting non-ASCII spaces to normal spaces during parsing. Accidentally
  typed no-break spaces are most likely to cause warnings, but also they ought
  to be rare. (`#3131`_)
- Collapsing spaces during parsing. Only affects the pipe separated format.
  (`#3132`_)
- Creating tests and keywords with name `...`. (`#3105`_)
- Escaping leading empty cells with `\​` except with for loops. (`#3148`_)

There are also some features that will be changed in RF 3.2 but they are not
deprecated:

- Documentation split into multiple columns will be concatenated with newlines,
  not spaces. (`#3106`_)
- In the pipe separated format for loops will require either the new style
  `END` or indentation needs to be escaped with `\​`. (`#3108`_)

Because the above changes are small, they should not affect many users. If
they anyway cause problems, let us know about them by commenting the linked
issues, sending an email to `robotframework-users`_ or joining the discussion
on the `#devel` channel on `Robot Framework Slack`_. Deprecation and removal
decisions can still be considered if they cause bigger problems.

Acknowledgements
================

Robot Framework 3.1.2 has been sponsored by `Robot Framework Foundation
<http://robotframework.org/foundation/>`_. Big thanks to all 27 member
organizations for your continued support, and hopefully there are even more
members in the future to help making development more active.

We have also got several great contributions by the community:

- Richard Turc (`@yamatoRT <https://github.com/yamatoRT>`__) fixed using
  literal `=` when keyword accepts named-only arguments. (`#3047`_)

- Dinara Aleskarova (`@aleskarovadi <https://github.com/aleskarovadi>`__)
  fixed type conversion in the dry-run mode when arguments contain variables.
  (`#3090`_)

- Maciej Brzozowski (`@mbrzozowski <https://github.com/mbrzozowski>`__)
  added true copy (i.e. `deepcopy`) support to `Copy List` and `Copy Dictionary`
  keywords. (`#2850`_)

- `@MaciejWiczk <https://github.com/MaciejWiczk>`__ implemented functionality
  to disable sorting with `Get Dictionary Keys` and `Get Dictionary Values`
  keywords. (`#3077`_)

- `@MisterChild <https://github.com/MisterChild>`__ fixed the egg. (`#3159`_)

Huge thanks to all contributors and to everyone else who has reported
problems, tested preview releases, participated discussion on various
forums, or otherwise helped to make Robot Framework as well as the ecosystem
and community around it better.

Thanks everyone and good luck with Robot Framework 3.1.2!

  | Pekka Klärck (`@pekkaklarck <https://github.com/pekkaklarck>`__)
  | Robot Framework Lead Developer

Full list of fixes and enhancements
===================================

.. list-table::
    :header-rows: 1

    * - ID
      - Type
      - Priority
      - Summary
    * - `#3064`_
      - bug
      - high
      - Tidy doesn't handle new for loop syntax correctly
    * - `#3102`_
      - bug
      - high
      - Creating scalar variables in resource files with custom separator does not work correctly
    * - `#3181`_
      - bug
      - high
      - Multiple instances of a library does not work with embedded arguments
    * - `#3047`_
      - bug
      - medium
      - Literal `=` needs to be escaped if keyword accepts named-only arguments
    * - `#3048`_
      - bug
      - medium
      - DateTime library documentation missing from releases
    * - `#3062`_
      - bug
      - medium
      - Regression if keyword uses `BuiltIn.run_keyword` internally to execute user keyword with timeouts and TRACE log level
    * - `#3090`_
      - bug
      - medium
      - Type conversion fails in dry-run if value contains variable
    * - `#3097`_
      - bug
      - medium
      - Document that `Create File` and `Append To File` convert `\n` to `\r\n` on Windows starting from RF 3.1
    * - `#3122`_
      - bug
      - medium
      - Avoid using deprecated PyYAML API
    * - `#2815`_
      - enhancement
      - medium
      - `Should Be Equal (As Strings)`: Support formatting values in error messages with `repr` and `ascii`
    * - `#2850`_
      - enhancement
      - medium
      - Support true copies (i.e. `deepcopy`) with `Copy List` and `Copy Dictionary`
    * - `#3077`_
      - enhancement
      - medium
      - Allow disabling sorting with `Collections.Get Dictionary Keys/Values`
    * - `#3105`_
      - enhancement
      - medium
      - Deprecate creating tests and keywords with name `...`
    * - `#3106`_
      - enhancement
      - medium
      - Document that handling documentation split to multiple columns will change in RF 3.2
    * - `#3107`_
      - enhancement
      - medium
      - Deprecate omitting lines with only `...`
    * - `#3108`_
      - enhancement
      - medium
      - Document that in pipe separated format for loops won't work without `END` or `\​` indentation in RF 3.2
    * - `#3131`_
      - enhancement
      - medium
      - Deprecate converting non-ASCII spaces to normal spaces during parsing
    * - `#3132`_
      - enhancement
      - medium
      - Deprecate collapsing spaces during parsing
    * - `#3148`_
      - enhancement
      - medium
      - Deprecate escaping leading empty cells with `\​`
    * - `#3164`_
      - enhancement
      - medium
      - `Log`: Support formatting message with `ascii` in addition to `repr`
    * - `#3052`_
      - bug
      - low
      - Syntax introduced in v3.1 not correctly highlighted in User Guide
    * - `#3135`_
      - bug
      - low
      - Links to demo projects in User Guide are broken
    * - `#3159`_
      - bug
      - low
      - Easter is coming but the egg is broken
    * - `#3160`_
      - bug
      - low
      - `Should Be Equal (As Strings)` doesn't handle multiline strings with different line endings well
    * - `#3168`_
      - bug
      - low
      - `Log` and elsewhere: `repr` of long strings cut on Python 3
    * - `#3169`_
      - bug
      - low
      - Collections: `Dictionary Should Contain Item` and some other kws have confusing documentation related to `values`
    * - `#3034`_
      - enhancement
      - low
      - Enhance error message when no test matches `--test`, `--include` or `--exclude`
    * - `#3098`_
      - enhancement
      - low
      - Document that `Create Dictionary` returns custom `DotDict` and `Convert To Dictionary` can convert it to normal `dict`
    * - `#3125`_
      - enhancement
      - low
      - Make resolving `ConnectionCache` alias into public API
    * - `#3150`_
      - enhancement
      - low
      - Show first logical test/suite documentation line on console
    * - `#3156`_
      - enhancement
      - low
      - Support native encoding with `Append To File`
    * - `#3172`_
      - enhancement
      - low
      - Update PyYAML included in standalone jar to v5.1
    * - `#3178`_
      - enhancement
      - low
      - Rephrase confusing "Data source does not exist." error

Altogether 33 issues. View on the `issue tracker <https://github.com/robotframework/robotframework/issues?q=milestone%3Av3.1.2>`__.

.. _#3064: https://github.com/robotframework/robotframework/issues/3064
.. _#3102: https://github.com/robotframework/robotframework/issues/3102
.. _#3181: https://github.com/robotframework/robotframework/issues/3181
.. _#3047: https://github.com/robotframework/robotframework/issues/3047
.. _#3048: https://github.com/robotframework/robotframework/issues/3048
.. _#3062: https://github.com/robotframework/robotframework/issues/3062
.. _#3090: https://github.com/robotframework/robotframework/issues/3090
.. _#3097: https://github.com/robotframework/robotframework/issues/3097
.. _#3122: https://github.com/robotframework/robotframework/issues/3122
.. _#2815: https://github.com/robotframework/robotframework/issues/2815
.. _#2850: https://github.com/robotframework/robotframework/issues/2850
.. _#3077: https://github.com/robotframework/robotframework/issues/3077
.. _#3105: https://github.com/robotframework/robotframework/issues/3105
.. _#3106: https://github.com/robotframework/robotframework/issues/3106
.. _#3107: https://github.com/robotframework/robotframework/issues/3107
.. _#3108: https://github.com/robotframework/robotframework/issues/3108
.. _#3131: https://github.com/robotframework/robotframework/issues/3131
.. _#3132: https://github.com/robotframework/robotframework/issues/3132
.. _#3148: https://github.com/robotframework/robotframework/issues/3148
.. _#3164: https://github.com/robotframework/robotframework/issues/3164
.. _#3052: https://github.com/robotframework/robotframework/issues/3052
.. _#3135: https://github.com/robotframework/robotframework/issues/3135
.. _#3159: https://github.com/robotframework/robotframework/issues/3159
.. _#3160: https://github.com/robotframework/robotframework/issues/3160
.. _#3168: https://github.com/robotframework/robotframework/issues/3168
.. _#3169: https://github.com/robotframework/robotframework/issues/3169
.. _#3034: https://github.com/robotframework/robotframework/issues/3034
.. _#3098: https://github.com/robotframework/robotframework/issues/3098
.. _#3125: https://github.com/robotframework/robotframework/issues/3125
.. _#3150: https://github.com/robotframework/robotframework/issues/3150
.. _#3156: https://github.com/robotframework/robotframework/issues/3156
.. _#3172: https://github.com/robotframework/robotframework/issues/3172
.. _#3178: https://github.com/robotframework/robotframework/issues/3178
