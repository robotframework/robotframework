===========================
Robot Framework 6.1 alpha 1
===========================

.. default-role:: code

`Robot Framework`_ 6.1 is a new feature release with support for converting
Robot Framework data to JSON and back as well as various other interesting
new features both for normal users and for external tool developers.
This first alpha release is especially
targeted for those interested to test JSON serialization. It also contains
all planned `backwards incompatible changes`_ and `deprecated features`_,
so everyone interested to make sure their tests, tasks or tools are compatible,
should test it in their environment.

All issues targeted for Robot Framework 6.1 can be found
from the `issue tracker milestone`_.

Questions and comments related to the release can be sent to the
`robotframework-users`_ mailing list or to `Robot Framework Slack`_,
and possible bugs submitted to the `issue tracker`_.

If you have pip_ installed, just run

::

   pip install --pre --upgrade robotframework

to install the latest available release or use

::

   pip install robotframework==6.1a1

to install exactly this version. Alternatively you can download the source
distribution from PyPI_ and install it manually. For more details and other
installation approaches, see the `installation instructions`_.

Robot Framework 6.1 alpha 1 was released on Friday March 17, 2023.

.. _Robot Framework: http://robotframework.org
.. _Robot Framework Foundation: http://robotframework.org/foundation
.. _pip: http://pip-installer.org
.. _PyPI: https://pypi.python.org/pypi/robotframework
.. _issue tracker milestone: https://github.com/robotframework/robotframework/issues?q=milestone%3Av6.1
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

JSON data format
----------------

The biggest new feature in Robot Framework 6.1 is the possibility to convert
test/task data to JSON and back (`#3902`_). This functionality has three main
use cases:

- Transferring suites between processes and machines. A suite can be converted
  to JSON in one machine and recreated somewhere else.
- Possibility to save a suite, possible a nested suite, constructed from data
  on the file system into a single file that is faster to parse.
- Alternative data format for external tools generating tests or tasks.

This feature is designed more for tool developers than for regular Robot Framework
users and we expect new interesting tools to emerge in the future. The feature
is not finalized yet, but the following things already work:

1. You can serialize a suite structure into JSON by using `TestSuite.to_json`__
   method. When used without arguments, it returns JSON data as a string, but
   it also accepts a path or an open file where to write JSON data along with
   configuration options related to JSON formatting:

   .. code:: python

      from robot.api import TestSuite

      suite = TestSuite.from_file_system('path/to/tests')
      suite.to_json('tests.rbt')

2. You can create a suite based on JSON data using `TestSuite.from_json`__.
   It works both with JSON strings and paths to JSON files:

   .. code:: python

      from robot.api import TestSuite

      suite = TestSuite.from_json('tests.rbt')

3. When using the `robot` command normally, JSON files with the `.rbt` extension
   are parsed automatically. This includes running individual JSON files like
   `robot tests.rbt` and running directories containing `.rbt` files.

We recommend everyone interested in this new functionality to test it and give
us feedback. It is a lot easier for us to make changes before the final release
is out and we need to take backwards compatibility into account. If you
encounter bugs or have enhancement ideas, you can comment the issue or start
discussion on the `#devel` channel on our Slack_.

__ https://robot-framework.readthedocs.io/en/latest/autodoc/robot.running.html#robot.running.model.TestSuite.to_json
__ https://robot-framework.readthedocs.io/en/latest/autodoc/robot.running.html#robot.running.model.TestSuite.from_json

User keywords with both embedded and normal arguments
-----------------------------------------------------

User keywords can nowadays mix embedded arguments and normal arguments (`#4234`_).
For example, this kind of usage is possible:

.. code:: robotframework

   *** Test Cases ***
   Example
       Number of horses is    2
       Number of dogs is      3

   *** Keywords ***
   Number of ${animals} is
       [Arguments]    ${count}
       Log to console    There are ${count} ${animals}.

This only works with user keywords at least for now. If there is interest,
the support can be extended to library keywords in future releases.

Possibility to flatten keyword structures during execution
----------------------------------------------------------

With nested keyword structures, especially with recursive keyword calls and with
WHILE and FOR loops, the log file can get hard do understand with many different
nesting levels. Such nested structures also increase the size of the output.xml
file. For example, even a simple keyword like:

.. code:: robotframework

    *** Keywords ***
    Keyword
        Log    Robot
        Log    Framework

creates this much content in output.xml:

.. code:: xml

    <kw name="Keyword">
      <kw name="Log" library="BuiltIn">
        <arg>Robot</arg>
        <doc>Logs the given message with the given level.</doc>
        <msg timestamp="20230103 20:06:36.663" level="INFO">Robot</msg>
        <status status="PASS" starttime="20230103 20:06:36.663" endtime="20230103 20:06:36.663"/>
      </kw>
      <kw name="Log" library="BuiltIn">
        <arg>Framework</arg>
        <doc>Logs the given message with the given level.</doc>
        <msg timestamp="20230103 20:06:36.663" level="INFO">Framework</msg>
        <status status="PASS" starttime="20230103 20:06:36.663" endtime="20230103 20:06:36.664"/>
      </kw>
      <status status="PASS" starttime="20230103 20:06:36.663" endtime="20230103 20:06:36.664"/>
    </kw>

We already have the `--flattenkeywords` option for "flattening" such structures
and it works great. When a keyword is flattened, its child keywords and control
structures are removed otherwise, but all their messages (`<msg>` elements) are
preserved. Using `--flattenkeywords` does not affect output.xml generated during
execution, but flattening happens when output.xml files are parsed and can save
huge amounts of memory. When `--flattenkeywords` is used with Rebot, it is
possible to create a new flattened output.xml. For example, the above structure
is converted into this if `Keyword` is flattened using `--flattenkeywords`:

.. code:: xml

    <kw name="Keyword">
      <doc>_*Content flattened.*_</doc>
      <msg timestamp="20230103 20:06:36.663" level="INFO">Robot</msg>
      <msg timestamp="20230103 20:06:36.663" level="INFO">Framework</msg>
      <status status="PASS" starttime="20230103 20:06:36.663" endtime="20230103 20:06:36.664"/>
    </kw>

Starting from Robot Framework 6.1, this kind of flattening can be done also
during execution and without using command line options. The only thing needed
is using the new keyword tag `robot:flatten` (`#4584`_) and Robot handles
flattening automatically. For example, if the earlier `Keyword` is changed
to:

.. code:: robotframework

    *** Keywords ***
    Keyword
        [Tags]    robot:flatten
        Log    Robot
        Log    Framework

the result in output.xml will be this:

.. code:: xml

    <kw name="Keyword">
      <tag>robot:flatten</tag>
      <msg timestamp="20230317 00:54:34.772" level="INFO">Robot</msg>
      <msg timestamp="20230317 00:54:34.772" level="INFO">Framework</msg>
      <status status="PASS" starttime="20230317 00:54:34.771" endtime="20230317 00:54:34.772"/>
    </kw>

The main benefit of using `robot:flatten` instead of `--flattenkeywords` is that
it is used already during execution making the resulting output.xml file
smaller. `--flattenkeywords` has more configuration options than `robot:flatten`,
though, but `robot:flatten` can be enhanced in that regard later if there are
needs.

Custom argument converters can access library
---------------------------------------------

Support for custom argument converters was added in Robot Framework 5.0
(`#4088`__) and they have turned out to be really useful. This functionality
is now enhanced so, that converters can easily get an access to the
library containing the keyword that is used, and can thus do conversion
based on the library state (`#4510`_). This can be done simply by creating
a converter that accepts two values. The first value is the value used in
the data, exactly as earlier, and the second is the library instance or module:

.. code:: python

    def converter(value, library):
        ...

Converters accepting only one argument keep working as earlier. There are no
plans to require changing them to accept two values.

__ https://github.com/robotframework/robotframework/issues/4088

JSON variable file support
--------------------------

It has been possible to create variable files using YAML in addition to Python
for long time, and nowadays also JSON variable files are supported (`#4532`_).
For example, a JSON file containing:

.. code:: json

    {
        "STRING": "Hello, world!",
        "INTEGER": 42
    }

could be used like this:

.. code:: robotframework

    *** Settings ***
    Variables        example.json

    *** Test Cases ***
    Example
        Should Be Equal    ${STRING}     Hello, world!
        Should Be Equal    ${INTEGER}    ${42}

New pseudo log level `CONSOLE`
------------------------------

There are often needs to log something to the console while tests or tasks
are running. Some keywords support it out-of-the-box and there is also
separate `Log To Console` keyword for that purpose.

The new `CONSOLE` pseudo log level (`#4536`_) adds this support to *any*
keyword that accepts a log level such as `Log List` in Collections and
`Page Should Contain` in SeleniumLibrary. When this level is used, the message
is logged both to the console and on `INFO` level to the log file.

Configuring virtual root suite when running multiple suites
-----------------------------------------------------------

When execution multiple suites like `robot first.robot second.robot`,
Robot Framework creates a virtual root suite containing the executed
suites as child suites. Earlier this virtual suite could be
configured only by using command line options like `--name`, but now
it is possible to use normal suite initialization files (`__init__.robot`)
for that purpose (`#4015`_). If an initialization file is included
in the call like::

    robot __init__.robot first.robot second.robot`

the root suite is configured based on data it contains.

The most important feature this enhancement allows is specifying suite
setup and teardown to the root suite. Earlier that was not possible at all.

`FOR IN ZIP` loop behavior if lists lengths differ can be configured
--------------------------------------------------------------------

Robot Framework's `FOR IN ZIP` loop behaves like Python's zip__ function so
that if lists lengths are not the same, items from longer ones are ignored.
For example, the following loop would be executed only twice:

.. code:: robotframework

    *** Variables ***
    @{ANIMALS}    dog      cat    horse    cow    elephant
    @{ELÄIMET}    koira    kissa

    *** Test Cases ***
    Example
        FOR    ${en}    ${fi}    IN ZIP    ${ANIMALS}    ${ELÄIMET}
            Log    ${en} is ${fi} in Finnish
        END

This behavior can cause problems when iterating over items received from
the automated system. For example, the following test would pass regardless
how many things `Get something` returns as long as the returned items match
the expected values. The example succeeds if `Get something` returns ten items
if three first ones match. What's even worse, it succeeds also if `Get something`
returns nothing.

.. code:: robotframework

    *** Test Cases ***
    Example
        Validate something    expected 1    expected 2    expected 3

    *** Keywords ****
    Validate something
        [Arguments]    @{expected}
        @{actual} =    Get something
        FOR    ${act}    ${exp}    IN ZIP    ${actual}    ${expected}
            Validate one thing    ${act}    ${exp}
        END

This situation is pretty bad because it can cause false positives where
automation succeeds but nothing is actually done. Python itself has this
same issue, and Python 3.10 added new optional `strict` argument to `zip`
(`PEP 681`__). In addition to that, Python has for long time had a separate
`zip_longest`__ function that loops over all values possibly filling-in
values to shorter lists.

To support the same features as Python, Robot Framework's `FOR IN ZIP`
loops now have an optional `mode` configuration option that accepts three
values (`#4682`_):

- `STRICT`: Lists must have equal lengths. If not, execution fails. This is
  the same as using `strict=True` with Python's `zip` function.
- `SHORTEST`: Items in longer lists are ignored. Infinitely long lists are supported
  in this mode as long as one of the lists is exhausted. This is the current
  default behavior.
- `LONGEST`: The longest list defines how many iterations there are. Missing
  values in shorter lists are filled-in with value specified using the `fill`
  option or `None` if it is not used. This is the same as using Python's
  `zip_longest` function except that it has `fillvalue` argument instead of
  `fill`.

All these modes are illustrated by the following examples:

.. code:: robotframework

   *** Variables ***
   @{CHARACTERS}     a    b    c    d    f
   @{NUMBERS}        1    2    3

   *** Test Cases ***
   STRICT mode
       [Documentation]    This loop fails due to lists lengths being different.
       FOR    ${c}    ${n}    IN ZIP    ${CHARACTERS}    ${NUMBERS}    mode=STRICT
           Log    ${c}: ${n}
       END

   SHORTEST mode
       [Documentation]    This loop executes three times.
       FOR    ${c}    ${n}    IN ZIP    ${CHARACTERS}    ${NUMBERS}    mode=SHORTEST
           Log    ${c}: ${n}
       END

   LONGEST mode
       [Documentation]    This loop executes five times.
       ...                On last two rounds `${n}` has value `None`.
       FOR    ${c}    ${n}    IN ZIP    ${CHARACTERS}    ${NUMBERS}    mode=LONGEST
           Log    ${c}: ${n}
       END

   LONGEST mode with custom fill value
       [Documentation]    This loop executes five times.
       ...                On last two rounds `${n}` has value `-`.
       FOR    ${c}    ${n}    IN ZIP    ${CHARACTERS}    ${NUMBERS}    mode=LONGEST    fill=-
           Log    ${c}: ${n}
       END

This enhancement makes it easy to activate strict validation and avoid
false positives. The default behavior is still problematic, though, and
the plan is to change it to `STRICT` in `Robot Framework 7.0`__.
Those who want to keep using the `SHORTEST` mode need to enable it explicitly

__ https://docs.python.org/3/library/functions.html#zip
__ https://peps.python.org/pep-0618/
__ https://docs.python.org/3/library/itertools.html#itertools.zip_longest
__ https://github.com/robotframework/robotframework/issues/4686

Backwards incompatible changes
==============================

We try to avoid backwards incompatible changes in general and especially in
non-major version. They cannot always be avoided, though, and there are some
features and fixes in this release that are not fully backwards compatible.
These changes *should not* cause problems in normal usage, but especially
tools using Robot Framework may nevertheless be affected.

Changes to output.xml
---------------------

Syntax errors such as invalid settings like `[Setpu]` or `END` in a wrong place
are nowadays reported better (`#4683`_). Part of that change was storing
invalid constructs in output.xml as `<error>` elements. Tools processing
output.xml files so that they go through all elements need to take `<error>`
elements into account, but tools just querying information using xpath
expression or otherwise should not be affected.

Another change is that with `FOR IN ENUMERATE` loops the `<for>` element
may get `start` attribute (`#4684`_) and with `FOR IN ZIP` loops it may get
`mode` and `fill` attributes (`#4682`_). This affects tools processing
all possible attributes, but such tools ought to be very rare.

Changes to `TestSuite` model structure
--------------------------------------

The aforementioned enhancements for handling invalid syntax better (`#4683`_)
required changes also to the TestSuite__ model structure. Syntax errors are
nowadays represented as Error__ objects and they can appear in the `body` of
TestCase__, Keyword__, and other such model objects. Tools interacting with
the `TestSuite` structure should take `Error` objects into account, but tools
using the `visitor API`__ should in general not be affected.

Another related change is that `doc`, `tags`, `timeout` and `teardown` attributes
were removed from the `robot.running.Keyword`__ object (`#4589`_). They were
left there accidentally and were not used for anything by Robot Framework.
Tools accessing them need to be updated.

Finally, the `TestSuite.source`__ attribute is nowadays a `pathlib.Path`__
instance instead of a string (`#4596`_).

__ https://robot-framework.readthedocs.io/en/latest/autodoc/robot.model.html#robot.model.testsuite.TestSuite
__ https://robot-framework.readthedocs.io/en/latest/autodoc/robot.model.html#robot.model.control.Error
__ https://robot-framework.readthedocs.io/en/latest/autodoc/robot.model.html#robot.model.testcase.TestCase
__ https://robot-framework.readthedocs.io/en/latest/autodoc/robot.model.html#robot.model.keyword.Keyword
__ https://robot-framework.readthedocs.io/en/latest/autodoc/robot.model.html#module-robot.model.visitor
__ https://robot-framework.readthedocs.io/en/latest/autodoc/robot.running.html#robot.running.model.Keyword
__ https://robot-framework.readthedocs.io/en/latest/autodoc/robot.model.html#robot.model.testsuite.TestSuite.source
__ https://docs.python.org/3/library/pathlib.html

Changes to parsing model
------------------------

Invalid section headers like `*** Bad ***` are nowadays represented in the
parsing model as InvalidSection__ objects when they earlier were generic
Error__ objects (`#4689`_).

New ReturnSetting__ object has been introduced as an alias for Return__.
This does not yet change anything, but in the future `Return` will be used
for other purposes tools using it should be updated to use `ReturnSetting`
instead (`#4656`_).

__ https://robot-framework.readthedocs.io/en/latest/autodoc/robot.parsing.model.html#robot.parsing.model.blocks.InvalidSection
__ https://robot-framework.readthedocs.io/en/latest/autodoc/robot.parsing.model.html#robot.parsing.model.statements.Error
__ https://robot-framework.readthedocs.io/en/latest/autodoc/robot.parsing.model.html#robot.parsing.model.statements.Return
__ https://robot-framework.readthedocs.io/en/latest/autodoc/robot.parsing.model.html#robot.parsing.model.statements.ReturnSetting

Changes to Libdoc spec files
----------------------------

Libdoc did not handle parameterized types like `list[int]` properly earlier.
Fixing that problem required storing information about nested types into
the spec files along with the top level type. In addition to the parameterized
types, also unions are now handled differently than earlier, but with normal
types there are no changes. With JSON spec files changes were pretty small,
but XML spec files required a bit bigger changes. What exactly was changed
and how is explained in comments of issue `#4538`_.

Argument conversion changes
---------------------------

If an argument has multiple types, Robot Framework tries to do argument
conversion with all of them, from left to right, until one of them succeeds.
Earlier if a type was not recognized at all, the used value was returned
as-is without trying conversion with the remaining types. For example, if
a keyword like:

.. code:: python

    def example(arg: Union[UnknownType, int]):
        ...

would be called like::

    Example    42

the integer conversion would not be attempted and the keyword would get
string `42`. This was changed so that unrecognized types are just skipped
and in the above case integer conversion is nowadays done (`#4648`_). That
obviously changes the value the keyword gets to an integer.

Another argument conversion change is that the `Any` type is now recognized
so that any value is accepted without conversion (`#4647`_). This change is
mostly backwards compatible, but in a special case where such an argument has
a default value like `arg: Any = 1` the behavior changes. Earlier when `Any`
was not recognized at all, conversion was attempted based on the default value
type. Nowadays when `Any` is recognized and explicitly not converted,
no conversion based on the default value is done either. The behavior change
can be avoided by using `arg: Union[int, Any] = 1` which is much better
typing in general.

Changes affecting execution
---------------------------

Invalid settings in tests and keywords like `[Tasg]` are nowadays considered
syntax errors that cause failures at execution time (`#4683`_). They were
reported also earlier, but they did not affect execution.

All invalid sections in resource files are considered to be syntax errors that
prevent importing the resource file (`#4689`_). Earlier having a `*** Test Cases ***`
header in a resource file caused such an error, but other invalid headers were
just reported as errors but imports succeeded.

Deprecated features
===================

Python 3.7 support
------------------

Python 3.7 will reach its end-of-life in `June 2023`__. We have decided to
support it with Robot Framework 6.1 and subsequent 6.x releases, but
Robot Framework 7.0 will not support it anymore (`#4637`_).

We have already earlier deprecated Python 3.6 that reached its end-of-life
already in `December 2021`__ the same way. The reason we still support it
is that it is the default Python version in Red Hat Enterprise Linux 8
that is still `actively supported`__.

__ https://peps.python.org/pep-0537/
__ https://peps.python.org/pep-0494/
__ https://endoflife.date/rhel

Old elements in Libdoc spec files
---------------------------------

Libdoc spec files have been enhanced in latest releases. For backwards
compatibility reasons old information has been preserved, but all such data
will be removed in Robot Framework 7.0. For more details about what will be
removed see issue `#4667`__.

__ https://github.com/robotframework/robotframework/issues/4667

Other deprecated features
-------------------------

- Return__ node in the parsing model has been deprecated and ReturnSetting__
  should be used instead (`#4656`_).
- `name` argument of `TestSuite.from_model`__ has been deprecated and will be
  removed in the future (`#4598`_).
- `accept_plain_values` argument of `robot.utils.timestr_to_secs` has been
  deprecated and will be removed in the future (`#4522`_).

__ https://robot-framework.readthedocs.io/en/latest/autodoc/robot.running.html#robot.running.model.TestSuite.from_model
__ https://robot-framework.readthedocs.io/en/latest/autodoc/robot.parsing.model.html#robot.parsing.model.statements.Return
__ https://robot-framework.readthedocs.io/en/latest/autodoc/robot.parsing.model.html#robot.parsing.model.statements.ReturnSetting

Acknowledgements
================

Robot Framework development is sponsored by the `Robot Framework Foundation`_
and its ~50 member organizations. If your organization is using Robot Framework
and benefiting from it, consider joining the foundation to support its
development as well.

Robot Framework 6.1 team funded by the foundation consists of
`Pekka Klärck <https://github.com/pekkaklarck>`_ and
`Janne Härkönen <https://github.com/yanne>`_ (part time).
In addition to that, the community has provided great contributions:

- `@sunday2 <https://github.com/sunday2>`__ implemented JSON variable file support
  (`#4532`_) and fixed User Guide generation on Windows (`#4680`_).

- `@turunenm <https://github.com/turunenm>`__ implemented `CONSOLE` pseudo log level
  (`#4536`_).

- `@Vincema <https://github.com/Vincema>`__ added support for long command line
  options with hyphens like `--pre-run-modifier` (`#4547`_).

There are several pull requests still in the pipeline to be accepted before
Robot Framework 6.1 final is released. If there is something you would like
to see in the release, there is still a little time to get it included.

Big thanks to Robot Framework Foundation for the continued support, to community
members listed above for their valuable contributions, and to everyone else who
has submitted bug reports, proposed enhancements, debugged problems, or otherwise
helped to make Robot Framework 6.1 such a great release!

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
    * - `#3902`_
      - enhancement
      - critical
      - Support serializing executable suite into JSON
      - alpha 1
    * - `#4234`_
      - enhancement
      - critical
      - Support user keywords with both embedded and normal arguments
      - alpha 1
    * - `#4015`_
      - enhancement
      - high
      - Support configuring virtual suite created when running multiple suites with `__init__.robot`
      - alpha 1
    * - `#4510`_
      - enhancement
      - high
      - Make it possible for custom converters to get access to the library
      - alpha 1
    * - `#4532`_
      - enhancement
      - high
      - JSON variable file support
      - alpha 1
    * - `#4536`_
      - enhancement
      - high
      - Add new pseudo log level `CONSOLE` that logs to console and to log file
      - alpha 1
    * - `#4584`_
      - enhancement
      - high
      - New `robot:flatten` tag for "flattening" keyword structures
      - alpha 1
    * - `#4637`_
      - enhancement
      - high
      - Deprecate Python 3.7
      - alpha 1
    * - `#4682`_
      - enhancement
      - high
      - Make `FOR IN ZIP` loop behavior if lists have different lengths configurable
      - alpha 1
    * - `#4538`_
      - bug
      - medium
      - Libdoc doesn't handle parameterized types like `list[int]` properly
      - alpha 1
    * - `#4571`_
      - bug
      - medium
      - Suite setup and teardown are executed even if all tests are skipped
      - alpha 1
    * - `#4589`_
      - bug
      - medium
      - Remove unused attributes from `robot.running.Keyword` model object
      - alpha 1
    * - `#4604`_
      - bug
      - medium
      - Listeners do not get source information for keywords executed with `Run Keyword`
      - alpha 1
    * - `#4626`_
      - bug
      - medium
      - Inconsistent argument conversion when using `None` as default value with Python 3.11 and earlier
      - alpha 1
    * - `#4635`_
      - bug
      - medium
      - Dialogs created by `Dialogs` on Windows don't have focus
      - alpha 1
    * - `#4648`_
      - bug
      - medium
      - Argument conversion should be attempted with all possible types even if some type wouldn't be recognized
      - alpha 1
    * - `#4680`_
      - bug
      - medium
      - User Guide generation broken on Windows
      - alpha 1
    * - `#4689`_
      - bug
      - medium
      - Invalid sections are not represented properly in parsing model
      - alpha 1
    * - `#4692`_
      - bug
      - medium
      - `ELSE IF` condition not passed to listeners
      - alpha 1
    * - `#4210`_
      - enhancement
      - medium
      - Enhance error detection at parsing time
      - alpha 1
    * - `#4547`_
      - enhancement
      - medium
      - Support long command line options with hyphens like `--pre-run-modifier`
      - alpha 1
    * - `#4567`_
      - enhancement
      - medium
      - Add optional typed base class for dynamic library API
      - alpha 1
    * - `#4568`_
      - enhancement
      - medium
      - Add optional typed base classes for listener API
      - alpha 1
    * - `#4569`_
      - enhancement
      - medium
      - Add type information to the visitor API
      - alpha 1
    * - `#4601`_
      - enhancement
      - medium
      - Add `robot.running.TestSuite.from_string` method
      - alpha 1
    * - `#4647`_
      - enhancement
      - medium
      - Add explicit argument converter for `Any` that does no conversion
      - alpha 1
    * - `#4666`_
      - enhancement
      - medium
      - Add public API to query is Robot running and is dry-run active
      - alpha 1
    * - `#4676`_
      - enhancement
      - medium
      - Propose using `$var` syntax if evaluation IF or WHILE condition using `${var}` fails
      - alpha 1
    * - `#4683`_
      - enhancement
      - medium
      - Report syntax errors better in log file
      - alpha 1
    * - `#4684`_
      - enhancement
      - medium
      - Handle start index with `FOR IN ENUMERATE` loops already in parser
      - alpha 1
    * - `#4611`_
      - bug
      - low
      - Some unit tests cannot be run independently
      - alpha 1
    * - `#4634`_
      - bug
      - low
      - Dialogs created by `Dialogs` are not centered and their minimum size is too small
      - alpha 1
    * - `#4638`_
      - bug
      - low
      - (:lady_beetle:) Using bare `Union` as annotation is not handled properly
      - alpha 1
    * - `#4646`_
      - bug
      - low
      - (🐞) Bad error message when function is annotated with an empty tuple `()`
      - alpha 1
    * - `#4663`_
      - bug
      - low
      - `BuiltIn.Log` documentation contains a defect
      - alpha 1
    * - `#4522`_
      - enhancement
      - low
      - Deprecate `accept_plain_values` argument used by `timestr_to_secs`
      - alpha 1
    * - `#4596`_
      - enhancement
      - low
      - Make `TestSuite.source` attribute `pathlib.Path` instance
      - alpha 1
    * - `#4598`_
      - enhancement
      - low
      - Deprecate `name` argument of `TestSuite.from_model`
      - alpha 1
    * - `#4619`_
      - enhancement
      - low
      - Dialogs created by `Dialogs` should bind `Enter` key to `OK` button
      - alpha 1
    * - `#4636`_
      - enhancement
      - low
      - Buttons in dialogs created by `Dialogs` should get keyboard shortcuts
      - alpha 1
    * - `#4656`_
      - enhancement
      - low
      - Deprecate `Return` node in parsing model
      - alpha 1

Altogether 41 issues. View on the `issue tracker <https://github.com/robotframework/robotframework/issues?q=milestone%3Av6.1>`__.

.. _#3902: https://github.com/robotframework/robotframework/issues/3902
.. _#4234: https://github.com/robotframework/robotframework/issues/4234
.. _#4015: https://github.com/robotframework/robotframework/issues/4015
.. _#4510: https://github.com/robotframework/robotframework/issues/4510
.. _#4532: https://github.com/robotframework/robotframework/issues/4532
.. _#4536: https://github.com/robotframework/robotframework/issues/4536
.. _#4584: https://github.com/robotframework/robotframework/issues/4584
.. _#4637: https://github.com/robotframework/robotframework/issues/4637
.. _#4682: https://github.com/robotframework/robotframework/issues/4682
.. _#4538: https://github.com/robotframework/robotframework/issues/4538
.. _#4571: https://github.com/robotframework/robotframework/issues/4571
.. _#4589: https://github.com/robotframework/robotframework/issues/4589
.. _#4604: https://github.com/robotframework/robotframework/issues/4604
.. _#4626: https://github.com/robotframework/robotframework/issues/4626
.. _#4635: https://github.com/robotframework/robotframework/issues/4635
.. _#4648: https://github.com/robotframework/robotframework/issues/4648
.. _#4680: https://github.com/robotframework/robotframework/issues/4680
.. _#4689: https://github.com/robotframework/robotframework/issues/4689
.. _#4692: https://github.com/robotframework/robotframework/issues/4692
.. _#4210: https://github.com/robotframework/robotframework/issues/4210
.. _#4547: https://github.com/robotframework/robotframework/issues/4547
.. _#4567: https://github.com/robotframework/robotframework/issues/4567
.. _#4568: https://github.com/robotframework/robotframework/issues/4568
.. _#4569: https://github.com/robotframework/robotframework/issues/4569
.. _#4601: https://github.com/robotframework/robotframework/issues/4601
.. _#4647: https://github.com/robotframework/robotframework/issues/4647
.. _#4666: https://github.com/robotframework/robotframework/issues/4666
.. _#4676: https://github.com/robotframework/robotframework/issues/4676
.. _#4683: https://github.com/robotframework/robotframework/issues/4683
.. _#4684: https://github.com/robotframework/robotframework/issues/4684
.. _#4611: https://github.com/robotframework/robotframework/issues/4611
.. _#4634: https://github.com/robotframework/robotframework/issues/4634
.. _#4638: https://github.com/robotframework/robotframework/issues/4638
.. _#4646: https://github.com/robotframework/robotframework/issues/4646
.. _#4663: https://github.com/robotframework/robotframework/issues/4663
.. _#4522: https://github.com/robotframework/robotframework/issues/4522
.. _#4596: https://github.com/robotframework/robotframework/issues/4596
.. _#4598: https://github.com/robotframework/robotframework/issues/4598
.. _#4619: https://github.com/robotframework/robotframework/issues/4619
.. _#4636: https://github.com/robotframework/robotframework/issues/4636
.. _#4656: https://github.com/robotframework/robotframework/issues/4656
