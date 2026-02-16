=======================================
Robot Framework 7.4 release candidate 2
=======================================

.. default-role:: code

`Robot Framework`_ 7.4 is a new feature release with support for `secret
variables`_, `typed standard library keywords`_, `enhancements to working with
bytes`_ and various other features and fixes. This release candidate
contains all planned code changes.

Questions and comments related to the release can be sent to the `#devel`
channel on `Robot Framework Slack`_ and possible bugs submitted to
the `issue tracker`_.

If you have pip_ installed, just run

::

   pip install --pre --upgrade robotframework

to install the latest available release or use

::

   pip install robotframework==7.4rc2

to install exactly this version. Alternatively you can download the package
from PyPI_ and install it manually. For more details and other installation
approaches, see the `installation instructions`_.

Robot Framework 7.4 release candidate 2 was released on Tuesday December 9, 2025.
`Robot Framework 7.4 final <rf-7.4rst>`_ was released on Friday December 12, 2025.

.. _Robot Framework: http://robotframework.org
.. _Robot Framework Foundation: http://robotframework.org/foundation
.. _pip: http://pip-installer.org
.. _PyPI: https://pypi.python.org/pypi/robotframework
.. _issue tracker milestone: https://github.com/robotframework/robotframework/issues?q=milestone%3Av7.4
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

Secret variables
----------------

The most important enhancement in Robot Framework 7.4 is the support for
"secret" variables that hide their values in data and log files (`#4537`_).
These variables encapsulate their values so that the real values are not
logged even on the trace level when variables are passed between keywords as
arguments and return values.

The actual value is available via the `value` attribute of a secret variable.
It is mainly meant to be used by `library keywords`__ that accept values with
the new Secret_ type, but it can be accessed also in the data using the extended
variable syntax like `${secret.value}`. Accessing the value in the data makes it
visible in the log file similarly as if it was a normal variable, so that should
only be done for debugging or testing purposes.

.. note:: Some keywords in OperatingSystem and Process libraries support
          secret variables (`#5512`_). For example, files can be created and
          process executed so that used values are not disclosed in log files.

.. warning:: Secret variables do not hide or encrypt their values. The real values
             are thus available for all code that can access these variables directly
             or indirectly via Robot Framework APIs.

__ `Keywords accepting only Secret values`_
.. _Secret: https://robot-framework.readthedocs.io/en/master/autodoc/robot.utils.html#robot.utils.secret.Secret
.. _robot.api.types.Secret: Secret_

Creating secrets in data
~~~~~~~~~~~~~~~~~~~~~~~~

In the data secret variables can be created in the Variables section and
by using the VAR syntax. To avoid secret values being visible to everyone who
has access to the data, it is not possible to create secret variables using
literal values. Instead the value must be created using an existing secret variable
or an environment variable like `%{NAME}`. In both cases joining a secret value
with a literal value like `%{SECRET}123` is allowed as well.

If showing the secret variable in the data is not an issue, it is possible to use
environment variable default values like `%{NAME=default}`. The name can even be
left empty like `%{=secret}` to always use the default value.

.. sourcecode:: robotframework

   *** Variables ***
   ${NORMAL: Secret}     ${XXX}          # ${XXX} must itself be a secret variable.
   ${ENVIRON: Secret}    %{EXAMPLE}      # Environment variables are supported directly.
   ${DEFAULT: Secret}    %{=robot123}    # Environment variable defaults work as well.
   ${JOIN: Secret}       ${XXX}-123      # Joining secrets with literals is ok.
   ${LITERAL: Secret}    robot123        # This fails.

Also list and dictionary variables support secret values:

.. sourcecode:: robotframework

   *** Variables ***
   @{LIST: Secret}     ${XXX}    %{EXAMPLE}    %{=robot123}    ${XXX}-123
   &{DICT: Secret}     normal=${XXX}    env=%{EXAMPLE}    env_default=%{=robot123}    join=${XXX}-123

.. note:: The above examples utilize the Variables section, but the syntax to create
          secret variables is exactly the same when using the VAR syntax.

Creating secrets on command line
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Command line variables support secret values directly::

    --variable "PASSWORD: Secret:robot123"

Having the secret value directly visible on the command line history or in continuous
integration system logs can be a security risk. One way to mitigate that is using
environment variables::

    --variable "PASSWORD: Secret:$PASSWORD"

Many systems running tests or tasks also support hiding secret values used on
the command line.

Creating secrets programmatically
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Secrets can be created programmatically by using the new `robot.api.types.Secret`_
class. This is most commonly done by libraries and variable files, but also
pre-run modifiers and listeners can utilize secrets if needed.

The simplest possible example of the programmatic usage is a variable file:

.. sourcecode:: python

    from robot.api.types import Secret


    USERNAME = "robot"
    PASSWORD = Secret("robot123")

Creating a keyword returning a secret is not much more complicated either:

.. sourcecode:: python

   from robot.api.types import Secret


   def get_token():
       return Secret("e5805f56-92e1-11f0-a798-8782a78eb4b5")

.. note:: Both examples above have the actual secret value visible in the code.
          When working with real secret values, it is typically better to read
          secrets from environment variables, get them from external systems or
          generate them randomly.

Keywords accepting only `Secret` values
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Keywords can restrict their argument types so that only Secret_ objects are
accepted and trying to use, for example, literal strings fails:

.. sourcecode:: python

   from example import SUT
   from robot.api.types import Secret


   def login_to_sut(user: str, token: Secret):
       SUT.login(user, token.value)

The above keyword could be used, for example, as follows:

.. sourcecode:: robotframework

    *** Variables ***
    ${USER}             robot
    ${TOKEN: Secret}    %{ROBOT_TOKEN}

    *** Test Cases ***
    Example
        Login to SUT    ${USER}    ${TOKEN}

Keywords can also accept `Secret` objects in addition to strings by using
the union syntax like `str | Secret`:

.. sourcecode:: python

   from example import SUT
   from robot.api import logger
   from robot.api.types import Secret


   def input_password(password: str | Secret):
        logger.debug(f"Typing password: {password}")
        if isinstance(password, Secret):
            password = password.value
        SUT.input_password(password)

In this kind of cases it is important to not log or otherwise disclose actual
secret values. The string representation of `Secret` objects is always
`<secret>` and thus logging `f"Typing password: {password}"` in the above
example is safe, but logging it at the end of the example would not be.
The `repr()` of `Secret` objects is `Secret(value=<secret>)` so the real
value is not shown in that string representation either.

.. warning:: Actual secret values that keywords pass forward may be logged or
             otherwise disclosed by external modules or tools using them.

Typed standard library keywords
-------------------------------

Standard library keywords have gotten type hints (`#5373`_). Types are shown
in Libdoc outputs and they document what kind of arguments are accepted. They
can also be useful for external tools like IDE plugins that can validate that
used values match the accepted types.

Enhancements to working with bytes
----------------------------------

There were several enhancements to working with bytes:

- Many keywords in BuiltIn, String and Collections either got support for bytes
  or their existing bytes support was enhanced (`#5548`_).

- If an argument has `bytes` or `bytestring` as its typing, it can be used
  with an integer or with a list of integers (`#5557`_).

- If bytes are used with an argument having `str` as its typing, the value is
  converted to a string by mapping each byte to a matching Unicode code point
  (`#5567`_). This means that, for example, bytes `b"example"` is converted to
  a string `"example"`. Earlier the value was converted with just `str(value)`
  that produced unusable results like a string `"b'example'"`.

Argument conversion enhancements
--------------------------------

There have been various smallish enhancements to automatic argument conversion:

- `object` got an explicit no-op argument converter (`#5529`_).

- Conversion to `bytes` and `bytearray` supports integers and lists of
  integers as input values (`#5557`_).

- `bytes` and `bytearray` are converted to `str` using the same logic as when
  converting `str` to `bytes` and `bytearray`. Earlier they were converted
  using `str(value)` that produced unusable strings like `"b'example'"` (`#5567`_).

- `None` converter accepts an empty string as an input value (`#5545`_).

- Any sequence literal is accepted when converting string arguments to `list`,
  `tuple` and `set` (`#5532`_).

- `Sequence` and `Mapping` converters do not convert all arguments to `list` and
  `dict`, but instead preserve the original type when feasible (`#5531`_).

- Using `Callable` with empty argument list like `Callable[[], None]` has been
  fixed (`#5562`_).

Possibility to detect names of keywords executed by other keywords
------------------------------------------------------------------

Various keywords in the BuiltIn library and also in some external libraries
execute other keywords either directly or allow registering them to be executed
on a certain event. So far external tools have not been able to reliably differentiate
arguments containing names and arguments of executed keywords from other arguments.
This has made it hard, for example, for editors to provide automatic completion
for keyword names.

Nowadays names of executed keywords can be typed with `KeywordName` and
their arguments with `KeywordArgument`. Both of these new types are defined in
the new `robot.api.types`__ module that also exposes the `Secret` type discussed
earlier. All BuiltIn keywords executing other keywords, such as `Run Keyword`
and `Wait Until Keyword Succeeds`, use these new type hints making it easy
to detect them (`#4857`_).

__ https://robot-framework.readthedocs.io/en/master/autodoc/robot.api.html#module-robot.api.types

Backwards incompatible changes
==============================

We try to avoid backwards incompatible changes especially with non-major releases,
but big changes like in this release may affect someone's
`workflow <https://xkcd.com/1172/>`__. Changes that are known to possibly
cause backwards compatibility issues are listed below:

- Automatic argument conversion done based on typing added to standard library
  keywords (`#5373`_) may cause subtle changes to how arguments are handled.

- How bytes are converted to string if an argument has `str` as its typing has
  changed (`#5567`_). The old format was considered unusable.

- `robot.api.TypeInfo.from_type_hint` does not anymore consider a sequence of types
  a union by default (`#5562`_). That behavior can be enabled by using
  `sequence_is_union=True` argument or by calling the separate
  `robot.api.TypeInfo.from_sequence` method instead.

- Argument conversion nowadays recognizes the `object` type and in such cases all
  values are accepted without conversion (`#5529`_). This change is mostly backwards
  compatible, but in a special case where such an argument has a default value
  like `arg: object = 1` there is no conversion based on the default value anymore.
  Possible problems can be avoided by explicitly specifying the default value type
  like `arg: int | object = 1`.

- Nowadays it is possible to remove globally specified keywords tags by using
  the `-tag` syntax also in keyword documentation, not only when using the `[Tags]`
  setting (`#5503`_). This means that it is not anymore possible to use a literal
  tag like `-example` in keyword documentation. If such a tag is needed, the escaped
  format like `\-example` can be used.

Deprecated features
===================

Creating scalar variable without value in non-local scope using `VAR` syntax
----------------------------------------------------------------------------

The VAR syntax can be used to create a scalar variable with an empty string
as its value simply by omitting the value altogether. This works regardless
the scope, but using this approach when a variable is created in a non-local
scope is nowadays deprecated (`#5439`_). The fix is specifying the value
explicitly:

.. sourcecode:: robotframework

    *** Test Cases ***
    Local scope example
        [Documentation]    This usage is not affected.
        VAR    ${local}

    Deprecated
        [Documentation]    These are nowadays deprecated.
        VAR    ${X}    scope=TEST
        VAR    ${Y}    scope=SUITE
        VAR    ${Z}    scope=GLOBAL

    Explicit empty values
        [Documentation]    All these work without deprecation.
        VAR    ${local}    ${EMPTY}
        VAR    ${X}        ${EMPTY}    scope=SUITE
        VAR    ${Y}        ${EMPTY}    scope=SUITE
        VAR    ${Z}        ${EMPTY}    scope=GLOBAL

The motivation for this deprecation is making it possible to use the same syntax
for promoting existing variables to other scopes (`#5369`__) in the future:

.. sourcecode:: robotframework

    *** Test Cases ***
    Promote existing variable
        [Documentation]    This is planned for RF 8.0.
        ${DATA} =    Get Data
        VAR    ${DATA}    scope=SUITE

__ https://github.com/robotframework/robotframework/issues/5369

More visible deprecation for `Run` and similar keywords in OperatingSystem
--------------------------------------------------------------------------

`Run`, `Run And Return RC` and `Run And Return RC And Output` in the OperatingSystem
have been considered deprecated since the Process library was introduced in
Robot Framework 2.8 in 2013. These keywords, especially `Run`, are still so widely
used that we cannot remove them in the near future and even emitting visible deprecation
warnings would likely be too distracting. Their deprecation status has nevertheless
been made more visible (`#5535`_).

Deprecations with standard libraries
------------------------------------

These deprecations have been done with standard library keywords:

- BuiltIn and Collections: Using `NO VALUES` to disable the `values` argument with
  various validation keywords (`#5550`_). `values=False` should be used instead.

- String and Collections: Possibility to use an empty string with some keywords so
  that it is interpreted the same way as if the argument was not used at all (`#5537`_).

- BuiltIn: Non-standard ways to get object length with `Get Length`, `Length Should Be`,
  `Should Be Empty` and `Should Not Be Empty` (`#5568`_).

Acknowledgements
================

Robot Framework is developed with support from the Robot Framework Foundation
and its 80+ member organizations. Join the journey — support the project by
`joining the Foundation <Robot Framework Foundation_>`_.

Robot Framework 7.4 team funded by the foundation consisted of `Pekka Klärck`_ and
`Janne Härkönen <https://github.com/yanne>`_. Janne worked only part-time and was
mainly responsible for Libdoc related fixes. In addition to work done by them, the
community has provided some great contributions:

- `Tatu Aalto <https://github.com/aaltat>`__ worked with Pekka to implement
  the secret variable support (`#4537`_), the biggest new feature in this release.
  Huge thanks to Tatu and to his employer `OP <https://www.op.fi/>`__, a member
  of the `Robot Framework Foundation`_, for dedicating work time to make this
  happen!

- `Oliver Boehmer <https://github.com/oboehmer>`_ added secret variable support
  to OperatingSystem and Process library keywords (`#5512`_).

- `Sahil Thakor <https://github.com/kiteretsu-daihyakka>`__ added support to
  collapse execution errors and warnings in the log file (`#4888`_).

- `@silentw0lf <https://github.com/silentw0lf>`_ added type hints to the DateTime
  and String libraries (`#5373`_).

- `Robin <https://github.com/robinmackaij>`_ added type hints to the Collections
  and XML libraries (`#5373`_).

- `Menium <https://github.com/menium878>`__ added Polish and Arabic support to
  the `Generate Random String` keyword (`#5093`_).

- `Son, Mai H. (Mason) <https://github.com/maisonsmd>`__ reported and fixed a bug in
  using the `robot.run` API multiple times if tests use async keywords (`#5500`_).

- `@adombeck <https://github.com/adombeck>`_ made it possible for libraries to
  log errors and warnings only to the log file, not to the console (`#5460`_).

Big thanks to Robot Framework Foundation, to community members listed above, and
to everyone else who has tested preview releases, submitted bug reports, proposed
enhancements, debugged problems, or otherwise helped with Robot Framework 7.4
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
    * - `#4537`_
      - feature
      - critical
      - Support creating "secret" variables that hide their values in data and log files
      - beta 1
    * - `#4857`_
      - feature
      - high
      - Enhance detecting keyword names used in arguments of other keywords (e.g. `Wait Until Keyword Succeeds`)
      - rc 2
    * - `#5373`_
      - feature
      - high
      - Add type hints to standard libraries
      - rc 1
    * - `#5439`_
      - feature
      - high
      - Deprecate using VAR without value to create empty scalar variable in non-local scope
      - beta 1
    * - `#5512`_
      - feature
      - high
      - `Secret` support to OperatingSystem and Process library keywords
      - beta 2
    * - `#5548`_
      - feature
      - high
      - Enhanced and explicit `bytes` support in BuiltIn, String and Collections
      - rc 1
    * - `#5472`_
      - bug
      - medium
      - Libdoc: Code examples in keyword documentation are not formatted correctly
      - beta 1
    * - `#5474`_
      - bug
      - medium
      - Keyword teardown fails if timeout has occurred when executing keyword
      - rc 1
    * - `#5491`_
      - bug
      - medium
      - Libdoc: Importing section header is shown in HTML outputs even if library accepts no parameters
      - beta 1
    * - `#5498`_
      - bug
      - medium
      - `robot.utils.restreader` module breaks API doc generation
      - beta 1
    * - `#5500`_
      - bug
      - medium
      - Robot API `run` fails after the first run with async keywords
      - beta 1
    * - `#5502`_
      - bug
      - medium
      - Disabling writing to output file programmatically using internal `LOGGER` does not work anymore
      - beta 1
    * - `#5503`_
      - bug
      - medium
      - Using `-tag` syntax to remove keyword tags does not work with tags in documentation
      - beta 1
    * - `#5504`_
      - bug
      - medium
      - Log: Items in element headers are slightly misaligned
      - beta 1
    * - `#5508`_
      - bug
      - medium
      - Links to keywords in Libdoc code blocks only work after filtering but then the indentation is broken
      - beta 1
    * - `#5522`_
      - bug
      - medium
      - Generator metadata missing from to Libdoc HTML outputs
      - beta 2
    * - `#5523`_
      - bug
      - medium
      - Libdoc: Type information is not formatted properly
      - beta 2
    * - `#5531`_
      - bug
      - medium
      - Argument conversion problems with `Sequence` and `Mapping`
      - beta 2
    * - `#5562`_
      - bug
      - medium
      - Type hints with `Callable` with empty argument list causes "Union cannot be empty" error
      - rc 1
    * - `#3874`_
      - feature
      - medium
      - Support `--no-status-rc` with `--help` and `--version`
      - beta 1
    * - `#4888`_
      - feature
      - medium
      - Support collapsing execution errors in log file
      - beta 1
    * - `#5025`_
      - feature
      - medium
      - BuiltIn: Explicitly mark arguments that are positional-only
      - beta 1
    * - `#5093`_
      - feature
      - medium
      - Add Arabic and Polish support to `Generate Random String` keyword
      - beta 1
    * - `#5186`_
      - feature
      - medium
      - Support expanding environment variables in argument files
      - beta 1
    * - `#5460`_
      - feature
      - medium
      - Support logging errors and warnings only to log file, not to console
      - beta 2
    * - `#5492`_
      - feature
      - medium
      - Emit warning if library is re-imported with different arguments
      - beta 1
    * - `#5529`_
      - feature
      - medium
      - Add explicit no-op argument converter for `object`
      - beta 2
    * - `#5535`_
      - feature
      - medium
      - Make it more explicit that `Run` and other similar keywords in OperatingSystem are deprecated
      - beta 2
    * - `#5536`_
      - feature
      - medium
      - Collections: Change keywords that mutate lists and dictionaries to also return them
      - rc 1
    * - `#5537`_
      - feature
      - medium
      - Deprecate possibility to use empty string so that it is interpreted as default value with some standard library keywords
      - rc 1
    * - `#5545`_
      - feature
      - medium
      - Support converting empty string to `None`
      - rc 1
    * - `#5550`_
      - feature
      - medium
      - Deprecate using `NO VALUES` to disable `values` argument with some BuiltIn and Collections keywords
      - rc 1
    * - `#5553`_
      - feature
      - medium
      - BuiltIn: Make normalization in validation keywords recursive
      - rc 1
    * - `#5557`_
      - feature
      - medium
      - Enhance argument conversion to `bytes` so that integers and lists of integers are accepted as values
      - rc 1
    * - `#5567`_
      - feature
      - medium
      - Convert bytes to `str` sanely in argument conversion
      - rc 1
    * - `#5490`_
      - bug
      - low
      - Libdoc: Tags from private keywords are not excluded from HTML outputs
      - beta 1
    * - `#5505`_
      - bug
      - low
      - Report: "Test Details" header background is wrong when viewing details
      - beta 1
    * - `#5543`_
      - bug
      - low
      - Libdoc: keyword tags should have a space between them
      - rc 1
    * - `#5563`_
      - bug
      - low
      - Argument types are not escaped in Libdoc HTML output
      - rc 1
    * - `#5573`_
      - bug
      - low
      - User Guide explains normalizing full keyword names wrong
      - rc 2
    * - `#3918`_
      - feature
      - low
      - Document that listeners can be used instead of pre-run modifiers to avoid filtering by `--include/--exclude`
      - beta 2
    * - `#5122`_
      - feature
      - low
      - Enhance documentation related to importing same library multiple times
      - beta 1
    * - `#5506`_
      - feature
      - low
      - Drop "Test/Task" prefixes from report and log headers
      - beta 1
    * - `#5515`_
      - feature
      - low
      - Document that `--include/--exclude` and other such options do not affect tests added by listeners
      - beta 2
    * - `#5532`_
      - feature
      - low
      - Allow any sequence literal when converting string arguments to lists, tuples and sets
      - beta 2
    * - `#5534`_
      - feature
      - low
      - Allow disabling `Wait Until Removed/Created` timeout using `None`
      - beta 2
    * - `#5546`_
      - feature
      - low
      - Add `timedelta` support to `Repeat Keyword`
      - rc 1
    * - `#5565`_
      - feature
      - low
      - Libdoc: Don't show return type documentation with standard types
      - rc 1
    * - `#5568`_
      - feature
      - low
      - BuiltIn: Deprecate non-standard ways to get object length with `Get Length` and related keywords
      - rc 1

Altogether 49 issues. View on the `issue tracker <https://github.com/robotframework/robotframework/issues?q=milestone%3Av7.4>`__.

.. _#4537: https://github.com/robotframework/robotframework/issues/4537
.. _#4857: https://github.com/robotframework/robotframework/issues/4857
.. _#5373: https://github.com/robotframework/robotframework/issues/5373
.. _#5439: https://github.com/robotframework/robotframework/issues/5439
.. _#5512: https://github.com/robotframework/robotframework/issues/5512
.. _#5548: https://github.com/robotframework/robotframework/issues/5548
.. _#5472: https://github.com/robotframework/robotframework/issues/5472
.. _#5474: https://github.com/robotframework/robotframework/issues/5474
.. _#5491: https://github.com/robotframework/robotframework/issues/5491
.. _#5498: https://github.com/robotframework/robotframework/issues/5498
.. _#5500: https://github.com/robotframework/robotframework/issues/5500
.. _#5502: https://github.com/robotframework/robotframework/issues/5502
.. _#5503: https://github.com/robotframework/robotframework/issues/5503
.. _#5504: https://github.com/robotframework/robotframework/issues/5504
.. _#5508: https://github.com/robotframework/robotframework/issues/5508
.. _#5522: https://github.com/robotframework/robotframework/issues/5522
.. _#5523: https://github.com/robotframework/robotframework/issues/5523
.. _#5531: https://github.com/robotframework/robotframework/issues/5531
.. _#5562: https://github.com/robotframework/robotframework/issues/5562
.. _#3874: https://github.com/robotframework/robotframework/issues/3874
.. _#4888: https://github.com/robotframework/robotframework/issues/4888
.. _#5025: https://github.com/robotframework/robotframework/issues/5025
.. _#5093: https://github.com/robotframework/robotframework/issues/5093
.. _#5186: https://github.com/robotframework/robotframework/issues/5186
.. _#5460: https://github.com/robotframework/robotframework/issues/5460
.. _#5492: https://github.com/robotframework/robotframework/issues/5492
.. _#5529: https://github.com/robotframework/robotframework/issues/5529
.. _#5535: https://github.com/robotframework/robotframework/issues/5535
.. _#5536: https://github.com/robotframework/robotframework/issues/5536
.. _#5537: https://github.com/robotframework/robotframework/issues/5537
.. _#5545: https://github.com/robotframework/robotframework/issues/5545
.. _#5550: https://github.com/robotframework/robotframework/issues/5550
.. _#5553: https://github.com/robotframework/robotframework/issues/5553
.. _#5557: https://github.com/robotframework/robotframework/issues/5557
.. _#5567: https://github.com/robotframework/robotframework/issues/5567
.. _#5490: https://github.com/robotframework/robotframework/issues/5490
.. _#5505: https://github.com/robotframework/robotframework/issues/5505
.. _#5543: https://github.com/robotframework/robotframework/issues/5543
.. _#5563: https://github.com/robotframework/robotframework/issues/5563
.. _#5573: https://github.com/robotframework/robotframework/issues/5573
.. _#3918: https://github.com/robotframework/robotframework/issues/3918
.. _#5122: https://github.com/robotframework/robotframework/issues/5122
.. _#5506: https://github.com/robotframework/robotframework/issues/5506
.. _#5515: https://github.com/robotframework/robotframework/issues/5515
.. _#5532: https://github.com/robotframework/robotframework/issues/5532
.. _#5534: https://github.com/robotframework/robotframework/issues/5534
.. _#5546: https://github.com/robotframework/robotframework/issues/5546
.. _#5565: https://github.com/robotframework/robotframework/issues/5565
.. _#5568: https://github.com/robotframework/robotframework/issues/5568
