==========================
Robot Framework 3.1 beta 1
==========================

.. default-role:: code

`Robot Framework`_ 3.1 is a new major release with Robotic Process Automation
(RPA) support, automatic type conversion for arguments, support for named-only
arguments, fix for intermittent corruption of `output.xml` files when using
timeouts, and several other interesting new features and as various bug
fixes. It also starts the deprecation process to remove the support of using
test data in HTML format and making test data parsing more strict also
otherwise. Robot Framework 3.1 beta 1 is the third preview release and
contains most of the features and fixes the final release is going to have.

All issues targeted for Robot Framework 3.1 can be found
from the `issue tracker milestone`_.

Questions and comments related to the release can be sent to the
`robotframework-users`_ mailing list or to `Robot Framework Slack`_,
and possible bugs submitted to the `issue tracker`_.

If you have pip_ installed, just run

::

   pip install --pre --upgrade robotframework

to install the latest available release or use

::

   pip install robotframework==3.1b1

to install exactly this version. Alternatively you can download the source
distribution from PyPI_ and install it manually. For more details and other
installation approaches, see the `installation instructions`_.

Robot Framework 3.1 beta 1 was released on Friday October 26, 2018.

.. _Robot Framework: http://robotframework.org
.. _pip: http://pip-installer.org
.. _PyPI: https://pypi.python.org/pypi/robotframework
.. _issue tracker milestone: https://github.com/robotframework/robotframework/issues?q=milestone%3Av3.1
.. _issue tracker: https://github.com/robotframework/robotframework/issues
.. _robotframework-users: http://groups.google.com/group/robotframework-users
.. _Robot Framework Slack: https://robotframework-slack-invite.herokuapp.com
.. _installation instructions: ../../INSTALL.rst

.. contents::
   :depth: 2
   :local:

Most important enhancements
===========================

.. _rpa support:

Terminology configuration to support Robotic Process Automation (RPA)
---------------------------------------------------------------------

`Robotic Process Automation (RPA)`__ means automating business processes that
typically have been designed for humans and thus involve a lot of GUIs. As
an automation tool Robot Framework has always supported this kind of usage,
but it has been a bit awkward to create test cases when not actually
automating tests.

Robot Framework 3.1 is taking first steps to really make Robot Framework
a valid RPA tool by allowing creation of *tasks* instead of tests and changing
terminology in reports and logs when tasks are executed (`#2788`_). There are
two ways to activate the RPA mode:

1. Use the new `*** Tasks ***` (or `*** Task ***`) header in test data files
   instead of the normal `*** Test Cases ***` header. This is useful when it
   is important that data contains tasks, not tests. It is an error to run
   multiple files together so that some have tasks and others have tests.

2. Use the new `--rpa` command line option. This is convenient when executing
   data that needs to be compatible with earlier Robot Framework versions
   and when using editors that do not support the new `*** Tasks ***` header.
   Also Rebot supports the `--rpa` option, so it is possible to execute tests
   as earlier and only create reports and logs using the `--rpa` option.

Regardless how the RPA mode is enabled, the generated reports and logs use
term "task", not "test".

As a convenience, a new command line option `--task` has been added as an
alias for the existing `--test` option. It is also possible to use
`Task Setup`, `Task Teardown`, `Task Template` and `Task Timeout` settings
instead of `Test Setup/Teardown/Template/Timeout`, and additionally
`Set Task Variable` keyword can be used instead of `Set Test Variable`.

Development related to the RPA support has been separately sponsored by
`Siili <https://www.siili.com/>`__, `Knowit <https://www.knowit.fi/>`__,
`Vala <https://www.valagroup.com/>`__, `Qentinel <https://qentinel.com/>`__
and `Eficode <https://www.eficode.com/home>`__. For more information about
Robot Framework and RPA see http://robotframework.org/rpa.

__ https://en.wikipedia.org/wiki/Robotic_process_automation

Automatic argument conversion
-----------------------------

By default all arguments that are not specified as variables are given to
Python based keywords as Unicode strings. This includes cases like this:

.. sourcecode:: robotframework

  *** Test Cases ***
  Example
      Example Keyword    42    False

Starting from Robot Framework 3.1, it is possible to specify argument types
when implementing keywords using few different approaches, and Robot Framework
then converts arguments to the specified types automatically.

When using Python 3, it is possible to use `function annotations`__ to
explicitly specify types (`#2890`_):

.. sourcecode:: python

  def example_keyword(count: int, case_insensitive: bool = True):
      if case_insensitive:
          # ...

An alternative way to explicitly specify types is using the `@keyword`
decorator (`#2947`_) that works also with Python 2. It is possible both
to map argument names to types using a dictionary and to use a list mapping
arguments to types based on position:

.. sourcecode:: python

  @keyword(types={'count': int, 'case_insensitive': bool})
  def example_keyword(count, case_insensitive=True):
      if case_insensitive:
          # ...

  @keyword(types=[int, bool])
  def example_keyword(count, case_insensitive=True):
      if case_insensitive:
          # ...

If an argument has no explicit type specified, Robot Framework still tries
to get the type implicitly from an argument default values (`#2932`_):

.. sourcecode:: python

  def example_keyword(count=-1, case_insensitive=True):
      if case_insensitive:
          # ...

__ https://www.python.org/dev/peps/pep-3107/

Named-only arguments support
----------------------------

Python 3 supports so called `keyword-only arguments`__ and Robot Framework
3.1 supports the same approach but uses the term *named-only arguments*.
The new syntax can be used with Python 3 based test libraries (`#2555`_),
user keywords (`#2896`_), and with dynamic libraries (`#2897`_).

With Python 3 libraries this syntax could be used, for example, like this:

.. sourcecode:: python

  def sort_words(*words, case_sensitive=False):
      key = str.lower if case_sensitive else None
      return sorted(words, key=key)

.. sourcecode:: robotframework

 *** Test Cases ***
 Example
     Sort Words    Foo    bar    baZ
     Sort Words    Foo    bar    baZ    case_sensitive=True

User keywords using the new syntax could look like this:

.. sourcecode:: robotframework

 *** Keywords ***
 With Varargs
     [Arguments]    @{varargs}    ${named}
     Log Many    @{varargs}    ${named}

 Without Varargs
     [Arguments]    @{}    ${first}    ${second}=default
     Log Many    ${first}    ${second}

__ https://www.python.org/dev/peps/pep-3102/


Fix intermittent corrupted outputs when using timeouts
------------------------------------------------------

There have now and then been reports about `output.xml` files being corrupted
and preventing log and report generation. These problems are typically
hard to reproduce and they may be due to bugs in Robot Framework itself
or in libraries/tools used with it. Issue `#2839`_ demonstrated
that this can happen when using Robot Framework's own test and keyword
timeouts if keywords log using the programmatic logging interface. This
problem is now fixed, so hopefully there are less reports about corrupted
outputs in the future.

Installation enhancements
-------------------------

There are various enhancements and other changes related to installation:

- The `robot` and `rebot` start-up scripts are nowadays `*.exe` files on
  Windows. They used to be `*.bat` files which caused all kinds of bigger
  and smaller issues. (`#2415`_)

- Robot Framework is now distributed as a `wheel <http://pythonwheels.com>`_
  distribution making installation faster. (`#1734`_)

- Source distribution format has been changed from tar.gz to zip. (`#2830`_)

- Old `pybot`, `jybot`, `ipybot`, `jyrebot` and `ipyrebot` start-up scripts
  have been removed. (`#2818`_)

Accessing nested list and dictionary variable items
---------------------------------------------------

There has been a syntax to access items of variables containing lists
or dictionaries, but this syntax has only supported accessing direct
items, not possible nested items. This limitation has now been lifted
by issue `#2601`_ and it is possible to use syntax like `${var}[key][0]`
to access as deeply nested items as needed. This is useful, for example,
when working with JSON objects typically used with REST interfaces.

Notice that at the same time the general item access syntax has changed
to use style `${var}[0]` and `${var}[key]` regardless is the variable
a list or dictionary. The old syntax `@{var}[0]` and `&{var}[key]` still
works without warnings, but it will be `deprecated in the future`__.

__ https://github.com/robotframework/robotframework/issues/2974

New `*.resource` extension for resource files
---------------------------------------------

Resource files can now have a dedicated `*.resource` extension, for example
`login.resource`, to differentiate them from `*.robot` files containing
test cases (`#2891`_). The `*.robot` extension continues to work with
resource files as well and there are no plans to deprecate it.

Better error reporting when test data is invalid
------------------------------------------------

There is now an explicit error in these cases where errors have earlier been
silently ignored:

- If parsing a file fails when executing a directory (`#2857`_)
- If test data contains unrecognized section header (`#2860`_)

Better compatibility with third party tools consuming xUnit outputs
-------------------------------------------------------------------

Robot Framework's xUnit compatible output files created with the `--xunit`
command line option were not compatible with tooling that was more strict
about the xUnit file format. This is mainly due to the format not being
officially standardized, but nowadays Robot's xUnit outputs use a format that
ought to be compatible with all or at least most tools. See `#2978`_
for more information.

No need to install external ElementTree module with IronPython 2.7.9+
---------------------------------------------------------------------

IronPython 2.7.9 finally contains a `working ElementTree implementation`__.
Robot Framework 3.1 uses the standard ElementTree with IronPython 2.7.9+
(`#2954`_) and there is no need to install an external ElementTree module
anymore.

__ https://github.com/IronLanguages/ironpython2/issues/370

Backwards incompatible changes
==============================

Python 2.6 and 3.3 are not supported anymore
--------------------------------------------

Neither Python 2.6 nor Python 3.3 are supported anymore. Both Python versions
have reached their end-of-life, the former already in 2013. (`#2276`_)

Old start-up scripts like `pybot` are removed
---------------------------------------------

Old start-up scripts `pybot`, `jybot`, `ipybot`, `jyrebot` and `ipyrebot`
have been removed in favor of the generic `robot` and `rebot` scripts
introduced in Robot Framework 3.0. (`#2818`_)

Changes to pattern matching syntax
----------------------------------

Robot Framework supports pattern matching using `glob-like patterns`__
in various places. This includes command line options like `--test` and
`--include` and keywords like `Should (Not) Match`, `Run Keyword And Expect
Error`, and various `Match` keywords in the XML library.

Starting from Robot Framework 3.1, these patterns support using `[chars]`
as a pattern matching any character inside the brackets (`#2471`_). This is
a useful enhancement, but also means that square brackets are considered
special and existing patterns using them as literal characters are affected.

A simple fix to possible problems is replacing brackets with a question
mark (`?`) which matches any single character. `Run Keyword And Expect Error`
also got a new feature making it possible to use, for example, exact match
in addition to glob pattern matching (`#2967`_).

Pattern matching also had a bug that a trailing newline in the matched
strings was ignored (`#2894`_). For example, `foobar\n` was earlier
considered to match both `*bar` and `foobar`. After this bug being fixed
pattern matching is more strict and trailing newlines need to be added to
matched strings if they are missing.

__ https://en.wikipedia.org/wiki/Glob_(programming)


Square brackets after variable like `${var}[xxx]` is considered item access
---------------------------------------------------------------------------

Syntax like `${var}[xxx]` is now considered variable item access (`#2601`_),
not variable `${var}` followed by a literal string `[xxx]`. If the latter
is desired, escaping like `${var}\[xxx]` is needed.

Underscores are not converted to spaces in values given from the command line
-----------------------------------------------------------------------------

Earlier underscores were automatically converted to spaces with command line
options `--name`, `--doc`, `--metadata`, `--tagdoc`, `--tagstatcombine`,
`--logtitle` and `--reporttitle`. For example, `--doc Underscores_used_here`
was interpreted as `Underscores used here`, but nowadays the value is used
as-is. A simple fix is quoting or escaping spaces on the command line like
`--doc "We got spaces"` or `--doc We\ got\ spaces`. (`#2399`_)

Changes to xUnit output file format
-----------------------------------

Third party tools consuming xUnit compatible XML files earlier supported
both `skip` and `skipped` attribute when reporting the number of skipped
tests, but nowadays many tools are stricter and only support `skipped`.
Earlier Robot Framework versions used `skip`, but it has now been changed
to `skipped` to fix compatibility with the more strict tools (`#2978`_).
This obviously affects possible tools that expect the attribute to be `skip`
but they ought to be rare. If such tool turn out to be common and not easy
to update, we can consider making the attribute name configurable.

Times in xUnit outputs are floats when they used to be integers (`#2397`).
This should not cause problems with 3rd party tools because they generally
parse times as floats, but custom tools parsing times as integers using
`int()` or equivalent need to be updated.

`time` attribute was added also to the `<testsuite>` element (`#2979`_).
Third party tools ought to handle this common optional attribute just fine,
but some overly strict custom tool may still be affected and needs to be
fixed.

Logs and reports do not support IE 8 and other old browsers anymore
-------------------------------------------------------------------

JavaScript dependencies used internally by logs and reports have been
updated. This may cause problems with ancient browsers, and most notably
IE 8 is not supported anymore. (`#2419`_)

Some deprecated syntax removed
------------------------------

Syntax that has been deprecated earlier has now been removed altogether:

- `*** Metadata ***` and `*** User Keywords ***` headers do not anymore work
  as synonyms for `*** Settings ***` and `*** Keywords ***`, respectively.
  (`#2864`_)

- `Document` cannot be used as a synonym for the `Documentation` setting.
  (`#2865`_)

- `Pre Condition` and `Post Condition` do not anymore work as synonyms for
  `Setup` and `Teardown`, respectively. (`#2865`_)

- It is not anymore possible to import a library with an extra space in its
  name like `Selenium Library`. (`#2879`_)

- Giving an alias to an imported library requires using `WITH NAME` with
  all uppercase letters. (`#2880`_)

Other issues possibly causing backwards incompatibility problems
----------------------------------------------------------------

- First logical, not physical, line of the keyword documentation is included
  in log files. (`#2491`_)

- Test libraries using the dynamic library API get all named arguments as
  part of `kwargs` (when their `run_keyword` accepts it), not mapped to
  positional arguments. (`#2930`_)

- `Run Keyword And Ignore Error` and others similar keywords let "passing
  exceptions" caused by `Pass Execution` and similar keywords to go through.
  (`#2799`_)

- `robot-exit` tag that is added automatically to tests if execution is stopped
  gracefully has been renamed to `robot:exit`. (`#2539`_)

- `Collections` keywords cannot anymore be used with strings. (`#2580`_)

- `FOR` alone, case-sensitively, is enough to start a for loop (`#2990`_).
  This may cause problems if a keyword is named `FOR` or when using templates
  and a data item is exactly `FOR`. In the former case a workaround is using
  the keyword like `For`, and in the latter case the value needs to be escaped
  like `\FOR`.

- Timer string format is more strict. For example, `01:02:03:123` and
  `01:02foo` do not work anymore. (`#2921`_)

- Deprecated `robot.running.TestSuite.(imports|variables|user_keywords)`
  propertys have been removed from the programmatic API. (`#2867`_)

Deprecated features
===================

HTML and TSV data formats have been deprecated
----------------------------------------------

The HTML format has been deprecated for good and it will not be supported
by future Robot Framework versions at all. The TSV format has been
deprecated as well, but it can be used if the data is fully compatible with
the plain text format and the `--extension` option is used to tell that TSV
files should be parsed. It is possible to use, for example, `--extension tsv`
(`*.tsv` only) or `--extension robot:tsv` (`*.robot` and `*.tsv`). (`#2819`_)

Parsing other than `*.robot` files by default is deprecated
-----------------------------------------------------------

The plan is that Robot Framework 3.2 would parse only files with the
`*.robot` extension by default, but the `--extension` option could be used
to tell that also some other files should be parsed. The first step towards
that goal is deprecating parsing other than `*.robot` files by default in
Robot Framework 3.1. This naturally includes HTML and TSV files that are
deprecated in general (see above), but also the otherwise supported plain
text test data in normal text files (`*.txt`) and embedded to
reStructuredText files (`*.rst` or `*.rest`). (`#2820`_)

Use the `--extension` option like `--extension rst` (`.rst` only) or
`--extension robot:rst:rest` (`*.robot`, `*.rst` and `*.rest`) to avoid
the deprecation warning and to get these files parsed also in the future.

Using section and setting names space-insensitively is deprecated
-----------------------------------------------------------------

Earlier it has been possible to use internal spaces freely in section headers
like `*** S e t t i n g s ***` and in settings like `Testsetup` or
`[ S e t u p ]`. This is now deprecated and formats like `*** Settings ***`,
`Test Setup` and `[Setup]` needs to be used. All names are still
case-insensitive, though, and a space can be used around the name
and a possible surrounding marker meaning that also `***Settings***` and
`[ Setup ]` are accepted. (`#2985`_)

Escaping problematic characters with `--escape` is deprecated
-------------------------------------------------------------

Robot Framework's custom `--escape` functionality has been deprecated
and normal command line escaping mechanism needs to be used instead.
Typically values can be quoted like `-v "VAR:Value with spaces"`, but
depending on the context and the terminal using the backslash character
may work as well. (`#2846`_)

`--warnonskippedfiles` has been deprecated
------------------------------------------

The `--warnonskippedfiles` option has made it possible to explicitly show
if certain files are skipped because they cannot be parsed successfully.
Because such problems are nowadays reported as explicit errors (`#2857`_),
the `--warnonskippedfiles` option is not useful anymore and it has been
deprecated.

Stricter for loop syntax
------------------------

Using other separators between for loop variables and values than exactly
`IN`, `IN RANGE`, `IN ZIP` and `IN ENUMERATE` has been deprecated. This means
the separator is nowadays both case- and space-sensitive and variants like
`in` or `INRANGE` will not work anymore in the future. (`#2991`_)

Forthcoming deprecations
========================

For loop marker to be changed from `:FOR` to `FOR`
--------------------------------------------------

Issue `#2990`_ makes it possible to start a for loop with only `FOR`
(case-sensitive) as a marker. The old format `:FOR` (case-insensitive, at
least one colon required) still works without warnings, but it will be
deprecated in the future. Users are advised to start using the new `FOR`
style already now.

List item access to be changed to use syntax `${var}[item]`
-----------------------------------------------------------

Issue `#2601`_ introduces syntax like `${var}[key][0]` to access nested
items in variables containing lists and dictionaries, and also makes
it possible to access direct items like `${var}[0]` and `${var}[key]`
regardless is the variable a list or dictionary. The old syntax `@{var}[0]`
and `&{var}[key]` still works, but it will be `deprecated in the future`__.
Using solely the new syntax is highly recommend already now.

__ https://github.com/robotframework/robotframework/issues/2974

Acknowledgements
================

There have been several valuable contributions by the community:

- `@Brian-Williams <https://github.com/Brian-Williams>`__ implemented
  keyword-only argument support with Python 3 libraries (`#2555`_).

- `@LSumbler <https://github.com/LSumbler>`__ added HTTPS support to
  the Remote interface (`#2912`_).

- Jonathan Koser (`@JonKoser <https://github.com/JonKoser>`__) fixed problems
  with signal handlers registered outside Python (`#2952`_).

- Jani Mikkonen (`@rasjani <https://github.com/rasjani>`__) investigated
  and fixed compatibility problems with third party tools consuming
  xUnit output files (`#2978`_).

- Juuso Issakainen (`@juusoi <https://github.com/juusoi>`__) changed times
  in xUnit outputs from integers to floats (`#2397`_) and enhanced error
  messages if keywords from the Collections library are used with invalid
  arguments (`#2580`_).

- `@kanchi240 <https://github.com/kanchi240>`__ added `time` attribute to
  `<testsuite>` elements in xUnit outputs (`#2979`_).

- `@andreeakovacs <https://github.com/andreeakovacs>`__ provided initial
  pull requests to fix a regression with global variables not being available
  in listeners' close method (`#2443`_) and to enhance parsing logic when
  using `--suite` option (`#2564`_). Mihai Pârvu
  (`@mihaiparvu <https://github.com/mihaiparvu>`__ finalized both of these
  PRs.

- `@DanielPBak <https://github.com/DanielPBak>`__ fixed problems with
  libraries imported using a filesystem path modifying `sys.path` (`#2923`_).

- `@skhomuti <https://github.com/skhomuti>`__ provided a simple example
  reliably reproducing a nasty problem with timeouts leading to `output.xml`
  files being corrupted (`#2839`_). The example made it easy to debug
  the problem and to come up with a proper fix.

Huge thanks for all contributors and to everyone else who has reported
problems, tested preview releases, participated discussion on various
forums, or otherwise helped to make Robot Framework as well as the ecosystem
and community around it better.

Robot Framework 3.1 is the first major release sponsored by `Robot Framework
Foundation <http://robotframework.org/foundation/>`_. Big thanks for all
the 20+ member organizations, and hopefully the foundation gets even more
members in the future to make the development more active. Separate thanks
for `Siili <https://www.siili.com/>`__, `Knowit <https://www.knowit.fi/>`__,
`Vala <https://www.valagroup.com/>`__, `Qentinel <https://qentinel.com/>`__
and `Eficode <https://www.eficode.com/home>`__ for sponsoring the development
related to the `RPA support`_.

Full list of fixes and enhancements
===================================

.. list-table::
    :header-rows: 1

    * - ID
      - Type
      - Priority
      - Summary
      - Added
    * - `#2839`_
      - bug
      - critical
      - Logging when timeouts are enabled may corrupt output
      - beta 1
    * - `#2415`_
      - enhancement
      - critical
      - Use .exe wrappers instead of .bat under Windows
      - alpha 1
    * - `#2788`_
      - enhancement
      - critical
      - Terminology configuration to support usage in generic automation
      - alpha 1
    * - `#2819`_
      - enhancement
      - critical
      - Deprecate using test data in HTML and TSV formats
      - alpha 2
    * - `#2820`_
      - enhancement
      - critical
      - Deprecate parsing other than `.robot` files
      - alpha 2
    * - `#2890`_
      - enhancement
      - critical
      - Automatic argument conversion based on Python 3 function annotations
      - alpha 2
    * - `#2947`_
      - enhancement
      - critical
      - Automatic argument conversion based on type information passed to `@keyword` decorator
      - alpha 2
    * - `#2857`_
      - bug
      - high
      - Emit error if parsing file fails when executing a directory
      - alpha 2
    * - `#2860`_
      - bug
      - high
      - Emit an error if test data contains unrecognized section header
      - alpha 2
    * - `#2978`_
      - bug
      - high
      - Fix xUnit compatibility with 3rd party tooling
      - beta 1
    * - `#1734`_
      - enhancement
      - high
      - Provide `wheel` distribution
      - alpha 1
    * - `#2276`_
      - enhancement
      - high
      - Remove support for Python 2.6 and 3.3
      - alpha 1
    * - `#2555`_
      - enhancement
      - high
      - Support keyword-only arguments in Python 3 libraries
      - alpha 2
    * - `#2601`_
      - enhancement
      - high
      - Accessing nested list and dictionary variable items like `${var}[key][0]`
      - beta 1
    * - `#2818`_
      - enhancement
      - high
      - Remove `pybot`, `jybot`, `ipybot`, `jyrebot` and `ipyrebot` start-up scripts
      - alpha 1
    * - `#2891`_
      - enhancement
      - high
      - Support `.resource` extension with resource files
      - alpha 2
    * - `#2896`_
      - enhancement
      - high
      - Support named-only arguments with user keywords
      - alpha 2
    * - `#2897`_
      - enhancement
      - high
      - Support named-only arguments with dynamic libraries
      - alpha 2
    * - `#2932`_
      - enhancement
      - high
      - Automatic type conversion based on argument default values
      - alpha 2
    * - `#2954`_
      - enhancement
      - high
      - Remove need for custom ElementTree installation with IronPython 2.7.9+
      - alpha 2
    * - `#2985`_
      - enhancement
      - high
      - Deprecate using section and setting names space-insensitively
      - beta 1
    * - `#2399`_
      - bug
      - medium
      - Underscores should not be replaced with spaces in values given from command line
      - alpha 1
    * - `#2443`_
      - bug
      - medium
      - Global variables not accessible in listener `close` method
      - beta 1
    * - `#2750`_
      - bug
      - medium
      - `PYTHONIOENCODING` is not honored with Python 2
      - alpha 1
    * - `#2817`_
      - bug
      - medium
      - `pip install -I` corrupts `robot.bat` if Robot Framework is already installed
      - alpha 1
    * - `#2829`_
      - bug
      - medium
      - Operating system encoding detection problems on Windows with Python 3.6
      - alpha 1
    * - `#2894`_
      - bug
      - medium
      - `Should Match` and other related keywords consider `foo\n` to match `foo`
      - alpha 2
    * - `#2930`_
      - bug
      - medium
      - Default values unnecessarily passed to keywords when using dynamic library API
      - beta 1
    * - `#2952`_
      - bug
      - medium
      - Signal handler registered outside Python causes error
      - alpha 2
    * - `#2397`_
      - enhancement
      - medium
      - Times in xUnit outputs should be floats not integers
      - alpha 2
    * - `#2419`_
      - enhancement
      - medium
      - Update JavaScript dependencies used by logs and reports internally
      - alpha 2
    * - `#2471`_
      - enhancement
      - medium
      - Support `[...]` syntax with glob patterns
      - alpha 2
    * - `#2491`_
      - enhancement
      - medium
      - Include first logical line of keyword documentation in log
      - alpha 2
    * - `#2539`_
      - enhancement
      - medium
      - Rename `robot-exit` tag to use `robot:` prefix
      - alpha 2
    * - `#2576`_
      - enhancement
      - medium
      - Possibility to configure number of error message lines in reports
      - beta 1
    * - `#2830`_
      - enhancement
      - medium
      - Change source distribution format from `tar.gz` to `zip`
      - alpha 1
    * - `#2846`_
      - enhancement
      - medium
      - Deprecate using `--escape` to escape characters problematic on console
      - alpha 2
    * - `#2864`_
      - enhancement
      - medium
      - Remove deprecated `Metadata` and `User Keyword` table name synonyms
      - alpha 2
    * - `#2865`_
      - enhancement
      - medium
      - Remove deprecated `Document` and `Suite/Test Pre/Post Condition` synonym settings
      - alpha 2
    * - `#2912`_
      - enhancement
      - medium
      - Remote Library Connection over HTTPS redirects to HTTP
      - alpha 2
    * - `#2925`_
      - enhancement
      - medium
      - Libdoc: Show function argument annotations
      - alpha 2
    * - `#2967`_
      - enhancement
      - medium
      - Support other than glob patterns with `Run Keyword And Expect Error`
      - beta 1
    * - `#2973`_
      - enhancement
      - medium
      - Support "slice access" with variables containing lists like `${var}[2:]`
      - beta 1
    * - `#2979`_
      - enhancement
      - medium
      - xUnit outputs: Add `time` attribute to `<testsuite>` element
      - beta 1
    * - `#2990`_
      - enhancement
      - medium
      - Allow creating for loop using `FOR` (case-sensitive) in addition to `:FOR` (case-insensitive)
      - beta 1
    * - `#2991`_
      - enhancement
      - medium
      - Deprecate using for loops with other separators than exact `IN`, `IN RANGE`, `IN ZIP` and `IN ENUMERATE`
      - beta 1
    * - `#2861`_
      - ---
      - medium
      - Deprecate `--warnonskippedfiles` because it is not needed anymore
      - alpha 2
    * - `#2564`_
      - bug
      - low
      - When using `--suite parent.child`, all test case files with name `child.robot` are parsed
      - beta 1
    * - `#2580`_
      - bug
      - low
      - `Collections` keywords fail with bad error message when used with invalid input
      - alpha 2
    * - `#2594`_
      - bug
      - low
      - `Run Keyword And Return` not returning in teardown context if executed test fails
      - beta 1
    * - `#2655`_
      - bug
      - low
      - User Guide: Broken reference to outdated Python tutorial
      - alpha 2
    * - `#2659`_
      - bug
      - low
      - Bad error if using `TestSuite.configure` with a non-root suite
      - alpha 2
    * - `#2761`_
      - bug
      - low
      - Log and report are broken if top-level suite has empty name (e.g. running  `_.robot`)
      - alpha 2
    * - `#2799`_
      - bug
      - low
      - `Run Keyword And Ignore Error` and others don't handle "passing" exceptions correctly
      - beta 1
    * - `#2833`_
      - bug
      - low
      - Document that `Run Keyword Unless` doesn't support `ELSE/ELSE IF` branches
      - alpha 1
    * - `#2834`_
      - bug
      - low
      - Problems with glob patterns on IronPython 2.7.8
      - alpha 1
    * - `#2837`_
      - bug
      - low
      - User Guide: Update reference to `decorator` module
      - alpha 1
    * - `#2871`_
      - bug
      - low
      - Document that nested `Run Keyword If` with `ELSE/ELSE IF` is not supported
      - alpha 2
    * - `#2872`_
      - bug
      - low
      - Rounding problem with `Should Be Equal As Numbers` (and elsewhere)
      - alpha 2
    * - `#2881`_
      - bug
      - low
      - Refreshing logs, reports and library docs don't always scroll to previous anchor
      - alpha 2
    * - `#2921`_
      - bug
      - low
      - Invalid strings work as timer strings
      - alpha 2
    * - `#2923`_
      - bug
      - low
      - Importing by path interferes with `sys.path` changes caused by imported modules
      - alpha 2
    * - `#2945`_
      - bug
      - low
      - `--timestampoutputs` generates files with different timestamps
      - beta 1
    * - `#2966`_
      - bug
      - low
      - Error reporting problems with `--ExitOnFailure` if test fails due to being empty
      - beta 1
    * - `#2821`_
      - enhancement
      - low
      - Document that importing library implemented as module with absolute path requires no trailing slash
      - alpha 2
    * - `#2867`_
      - enhancement
      - low
      - Remove deprecated `robot.running.TestSuite.(imports|variables|user_keywords)` propertys
      - alpha 2
    * - `#2879`_
      - enhancement
      - low
      - Remove support to import library with extra spaces in name
      - alpha 2
    * - `#2880`_
      - enhancement
      - low
      - Remove support to import libraries with alias using `WITH NAME` case-insensitively
      - alpha 2
    * - `#2895`_
      - enhancement
      - low
      - User Guide: Adjust Python code examples to be Python 3 compatible
      - alpha 2
    * - `#2903`_
      - enhancement
      - low
      - Add note in documentation about `${SPACE}` to clarify that it means the ASCII space
      - alpha 2
    * - `#2913`_
      - enhancement
      - low
      - Clarify documentation related to specifying test setup/teardown in initialization files
      - alpha 2
    * - `#2927`_
      - enhancement
      - low
      - Consider strings `0` and `OFF` to be false when used in Boolean context
      - alpha 2

Altogether 72 issues. View on the `issue tracker <https://github.com/robotframework/robotframework/issues?q=milestone%3Av3.1>`__.

.. _#2839: https://github.com/robotframework/robotframework/issues/2839
.. _#2415: https://github.com/robotframework/robotframework/issues/2415
.. _#2788: https://github.com/robotframework/robotframework/issues/2788
.. _#2819: https://github.com/robotframework/robotframework/issues/2819
.. _#2820: https://github.com/robotframework/robotframework/issues/2820
.. _#2890: https://github.com/robotframework/robotframework/issues/2890
.. _#2947: https://github.com/robotframework/robotframework/issues/2947
.. _#2857: https://github.com/robotframework/robotframework/issues/2857
.. _#2860: https://github.com/robotframework/robotframework/issues/2860
.. _#2978: https://github.com/robotframework/robotframework/issues/2978
.. _#1734: https://github.com/robotframework/robotframework/issues/1734
.. _#2276: https://github.com/robotframework/robotframework/issues/2276
.. _#2555: https://github.com/robotframework/robotframework/issues/2555
.. _#2601: https://github.com/robotframework/robotframework/issues/2601
.. _#2818: https://github.com/robotframework/robotframework/issues/2818
.. _#2891: https://github.com/robotframework/robotframework/issues/2891
.. _#2896: https://github.com/robotframework/robotframework/issues/2896
.. _#2897: https://github.com/robotframework/robotframework/issues/2897
.. _#2932: https://github.com/robotframework/robotframework/issues/2932
.. _#2954: https://github.com/robotframework/robotframework/issues/2954
.. _#2985: https://github.com/robotframework/robotframework/issues/2985
.. _#2399: https://github.com/robotframework/robotframework/issues/2399
.. _#2443: https://github.com/robotframework/robotframework/issues/2443
.. _#2750: https://github.com/robotframework/robotframework/issues/2750
.. _#2817: https://github.com/robotframework/robotframework/issues/2817
.. _#2829: https://github.com/robotframework/robotframework/issues/2829
.. _#2894: https://github.com/robotframework/robotframework/issues/2894
.. _#2930: https://github.com/robotframework/robotframework/issues/2930
.. _#2952: https://github.com/robotframework/robotframework/issues/2952
.. _#2397: https://github.com/robotframework/robotframework/issues/2397
.. _#2419: https://github.com/robotframework/robotframework/issues/2419
.. _#2471: https://github.com/robotframework/robotframework/issues/2471
.. _#2491: https://github.com/robotframework/robotframework/issues/2491
.. _#2539: https://github.com/robotframework/robotframework/issues/2539
.. _#2576: https://github.com/robotframework/robotframework/issues/2576
.. _#2830: https://github.com/robotframework/robotframework/issues/2830
.. _#2846: https://github.com/robotframework/robotframework/issues/2846
.. _#2864: https://github.com/robotframework/robotframework/issues/2864
.. _#2865: https://github.com/robotframework/robotframework/issues/2865
.. _#2912: https://github.com/robotframework/robotframework/issues/2912
.. _#2925: https://github.com/robotframework/robotframework/issues/2925
.. _#2967: https://github.com/robotframework/robotframework/issues/2967
.. _#2973: https://github.com/robotframework/robotframework/issues/2973
.. _#2979: https://github.com/robotframework/robotframework/issues/2979
.. _#2990: https://github.com/robotframework/robotframework/issues/2990
.. _#2991: https://github.com/robotframework/robotframework/issues/2991
.. _#2861: https://github.com/robotframework/robotframework/issues/2861
.. _#2564: https://github.com/robotframework/robotframework/issues/2564
.. _#2580: https://github.com/robotframework/robotframework/issues/2580
.. _#2594: https://github.com/robotframework/robotframework/issues/2594
.. _#2655: https://github.com/robotframework/robotframework/issues/2655
.. _#2659: https://github.com/robotframework/robotframework/issues/2659
.. _#2761: https://github.com/robotframework/robotframework/issues/2761
.. _#2799: https://github.com/robotframework/robotframework/issues/2799
.. _#2833: https://github.com/robotframework/robotframework/issues/2833
.. _#2834: https://github.com/robotframework/robotframework/issues/2834
.. _#2837: https://github.com/robotframework/robotframework/issues/2837
.. _#2871: https://github.com/robotframework/robotframework/issues/2871
.. _#2872: https://github.com/robotframework/robotframework/issues/2872
.. _#2881: https://github.com/robotframework/robotframework/issues/2881
.. _#2921: https://github.com/robotframework/robotframework/issues/2921
.. _#2923: https://github.com/robotframework/robotframework/issues/2923
.. _#2945: https://github.com/robotframework/robotframework/issues/2945
.. _#2966: https://github.com/robotframework/robotframework/issues/2966
.. _#2821: https://github.com/robotframework/robotframework/issues/2821
.. _#2867: https://github.com/robotframework/robotframework/issues/2867
.. _#2879: https://github.com/robotframework/robotframework/issues/2879
.. _#2880: https://github.com/robotframework/robotframework/issues/2880
.. _#2895: https://github.com/robotframework/robotframework/issues/2895
.. _#2903: https://github.com/robotframework/robotframework/issues/2903
.. _#2913: https://github.com/robotframework/robotframework/issues/2913
.. _#2927: https://github.com/robotframework/robotframework/issues/2927
