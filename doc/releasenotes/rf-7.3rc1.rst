=======================================
Robot Framework 7.3 release candidate 1
=======================================

.. default-role:: code

`Robot Framework`_ 7.3 is a feature release with variable type conversion,
enhancements and fixes related to timeouts, and various other exciting new
features and high priority bug fixes. This release candidate contains all
planned code changes.

Questions and comments related to the release can be sent to the `#devel`
channel on `Robot Framework Slack`_ and possible bugs submitted to
the `issue tracker`_.

If you have pip_ installed, just run

::

   pip install --pre --upgrade robotframework

to install the latest available release or use

::

   pip install robotframework==7.3rc1

to install exactly this version. Alternatively you can download the package
from PyPI_ and install it manually. For more details and other installation
approaches, see the `installation instructions`_.

Robot Framework 7.3 rc 1 was released on Thursday May 8, 2025.
The final release is targeted for Thursday May 15, 2025.

.. _Robot Framework: http://robotframework.org
.. _Robot Framework Foundation: http://robotframework.org/foundation
.. _pip: http://pip-installer.org
.. _PyPI: https://pypi.python.org/pypi/robotframework
.. _issue tracker milestone: https://github.com/robotframework/robotframework/issues?q=milestone%3Av7.3
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

Variable type conversion
------------------------

The most important new feature in Robot Framework 7.3 is variable type conversion
(`#3278`_). The syntax to specify variable types is `${name: type}` and the space
after the colon is mandatory. Variable type conversion supports the same types
that the `argument conversion`__ supports. For example, `${number: int}`
means that the value of the variable `${number}` is converted to an integer.

__ http://robotframework.org/robotframework/latest/RobotFrameworkUserGuide.html#supported-conversions

Variable types work in the Variables section, with the `VAR` syntax, when creating
variables based on keyword return values and, very importantly, with user keyword
arguments. All these usages are demonstrated by the following examples:

.. sourcecode:: robotframework

   *** Variables ***
   # Simple type.
   ${VERSION: float}         7.3
   # Parameterized type.
   ${CRITICAL: list[int]}    [3278, 5368, 5417]
   # With @{list} variables the type specified the item type.
   @{HIGH: int}              4173    5334    5386    5387
   # With @{dict} variables the type specified the value type.
   &{DATES: date}            rc1=2025-05-08    final=2025-05-15
   # Alternative syntax to specify both key and value types.
   &{NUMBERS: int=float}     1=2.3    4=5.6

   *** Test Cases ***
   Variables section
       # Validate above variables using the inline Python evaluation syntax.
       # This syntax is much more complicated than the syntax used above!
       Should Be Equal    ${VERSION}       ${{7.3}}
       Should Be Equal    ${CRITICAL}      ${{[3278, 5368, 5417]}}
       Should Be Equal    ${HIGH}          ${{[4173, 5334, 5386, 5387]}}
       Should Be Equal    ${DATES}         ${{{'rc1': datetime.date(2025, 5, 8), 'final': datetime.date(2025, 5, 15)}}}
       Should Be Equal    ${NUMBERS}       ${{{1: 2.3, 4: 5.6}}}

   VAR syntax
       # The VAR syntax supports types the same way as the Variables section
       VAR    ${number: int}      42
       Should Be Equal    ${number}    ${42}

   Assignment
       # In simple cases the VAR syntax is more convenient.
       ${number: int} =    Set Variable    42
       Should Be Equal    ${number}    ${42}
       # In this example conversion is more useful.
       ${match}    ${version: float} =    Should Match Regexp    RF 7.3    ^RF (\\d+\\.\\d+)$
       Should Be Equal    ${match}      RF 7.3
       Should Be Equal    ${version}    ${7.3}

   Keyword arguments
       # Argument conversion with user keywords is very convenient!
       Move    10    down    slow=no
       # Conversion handles validation automatically. This usage fails.
       Move    10    invalid

   Embedded argumemts
       # Also embedded arguments can be converted.
       Move 3.14 meters

   *** Keywords ***
   Move
       [Arguments]    ${distance: int}    ${direction: Literal["UP", "DOWN"]}    ${slow: bool}=True
       Should Be Equal    ${distance}     ${10}
       Should Be Equal    ${direction}    DOWN
       Should Be Equal    ${slow}         ${False}

   Move ${distance: int | float} meters
       Should Be Equal    ${distance}     ${3.14}

Fixes and enhancements for timeouts
-----------------------------------

Several high priority and even critical issues related to timeouts have been fixed.
Most of them are related to library keywords using `BuiltIn.run_keyword` which is
a somewhat special case, but some problems occurred also with normal keywords.
In addition to fixes, there have been some enhancements as well.

Avoid output file corruption
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Library keywords can use `BuiltIn.run_keyword` as an API to execute other keywords.
If Robot Framework timeouts occur when that is done, the timeout can interrupt
Robot Framework's own code that is preparing the new keyword to be executed.
That situation is otherwise handled fine, but if the timeout occurs when Robot
Framework is writing information to the output file, the output file can be
corrupted and it is not possible to generate log and report after the execution.
This severe problem has now been fixed by automatically pausing timeouts when
`BuiltIn.run_keyword` is used (`#5417`_).

Normally the odds that a timeout occurs after the parent keyword has called
`BuiltIn.run_keyword` but before the child keyword has actually started running
are pretty small, but if there are lof of such calls and also if child keywords
write a lot of log messages, the odds grow bigger. It is very likely that some
of the mysterious problems with output files being corrupted that have been
reported to our issue tracker have been caused by this issue. Hopefully we get
less such reports in the future!

Other fixes related to `BuiltIn.run_keyword` and timeouts
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

There are also some other fixes related to library keywords using `BuiltIn.run_keyword`
when timeouts are enabled:

- Timeouts are not deactivated after the child keyword returns (`#5422`_).
  This problem occurred only outside Windows and actually prevented the above
  bug corrupting output files outside Windows as well.
- Order and position of logged messages is correct (`#5423`_).

Other fixes related to timeouts
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- Logged messages respect the current log level (`#5395`_).
- Writing messages to the debug file and to the console is not delayed (`#3644`_).

Timeout related enhancements
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- It was discovered that libraries can easily handle Robot Framework's timeouts
  so that they can do cleanup activities if needed. How to do that in practice
  has been now documented in the User Guide (`#5377`_).
- Timeout support with Dialogs (`#5386`_) and Process (`#5345`_, `#5376`_)
  libraries has been enhanced. These enhancements are discussed separately below.

Fix crash if library has implemented `__dir__` and `__getattr__`
----------------------------------------------------------------

Although implementing `__dir__` is pretty rare, hard crashes are always severe.
As a concrete problem this bug prevented using the Faker tool directly as
a library (`#5368`_).

Enhancements to the Dialogs library
-----------------------------------

The Dialogs library is widely used in cases where something cannot be fully
automated or execution needs to be paused for some reason. It got two major
enhancements in this release.

Support timeouts and closing with Ctrl-C
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Robot Framework's timeouts are now finally able to kill opened dialogs (`#5386`_).
Earlier execution hang indefinitely if dialogs were open even if a timeout occurred,
and the timeout was really activated only after the dialog was manually closed.
The same fix also makes it possible to stop the execution with Ctrl-C even if
a dialog would be open.

Enhanced look and feel
~~~~~~~~~~~~~~~~~~~~~~

The actual dialogs were enhanced in different ways (`#5334`_):

- Dialogs got application and taskbar icons.
- Font size has been increased a bit to make text easier to read.
- More padding has been added around elements to make dialogs look better.
  Buttons being separated from each others a bit more also avoids misclicks.
- As the result of the above two changes, also the dialog size has increased.

See `this comment`__ for an example how new and old dialogs look like.

__ https://github.com/robotframework/robotframework/issues/5334#issuecomment-2761597900

Enhancements to the Process library
-----------------------------------

Also the Process library got two major enhancements in this release.

Avoid deadlock if process produces lot of output
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

It has been possible to avoid the deadlock by redirecting `stdout` and `stderr`
to files, but that is not necessary anymore (`#4173`_). Redirecting outputs to
files is often a good idea anyway, and should be done at least if a process
produces a huge amount of output.

Better support for Robot Framework's timeouts
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The Process library has its own timeout mechanism, but it now works better also
with Robot Framework's test and keyword timeouts:

- Robot Framework's timeouts were not able to interrupt `Run Process` and
  `Wait For Process` at all on Windows earlier (`#5345`_). In the worst case
  the execution could hang.
- Nowadays the process that is waited for is killed if Robot Framework timeout
  occurs (`#5376`_). This is better than leaving the process running on
  the background.

Automatic code formatting
-------------------------

Robot Framework source code and also test code has been auto-formatted
(`#5387`_). This is not really an enhancement in the tool itself, but
automatic formatting makes it easier to create and review pull requests.

Formatting is done using a combination of Ruff__, Black__ and isort__. These
tools should not be used directly, but instead formatting should be done
using an invoke__ task like::

    invoke format

More detailed instructions will be written to the `contribution guidelines`__
in the near future.

__ https://docs.astral.sh/ruff/
__ https://black.readthedocs.io/en/stable/
__ https://pycqa.github.io/isort/
__ https://www.pyinvoke.org/
__ https://github.com/robotframework/robotframework/blob/master/CONTRIBUTING.rst

Backwards incompatible changes
==============================

There is only one known backwards incompatible change in this release, but
`every change can break someones workflow`__.

__ https://xkcd.com/1172/

Variable type syntax may clash with existing variables
------------------------------------------------------

The syntax to specify variable types like `${x: int}` (`#3278`_) may clash with
existing variables having names with colons. This is not very likely, though,
because the type syntax requires having a space after the colon and names like
`${foo:bar}` are thus not affected. If someone actually has a variable with
a space after a colon, the space needs to be removed.

Deprecated features
===================

Deprecated utility functions
----------------------------

The following functions and other utilities under the `robot.utils` package
have been deprecated:

- `is_string`, `is_bytes`, `is_number`, `is_integer` and `is_pathlike` have been
  deprecated and should be replaced with `isinstance` like `isinstance(item, str)`
  and `isinstance(item, int)` (`#5416`_).
- `robot.utils.ET` has been deprecated and `xml.etree.ElementTree` should be
  used instead (`#5415`_).

Various other__ utilities__ have been deprecated in previous releases. Currently
deprecation warnings related to all these utils are not visible by default,
but they will be changed to more visible warnings in Robot Framework 8.0 and
the plan is to remove the utils in Robot Framework 9.0. Use the PYTHONWARNINGS__
environment variable or Python's `-W`__ option to make warnings more visible
if you want to see is your tool using any deprecated APIs. For example,
`-W error` turns all deprecation warnings to exceptions making them very
easy to discover.

__ https://github.com/robotframework/robotframework/issues/4150
__ https://github.com/robotframework/robotframework/issues/4500
__ https://docs.python.org/3/using/cmdline.html#envvar-PYTHONWARNINGS
__ https://docs.python.org/3/using/cmdline.html#cmdoption-W

Acknowledgements
================

Robot Framework development is sponsored by the `Robot Framework Foundation`_
and its over 70 member organizations. If your organization is using Robot Framework
and benefiting from it, consider joining the foundation to support its
development as well.

Robot Framework 7.3 team funded by the foundation consisted of `Pekka Klärck`_ and
`Janne Härkönen <https://github.com/yanne>`_. Janne worked only part-time and was
mainly responsible on Libdoc related fixes. In addition to work done by them, the
community has provided some great contributions:

- `Tatu Aalto <https://github.com/aaltat>`__ worked with Pekka to implement
  variable type conversion (`#3278`_). That was big task so huge thanks for
  Tatu and his employer `OP <https://www.op.fi/>`__ who let Tatu to use his
  work time for this enhancement.

- `@franzhaas <https://github.com/franzhaas>`__ helped with the Process library.
  He provided initial implementation both for avoiding deadlock (`#4173`_) and
  for fixing Robot Framework timeout support on Windows (`#5345`_).

- `Olivier Renault <https://github.com/orenault>`__ fixed a bug with BDD prefixes
  having same beginning (`#5340`_) and enhanced French BDD prefixes (`#5150`_).

- `Gad Hassine <https://github.com/hassineabd>`__ provided Arabic localization (`#5357`_).

- `Lucian D. Crainic <https://github.com/LucianCrainic>`__ added Italian Libdoc UI
  translation (`#5351`_)

Big thanks to Robot Framework Foundation, to community members listed above, and to
everyone else who has tested preview releases, submitted bug reports, proposed
enhancements, debugged problems, or otherwise helped with Robot Framework 7.3
development.

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
      - Added
    * - `#5368`_
      - bug
      - critical
      - Library with custom `__dir__` and attributes implemented via `__getattr__` causes crash
      - rc 1
    * - `#5417`_
      - bug
      - critical
      - Output file can be corrupted if library keyword uses `BuiltIn.run_keyword` and timeout occurs
      - rc 1
    * - `#3278`_
      - enhancement
      - critical
      - Variable type conversion
      - rc 1
    * - `#4173`_
      - bug
      - high
      - Process: Avoid deadlock when standard streams are not redirected to files
      - rc 1
    * - `#5386`_
      - bug
      - high
      - Dialogs: Not possible to stop execution with timeouts or by pressing Ctrl⁠-⁠C
      - rc 1
    * - `#5334`_
      - enhancement
      - high
      - Dialogs: Enhance look and feel
      - rc 1
    * - `#5387`_
      - enhancement
      - high
      - Automatic code formatting
      - rc 1
    * - `#3644`_
      - bug
      - medium
      - Writing messages to debug file and to console is delayed when timeouts are used
      - rc 1
    * - `#5330`_
      - bug
      - medium
      - Keyword accepting embedded arguments cannot be used with variable containing characters used in keyword name
      - rc 1
    * - `#5340`_
      - bug
      - medium
      - BDD prefixes with same beginning are not handled properly
      - rc 1
    * - `#5345`_
      - bug
      - medium
      - Process: Test and keyword timeouts do not work when running processes on Windows
      - rc 1
    * - `#5358`_
      - bug
      - medium
      - Libdoc: TypedDict documentation is broken in HTML output
      - rc 1
    * - `#5367`_
      - bug
      - medium
      - Embedded arguments are not passed as objects when executed as setup/teardown
      - rc 1
    * - `#5393`_
      - bug
      - medium
      - Cannot use keyword with parameterized special form like `TypeForm[param]` as type hint
      - rc 1
    * - `#5394`_
      - bug
      - medium
      - Embedded arguments using custom regexps cannot be used with inline Python evaluation syntax
      - rc 1
    * - `#5395`_
      - bug
      - medium
      - Messages logged when timeouts are active do not respect current log level
      - rc 1
    * - `#5399`_
      - bug
      - medium
      - TEST scope variable set on suite level removes SUITE scope variable with same name
      - rc 1
    * - `#5405`_
      - bug
      - medium
      - Extended variable assignment doesn't work with `@` or `&` syntax
      - rc 1
    * - `#5422`_
      - bug
      - medium
      - Timeouts are deactivated if library keyword uses `BuiltIn.run_keyword` (except on Windows)
      - rc 1
    * - `#5423`_
      - bug
      - medium
      - Log messages are in wrong order if library keyword uses `BuiltIn.run_keyword` and timeouts are used
      - rc 1
    * - `#5150`_
      - enhancement
      - medium
      - Enhance BDD support (GIVEN/WHEN/THEN) for French language
      - rc 1
    * - `#5351`_
      - enhancement
      - medium
      - Add Italian Libdoc UI translation
      - rc 1
    * - `#5357`_
      - enhancement
      - medium
      - Add Arabic localization
      - rc 1
    * - `#5376`_
      - enhancement
      - medium
      - Process: Kill process if Robot's timeout occurs when waiting for process to end
      - rc 1
    * - `#5377`_
      - enhancement
      - medium
      - Document how libraries can do cleanup activities if Robot's timeout occurs
      - rc 1
    * - `#5385`_
      - enhancement
      - medium
      - Bundle logo to distribution package and make it available for external tools
      - rc 1
    * - `#5412`_
      - enhancement
      - medium
      - Change keywords accepting configuration arguments as `**config` to use named-only arguments instead
      - rc 1
    * - `#5414`_
      - enhancement
      - medium
      - Add explicit APIs to `robot` root package and to all sub packages
      - rc 1
    * - `#5416`_
      - enhancement
      - medium
      - Deprecate `is_string`, `is_bytes`, `is_number`, `is_integer` and `is_pathlike` utility functions
      - rc 1
    * - `#5398`_
      - bug
      - low
      - Variable assignment is not validated during parsing
      - rc 1
    * - `#5403`_
      - bug
      - low
      - Confusing error message when using arguments with user keyword having invalid argument specification
      - rc 1
    * - `#5404`_
      - bug
      - low
      - Time strings using same marker multiple times like `2 seconds 3 seconds` should be invalid
      - rc 1
    * - `#5418`_
      - bug
      - low
      - DateTime: Getting timestamp as epoch seconds fails close to the epoch on Windows
      - rc 1
    * - `#5332`_
      - enhancement
      - low
      - Make list of languages in Libdoc's default language selection dynamic
      - rc 1
    * - `#5396`_
      - enhancement
      - low
      - Document limitations with embedded arguments utilizing custom regexps with variables
      - rc 1
    * - `#5397`_
      - enhancement
      - low
      - Expose execution mode via `${OPTIONS.rpa}`
      - rc 1
    * - `#5415`_
      - enhancement
      - low
      - Deprecate `robot.utils.ET` and use `xml.etree.ElementTree` instead
      - rc 1
    * - `#5424`_
      - enhancement
      - low
      - Document ERROR level and that logging with it stops execution if `--exit-on-error` is enabled
      - rc 1

Altogether 38 issues. View on the `issue tracker <https://github.com/robotframework/robotframework/issues?q=milestone%3Av7.3>`__.

.. _#5368: https://github.com/robotframework/robotframework/issues/5368
.. _#5417: https://github.com/robotframework/robotframework/issues/5417
.. _#3278: https://github.com/robotframework/robotframework/issues/3278
.. _#4173: https://github.com/robotframework/robotframework/issues/4173
.. _#5386: https://github.com/robotframework/robotframework/issues/5386
.. _#5334: https://github.com/robotframework/robotframework/issues/5334
.. _#5387: https://github.com/robotframework/robotframework/issues/5387
.. _#3644: https://github.com/robotframework/robotframework/issues/3644
.. _#5330: https://github.com/robotframework/robotframework/issues/5330
.. _#5340: https://github.com/robotframework/robotframework/issues/5340
.. _#5345: https://github.com/robotframework/robotframework/issues/5345
.. _#5358: https://github.com/robotframework/robotframework/issues/5358
.. _#5367: https://github.com/robotframework/robotframework/issues/5367
.. _#5393: https://github.com/robotframework/robotframework/issues/5393
.. _#5394: https://github.com/robotframework/robotframework/issues/5394
.. _#5395: https://github.com/robotframework/robotframework/issues/5395
.. _#5399: https://github.com/robotframework/robotframework/issues/5399
.. _#5405: https://github.com/robotframework/robotframework/issues/5405
.. _#5422: https://github.com/robotframework/robotframework/issues/5422
.. _#5423: https://github.com/robotframework/robotframework/issues/5423
.. _#5150: https://github.com/robotframework/robotframework/issues/5150
.. _#5351: https://github.com/robotframework/robotframework/issues/5351
.. _#5357: https://github.com/robotframework/robotframework/issues/5357
.. _#5376: https://github.com/robotframework/robotframework/issues/5376
.. _#5377: https://github.com/robotframework/robotframework/issues/5377
.. _#5385: https://github.com/robotframework/robotframework/issues/5385
.. _#5412: https://github.com/robotframework/robotframework/issues/5412
.. _#5414: https://github.com/robotframework/robotframework/issues/5414
.. _#5416: https://github.com/robotframework/robotframework/issues/5416
.. _#5398: https://github.com/robotframework/robotframework/issues/5398
.. _#5403: https://github.com/robotframework/robotframework/issues/5403
.. _#5404: https://github.com/robotframework/robotframework/issues/5404
.. _#5418: https://github.com/robotframework/robotframework/issues/5418
.. _#5332: https://github.com/robotframework/robotframework/issues/5332
.. _#5396: https://github.com/robotframework/robotframework/issues/5396
.. _#5397: https://github.com/robotframework/robotframework/issues/5397
.. _#5415: https://github.com/robotframework/robotframework/issues/5415
.. _#5424: https://github.com/robotframework/robotframework/issues/5424
