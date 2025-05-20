===========================
Robot Framework 7.0 alpha 2
===========================

.. default-role:: code


`Robot Framework`_ 7.0 is a new major release with native `VAR` syntax for creating
variables (`#3761`_), support for mixing embedded and normal arguments with library
keywords (`#4710`_) and various other enhancements and bug fixes. Robot Framework 7.0
requires Python 3.8 or newer (`#4294`_).

Robot Framework 7.0 alpha 2 was released on Wednesday November 22, 2023.
It is especially targeted for external tool developers for testing how
`backwards incompatible changes`_ and deprecations_ possibly affect their tools.
We can still make adjustments or even revert problematic changes before
the final release.

We also hope to get feedback from the general user base related to the `VAR`
syntax (`#3761`_) and other new features. Making changes to them is much easier
now than after the final release when we need to take backwards compatibility
into account.

Questions and comments related to the release can be sent to the `#devel`
channel on `Robot Framework Slack`_ and possible bugs submitted to
the `issue tracker`_. All issues targeted for Robot Framework 7.0 can be found
from the `issue tracker milestone`_.

.. _Robot Framework: http://robotframework.org
.. _Robot Framework Foundation: http://robotframework.org/foundation
.. _pip: http://pip-installer.org
.. _PyPI: https://pypi.python.org/pypi/robotframework
.. _issue tracker milestone: https://github.com/robotframework/robotframework/milestone/64
.. _issue tracker: https://github.com/robotframework/robotframework/issues
.. _robotframework-users: http://groups.google.com/group/robotframework-users
.. _Slack: http://slack.robotframework.org
.. _Robot Framework Slack: Slack_
.. _installation instructions: ../../INSTALL.rst

.. contents::
   :depth: 2
   :local:

Installation
============

If you have pip_ installed, just run

::

   pip install --pre --upgrade robotframework

to install the latest available release or use

::

   pip install robotframework==7.0a2

to install exactly this version. Alternatively you can download the package
from PyPI_ and install it manually. For more details and other installation
approaches, see the `installation instructions`_.

Most important enhancements
===========================

Native `VAR` syntax
-------------------

The new `VAR` syntax (`#3761`_) makes it possible to create local variables
as well as global, suite and test/task scoped variables dynamically during
execution. The motivation is to have a more convenient syntax than using
the `Set Variable` keyword for creating local variables and to unify
the syntax for creating variables in different scopes. Except for the mandatory
`VAR` marker, the syntax is also the same as when creating variables in the
Variables section. The syntax is best explained with examples:

.. code:: robotframework

    *** Test Cases ***
    Example
        # Create a local variable `${local}` with value `value`.
        VAR    ${local}    value

        # Create a suite-scoped variable, visible throughout the whole suite.
        # Supported scopes are GLOBAL, SUITE, TEST, TASK and LOCAL (default).
        VAR    ${suite}    value    scope=SUITE

        # Validate created variables.
        Should Be Equal    ${local}    value
        Should Be Equal    ${suite}    value

    Example continued
        # Suite level variables are seen also by subsequent tests.
        Should Be Equal    ${suite}    value

When creating `${scalar}` variables having long values, it is possible to split
the value to multiple lines. Lines are joined together with a space by default,
but that can be changed with the `separator` configuration option. Similarly as
in the Variables section, it is possible to create also `@{list}` and `&{dict}`
variables. Unlike in the Variables section, variables can be created conditionally
using IF/ELSE structures:

.. code:: robotframework

    *** Test Cases ***
    Long value
        VAR    ${long}
        ...    This value is rather long.
        ...    It has been split to multiple lines.
        ...    Parts will be joined together with a space.

    Multiline
        VAR    ${multiline}
        ...    First line.
        ...    Second line.
        ...    Last line.
        ...    separator=\n

    List
        # Creates a list with three items.
        VAR    @{list}    a    b    c

    Dictionary
        # Creates a dict with two items.
        VAR    &{dict}    key=value    second=item

    Normal IF
        IF    1 > 0
            VAR    ${x}    true value
        ELSE
            VAR    ${x}    false value
        END

    Inline IF
        IF    1 > 0    VAR    ${x}    true value    ELSE    VAR    ${x}    false value

Mixed argument support with library keywords
--------------------------------------------

User keywords got support to use both embedded and normal arguments in Robot
Framework 6.1 (`#4234`__) and now that support has been added also to library keywords
(`#4710`_). The syntax works so, that if the function or method implementing the keyword
accepts more arguments than there are embedded arguments, the remaining arguments
can be passed in as normal arguments. This is illustrated by the following example
keyword:

.. code:: python

    @keyword('Number of ${animals} should be')
    def example(animals, count):
        ...

The above keyword could be used like this:

.. code:: robotframework

    *** Test Cases ***
    Example
        Number of horses should be    2
        Number of horses should be    count=2
        Number of dogs should be    3

__ https://github.com/robotframework/robotframework/issues/4234

Tags set globally can be removed using `-tag` syntax
----------------------------------------------------

Individual tests and keywords can nowadays remove tags set in the Settings
section with `Test Tags` or `Keyword Tags` settings by using the `-tag` syntax
(`#4374`_). For example, tests `T1` and `T3` below are given tags `all` and
`most`, and test `T2` gets tags `all` and `one`:

.. code:: robotframework

    *** Settings ***
    Test Tags      all    most

    *** Test Cases ***
    T1
        No Operation
    T2
        [Tags]    one    -most
        No Operation
    T3
        No Operation

With tests it is possible to get the same effect by using the `Default Tags`
setting and overriding it where needed. That syntax is, however, considered
deprecated (`#4365`__) and using the new `-tag` syntax is recommended.

__ https://github.com/robotframework/robotframework/issues/4365

Dynamic and hybrid library APIs support asynchronous execution
--------------------------------------------------------------

Dynamic and hybrid libraries nowadays support asynchronous execution.
In practice the special methods like `get_keyword_names` and `run_keyword`
can be implemented as async methods. (`#4803`_)

Async support was added to the normal static library API in Robot Framework
6.1 (`#4089`_). A bug related to handling asynchronous keywords if the whole
execution is stopped gracefully has also been fixed (`#4808`_).

.. _#4089: https://github.com/robotframework/robotframework/issues/4089

Support `'list[int]'` and `'int | float'` in argument conversion
----------------------------------------------------------------

Python's type hinting syntax has evolved so that generic types can be parameterized
like `list[int]` (new in `Python 3.9`__) and unions written as `int | float`
(new in `Python 3.10`__). Using these constructs with older Python versions causes
errors, but Python type checkers support also "stringified" type hints like
`'list[int]'` and `'int | float'` that work regardless the Python version.

Support for stringified generics and unions has now been added also to
Robot Framework's argument conversion (`#4711`_). For example,
the following typing now also works with Python 3.8:

.. code:: python

    def example(a: 'list[int]', b: 'int | float'):
        ...

These stringified types are also compatible with the Remote library API and other
scenarios where using actual types is not feasible.

__ https://peps.python.org/pep-0585/
__ https://peps.python.org/pep-0604/

Timestamps in result model and output.xml use standard format
-------------------------------------------------------------

Timestamps used in the result model and stored to the output.xml file earlier
used custom format like `20231107 19:57:01.123`. Non-standard formats are seldom
a good idea, and in this case parsing the custom format turned out to be slow
as well.

Nowadays the result model stores timestamps as standard datetime_ objects and
elapsed times as timedelta_ (`#4258`_). This makes creating timestamps and
operating with them more convenient and considerably faster. The new objects can
be accessed via `start_time`, `end_time` and `elapsed_time` attributes that were
added as forward compatibility already in Robot Framework 6.1 (`#4765`_).
Old information is still available via the old `starttime`, `endtime` and
`elapsedtime` attributes so this change is fully backwards compatible.

The timestamp format in output.xml has also been changed from the custom
`YYYYMMDD HH:MM:SS.mmm` format to `ISO 8601`_ compatible
`YYYY-MM-DDTHH:MM:SS.mmmmmm`. Using a standard format makes it
easier to process output.xml files, but this change also has big positive
performance effect. Now that the result model stores timestamps as datetime_
objects, formatting and parsing them with the available `isoformat()`__ and
`fromisoformat()`__ methods is very fast compared to custom formatting and parsing.

A related change is that instead of storing start and end times of each executed
item in output.xml, we nowadays store their start and elapsed times. Elapsed times
are represented as floats denoting seconds. Having elapsed times directly available
is a lot more convenient than calculating them based on start and end times.
Storing start and elapsed times also takes less space than storing start and end times.

As the result of these changes, times are available in the result model and in
output.xml in higher precision than earlier. Earlier times were stored in millisecond
granularity, but nowadays we use microseconds. Logs and reports still use milliseconds,
but that can be changed in the future if there are needs.

Changes to output.xml are backwards incompatible and affect all external tools
that process timestamps. This is discussed more in `Changes to output.xml`_
section below along with other output.xml changes.

.. _datetime: https://docs.python.org/3/library/datetime.html#datetime-objects
.. _timedelta: https://docs.python.org/3/library/datetime.html#timedelta-objects
.. _#4765: https://github.com/robotframework/robotframework/issues/4765
.. _ISO 8601: https://en.wikipedia.org/wiki/ISO_8601
__ https://docs.python.org/3/library/datetime.html#datetime.datetime.isoformat
__ https://docs.python.org/3/library/datetime.html#datetime.datetime.fromisoformat

Backwards incompatible changes
==============================

Python 3.6 and 3.7 are no longer supported
------------------------------------------

Robot Framework 7.0 requires Python 3.8 or newer (`#4294`_). The last version
that supports Python 3.6 and 3.7 is Robot Framework 6.1.1.

Changes to output.xml
---------------------

The output.xml file has changed in different ways making Robot Framework 7.0
incompatible with external tools processing output.xml files until these tools
are updated. We try to avoid this kind of breaking changes, but in this case
especially the changes to timestamps were considered so important that we
eventually would have needed to do them anyway.

Due to the changes being relatively big, it can take some time before external
tools are updated. To allow users to take Robot Framework 7.0 into use also
if they depend on an incompatible tool, it is possible to use the new
`--legacy-output` option both as part of execution and with the Rebot tool
to generate output.xml files that are compatible with older versions.

Timestamp related changes
~~~~~~~~~~~~~~~~~~~~~~~~~

The biggest changes in output.xml are related to timestamps (`#4258`_).
With earlier versions start and end times of executed items, as well as timestamps
of the logged messages, were stored using a custom `YYYYMMDD HH:MM:SS.mmm` format,
but nowadays the format is `ISO 8601`_ compatible `YYYY-MM-DDTHH:MM:SS.mmmmmm`.
In addition to that, instead of saving start and end times to `starttime` and
`endtime` attributes and message times to `timestamp`, start and elapsed times
are now stored to `start` and `elapsed` attributes and message times to `time`.

Examples:

.. code:: xml

    <!-- Old format -->
    <msg timestamp="20231108 15:36:34.278" level="INFO">Hello world!</msg>
    <status status="PASS" starttime="20231108 15:37:35.046" endtime="20231108 15:37:35.046"/>

    <!-- New format -->
    <msg time="2023-11-08T15:36:34.278343" level="INFO">Hello world!</msg>
    <status status="PASS" start="2023-11-08T15:37:35.046153" elapsed="0.000161"/>

The new format is standard compliant, contains more detailed times, makes the elapsed
time directly available and makes the `<status>` elements over 10% shorter.
These are all great benefits, but we are still sorry for all the extra work
this causes for those developing tools that process output.xml files.

Keyword name related changes
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

How keyword names are stored in output.xml has changed slightly as well (`#4884`_).
With each executed keywords we store both the name of the keyword and the name
of the library or resource file containing it. Earlier the latter was stored to
attribute `library` also with resource files, but nowadays the attribute is generic
`owner`. In addition to `owner` being a better name in general, it also
matches the new `owner` attribute keywords in the result model have.

Another change is that the original name stored with keywords using embedded
arguments is nowadays in `source_name` attribute when it used to be in `sourcename`.
This change was done to make the attribute consistent with the attribute in
the result model.

Examples:

.. code:: xml

    <!-- Old format -->
    <kw name="Log" library="BuiltIn">...</kw>
    <kw name="Number of horses should be" sourcename="Number of ${animals} should be" library="my_resource">...</kw>

    <!-- New format -->
    <kw name="Log" owner="BuiltIn">...</kw>
    <kw name="Number of horses should be" source_name="Number of ${animals} should be" owner="my_resource">...</kw>

Other changes
~~~~~~~~~~~~~

Nowadays keywords and control structures can have a message. Messages are represented
as the text of the `<status>` element, and they have been present already earlier with
tests and suites. Related to this, control structured cannot anymore have `<doc>`.
(`#4883`_)

These changes should not cause problems for tools processing output.xml files,
but storing messages with each failed keyword and control structure may
increase the output.xml size.

Schema updates
~~~~~~~~~~~~~~

The output.xml schema has been updated and can be found via
https://github.com/robotframework/robotframework/tree/master/doc/schema/.

Changes to result model
-----------------------

There have been some changes to the result model that unfortunately affect
external tools using it. The main motivation for these changes has been
cleaning up the model before creating a JSON representation for it (`#4847`_).

.. _#4847: https://github.com/robotframework/robotframework/issues/4847

Changes related to keyword names
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The biggest changes are related to keyword names (`#4884`_). Earlier `Keyword`
objects had a `name` attribute that contained the full keyword name like
`BuiltIn.Log`. The actual keyword name and the name of the library or resource
file that the keyword belonged to were in `kwname` and `libname` attributes,
respectively. In addition to these, keywords using embedded arguments also had
a `sourcename` attribute containing the original keyword name.

Due to reasons explained in `#4884`_, the following changes have been made
in Robot Framework 7.0:

- Old `kwname` is renamed to `name`. This is consistent with the execution side `Keyword`.
- Old `libname` is renamed to generic `owner`.
- New `full_name` is introduced to replace the old `name`.
- `sourcename` is renamed to `source_name`.
- `kwname`, `libname` and `sourcename` are preserved as properties. They are considered
  deprecated, but accessing them will not cause a deprecation in this release yet.

The backwards incompatible part of this change is changing the meaning of the
`name` attribute. It used to be a read-only property yielding the full name
like `BuiltIn.Log`, but now it is a normal attribute that contains just the actual
keyword name like `Log`. All other old attributes have been preserved as properties.

Deprecated attributes have been removed
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The following attributes that were deprecated already in Robot Framework 4.0
have been removed (`#4846`_):

- `TestSuite.keywords`. Use `TestSuite.setup` and `TestSuite.teardown` instead.
- `TestCase.keywords`. Use `TestCase.body`, `TestCase.setup` and `TestCase.teardown` instead.
- `Keyword.keywords`. Use `Keyword.body` and `Keyword.teardown` instead.
- `Keyword.children`. Use `Keyword.body` and `Keyword.teardown` instead.
- `TestCase.critical`. The whole criticality concept has been removed.

Additionally, `TestSuite.keywords` and `TestCase.keywords` have been removed
from the execution model.

Changes to parsing model
------------------------

There have been some changes also to the parsing model:

- The node representing the deprecated `[Return]` setting has been renamed from
  `Return` to `ReturnSetting`. At the same time, the node representing the
  `RETURN` statement has been renamed from `ReturnStatement` to `Return` (`#4939`_).

  To ease transition, `ReturnSetting` has existed as an alias for `Return` starting
  from Robot Framework 6.1 (`#4656`_) and `ReturnStatement` is preserved as an alias
  now. In addition to that, the `ModelVisitor` base class has special handling for
  `visit_ReturnSetting` and `visit_ReturnStatement` visitor methods so that they work
  correctly with `ReturnSetting` and `ReturnStatement` with Robot Framework 6.1 and
  newer. Issue `#4939`_ explains this in more detail and has a concrete example
  how to support also older Robot Framework versions.

- The node representing the `Test Tags` setting as well as the deprecated
  `Force Tags` setting has been renamed from `ForceTags` to `TestTags` (`#4385`_).
  `ModelVisitor` has special handling for the `visit_ForceTags` method so
  that it will continue to work also after the change.

- The token type used with `AS` (or `WITH NAME`) in library imports has been changed
  to `Token.AS` (`#4375`_). `Token.WITH_NAME` still exists as an alias for `Token.AS`.

- Statement `type` and `tokens` have been moved from `_fields` to `_attributes` (`#4912`_).
  This may affect debugging the model.

.. _#4656: https://github.com/robotframework/robotframework/issues/4656

Changes to Libdoc spec files
----------------------------

The following deprecated constructs have been removed from Libdoc spec files (`#4667`_):

- `datatypes` have been removed from XML or JSON spec files. They were deprecated in
  favor of `typedocs` already in Robot Framework 5.0 (`#4160`_).
- Type names are not anymore written to XML specs as content of the `<type>` elements.
  The name is available as the `name` attribute of `<type>` elements since
  Robot Framework 6.1 (`#4538`_).
- `types` and `typedocs` attributes have been removed from arguments in JSON specs.
  The `type` attribute introduced in RF 6.1 (`#4538`_) needs to be used instead.

Libdoc schema files have been updated and can be found via
https://github.com/robotframework/robotframework/tree/master/doc/schema/.

.. _#4160: https://github.com/robotframework/robotframework/issues/4160
.. _#4538: https://github.com/robotframework/robotframework/issues/4538

Changes to selecting tests with `--suite`, `--test` and `--include`
-------------------------------------------------------------------

There are two changes related to selecting tests:

- When using `--test` and `--include` together, tests matching either of them
  are selected (`#4721`_). Earlier tests need to match both options to be selected.

- When selecting a suite using its parent suite as a prefix like `--suite parent.suite`,
  the given name must match the full suite name (`#4720`_). Earlier it was enough if
  the prefix matched the closest parent or parents.

Other backwards incompatible changes
------------------------------------

- The default value of the `stdin` argument used with `Process` library keyword
  has been changed from `subprocess.PIPE` to `None` (`#4103`_). This change ought
  to avoid processes hanging in some cases. Those who depend on the old behavior
  need to use `stdin=PIPE` explicitly to enable that.

- When type hints are specified as strings, they must use format `type`, `type[param]`,
  `type[p1, p2]` or `t1 | t2` (`#4711`_). Using other formats will cause errors taking
  keywords into use. In practice problems occur if the special characters `[`, `]`, `,`
  and `|` occur in unexpected places. For example, `arg: "Hello, world!"` will cause
  an error due to the comma.

- `datetime`, `date` and `timedelta` objects are sent over the Remote interface
  differently than earlier (`#4784`_). They all used to be converted to strings, but
  nowadays `datetime` is sent as-is, `date` is converted to `datetime` and sent like
  that, and `timedelta` is converted to a `float` by using `timedelta.total_seconds()`.

- `robot.utils.normalize` does not anymore support bytes (`#4936`_).

- Deprecated `accept_plain_values` argument has been removed from the
  `timestr_to_secs` utility function (`#4861`_).

Deprecations
============

`[Return]` setting
------------------

The `[Return]` setting for specifying the return value from user keywords has
been "loudly" deprecated (`#4876`_). It has been "silently" deprecated since
Robot Framework 5.0 when the much more versatile `RETURN` setting was introduced
(`#4078`_), but now using it will cause a deprecation warning. The plan is to
preserve the `[Return]` setting at least until Robot Framework 8.0.

If you have lot of data that uses `[Return]`, the easiest way to update it is
using the Robotidy_ tool that can convert `[Return]` to `RETURN` automatically.
If you have data that is executed also with Robot Framework versions that do
not support `RETURN`, you can use the `Return From Keyword` keyword instead.
That keyword will eventually be deprecated and removed as well, though.

.. _#4078: https://github.com/robotframework/robotframework/issues/4078
.. _Robotidy: https://robotidy.readthedocs.io

Singular section headers
------------------------

Using singular section headers like `*** Test Case ***` or `*** Setting ***`
nowadays causes a deprecation warning (`#4432`_). They were silently deprecated
in Robot Framework 6.0 for reasons explained in issue `#4431`_.

.. _#4431: https://github.com/robotframework/robotframework/issues/4431

Deprecated attributes in parsing, running and result models
-----------------------------------------------------------

- In the parsing model, `For.variables`, `ForHeader.variables`, `Try.variable` and
  `ExceptHeader.variable` attributes have been deprecated in favor of the new `assign`
  attribute (`#4708`_).

- In running and result models, `For.variables` and `TryBranch.variable` have been
  deprecated in favor of the new `assign` attribute (`#4708`_).

- In the result model, control structures like `FOR` were earlier modeled so that they
  looked like keywords. Nowadays they are considered totally different objects and
  their keyword specific attributes `name`, `kwnane`, `libname`, `doc`, `args`,
  `assign`, `tags` and `timeout` have been deprecated  (`#4846`_).

- `starttime`, `endtime` and `elapsed` time attributes in the result model have been
  silently deprecated (`#4258`_). Accessing them does not yet cause a deprecation
  warning, but users are recommended to use `start_time`, `end_time` and
  `elapsed_time` attributes that are available since Robot Framework 6.1.

- `kwname`, `libname` and `sourcename` attributes used by the `Keyword` object
  in the result model have been silently deprecated (`#4884`_). New code should use
  `name`, `owner` and `source_name` instead.

Other deprecated features
-------------------------

- Using embedded arguments with a variable that has a value not matching custom
  embedded argument patterns nowadays causes a deprecation warning (`#4524`_).
  Earlier variables used as embedded arguments were always accepted without
  validating values.

- Using `FOR IN ZIP` loops with lists having different lengths without explicitly
  using `mode=SHORTEST` has been deprecated (`#4685`_). The strict mode where lengths
  must match will be the default mode in the future.

- Various utility functions in the `robot.utils` package, including the whole
  Python 2/3 compatibility layer, that are no longer used by Robot Framework itself
  have been deprecated (`#4501`_). If you need some of these utils, you can copy
  their code to your own tool or library. This change may affect existing
  libraries and tools in the ecosystem.

- `case_insensitive` and `whitespace_insensitive` arguments used by some
  Collections and String library keywords have been deprecated in favor of
  `ignore_case` and `ignore_whitespace`. The new arguments were added for
  consistency reasons (`#4954`_) and the old arguments will continue to work
  for the time being.

- Passing time as milliseconds to the `elapsed_time_to_string` utility function
  has been deprecated (`#4862`_).

Acknowledgements
================

Robot Framework development is sponsored by the `Robot Framework Foundation`_
and its over 60 member organizations. If your organization is using Robot Framework
and benefiting from it, consider joining the foundation to support its
development as well.

Robot Framework 7.0 team funded by the foundation consists of
`Pekka Klärck <https://github.com/pekkaklarck>`_ and
`Janne Härkönen <https://github.com/yanne>`_ (part time).
In addition to work done by them, the community has provided some great contributions:

- `Ygor Pontelo <https://github.com/ygorpontelo>`__ added async support to the
  dynamic and hybrid library APIs (`#4803`_) and fixed a bug with handling async
  keywords when the whole execution is stopped gracefully (`#4808`_).

- `Topi 'top1' Tuulensuu <https://github.com/totu>`__ fixed a performance regression
  when using `Run Keyword` so that the name of the executed keyword contains a variable
  (`#4659`_).

- `Robin <https://github.com/robinmackaij>`__ added type hints to modules that
  did not yet have them under the public `robot.api` package (`#4841`_).

- `Mark Moberts <https://github.com/MobyNL>`__ added case-insensitive list and
  dictionary comparison support to the Collections library (`#4343`_).

- `Daniel Biehl <https://github.com/d-biehl>`__ enhanced performance of traversing
  the parsing model using `ModelVisitor` (`#4934`_).

- `René <https://github.com/Snooz82>`__ added return type information to Libdoc's
  HTML output (`#3017`_).

Big thanks to Robot Framework Foundation, to community members listed above, and to
everyone else who has tested preview releases, submitted bug reports, proposed
enhancements, debugged problems, or otherwise helped with Robot Framework 7.0
development.

| `Pekka Klärck`_
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
    * - `#3761`_
      - enhancement
      - critical
      - Native `VAR` syntax to create variables inside tests and keywords
      - alpha 1
    * - `#4294`_
      - enhancement
      - critical
      - Drop Python 3.6 and 3.7 support
      - alpha 1
    * - `#4710`_
      - enhancement
      - critical
      - Support library keywords with both embedded and normal arguments
      - alpha 1
    * - `#4659`_
      - bug
      - high
      - Performance regression when using `Run Keyword` and keyword name contains a variable
      - alpha 1
    * - `#4258`_
      - enhancement
      - high
      - Change timestamps from custom strings to `datetime` in result model and to ISO 8601 format in output.xml
      - alpha 1
    * - `#4374`_
      - enhancement
      - high
      - Support removing tags set globally by using `-tag` syntax with `[Tags]` setting
      - alpha 1
    * - `#4711`_
      - enhancement
      - high
      - Support type aliases in formats `'list[int]'` and `'int | float'` in argument conversion
      - alpha 1
    * - `#4803`_
      - enhancement
      - high
      - Async support to dynamic and hybrid library APIs
      - alpha 2
    * - `#4808`_
      - bug
      - medium
      - Async keywords are not stopped when execution is stopped gracefully
      - alpha 2
    * - `#4859`_
      - bug
      - medium
      - Parsing errors in reStructuredText files have no source
      - alpha 1
    * - `#4880`_
      - bug
      - medium
      - Initially empty test fails even if pre-run modifier adds content to it
      - alpha 1
    * - `#4886`_
      - bug
      - medium
      - `Set Variable If` is slow if it has several conditions
      - alpha 1
    * - `#4898`_
      - bug
      - medium
      - Resolving special variables can fail with confusing message
      - alpha 1
    * - `#4915`_
      - bug
      - medium
      - `cached_property` attributes are called when importing library
      - alpha 1
    * - `#4921`_
      - bug
      - medium
      - Log levels don't work correctly with `robot:flatten`
      - alpha 1
    * - `#4924`_
      - bug
      - medium
      - WHILE `on_limit` missing from listener v2 attributes
      - alpha 1
    * - `#4926`_
      - bug
      - medium
      - WHILE and TRY content are not removed with `--removekeywords all`
      - alpha 1
    * - `#4945`_
      - bug
      - medium
      - `TypedDict` with forward references do not work in argument conversion
      - alpha 2
    * - `#3017`_
      - enhancement
      - medium
      - Add return type to Libdoc specs and HTML output
      - alpha 2
    * - `#4103`_
      - enhancement
      - medium
      - Process: Change the default `stdin` behavior from `subprocess.PIPE` to `None`
      - alpha 1
    * - `#4302`_
      - enhancement
      - medium
      - Remove `Reserved` library
      - alpha 1
    * - `#4343`_
      - enhancement
      - medium
      - Collections. Support case-insensitive comparisons
      - alpha 2
    * - `#4375`_
      - enhancement
      - medium
      - Change token type of `AS` (or `WITH NAME`) used with library imports to `Token.AS`
      - alpha 1
    * - `#4385`_
      - enhancement
      - medium
      - Change the parsing model object produced by `Test Tags` (and `Force Tags`) to `TestTags`
      - alpha 1
    * - `#4432`_
      - enhancement
      - medium
      - Loudly deprecate singular section headers
      - alpha 1
    * - `#4501`_
      - enhancement
      - medium
      - Loudly deprecate old Python 2/3 compatibility layer and other deprecated utils
      - alpha 1
    * - `#4524`_
      - enhancement
      - medium
      - Loudly deprecate variables used as embedded arguments not matching custom patterns
      - alpha 1
    * - `#4545`_
      - enhancement
      - medium
      - Support creating assigned variable name based on another variable like `${${var}} =    Keyword`
      - alpha 1
    * - `#4667`_
      - enhancement
      - medium
      - Remove deprecated constructs from Libdoc spec files
      - alpha 1
    * - `#4685`_
      - enhancement
      - medium
      - Deprecate `SHORTEST` mode being default with `FOR IN ZIP` loops
      - alpha 1
    * - `#4708`_
      - enhancement
      - medium
      - Use `assing`, not `variable`, with FOR and TRY/EXCEPT model objects when referring to assigned variables
      - alpha 1
    * - `#4720`_
      - enhancement
      - medium
      - Require `--suite parent.suite` to match the full suite name
      - alpha 1
    * - `#4721`_
      - enhancement
      - medium
      - Change behavior of `--test` and `--include` so that they are cumulative
      - alpha 1
    * - `#4747`_
      - enhancement
      - medium
      - Support `[Setup]` with user keywords
      - alpha 1
    * - `#4784`_
      - enhancement
      - medium
      - Remote: Enhance `datetime`, `date` and `timedelta` conversion
      - alpha 1
    * - `#4841`_
      - enhancement
      - medium
      - Add typing to all modules under `robot.api`
      - alpha 2
    * - `#4846`_
      - enhancement
      - medium
      - Result model: Loudly deprecate not needed attributes and remove already deprecated ones
      - alpha 1
    * - `#4876`_
      - enhancement
      - medium
      - Loudly deprecate `[Return]` setting
      - alpha 1
    * - `#4883`_
      - enhancement
      - medium
      - Result model: Add `message` to keywords and control structures and remove `doc` from controls
      - alpha 1
    * - `#4884`_
      - enhancement
      - medium
      - Result model: Enhance storing keyword name
      - alpha 1
    * - `#4896`_
      - enhancement
      - medium
      - Support `separator=<value>` configuration option with scalar variables in Variables section
      - alpha 1
    * - `#4903`_
      - enhancement
      - medium
      - Support argument conversion and named arguments with dynamic variable files
      - alpha 1
    * - `#4905`_
      - enhancement
      - medium
      - Support creating variable name based on another variable like `${${VAR}}` in Variables section
      - alpha 1
    * - `#4912`_
      - enhancement
      - medium
      - Parsing model: Move `type` and `tokens` from `_fields` to `_attributes`
      - alpha 1
    * - `#4939`_
      - enhancement
      - medium
      - Parsing model: Rename `Return` to `ReturnSetting` and `ReturnStatement` to `Return`
      - alpha 2
    * - `#4942`_
      - enhancement
      - medium
      - Add public argument conversion API for libraries and other tools
      - alpha 2
    * - `#4952`_
      - enhancement
      - medium
      - Collections: Make `ignore_order` and `ignore_keys` recursive
      - alpha 2
    * - `#4934`_
      - ---
      - medium
      - Enhance performance of visiting parsing model
      - alpha 1
    * - `#4867`_
      - bug
      - low
      - Original order of dictionaries is not preserved when they are pretty printed in log messages
      - alpha 1
    * - `#4870`_
      - bug
      - low
      - User keyword teardown missing from running model JSON schema
      - alpha 1
    * - `#4904`_
      - bug
      - low
      - Importing static variable file with arguments does not fail
      - alpha 1
    * - `#4913`_
      - bug
      - low
      - Trace log level logs arguments twice for embedded arguments
      - alpha 1
    * - `#4927`_
      - bug
      - low
      - WARN level missing from the log level selector in log.html
      - alpha 1
    * - `#4861`_
      - enhancement
      - low
      - Remove deprecated `accept_plain_values` from `timestr_to_secs` utility function
      - alpha 1
    * - `#4862`_
      - enhancement
      - low
      - Deprecate `elapsed_time_to_string` accepting time as milliseconds
      - alpha 1
    * - `#4864`_
      - enhancement
      - low
      - Process: Make warning about processes hanging if output buffers get full more visible
      - alpha 1
    * - `#4885`_
      - enhancement
      - low
      - Add `full_name` to replace `longname` to suite and test objects
      - alpha 1
    * - `#4900`_
      - enhancement
      - low
      - Make keywords and control structures in log look more like original data
      - alpha 1
    * - `#4922`_
      - enhancement
      - low
      - Change the log level of `Set Log Level` message from INFO to DEBUG
      - alpha 1
    * - `#4933`_
      - enhancement
      - low
      - Type conversion: Ignore hyphens when matching enum members
      - alpha 1
    * - `#4935`_
      - enhancement
      - low
      - Use `casefold`, not `lower`, when comparing strings case-insensitively
      - alpha 1
    * - `#4954`_
      - enhancement
      - low
      - Collections and String: Add `ignore_case` as alias for `case_insensitive`
      - alpha 2
    * - `#4936`_
      - enhancement
      - ---
      - Remove bytes support from `normalize` unitility
      - alpha 1

Altogether 63 issues. View on the `issue tracker <https://github.com/robotframework/robotframework/issues?q=milestone%3Av7.0>`__.

.. _#3761: https://github.com/robotframework/robotframework/issues/3761
.. _#4294: https://github.com/robotframework/robotframework/issues/4294
.. _#4710: https://github.com/robotframework/robotframework/issues/4710
.. _#4659: https://github.com/robotframework/robotframework/issues/4659
.. _#4258: https://github.com/robotframework/robotframework/issues/4258
.. _#4374: https://github.com/robotframework/robotframework/issues/4374
.. _#4711: https://github.com/robotframework/robotframework/issues/4711
.. _#4803: https://github.com/robotframework/robotframework/issues/4803
.. _#4808: https://github.com/robotframework/robotframework/issues/4808
.. _#4859: https://github.com/robotframework/robotframework/issues/4859
.. _#4880: https://github.com/robotframework/robotframework/issues/4880
.. _#4886: https://github.com/robotframework/robotframework/issues/4886
.. _#4898: https://github.com/robotframework/robotframework/issues/4898
.. _#4915: https://github.com/robotframework/robotframework/issues/4915
.. _#4921: https://github.com/robotframework/robotframework/issues/4921
.. _#4924: https://github.com/robotframework/robotframework/issues/4924
.. _#4926: https://github.com/robotframework/robotframework/issues/4926
.. _#4945: https://github.com/robotframework/robotframework/issues/4945
.. _#3017: https://github.com/robotframework/robotframework/issues/3017
.. _#4103: https://github.com/robotframework/robotframework/issues/4103
.. _#4302: https://github.com/robotframework/robotframework/issues/4302
.. _#4343: https://github.com/robotframework/robotframework/issues/4343
.. _#4375: https://github.com/robotframework/robotframework/issues/4375
.. _#4385: https://github.com/robotframework/robotframework/issues/4385
.. _#4432: https://github.com/robotframework/robotframework/issues/4432
.. _#4501: https://github.com/robotframework/robotframework/issues/4501
.. _#4524: https://github.com/robotframework/robotframework/issues/4524
.. _#4545: https://github.com/robotframework/robotframework/issues/4545
.. _#4667: https://github.com/robotframework/robotframework/issues/4667
.. _#4685: https://github.com/robotframework/robotframework/issues/4685
.. _#4708: https://github.com/robotframework/robotframework/issues/4708
.. _#4720: https://github.com/robotframework/robotframework/issues/4720
.. _#4721: https://github.com/robotframework/robotframework/issues/4721
.. _#4747: https://github.com/robotframework/robotframework/issues/4747
.. _#4784: https://github.com/robotframework/robotframework/issues/4784
.. _#4841: https://github.com/robotframework/robotframework/issues/4841
.. _#4846: https://github.com/robotframework/robotframework/issues/4846
.. _#4876: https://github.com/robotframework/robotframework/issues/4876
.. _#4883: https://github.com/robotframework/robotframework/issues/4883
.. _#4884: https://github.com/robotframework/robotframework/issues/4884
.. _#4896: https://github.com/robotframework/robotframework/issues/4896
.. _#4903: https://github.com/robotframework/robotframework/issues/4903
.. _#4905: https://github.com/robotframework/robotframework/issues/4905
.. _#4912: https://github.com/robotframework/robotframework/issues/4912
.. _#4939: https://github.com/robotframework/robotframework/issues/4939
.. _#4942: https://github.com/robotframework/robotframework/issues/4942
.. _#4952: https://github.com/robotframework/robotframework/issues/4952
.. _#4934: https://github.com/robotframework/robotframework/issues/4934
.. _#4867: https://github.com/robotframework/robotframework/issues/4867
.. _#4870: https://github.com/robotframework/robotframework/issues/4870
.. _#4904: https://github.com/robotframework/robotframework/issues/4904
.. _#4913: https://github.com/robotframework/robotframework/issues/4913
.. _#4927: https://github.com/robotframework/robotframework/issues/4927
.. _#4861: https://github.com/robotframework/robotframework/issues/4861
.. _#4862: https://github.com/robotframework/robotframework/issues/4862
.. _#4864: https://github.com/robotframework/robotframework/issues/4864
.. _#4885: https://github.com/robotframework/robotframework/issues/4885
.. _#4900: https://github.com/robotframework/robotframework/issues/4900
.. _#4922: https://github.com/robotframework/robotframework/issues/4922
.. _#4933: https://github.com/robotframework/robotframework/issues/4933
.. _#4935: https://github.com/robotframework/robotframework/issues/4935
.. _#4954: https://github.com/robotframework/robotframework/issues/4954
.. _#4936: https://github.com/robotframework/robotframework/issues/4936
