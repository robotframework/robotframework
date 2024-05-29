==========================
Robot Framework 4.0 beta 2
==========================

.. default-role:: code

`Robot Framework`_ 4.0  is a new major release with lot of big new features
such as the SKIP status and native IF/ELSE support as well as enhancements
to, for example, type conversion and Libdoc. Robot Framework beta 2 contains
most of the planned new features and internal changes. The remaining
issues targeted for Robot Framework 4.0 can be found from the `issue tracker
milestone`_. After some delays the plan is to get the final release out in
February 2021.

Questions and comments related to the release can be sent to the
`robotframework-users`_ mailing list or to `Robot Framework Slack`_,
and possible bugs submitted to the `issue tracker`_.
If you have pip_ installed, just run

::

   pip install --pre --upgrade robotframework

to install the latest available release or use

::

   pip install robotframework==4.0b2

to install exactly this version. Alternatively you can download the source
distribution from PyPI_ and install it manually. For more details and other
installation approaches, see the `installation instructions`_.

Robot Framework 4.0 beta 2 was released on Wednesday February 3, 2021.

.. _Robot Framework: http://robotframework.org
.. _Robot Framework Foundation: http://robotframework.org/foundation
.. _pip: http://pip-installer.org
.. _PyPI: https://pypi.python.org/pypi/robotframework
.. _issue tracker milestone: https://github.com/robotframework/robotframework/issues?q=milestone%3Av4.0
.. _issue tracker: https://github.com/robotframework/robotframework/issues
.. _robotframework-users: http://groups.google.com/group/robotframework-users
.. _Robot Framework Slack: https://robotframework-slack-invite.herokuapp.com
.. _installation instructions: ../../INSTALL.rst

.. contents::
   :depth: 2
   :local:


Most important enhancements
===========================

New SKIP status
---------------

Robot Framework tests (and tasks) finally have SKIP status in addition to
PASS and FAIL (`#3622`_). There are many different ways for tests get skipped:

1. Tests can use new `Skip` and `Skip If` BuiltIn keywords. The former skips the test
   unconditionally and the latter accepts an expression that is evaluated using the
   same logic as with `Run Keyword If` and skips the test if the condition is true.
   Both also support an optional message telling why the test was skipped.

2. Libraries can raise an exception that tells that the test should be skipped. The
   easiest way is using the new `robot.api.SkipExecution` exception (also other special
   exceptions have been exposed similarly, see `#3685`_), but it is also possible to
   create a custom exception that has a special `ROBOT_SKIP_EXECUTION` attribute set
   to a true value.

3. If a suite setup is skipped using a keyword or an exception, all tests in that
   suite will be marked skipped without executing them. If a suite teardown is skipped,
   all tests in the suite are marked skipped retroactively.

4. New command line option `--skip` can be used to skip tests based on tags without
   running them. The difference compared to the old `--exclude` option is that skipped
   tests are shown in logs/reports as skipped while excluded tests are omitted
   altogether.

5. New command line option `--skiponfailure` can be used to mark tests that fail
   skipped. The idea is to allow having tests that are not ready, or that test
   a feature that is not ready, included in test runs without them failing the whole
   execution. This is in many ways similar to the old criticality concept that,
   as discussed in the next section, has been removed.

The SKIP status also affects the statuses of the executed suites. Their statuses are
set based on test statuses using these rules:

- If there are failed tests, suite status is FAIL.
- If there are no failures but there are passed tests, suite status is PASS.
- If there are only skipped tests, or no tests at all, suite status is SKIP.

The return code to the system is the number of failed tests, skipped tests do not
affect it.

Criticality has been removed
----------------------------

Robot Framework has had a concept of criticality that made it possible to run tests so
that their failures did not affect the overall test execution verdict. The motivation
for this feature was acceptance test driven development (ATDD) where you create tests
before implementing features and those tests obviously cannot initially pass. In
addition to that, this functionality has been used for emulating skipping tests by
dynamically marking them non-critical before failing. The system worked by using
`--critical` and `--noncritical` options matching tests by tags.

Although this functionality worked ok in its designed usage, it also had several
problems discussed in more detail below. Due to these problems the decision was made
to remove the criticality concept in Robot Framework 4.0. (`#3624`_)

Problems with criticality
~~~~~~~~~~~~~~~~~~~~~~~~~

1. Robot Framework 4.0 introduces real skip status (`#3622`_) which is conceptually very
   close to the criticality functionality. There are some differences, but these
   features are so close that having both does not add much benefits but instead causes
   confusion and adds unnecessary complexity.

2. Criticality makes the final outcome of a test two dimensional so that one axis is
   the actual status and the other is criticality. Even with only pass and fail statuses
   we end up with four different end results "critical pass", "critical fail",
   "non-critical pass" and "non-critical fail", and adding the skip status to the mix
   would add "critical skip" and "non-critical skip". Most of these final statuses make
   no sense and everything is a lot easier if there's only "pass", "fail" and "skip".

3. When looking at suite statistics in reports and logs, you can only see the total
   number of passed and failed tests without any indication are failures critical or not.
   We have experimented showing statistics separately both for critical and non-critical
   tests but that did not work well at all. This is similar problem as the one above
   and having just pass, fail and skip statuses resolves this one as well.

4. Related to the above, having statistics both for "Critical Tests" and "All Tests"
   in reports and logs is rather strange especially for new users. Just having single
   statistics with pass, fail and skip statuses is a lot simpler and intuitive.

5. Criticality is a unique feature in Robot Framework. Unique tool features can be
   really useful, but they also require learning by new (and old) users and they do not
   always play nicely together with other tools. In this particular case skip is
   a familiar feature for most people working with automation and it is also
   a functionality that external tools like test management systems generally support.

Migrating from criticality to skipping
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Part of the new skip functionality (`#3622`_) is adding `--skiponfailure` command line
option that automatically changes status of failed tests to skip if they have a matching
tag. This works very much like the old `--noncritical` option that marks tests
non-critical and thus their failures are in practice ignored. To make migration to
skipping easier, `--noncritical` and also `--critical` will be preserved as deprecated
aliases to `--skiponfailure` when starting execution. They will also be preserved with
Rebot, but with it they will have no effect.

Although `--noncritical` and `--critical` will continued to work mostly like earlier,
there are various other changes affecting the current criticality users. Especially
visible are changes in reports and logs where critical/non-critical distinction will
be gone. Other changes include removing the `critical` attribute from `test` elements
in output.xml and changes to the result related APIs.

Migrating to skipping very importantly requires changes to integration with external
tools. This will certainly add some work to projects providing such integration
(e.g. Robot Framework Jenkins Plugin), but in the end using commonly used skip status
and not the unique criticality is likely to make things easier.

Native IF/ELSE syntax
---------------------

Robot Framework finally has support for real IF/ELSE syntax (`#3074`_) avoiding
the need to use the `Run Keyword If` keyword for conditional execution.

Basic `IF` syntax
~~~~~~~~~~~~~~~~~

The new native IF syntax starts with `IF` (case-sensitive) and ends
with `END` (case-sensitive). The `IF` marker requires exactly one value that is
the condition to evaluate. Keywords to execute if the condition is true are on
their own rows between the `IF` and `END` markers. Indenting keywords in the IF
block is highly recommended but not mandatory.

In the following example keywords `Some keyword` and `Another keyword`
are executed if `${rc}` is greater than zero:

.. code:: robotframework

    *** Test Cases ***
    Example
       IF    ${rc} > 0
           Some keyword
           Another keyword
       END

The condition is evaluated in Python so that Python builtins like `len()` are
available and modules are imported automatically to support usages like
`platform.system() == 'Linux'` and `math.ceil(${x}) == 1`. Normal variables,
like `${rc}` in the above example, are replaced before evaluation, but variables
are also available in the evaluation namespace using the special `$rc` syntax.
The latter approach is handy when the string representation of the variable cannot
be used in the condition directly. In practice the condition syntax is the same
as with the `Run Keyword If` keyword.

`ELSE`
~~~~~~

Like most other languages supporting conditional execution, Robot Framework's IF
syntax also supports ELSE branches that are executed if the IF condition is
not true.

In this example `Some keyword` is executed if `${rc}` is greater than
zero and `Another keyword` is executed otherwise:

.. code:: robotframework

    *** Test Cases ***
    Example
        IF    ${rc} > 0
            Some keyword
        ELSE
            Another keyword
        END

`ELSE IF`
~~~~~~~~~

Robot Framework also supports ELSE IF branches that have their own condition
that is evaluated if the initial condition is not true. There can be any number
of ELSE IF branches and they are gone through in the order they are specified.
If one of the ELSE IF conditions is true, the block following it is executed
and remaining ELSE IF branches are ignored. An optional ELSE branch can follow
ELSE IF branches and it is executed if all conditions are false.

In the following example different keyword is executed depending on is `${rc}`
positive, negative, zero, or something else like a string or `None`:

.. code:: robotframework

    *** Test Cases ***
    Example
        IF    $rc > 0
            Positive keyword
        ELSE IF    $rc < 0
            Negative keyword
        ELSE IF    $rc == 0
            Zero keyword
        ELSE
            Fail    Unexpected rc: ${rc}
        END

Notice that this example uses the `${rc}` variable in the special `$rc` format.
This means that the variable value itself, not its string representation, is
used when conditions are evaluated.

Support for nested control structures
-------------------------------------

It is now possible to nest old FOR loops as well new IF/ELSE structures (`#3079`_).
Previously, nesting FOR loops was only possible by using a keyword that has a loop
in a top level loop.

Here is an example with FOR and IF::

    FOR    ${row}    IN    @{rows}
        FOR    ${cell}    IN    @{row}
            IF    "${cell}" != "IGNORE"
                Process Cell    ${cell}
            END
        END
    END

Libdoc enhancements
-------------------

HTML output enhancements
~~~~~~~~~~~~~~~~~~~~~~~~

Libdoc generated HTML documentation has been enhanced so that it contains a navigation
bar with easier access to keywords both directly and via search. Support for mobile
browsers has also been improved. (`#3687`_)

Showing keyword arguments has been improved. Nowadays argument names and
possible types and default values are shown separately and not anymore as
a single string like `arg: int = 42`. (`#3586`_)

Enums_ or a TypedDicts_ used as argument types are automatically listed in the new
Data types section in Libdoc HTML output. The type information keywords have also
contain links to this information where applicable. (`#3783`_)

.. _Enums: https://docs.python.org/3/library/enum.html
.. _TypedDicts: https://docs.python.org/3/library/typing.html#typing.TypedDict

Spec file enhancements
~~~~~~~~~~~~~~~~~~~~~~

Most important enhancement to the machine readable spec files is that Libdoc nowadays
can generate specs in the JSON format in addition to XML. The JSON spec is more
convenient especially when working with JavaScript and other web technologies. (`#3730`_)

Another important change is that specs nowadays store keyword argument information
so that name and possible type and default value are separated. (`#3578`_)

Enums_ and TypedDicts_ shown specially in HTML are also stored separately in the spec
files. This makes it possible, for example, to implement completion for enum members
in IDEs. (`#3607`_)

Argument conversion enhancements
--------------------------------

Automatic argument conversion that was initially added in `Robot Framework 3.1`__
has been enhanced in multiple ways:

- It is possible to specify that an argument has multiple possible types, for
  example, like `arg: Union[int, float]`. (`#3738`_)
- Conversion is done also when the given argument is not a string. (`#3735`_)
- Conversion to string (e.g. `arg: str`) has been added. (`#3736`_)
- Conversion to `None` is done only if an argument has `None` as an explicit
  type or as a default value. (`#3729`_)
- `None` can be used as a type instead of `NoneType` consistently. (`#3739`_)

__ https://github.com/robotframework/robotframework/blob/master/doc/releasenotes/rf-3.1.rst#automatic-argument-conversion

List and dictionary expansion with item access
----------------------------------------------

List and dictionary expansion using `@{list}` and `&{dict}` syntax, respectively,
now works also in combination with item access like `@{var}[item]` (`#3487`_). This
is how that syntax is handled:

- Both `@{var}[item]` and `&{var}[item]` first make a normal variable item lookup,
  exactly like when using `${var}[item]`.
- Nested access like `@{var}[item1][item2]` and using the slice notation with lists
  like `@{var}[1:]` are supported as well.
- When using the `@{var}[item]` syntax, the found item must be a list or list-like.
  It is expanded exactly like `@{var}` is expanded normally.
- When using the `&{var}[item]` syntax, the found item must be a mapping. It is
  expanded exactly like `&{var}` is expanded normally.

In practice the above means that if we have, for example, a variable `${var}` with
value `{'items': ['a', 'b', 'c']}`, we could use it like this::

    FOR    ${item}    IN    @{var}[items]
        Log    ${item}
    END

Prior to this change the item access needed to be done separately::

    @{items} =    Set Variable    ${var}[items]
    FOR    ${item}    IN    @{items}
        Log    ${item}
    END

This change is backward incompatible because with earlier versions `@{var}[item]` and
`&{var}[item]` meant normal item access with lists and dictionaries, respectively.
The new generic `${var}[item]` access was introduced already in Robot Framework 3.1
(`#2601`__) and the old syntax was deprecated in Robot Framework 3.2 (`#2974`__).

__ https://github.com/robotframework/robotframework/issues/2601
__ https://github.com/robotframework/robotframework/issues/2974

Relative order of keywords and messages is preserved in log file
----------------------------------------------------------------

Keywords typically only contain either other keywords (user keywords) or messages
(library keywords), but in some special cases like when using the TRACE log level
keywords can have both. Earlier child keywords were always shown first in the log
file and messages followed them even if some of the messages actually were logged
before running the child keywords. This problem has now been fixed and the relative
order of keywords and messages, as well as IF/ELSE and FOR structures, is
preserved. (`#2086`_)

Keywords after failures are shown in log file as "not run"
----------------------------------------------------------

When a keyword fails, remaining keywords in the current test (or task) are not
executed and execution continues from possible teardown or from the next test.
This is done because typically remaining keywords would also fail making it
harder to see the original problem. Sometimes it would, however, be convenient
to see what keywords would have been executed if there had not been a failure.
That can obviously be seen from the original script, but they are not always
easily or at all available.

Starting from Robot Framework 4.0, keywords after failures are gone through
and shown in log files using "NOT RUN" status. Keywords are not executed
so there is only a minimal overhead compared to the earlier behaviour and
this overhead is only seen when there are failures.

When this functionality was discussed on the `#devel` channel on our `Slack
<https://rf-invite.herokuapp.com>`_, majority of the users liked it and some
found it very useful, but there were also some who opposed the change. If there
are more users who do not like this change, we can still consider making it
configurable. If you have opinions either way, comment the issue `#3842`_ or
join the Slack_ discussion!

Positional-only arguments
-------------------------

`Positional-only arguments`__ introduced in Python 3.8 are now supported (`#3695`_).
They work for most parts already with earlier releases but now, for example, error
reporting is better. Positional-only arguments are currently only supported with
Python based keywords as well as with Java based keywords that have technically
always been positional-only. There are no plans to support them with user keywords,
but adding support to the dynamic API would probably be a good idea.

__ https://www.python.org/dev/peps/pep-0570/

Enhancements to parsing APIs
----------------------------

Robot Framework 3.2 contained a totally rewritten parser and enhanced parsing APIs.
These APIs were mainly designed to be used for inspecting parsed data and modifying
the data was not very convenient. Robot Framework 4.0 further enhances these APIs
and now modifying data is a lot more convenient (`#3791`_) and parsing APIs
have been slightly enhanced also otherwise (`#3776`_).

People interested in the new and old parsing APIs can find them documented here__.
These APIs are already used by the new external `robotidy
<https://github.com/MarketSquare/robotframework-tidy>`_ tool that already now
has a lot more features than the built-in `tidy`.

__ https://robot-framework.readthedocs.io/en/master/autodoc/robot.api.html#module-robot.api.parsing

Enhancements to running and result model objects
------------------------------------------------

Execution and result side models now contain separate objects representing
FOR and IF/ELSE constructs. Earlier these models considered everything,
including FOR loops, to be keywords, but that did not work too well when
new control structures were added. These changes are invisible for majority
of users, but people using the programmatic APIs somehow should study
issue `#3749`_ for more information.


Backwards incompatible changes
==============================

Big changes in Robot Framework 4.0 have not been possible without breaking
backwards incompatibility in some cases.

Old `:FOR` loop syntax is not supported anymore
-----------------------------------------------

Prior to Robot Framework 3.1 the FOR loop syntax looked like this::

   :FOR    ${animal}    IN    cat    dog    cow
   \    Keyword    ${animal}
   \    Another keyword

Robot Framework 3.1 `added the new loop syntax`__ that makes it possible to
write loops like this::

   FOR    ${animal}    IN    cat    dog    cow
       Keyword    ${animal}
       Another keyword
   END

The old loop syntax was `deprecated in Robot Framework 3.2`__ and now in
Robot Framework 4.0 the support for it has been removed altogether. (`#3733`_)

__ https://github.com/robotframework/robotframework/blob/master/doc/releasenotes/rf-3.1.rst#for-loop-enhancements
__ https://github.com/robotframework/robotframework/blob/master/doc/releasenotes/rf-3.2.rst#old-for-loop-syntax

Meaning of `@{var}[item]` and `&{var}[item]` syntax has changed
---------------------------------------------------------------

As discussed earlier, `@{var}[item]` and `&{var}[item]` nowadays mean
`list and dictionary expansion with item access`_, respectively (`#3487`_).
With earlier versions they meant accessing items from lists or dictionaries
without expansion, but that functionality was `deprecated in Robot Framework 3.2`__.

__ https://github.com/robotframework/robotframework/blob/master/doc/releasenotes/rf-3.2.rst#accessing-list-and-dictionary-items-using-varitem-and-varitem

Argument conversion changes
---------------------------

Argument type conversion has been `enhanced in many ways`__ and some of these
changes are backwards incompatible:

- Also non-string arguments are used in automatic argument conversion instead of
  passing them to keywords as-is. Keywords may thus get arguments in different
  type than earlier or the type conversion can fail. (`#3735`_)

- String `NONE` (case-insensitively) is converted to `None` only if the argument has
  `None` as an explicit type or as a default value. This may lead to argument
  conversion failure instead of the keyword getting `None`. (`#3729`_)

__ `Argument conversion enhancements`_

output.xml has been changed
---------------------------

The generated output.xml file has seen various changes:

- Suites, tests and keywords can have SKIP status. (`#3622`_)
- Log messages can have SKIP level. (`#3622`_)
- Tests do not anymore have `criticality` attribute. (`#3624`_)
- Keywords as well as IF and FOR structures can have NOT RUN status if they
  are not executed due to earlier failures (`#3842`_) or if they are in
  an unexecuted IF/ELSE branch (`#3074`_).
- FOR loops are represented as `<for>` elements instead of using `<kw type='for'>`.
- New IF/ELSE structures are represented as `<if>` elements.

The `schema defining the output.xml structure`__ has also not been fully updated yet
but that will be done before the final release. It is also possible that output.xml
will be still changed slightly before that.

Although there are lot of changes, most of them are pretty small and should not
cause too much problems for tools processing output.xml. Especially tools only
interested in suite and test level information are mostly unaffected.

.. note:: Instead of processing output.xml using generic XML parsing tools,
          it may be easier to use Robot Framework's own result APIs that parse
          the data into convenient suite structure that can be inspected and
          modified as needed. For more details about these APIs see their
          documentation here__.

__ https://github.com/robotframework/robotframework/tree/master/doc/schema
__ https://robot-framework.readthedocs.io/en/master/autodoc/robot.result.html

Libdoc spec changes
-------------------

Libdoc XML spec files have been changed:

- Argument name, type and default are stored separately. (`#3578`_)
- Information about named argument support has been removed. (`#3705`_)
- Spec files have new information such as Enum and TypedDict data types. (`#3607`_)
- When generating specs, it is not possible to use the special `XML:HTML` format
  anymore. The new `--specdocformat` option must be used instead. (`#3731`_)

As the result the `XML schema version`__ has been raised to 3.

__ https://github.com/robotframework/robotframework/tree/master/doc/schema

Other backwards incompatible changes
------------------------------------

- Python 3.4 is not anymore supported. (`#3577`_)
- Parsing model has been changed slightly. (`#3776`_)
- Result and running models have been changed (`#3749`_)
- Space after a literal newline is not ignored anymore. (`#3746`_)
- Small changes to importing listeners and model modifiers from the command line. (`#3809`_)


Acknowledgements
================

Robot Framework development is sponsored by the `Robot Framework Foundation`_
and its `40+ member organizations <https://robotframework.org/foundation/#members>`_.
Due to some extra funding we have had a bit bigger team developing Robot Framework 4.0
consisting of
`Pekka Klärck <https://github.com/pekkaklarck>`_,
`Janne Härkönen <https://github.com/yanne>`_,
`Mikko Korpela <https://github.com/mkorpela>`_ and
`René Rohner <https://github.com/Snooz82>`_.
Pekka's work has been sponsored by the foundation, Janne and Mikko who work for
`Reaktor <https://www.reaktor.com/>`__ have been sponsored by
`Robocorp <https://robocorp.com/>`__, and René's work has been
sponsored by his employer `imbus <https://www.imbus.de/en/>`__.

In addition to the work done by the dedicated team, we have got great
contributions by the wider open source community:

- `Simandan Andrei-Cristian <https://github.com/cristii006>`__ implemented
  `Run Keyword And Warn On Failure` keyword. It is especially handy with suite
  teardowns if you do not want failures to fail all tests but do not want to hide
  the failure fully either. (`#2294`_)

- `Maciej Wiczk <https://github.com/MaciejWiczk>`__ added the original name of
  keywords using embedded arguments to output.xml (`#3750`_) and added information
  about all tags to Libdoc XML spec files (`#3770`_).

- `Bartłomiej Hirsz <https://github.com/bhirsz>`_ enhanced parsing APIs by
  adding convenience methods for creating new data.
  (PR `#3808 <https://github.com/robotframework/robotframework/pull/3808>`_)

- `Mihai Pârvu <https://github.com/mihaiparvu>`__ fixed problems using string 'none'
  (case-insensitively) with various keywords, most importantly with XML library
  keywords setting element text. (`#3649`_)

- `Hugo van Kemenade <https://github.com/hugovk>`__ did metadata and documentation
  changes to drop Python 3.4 support. (`#3577`_)

- `Sergio Freire <https://github.com/bitcoder>`__ updated output.xml schema after
  changes to status and criticality. (`#3726`_)

Huge thanks to all sponsors, contributors and to everyone else who has reported
problems, participated in discussions on various forums, or otherwise helped to make
Robot Framework and its community and ecosystem better.

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
    * - `#3074`_
      - enhancement
      - critical
      - Native support for `IF/ELSE` syntax
      - alpha 3
    * - `#3079`_
      - enhancement
      - critical
      - Support for nested control structures
      - alpha 3
    * - `#3622`_
      - enhancement
      - critical
      - New `SKIP` status
      - alpha 1
    * - `#3624`_
      - enhancement
      - critical
      - Remove criticality concept in favor of skip status
      - alpha 1
    * - `#2086`_
      - bug
      - high
      - Relative order of messages and keywords is not preserved in log
      - beta 2
    * - `#3487`_
      - enhancement
      - high
      - Allow using `@{list}[index]` as a list and `&{dict}[key]` as a dict
      - alpha 1
    * - `#3578`_
      - enhancement
      - high
      - Libdoc specs: Argument name, type and default should be stored separately
      - alpha 2
    * - `#3586`_
      - enhancement
      - high
      - Libdoc should format argument names, defaults and types differently
      - alpha 1
    * - `#3607`_
      - enhancement
      - high
      - Libdoc: Store information about enums and TypedDicts used as argument types in spec files
      - beta 1
    * - `#3687`_
      - enhancement
      - high
      - Libdoc html UX responsive improvements.
      - alpha 1
    * - `#3695`_
      - enhancement
      - high
      - Positional only argument support with Python keywords
      - alpha 1
    * - `#3730`_
      - enhancement
      - high
      - Libdoc: Support JSON spec files
      - alpha 2
    * - `#3735`_
      - enhancement
      - high
      - Argument conversion and validation with non-string argument values
      - alpha 2
    * - `#3738`_
      - enhancement
      - high
      - Support type conversion with multiple possible types
      - alpha 2
    * - `#3749`_
      - enhancement
      - high
      - Refactor execution and result side model objects
      - beta 2
    * - `#3783`_
      - enhancement
      - high
      - Libdoc: List enums and TypedDicts used as argument types in HTML automatically
      - beta 1
    * - `#3791`_
      - enhancement
      - high
      - Add public APIs to allow modifying parsing model
      - beta 2
    * - `#3842`_
      - enhancement
      - high
      - Show keywords unexecuted due to earlier failures in log
      - beta 2
    * - `#3547`_
      - bug
      - medium
      - Some non-iterable objects considered iterable
      - alpha 1
    * - `#3648`_
      - bug
      - medium
      - Enhance error reporting when using markers like `FOR` in wrong case like `for`
      - alpha 3
    * - `#3649`_
      - bug
      - medium
      - XML: Setting element text to `none` (case-insensitively) doesn't work
      - alpha 1
    * - `#3681`_
      - bug
      - medium
      - Evaluate: NameError - variable not recognized
      - alpha 1
    * - `#3708`_
      - bug
      - medium
      - Libdoc: Automatic table of contents generation does not work with spec files when using XML:HTML format
      - alpha 1
    * - `#3721`_
      - bug
      - medium
      - Line starting with single space followed by `#` is not considered comment
      - beta 2
    * - `#3729`_
      - bug
      - medium
      - `None` conversion should not be done unless argument has `None` as explicit type or as default value
      - alpha 2
    * - `#3772`_
      - bug
      - medium
      - If library has listener but no keywords, other library listeners' `close` method is called multiple times
      - beta 1
    * - `#3801`_
      - bug
      - medium
      - Upgrade jQuery
      - beta 2
    * - `#2294`_
      - enhancement
      - medium
      - Run Keyword And Warn On Failure keyword
      - alpha 1
    * - `#3577`_
      - enhancement
      - medium
      - Drop Python 3.4 support
      - alpha 1
    * - `#3685`_
      - enhancement
      - medium
      - Expose special exceptions via `robot.api`
      - alpha 1
    * - `#3697`_
      - enhancement
      - medium
      - Libdoc: Escape backslashes, spaces, line breaks etc. in default values to make them Robot compatible
      - alpha 2
    * - `#3726`_
      - enhancement
      - medium
      - Update output.xml schema to reflect v4.0 changes
      - beta 1
    * - `#3733`_
      - enhancement
      - medium
      - Remove support for old `:FOR` loop syntax
      - alpha 3
    * - `#3736`_
      - enhancement
      - medium
      - Support argument conversion to string
      - alpha 2
    * - `#3739`_
      - enhancement
      - medium
      - Support `None` as alias for `NoneType` in type conversion consistently
      - alpha 2
    * - `#3746`_
      - enhancement
      - medium
      - Remove ignoring space after literal newline
      - alpha 2
    * - `#3748`_
      - enhancement
      - medium
      - Libdoc: Support argument types with multiple possible values
      - beta 1
    * - `#3750`_
      - enhancement
      - medium
      - Improve embedded keyword logging in output.xml
      - beta 2
    * - `#3769`_
      - enhancement
      - medium
      - Reserved keywords should be executed in dry-run
      - beta 1
    * - `#3770`_
      - enhancement
      - medium
      - Libdoc: XML spec files should have info about all tags used by keywords
      - beta 2
    * - `#3781`_
      - enhancement
      - medium
      - Support optional start index with `FOR ... IN ENUMERATE` loops
      - beta 1
    * - `#3785`_
      - enhancement
      - medium
      - Libdoc: Add standalone `libdoc` command
      - beta 2
    * - `#3809`_
      - enhancement
      - medium
      - Support named arguments and argument conversion when importing listeners and modifiers
      - beta 2
    * - `#3731`_
      - ---
      - medium
      - Libdoc: Replace special `XML:HTML` format with dedicated `--specdocformat` option to control documentation format in spec files
      - alpha 2
    * - `#3214`_
      - enhancement
      - low
      - Document that the position of the `[Return]` setting does not affect its usage
      - alpha 2
    * - `#3691`_
      - enhancement
      - low
      - Document omitting files starting with `.` or `_` when running a directory better
      - alpha 1
    * - `#3705`_
      - enhancement
      - low
      - Remove information about named argument support from Libdoc metadata
      - alpha 2
    * - `#3724`_
      - enhancement
      - low
      - Libdoc: Drop `typing.` prefix from type hints originating from the `typing` module
      - beta 1
    * - `#3758`_
      - enhancement
      - low
      - Libdoc: Support quiet mode to not print output file to console
      - alpha 3
    * - `#3767`_
      - enhancement
      - low
      - Write elements without text as self closing to XML outputs
      - beta 1
    * - `#3776`_
      - enhancement
      - low
      - Cleanup parsing model
      - beta 1
    * - `#3815`_
      - enhancement
      - low
      - Allow using `libdoc_cli` programmatically without closing Python interpreter
      - beta 2

Altogether 52 issues. View on the `issue tracker <https://github.com/robotframework/robotframework/issues?q=milestone%3Av4.0>`__.

.. _#3074: https://github.com/robotframework/robotframework/issues/3074
.. _#3079: https://github.com/robotframework/robotframework/issues/3079
.. _#3622: https://github.com/robotframework/robotframework/issues/3622
.. _#3624: https://github.com/robotframework/robotframework/issues/3624
.. _#2086: https://github.com/robotframework/robotframework/issues/2086
.. _#3487: https://github.com/robotframework/robotframework/issues/3487
.. _#3538: https://github.com/robotframework/robotframework/issues/3538
.. _#3578: https://github.com/robotframework/robotframework/issues/3578
.. _#3586: https://github.com/robotframework/robotframework/issues/3586
.. _#3607: https://github.com/robotframework/robotframework/issues/3607
.. _#3687: https://github.com/robotframework/robotframework/issues/3687
.. _#3695: https://github.com/robotframework/robotframework/issues/3695
.. _#3730: https://github.com/robotframework/robotframework/issues/3730
.. _#3735: https://github.com/robotframework/robotframework/issues/3735
.. _#3738: https://github.com/robotframework/robotframework/issues/3738
.. _#3749: https://github.com/robotframework/robotframework/issues/3749
.. _#3783: https://github.com/robotframework/robotframework/issues/3783
.. _#3791: https://github.com/robotframework/robotframework/issues/3791
.. _#3842: https://github.com/robotframework/robotframework/issues/3842
.. _#3547: https://github.com/robotframework/robotframework/issues/3547
.. _#3648: https://github.com/robotframework/robotframework/issues/3648
.. _#3649: https://github.com/robotframework/robotframework/issues/3649
.. _#3681: https://github.com/robotframework/robotframework/issues/3681
.. _#3708: https://github.com/robotframework/robotframework/issues/3708
.. _#3721: https://github.com/robotframework/robotframework/issues/3721
.. _#3729: https://github.com/robotframework/robotframework/issues/3729
.. _#3772: https://github.com/robotframework/robotframework/issues/3772
.. _#3801: https://github.com/robotframework/robotframework/issues/3801
.. _#2294: https://github.com/robotframework/robotframework/issues/2294
.. _#3577: https://github.com/robotframework/robotframework/issues/3577
.. _#3685: https://github.com/robotframework/robotframework/issues/3685
.. _#3697: https://github.com/robotframework/robotframework/issues/3697
.. _#3726: https://github.com/robotframework/robotframework/issues/3726
.. _#3733: https://github.com/robotframework/robotframework/issues/3733
.. _#3736: https://github.com/robotframework/robotframework/issues/3736
.. _#3739: https://github.com/robotframework/robotframework/issues/3739
.. _#3746: https://github.com/robotframework/robotframework/issues/3746
.. _#3748: https://github.com/robotframework/robotframework/issues/3748
.. _#3750: https://github.com/robotframework/robotframework/issues/3750
.. _#3769: https://github.com/robotframework/robotframework/issues/3769
.. _#3770: https://github.com/robotframework/robotframework/issues/3770
.. _#3781: https://github.com/robotframework/robotframework/issues/3781
.. _#3785: https://github.com/robotframework/robotframework/issues/3785
.. _#3809: https://github.com/robotframework/robotframework/issues/3809
.. _#3731: https://github.com/robotframework/robotframework/issues/3731
.. _#3214: https://github.com/robotframework/robotframework/issues/3214
.. _#3691: https://github.com/robotframework/robotframework/issues/3691
.. _#3705: https://github.com/robotframework/robotframework/issues/3705
.. _#3724: https://github.com/robotframework/robotframework/issues/3724
.. _#3758: https://github.com/robotframework/robotframework/issues/3758
.. _#3767: https://github.com/robotframework/robotframework/issues/3767
.. _#3776: https://github.com/robotframework/robotframework/issues/3776
.. _#3815: https://github.com/robotframework/robotframework/issues/3815
