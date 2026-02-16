==========================
Robot Framework 7.4 beta 1
==========================

.. default-role:: code

`Robot Framework`_ 7.4 is a new feature release with support for `secret
variables`_ and various other enhancements and bug fixes. This beta release
contains the majority of the planned features and it is especially targeted for
users interested to test the aforementioned secret variables.

All issues targeted for Robot Framework 7.4 can be found
from the `issue tracker milestone`_.

Questions and comments related to the release can be sent to the `#devel`
channel on `Robot Framework Slack`_ and possible bugs submitted to
the `issue tracker`_.

If you have pip_ installed, just run

::

   pip install --pre --upgrade robotframework

to install the latest available release or use

::

   pip install robotframework==7.4b1

to install exactly this version. Alternatively you can download the package
from PyPI_ and install it manually. For more details and other installation
approaches, see the `installation instructions`_.

Robot Framework 7.4 beta 1 was released on Tuesday October 7, 2025.

.. _Robot Framework: http://robotframework.org
.. _Robot Framework Foundation: http://robotframework.org/foundation
.. _pip: http://pip-installer.org
.. _PyPI: https://pypi.python.org/pypi/robotframework
.. _issue tracker milestone: https://github.com/robotframework/robotframework/issues?q=milestone%3Av7.4
.. _issue tracker: https://github.com/robotframework/robotframework/issues
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

.. warning:: Actual secret values that keywords pass forward may be logged or
             otherwise disclosed by external modules or tools using them.

Backwards incompatible changes
==============================

Nowadays it is possible to remove globally specified keywords tags by using
the `-tag` syntax also in keyword documentation, not only when using the `[Tags]`
setting (`#5503`_). This means that it is not anymore possible to use a literal
tag like `-example` in keyword documentation. If such a tag is needed, the escaped
format like `\-example` can be used.

Deprecated features
===================

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

    Deprecated suite scope example
        [Documentation]    This is nowadays deprecated.
        VAR    ${SUITE}    scope=SUITE

    Explicit empty values
        [Documentation]    Both of these usages work and neither is deprecated.
        VAR    ${local}    ${EMPTY}
        VAR    ${SUITE}    ${EMPTY}    scope=SUITE

The motivation for this deprecation is making it possible to use the same syntax
for promoting existing variables to other scopes (`#5369`__) in the future:

.. sourcecode:: robotframework

    *** Test Cases ***
    Promote existing variable
        [Documentation]    This is planned for RF 8.0.
        ${DATA} =    Get Data
        VAR    ${DATA}    scope=SUITE

__ https://github.com/robotframework/robotframework/issues/5369

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

- `Sahil Thakor <https://github.com/kiteretsu-daihyakka>`__ added support to
  collapse execution errors and warnings in the log file (`#4888`_).

- `Menium <https://github.com/menium878>`__ added Polish and Arabic support to
  the `Generate Random String` keyword (`#5093`_).

- `Son, Mai H. (Mason) <https://github.com/maisonsmd>`__ reported and fixed a bug in
  using the `robot.run` API multiple times if tests use use async keywords (`#5500`_).

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
      - enhancement
      - critical
      - Support creating "secret" variables that hide their values in data and log files
      - beta 1
    * - `#5439`_
      - enhancement
      - high
      - Deprecate using VAR without value to create empty scalar variable in non-local scope
      - beta 1
    * - `#5472`_
      - bug
      - medium
      - Libdoc: Code examples in keyword documentation are not formatted correctly
      - beta 1
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
    * - `#3874`_
      - enhancement
      - medium
      - Support `--no-status-rc` with `--help` and `--version`
      - beta 1
    * - `#4888`_
      - enhancement
      - medium
      - Support collapsing execution errors in log file
      - beta 1
    * - `#5025`_
      - enhancement
      - medium
      - BuiltIn: Explicitly mark arguments that are positional-only
      - beta 1
    * - `#5093`_
      - enhancement
      - medium
      - Add Arabic and Polish support to `Generate Random String` keyword
      - beta 1
    * - `#5186`_
      - enhancement
      - medium
      - Support expanding environment variables in argument files
      - beta 1
    * - `#5492`_
      - enhancement
      - medium
      - Emit warning if library is re-imported with different arguments
      - beta 1
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
    * - `#5122`_
      - enhancement
      - low
      - Enhance documentation related to importing same library multiple times
      - beta 1
    * - `#5506`_
      - enhancement
      - low
      - Drop "Test/Task" prefixes from report and log headers
      - beta 1

Altogether 20 issues. View on the `issue tracker <https://github.com/robotframework/robotframework/issues?q=milestone%3Av7.4>`__.

.. _#4537: https://github.com/robotframework/robotframework/issues/4537
.. _#5439: https://github.com/robotframework/robotframework/issues/5439
.. _#5472: https://github.com/robotframework/robotframework/issues/5472
.. _#5491: https://github.com/robotframework/robotframework/issues/5491
.. _#5498: https://github.com/robotframework/robotframework/issues/5498
.. _#5500: https://github.com/robotframework/robotframework/issues/5500
.. _#5502: https://github.com/robotframework/robotframework/issues/5502
.. _#5503: https://github.com/robotframework/robotframework/issues/5503
.. _#5504: https://github.com/robotframework/robotframework/issues/5504
.. _#5508: https://github.com/robotframework/robotframework/issues/5508
.. _#3874: https://github.com/robotframework/robotframework/issues/3874
.. _#4888: https://github.com/robotframework/robotframework/issues/4888
.. _#5025: https://github.com/robotframework/robotframework/issues/5025
.. _#5093: https://github.com/robotframework/robotframework/issues/5093
.. _#5186: https://github.com/robotframework/robotframework/issues/5186
.. _#5492: https://github.com/robotframework/robotframework/issues/5492
.. _#5490: https://github.com/robotframework/robotframework/issues/5490
.. _#5505: https://github.com/robotframework/robotframework/issues/5505
.. _#5122: https://github.com/robotframework/robotframework/issues/5122
.. _#5506: https://github.com/robotframework/robotframework/issues/5506
