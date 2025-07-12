===================
Robot Framework 7.1
===================

.. default-role:: code

`Robot Framework`_ 7.1 is a feature release with enhancements, for example,
to listeners and to the `VAR` syntax that was introduced in `Robot Framework 7.0`_.

Questions and comments related to the release can be sent to the `#devel`
channel on `Robot Framework Slack`_ and possible bugs submitted to
the `issue tracker`_.

If you have pip_ installed, just run

::

   pip install --upgrade robotframework

to install the latest available stable release or use

::

   pip install robotframework==7.1

to install exactly this version. Alternatively you can download the package
from PyPI_ and install it manually. For more details and other installation
approaches, see the `installation instructions`_.

Robot Framework 7.1 was released on Tuesday September 10, 2024.
It has been superseded by `Robot Framework 7.1.1 <rf-7.1.1.rst>`_

.. _Robot Framework: http://robotframework.org
.. _Robot Framework Foundation: http://robotframework.org/foundation
.. _pip: http://pip-installer.org
.. _PyPI: https://pypi.python.org/pypi/robotframework
.. _issue tracker milestone: https://github.com/robotframework/robotframework/issues?q=milestone%3Av7.1
.. _issue tracker: https://github.com/robotframework/robotframework/issues
.. _robotframework-users: http://groups.google.com/group/robotframework-users
.. _Slack: http://slack.robotframework.org
.. _Robot Framework Slack: Slack_
.. _installation instructions: ../../INSTALL.rst
.. _Robot Framework 7.0: rf-7.0.rst

.. contents::
   :depth: 2
   :local:

Most important enhancements
===========================

Listener enhancements
---------------------

The listener interface was enhanced heavily in `Robot Framework 7.0`_
and Robot Framework 7.1 contains some further improvements:

- Listener calling order can be controlled with the `ROBOT_LISTENER_PRIORITY`
  attribute (`#3473`_).

- Listeners can change execution status (`#5090`_). For example, changing a keyword status
  from PASS to FAIL used to affect only that keyword and execution continued normally, but
  nowadays execution is stopped and the current test or task is failed.

- Listener API version 3 got library, resource file and variable file import related
  methods (`#5008`_). It now has all the same methods as listener API version 2.

- Listeners can modify WHILE loop limits (`#5194`_).

`VAR` enhancements
------------------

`Robot Framework 7.0`_ introduced the new `VAR` syntax for creating variables in different
scopes using an uniform syntax. This syntax has been enhanced as follows:

- The value of the created variable is logged similarly as when using `Set Test Variable`,
  `Set Suite Variable` and other similar keywords (`#5077`_).

- A new `SUITES` scope has been introduced to allow setting variables to the current
  suite and to its child suites (`#5060`_). The existing `SUITE` scope only added
  variables to the current suite, not to its children. This enhancement makes
  the `VAR` syntax featurewise compatible with the `Set Suite Variable` keyword
  that supports same functionality with slightly different syntax.

Other enhancements
------------------

- Paths to log and report written to the console after execution are hyperlinks
  making it easier to open them in a browser (`#5189`_). This requires the terminal
  to support hyperlinks, but practically all Linux and OSX terminals support them
  and although the classic `Windows Console`__ does not, the newer
  `Windows Terminal`__ and most third-party terminals on Windows are compatible.

- New API has been introduced for using named arguments programmatically (`#5143`_).
  This API is targeted for pre-run modifiers and listeners that modify tests or tasks
  before or during execution. There was an attempt to add such an API already in
  Robot Framework 7.0 (`#5000`__), but the selected approach caused backwards
  incompatibility problems and it was reverted in Robot Framework 7.0.1 (`#5031`__).
  Hopefully this new API works better.

- Korean translations have been added (`#5187`_) and Dutch translations have been
  updated (`#5148`_).

- If a keyword has a name like `${kind} example` and it is used like `Given good example`,
  the variable `${kind}` will only contain value `good` when it used to contain `Given good`
  (`#4577`_).

- Robot Framework 7.1 is officially compatible with the forthcoming `Python 3.13`__
  release (`#5091`_). No code changes were needed so also older Robot Framework
  versions ought to work fine.

__ https://en.wikipedia.org/wiki/Windows_Console
__ https://en.wikipedia.org/wiki/Windows_Terminal
__ https://github.com/robotframework/robotframework/issues/5000
__ https://github.com/robotframework/robotframework/issues/5031
__ https://docs.python.org/3.13/whatsnew/3.13.html

Most important bug fixes
------------------------

- `List Should Contain Sub List` did not detect a failure if there was only one
  different item and it was an empty string (`#5172`_).

- Variables containing mutable values were resolved incorrectly in some cases
  (`#5181`_). This had an effect that modifications to the created variable were
  not seen properly.

Backwards incompatible changes
==============================

- The `VAR` syntax nowadays logs the value of the created variable (`#5077`_) and this
  can disclose confidential information. If this is a concern, it is possible to disable
  logging all variable assignments with the `--max-assign-length` command line option.

- Dutch translations have been updated (`#5148`_) and some of the old terms do not
  work anymore. If this is a problem, users can create a custom language file that
  contains the old variants. If there are wider problems, we can also look at changing
  the localization system so that old terms would still work but cause a deprecation
  warning.

- As already mentioned above, the behavior when a keyword has a name like `${kind} example`
  and it is used like `Given good example` has changed. Earlier the variable `${kind}`
  contained `Given good`, but nowadays it contain only `good` (`#4577`_). This is a very
  nice enhancement in general, but possible existing code handling the prefix that was
  earlier included may need to be updated.

Acknowledgements
================

Robot Framework development is sponsored by the `Robot Framework Foundation`_
and its over 60 member organizations. If your organization is using Robot Framework
and benefiting from it, consider joining the foundation to support its
development as well.

The community has also provided some great contributions:

- `J. Foederer <https://github.com/JFoederer>`__ enhanced the embedded argument
  syntax so that possible BDD prefixes are not included if the keyword starts
  with an embedded argument (`#4577`_) and also updated Dutch translations (`#5148`_).

- `Hyeonho Kang <https://github.com/rivercory>`__ provided Korean translations (`#5187`_).

- `Adrian Błasiak <https://github.com/Blashaq>`_ made it possible to modify WHILE
  loop limits by listeners (`#5194`_).

- `@ChristopherJHart <https://github.com/ChristopherJHart>`__ added support for
  `week` in time strings like `2 weeks 1 day` (`#5135`_).

- `@wendi616 <https://github.com/wendi616>`__ enhanced the `Import Resource` keyword
  so that it is executed in dry-run (`#3418`_).

- `Peter <https://github.com/LowEQ>`__ added default value support to the
  `Get Selection From User` keyword (`#5038`_).

- `Tatu Aalto <https://github.com/aaltat>`__ added generation time from output.xml
  to the `Result` object (`#5087`_).

- `@droeland <https://github.com/droeland>`__ did the initial work to make
  `Should Contain` work better with bytes (`#5054`_).

Big thanks to Robot Framework Foundation, to community members listed above, and to
everyone else who has tested preview releases, submitted bug reports, proposed
enhancements, debugged problems, or otherwise helped with Robot Framework 7.1
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
    * - `#3473`_
      - enhancement
      - critical
      - Support controlling listener calling order with `ROBOT_LISTENER_PRIORITY` attribute
    * - `#5090`_
      - enhancement
      - critical
      - Allow listeners to change execution status
    * - `#5091`_
      - enhancement
      - critical
      - Python 3.13 compatibility
    * - `#5094`_
      - bug
      - high
      - Positional-only argument containing `=` is considered named argument if keyword accepts `**named`
    * - `#5172`_
      - bug
      - high
      - `List Should Contain Sub List` does not detect failure if only difference is empty string
    * - `#5181`_
      - bug
      - high
      - Variables containing mutable values are resolved incorrectly in some cases
    * - `#4577`_
      - enhancement
      - high
      - Strip prefix from argument value if BDD keyword starts with embedded argument
    * - `#5008`_
      - enhancement
      - high
      - Add library, resource file and variable file import related methods to listener version 3
    * - `#5060`_
      - enhancement
      - high
      - Support setting values for child suites with `VAR` syntax using `scope=SUITES`
    * - `#5077`_
      - enhancement
      - high
      - `VAR` syntax doesn't log the variable value like `Set * Variable` does
    * - `#5143`_
      - enhancement
      - high
      - New API for using named arguments programmatically
    * - `#5187`_
      - enhancement
      - high
      - Korean translation
    * - `#5189`_
      - enhancement
      - high
      - Make result file paths hyperlinks on terminal
    * - `#5010`_
      - bug
      - medium
      - Setting `PYTHONWARNDEFAULTENCODING` causes warnings
    * - `#5151`_
      - bug
      - medium
      - `Evaluate` keyword doesn't take attributes added into `builtins` module into account
    * - `#5159`_
      - bug
      - medium
      - Bad error message when using Rebot with a non-existing JSON output file
    * - `#5177`_
      - bug
      - medium
      - Rounding error leads to bad display of status color bar
    * - `#3418`_
      - enhancement
      - medium
      - `Import Resource` should be executed in dry-run
    * - `#4821`_
      - enhancement
      - medium
      - `Format String`: Allow using template strings containing `=` without escaping
    * - `#5038`_
      - enhancement
      - medium
      - Dialogs: Default option for `Get Selection From User`
    * - `#5054`_
      - enhancement
      - medium
      - Better support for bytes with `Should Contain`
    * - `#5087`_
      - enhancement
      - medium
      - Add generation time from output.xml to `Result` object
    * - `#5135`_
      - enhancement
      - medium
      - Add support for time strings containing `week` values
    * - `#5148`_
      - enhancement
      - medium
      - Updates to Dutch translations
    * - `#5194`_
      - enhancement
      - medium
      - Allow WHILE limit to be modified in listener V3
    * - `#5169`_
      - bug
      - low
      - Spaces are not normalized when matching keywords with embedded arguments
    * - `#5200`_
      - enhancement
      - low
      - Add `--console-width` value from CLI option to built-in variable  `&{OPTIONS}`

Altogether 27 issues. View on the `issue tracker <https://github.com/robotframework/robotframework/issues?q=milestone%3Av7.1>`__.

.. _#3473: https://github.com/robotframework/robotframework/issues/3473
.. _#5090: https://github.com/robotframework/robotframework/issues/5090
.. _#5091: https://github.com/robotframework/robotframework/issues/5091
.. _#5094: https://github.com/robotframework/robotframework/issues/5094
.. _#5172: https://github.com/robotframework/robotframework/issues/5172
.. _#5181: https://github.com/robotframework/robotframework/issues/5181
.. _#4577: https://github.com/robotframework/robotframework/issues/4577
.. _#5008: https://github.com/robotframework/robotframework/issues/5008
.. _#5060: https://github.com/robotframework/robotframework/issues/5060
.. _#5077: https://github.com/robotframework/robotframework/issues/5077
.. _#5143: https://github.com/robotframework/robotframework/issues/5143
.. _#5187: https://github.com/robotframework/robotframework/issues/5187
.. _#5189: https://github.com/robotframework/robotframework/issues/5189
.. _#5010: https://github.com/robotframework/robotframework/issues/5010
.. _#5151: https://github.com/robotframework/robotframework/issues/5151
.. _#5159: https://github.com/robotframework/robotframework/issues/5159
.. _#5177: https://github.com/robotframework/robotframework/issues/5177
.. _#3418: https://github.com/robotframework/robotframework/issues/3418
.. _#4821: https://github.com/robotframework/robotframework/issues/4821
.. _#5038: https://github.com/robotframework/robotframework/issues/5038
.. _#5054: https://github.com/robotframework/robotframework/issues/5054
.. _#5087: https://github.com/robotframework/robotframework/issues/5087
.. _#5135: https://github.com/robotframework/robotframework/issues/5135
.. _#5148: https://github.com/robotframework/robotframework/issues/5148
.. _#5194: https://github.com/robotframework/robotframework/issues/5194
.. _#5169: https://github.com/robotframework/robotframework/issues/5169
.. _#5200: https://github.com/robotframework/robotframework/issues/5200
