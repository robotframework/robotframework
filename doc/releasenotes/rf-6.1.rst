===================
Robot Framework 6.1
===================

.. default-role:: code

`Robot Framework`_ 6.1 is a new feature release with support for converting
Robot Framework data to JSON and back, a new external parser API, possibility
to mix embedded and normal arguments, and various other interesting new features
both for normal users and for external tool developers.

Questions and comments related to the release can be sent to the
`robotframework-users`_ mailing list or to `Robot Framework Slack`_,
and possible bugs submitted to the `issue tracker`_.

If you have pip_ installed, just run

::

   pip install --upgrade robotframework

to install the latest available release or use

::

   pip install robotframework==6.1

to install exactly this version. Alternatively you can download the source
distribution from PyPI_ and install it manually. For more details and other
installation approaches, see the `installation instructions`_.

Robot Framework 6.1 was released on Monday June 12, 2023.
It was superseded by `Robot Framework 6.1.1 <rf-6.1.1.rst>`_.

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

- Transferring data between processes and machines. A suite can be converted
  to JSON in one machine and recreated somewhere else.
- Saving a suite, possibly a nested suite, constructed from normal Robot Framework
  data into a single JSON file that is faster to parse.
- Alternative data format for external tools generating tests or tasks.

This feature is designed more for tool developers than for regular Robot Framework
users and we expect new interesting tools to emerge in the future. The main
functionalities are explained below:

1. You can serialize a suite structure into JSON by using `TestSuite.to_json`__
   method. When used without arguments, it returns JSON data as a string, but
   it also accepts a path or an open file where to write JSON data along with
   configuration options related to JSON formatting:

   .. code:: python

      from robot.running import TestSuite

      # Construct suite based on data on the file system.
      suite = TestSuite.from_file_system('/path/to/data')

      # Get JSON data as a string.
      data = suite.to_json()

      # Save JSON data to a file with custom indentation.
      suite.to_json('data.rbt', indent=2)

   If you would rather work with Python data and then convert that to JSON
   or some other format yourself, you can use `TestSuite.to_dict`__ instead.

2. You can create a suite based on JSON data using `TestSuite.from_json`__.
   It works both with JSON strings and paths to JSON files:

   .. code:: python

      from robot.running import TestSuite

      # Create suite from JSON data in a file.
      suite = TestSuite.from_json('data.rbt')

      # Create suite from a JSON string.
      suite = TestSuite.from_json('{"name": "Suite", "tests": [{"name": "Test"}]}')

   If you have data as a Python dictionary, you can use `TestSuite.from_dict`__
   instead.

3. When executing tests or tasks using the `robot` command, JSON files with
   the custom `.rbt` extension are parsed automatically. This includes running
   individual JSON files like `robot tests.rbt` and running directories
   containing `.rbt` files.

Suite source information in the data got from `TestSuite.to_json` and
`TestSuite.to_dict` is in absolute format. If a suite is recreated later on
a different machine, the source may thus not match the directory structure on
that machine. To avoid such problems, it is possible to use the new
`TestSuite.adjust_source`__ method to make the suite source relative
before getting the data and add a correct root directory after the suite is
recreated:

.. code:: python

   from robot.running import TestSuite

   # Create a suite, adjust source and convert to JSON.
   suite = TestSuite.from_file_system('/path/to/data')
   suite.adjust_source(relative_to='/path/to')
   suite.to_json('data.rbt')

   # Recreate suite elsewhere and adjust source accordingly.
   suite = TestSuite.from_json('data.rbt')
   suite.adjust_source(root='/new/path/to')

Ths JSON serialization support can be enhanced in future Robot Framework versions.
If you have an enhancement idea or believe you have encountered a bug,
please submit an issue or start a discussion thread on the `#devel` channel
on our Slack_.

The JSON data format is documented using the `running.json` `schema file`__.

__ https://robot-framework.readthedocs.io/en/latest/autodoc/robot.running.html#robot.running.model.TestSuite.to_json
__ https://robot-framework.readthedocs.io/en/latest/autodoc/robot.running.html#robot.running.model.TestSuite.to_dict
__ https://robot-framework.readthedocs.io/en/latest/autodoc/robot.running.html#robot.running.model.TestSuite.from_json
__ https://robot-framework.readthedocs.io/en/latest/autodoc/robot.running.html#robot.running.model.TestSuite.from_dict
__ https://robot-framework.readthedocs.io/en/latest/autodoc/robot.running.html#robot.running.model.TestSuite.adjust_source
__ https://github.com/robotframework/robotframework/tree/master/doc/schema#readme

External parser API
-------------------

The parser API is another important new interface targeted for tool developers
(`#1283`_). It makes it possible to create custom parsers that can handle their
own data formats or even override Robot Framework's own parser.

Parsers are taken into use from the command line using the new `--parser` option
the same way as, for example, listeners. This includes specifying parsers as
names or paths, giving arguments to parser classes, and so on::

    robot --parser MyParser tests.custom
    robot --parser path/to/MyParser.py tests.custom
    robot --parser Parser1:arg --parser Parser2:a1:a2 path/to/tests

In simple cases parsers can be implemented as modules. They only thing they
need is an `EXTENSION` or `extension` attribute that specifies the extension
or extensions they support, and a `parse` method that gets the path of the
source file to parse as an argument:

.. code:: python

    from robot.api import TestSuite

    EXTENSION = '.example'

    def parse(source):
        suite = TestSuite(name='Example', source=source)
        test = suite.tests.create(name='Test')
        test.body.create_keyword(name='Log', args=['Hello!'])
        return suite

As the example demonstrates, the `parse` method must return a TestSuite__
instance. In the above example the suite contains only some dummy data and
the source file is not actually parsed.

__ https://robot-framework.readthedocs.io/en/latest/autodoc/robot.running.html#robot.running.model.TestSuite

Parsers can also be implemented as classes which makes it possible for them to
preserve state and allows passing arguments from the command like. The following
example illustrates that and, unlike the previous example, actually processes the
source file:

.. code:: python

    from pathlib import Path
    from robot.api import TestSuite


    class ExampleParser:

        def __init__(self, extension: str):
            self.extension = extension

        def parse(self, source: Path) -> TestSuite:
            suite = TestSuite(TestSuite.name_from_source(source), source=source)
            for line in source.read_text().splitlines():
                test = suite.tests.create(name=line)
                test.body.create_keyword(name='Log', args=['Hello!'])
            return suite

As the earlier examples have demonstrated, parsers do not need to extend any
explicit base class or interface. There is, however, an optional Parser__
base class that can be extended. The following example
does that and has also two other differences compared to earlier examples:

__ https://robot-framework.readthedocs.io/en/latest/autodoc/robot.api.html#robot.api.interfaces.Parser

- The parser has optional `parse_init` file for parsing suite initialization files.
- Both `parse` and `parse_init` accept optional `defaults` argument. When this
  second argument is present, the `parse` method gets a TestDefaults__ instance
  that contains possible test related default values (setup, teardown, tags and
  timeout) from initialization files. Also `parse_init` can get it and possible
  changes are seen by subsequently called `parse` methods.

__ https://robot-framework.readthedocs.io/en/latest/autodoc/robot.running.builder.html#robot.running.builder.settings.TestDefaults

.. code:: python

    from pathlib import Path
    from robot.api import TestSuite
    from robot.api.interfaces import Parser, TestDefaults


    class ExampleParser(Parser):
        extension = ('example', 'another')

        def parse(self, source: Path, defaults: TestDefaults) -> TestSuite:
            """Create a suite and set possible defaults from init files to tests."""
            suite = TestSuite(TestSuite.name_from_source(source), source=source)
            for line in source.read_text().splitlines():
                test = suite.tests.create(name=line, doc='Example')
                test.body.create_keyword(name='Log', args=['Hello!'])
                defaults.set_to(test)
            return suite

        def parse_init(self, source: Path, defaults: TestDefaults) -> TestSuite:
            """Create a dummy suite and set some defaults.

            This method is called only if there is an initialization file with
            a supported extension.
            """
            defaults.tags = ('tags', 'from init')
            defaults.setup = {'name': 'Log', 'args': ['Hello from init!']}
            return TestSuite(TestSuite.name_from_source(source.parent), doc='Example',
                             source=source, metadata={'Example': 'Value'})

The final parser acts as a preprocessor for Robot Framework data files that
supports headers in format `=== Test Cases ===` in addition to
`*** Test Cases ***`. In this kind of usage it is convenient to use
`TestSuite.from_string`__, `TestSuite.from_model`__ or
`TestSuite.from_file_system`__ factory methods for constructing the returned suite.

.. code:: python

    from pathlib import Path
    from robot.running import TestDefaults, TestSuite

    class RobotPreprocessor:
        extension = '.robot'

        def parse(self, source: Path, defaults: TestDefaults) -> TestSuite:
            data = source.read_text()
            for header in 'Settings', 'Variables', 'Test Cases', 'Keywords':
                data = data.replace(f'=== {header} ===', f'*** {header} ***')
            suite = TestSuite.from_string(data, defaults=defaults)
            return suite.config(name=TestSuite.name_from_source(source), source=source)

__ https://robot-framework.readthedocs.io/en/latest/autodoc/robot.running.html#robot.running.model.TestSuite.from_string
__ https://robot-framework.readthedocs.io/en/latest/autodoc/robot.running.html#robot.running.model.TestSuite.from_model
__ https://robot-framework.readthedocs.io/en/latest/autodoc/robot.running.html#robot.running.model.TestSuite.from_file_system

Python 3.12 compatibility
-------------------------

Python 3.12 will be released in `October 2023`__. It contains a `subtle change
to tokenization`__ that affects Robot Framework's Python evaluation when the
special `$var` syntax is used. This issue has been fixed and Robot Framework 6.1
is also otherwise Python 3.12 compatible (`#4771`_).

__ https://peps.python.org/pep-0693/
__ https://github.com/python/cpython/issues/104802

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

Support item assignment with lists and dictionaries
---------------------------------------------------

Robot Framework 6.1 makes it possible to assign return values from keywords
to list and dictionary items (`#4546`_)::

    ${list}[0] =    Keyword
    ${dict}[key] =    Keyword
    ${result}[users][0] =    Keyword

Possibility to flatten keyword structures during execution
----------------------------------------------------------

With nested keyword structures, especially with recursive keyword calls and with
WHILE and FOR loops, the log file can get hard to understand with many different
nesting levels. Such nested structures also increase the size of the output.xml
file. For example, even a simple keyword like:

.. code:: robotframework

    *** Keywords ***
    Example
        Log    Robot
        Log    Framework

creates this much content in output.xml:

.. code:: xml

    <kw name="Example">
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
is converted into this if the `Example` keyword is flattened using `--flattenkeywords`:

.. code:: xml

    <kw name="Keyword">
      <doc>_*Content flattened.*_</doc>
      <msg timestamp="20230103 20:06:36.663" level="INFO">Robot</msg>
      <msg timestamp="20230103 20:06:36.663" level="INFO">Framework</msg>
      <status status="PASS" starttime="20230103 20:06:36.663" endtime="20230103 20:06:36.664"/>
    </kw>

Starting from Robot Framework 6.1, this kind of flattening can be done also
during execution and without using command line options. The only thing needed
is using the new keyword tag `robot:flatten` (`#4584`_) and flattening is done
automatically. For example, if the earlier `Keyword` is changed to:

.. code:: robotframework

    *** Keywords ***
    Example
        [Tags]    robot:flatten
        Log    Robot
        Log    Framework

the result in output.xml will be this:

.. code:: xml

    <kw name="Example">
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

Type information added to public APIs
-------------------------------------

Robot Framework has several public APIs that library and tool developers can
use. These APIs nowadays have type hints making their usage easier:

- The `TestSuite` structure used by listeners, model modifiers, external parsers,
  and various other tools (`#4570`_)
- Listener API (`#4568`_)
- Dynamic and hybrid library APIs (`#4567`_)
- Parsing API (`#4740`_)
- Visitor API (`#4569`_)

Custom argument converters can access library
---------------------------------------------

Support for custom argument converters was added in Robot Framework 5.0
(`#4088`__) and they have turned out to be really useful. This functionality
is now enhanced so that converters can easily get an access to the
library containing the keyword that is used and can thus do conversion
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


`WHILE` loop enhancements
-------------------------

Robot Framework's WHILE__ loop has been enhanced in several different ways:

- The biggest enhancement is that `WHILE` loops got an optional
  `on_limit` configuration option that controls what to do if the configured
  loop `limit` is reached (`#4562`_). By default execution fails, but setting
  the option to `PASS` changes that. For example, the following loop runs ten
  times and continues execution afterwards:

  .. code:: robotframework

      *** Test Cases ***
      WHILE with 'limit' and 'on_limit'
          WHILE    True    limit=10    on_limit=PASS
              Log to console    Hello!
          END
          Log to console    Hello once more!

- The loop condition is nowadays optional (`#4576`_). For example, the above
  loop header could be simplified to this::

    WHILE    limit=10   on_limit=PASS

- New `on_limit_message` configuration option can be used to set the message
  that is used if the loop limit exceeds and the loop fails (`#4575`_).

- A bug with the loop limit in teardowns has been fixed (`#4744`_).

__ http://robotframework.org/robotframework/latest/RobotFrameworkUserGuide.html#while-loops

`FOR IN ZIP` loop behavior if lists lengths differ can be configured
--------------------------------------------------------------------

Robot Framework's `FOR IN ZIP`__ loop behaves like Python's zip__ function so
that if lists lengths are not the same, items from longer ones are ignored.
For example, the following loop is executed only twice:

__ http://robotframework.org/robotframework/latest/RobotFrameworkUserGuide.html#for-in-zip-loop
__ https://docs.python.org/3/library/functions.html#zip

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

__ https://peps.python.org/pep-0618/
__ https://docs.python.org/3/library/itertools.html#itertools.zip_longest

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
the plan is to change it to `STRICT` `in the future`__.
Those who want to keep using the `SHORTEST` mode need to enable it explicitly.

__ https://github.com/robotframework/robotframework/issues/4686

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
in the call as in the following example, the root suite is configured
based on data it contains::

    robot __init__.robot first.robot second.robot

The most important feature this enhancement allows is specifying suite
setup and teardown to the virtual root suite. Earlier that was not possible
at all.

Support for asynchronous functions and methods as keywords
----------------------------------------------------------

It is nowadays possible to use asynchronous functions (created using
`async def`) as keywords just like normal functions (`#4089`_). For example,
the following async functions could be used as keyword `Gather Something` and
`Async Sleep`:

.. code:: python

    from asyncio import gather, sleep

    async def gather_something():
        print('start')
        await gather(something(1), something(2), something(3))
        print('done')

    async def async_sleep(time: int):
        await sleep(time)

`zipapp` compatibility
----------------------

Robot Framework 6.1 is compatible with zipapp__ (`#4613`_). This makes it possible
to create standalone distributions using either only the `zipapp` module or
with a help from an external packaging tool like PDM__.

__ https://docs.python.org/3/library/zipapp.html
__ https://pdm.fming.dev

New translations
----------------

Robot Framework 6.0 started our `localization efforts`__ and added built-in support
for various languages. Robot Framework 6.1 adds support for Vietnamese (`#4792`_)
and we hope to add more languages in the future.

The new `Name` setting (`#4583`_) has also been translated to various languages
but not yet for all. All supported languages and exact translations used by
them are listed in the `User Guide`__.

__ https://github.com/robotframework/robotframework/blob/master/doc/releasenotes/rf-6.0.rst#localization
__ http://robotframework.org/robotframework/latest/RobotFrameworkUserGuide.html#translations


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

Another change is that `<for>` and `<while>` elements may have new attributes.
With `FOR IN ENUMERATE` loops the `<for>` element may get `start` attribute
(`#4684`_), with `FOR IN ZIP` loops the `<for>` element may get `mode` and `fill`
attributes (`#4682`_), and with `WHILE` loops the `<while>` element may get
`on_limit` (`#4562`_) and `on_limit_message` (`#4575`_) attributes. This
affects tools processing all possible attributes, but such tools ought to
be very rare.

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
for other purposes and tools using it should be updated to use `ReturnSetting`
instead (`#4656`_).

__ https://robot-framework.readthedocs.io/en/latest/autodoc/robot.parsing.model.html#robot.parsing.model.blocks.InvalidSection
__ https://robot-framework.readthedocs.io/en/latest/autodoc/robot.parsing.model.html#robot.parsing.model.statements.Error
__ https://robot-framework.readthedocs.io/en/latest/autodoc/robot.parsing.model.html#robot.parsing.model.statements.Return
__ https://robot-framework.readthedocs.io/en/latest/autodoc/robot.parsing.model.html#robot.parsing.model.statements.ReturnSetting

Files are not excluded from parsing when using `--suite` option
---------------------------------------------------------------

Earlier when the `--suite` option was used, files not matching the specified
suite name were excluded from parsing altogether. This performance enhancement
was convenient especially with bigger suite structures, but it needed to be removed
(`#4688`_) because the new `Name` setting (`#4583`_) made it impossible to
get the suite name solely based on the file name.
Users who are affected by this change can use the new `--parseinclude` option
that explicitly specifies which files should be parsed (`#4687`_).

Changes to Libdoc spec files
----------------------------

Libdoc did not handle parameterized types like `list[int]` properly earlier.
Fixing that problem required storing information about nested types into
the spec files along with the top level type. In addition to the parameterized
types, also unions are now handled differently than earlier, but with normal
types there are no changes. With JSON spec files changes were pretty small,
but XML spec files required a bit bigger changes. See issue `#4538`_ for more
details about what exactly has changed and how.

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
support it with Robot Framework 6.1 and its bug fix releases, but
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
and its over 60 member organizations. If your organization is using Robot Framework
and benefiting from it, consider joining the foundation to support its
development as well.

Robot Framework 6.1 team funded by the foundation consists of
`Pekka Klärck <https://github.com/pekkaklarck>`_ and
`Janne Härkönen <https://github.com/yanne>`_ (part time).
In addition to that, the community has provided several great contributions:

- `@Serhiy1 <https://github.com/Serhiy1>`__ helped massively with adding type
  information to the `TestSuite` structure (`#4570`_).

- `@Vincema <https://github.com/Vincema>`__ added support for long command line
  options with hyphens like `--pre-run-modifier` (`#4547`_) and implemented
  possibility to assign keyword return values directly to list and dictionary items
  (`#4546`_).

- `@sunday2 <https://github.com/sunday2>`__ implemented JSON variable file support
  (`#4532`_) and fixed User Guide generation on Windows (`#4680`_).

- `Tatu Aalto <https://github.com/aaltat>`__ added positional-only argument
  support to the dynamic library API (`#4660`_).

- `@otemek <https://github.com/otemek>`__ implemented possibility to give
  a custom name to a suite using a new `Name` setting (`#4583`_).

- `@franzhaas <https://github.com/franzhaas>`__ made Robot Framework
  `zipapp <https://docs.python.org/3/library/zipapp.html>`__ compatible (`#4613`_).

- `Ygor Pontelo <https://github.com/ygorpontelo>`__ added support for using
  asynchronous functions and methods as keywords (`#4089`_).

- `@ursa-h <https://github.com/ursa-h>`__ enhanced keyword conflict resolution
  so that library search order has higher precedence (`#4609`_).

- `Jonathan Arns <https://github.com/JonathanArns>`__ and
  `Fabian Zeiher <https://github.com/cetceeve>`__ made the initial implementation
  to limit which files are parsed (`#4687`_).

- `@asaout <https://github.com/asaout>`__ added `on_limit_message` option to WHILE
  loops to control the failure message used if the loop limit is exceeded (`#4575`_).

- `@turunenm <https://github.com/turunenm>`__ implemented `CONSOLE` pseudo log level
  (`#4536`_).

- `Yuri Verweij <https://github.com/yuriverweij>`__ enhanced `Dictionaries Should Be Equal`
  so that it supports ignoring keys (`#2717`_).

- `Hưng Trịnh <https://github.com/hungtrinh>`__ provided Vietnamese translation (`#4792`_)
  and `Elout van Leeuwen <https://github.com/leeuwe>`__ helped with localization otherwise.

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
    * - `#1283`_
      - enhancement
      - critical
      - External parser API for custom parsers
    * - `#3902`_
      - enhancement
      - critical
      - Support serializing executable suite into JSON
    * - `#4234`_
      - enhancement
      - critical
      - Support user keywords with both embedded and normal arguments
    * - `#4771`_
      - enhancement
      - critical
      - Python 3.12 compatibility
    * - `#4705`_
      - bug
      - high
      - Items are not converted when using generics like `list[int]` and passing object, not string
    * - `#4744`_
      - bug
      - high
      - WHILE limit doesn't work in teardown
    * - `#4015`_
      - enhancement
      - high
      - Support configuring virtual suite created when running multiple suites with `__init__.robot`
    * - `#4089`_
      - enhancement
      - high
      - Support asynchronous functions and methods as keywords
    * - `#4510`_
      - enhancement
      - high
      - Make it possible for custom converters to get access to the library
    * - `#4532`_
      - enhancement
      - high
      - JSON variable file support
    * - `#4536`_
      - enhancement
      - high
      - Add new pseudo log level `CONSOLE` that logs to console and to log file
    * - `#4546`_
      - enhancement
      - high
      - Support item assignment with lists and dicts like `${x}[key] =    Keyword`
    * - `#4562`_
      - enhancement
      - high
      - Possibility to continue execution after WHILE limit is reached
    * - `#4570`_
      - enhancement
      - high
      - Add type information to `TestSuite` structure
    * - `#4584`_
      - enhancement
      - high
      - New `robot:flatten` tag for "flattening" keyword structures
    * - `#4613`_
      - enhancement
      - high
      - Make Robot Framework compatible with `zipapp`
    * - `#4637`_
      - enhancement
      - high
      - Deprecate Python 3.7
    * - `#4682`_
      - enhancement
      - high
      - Make `FOR IN ZIP` loop behavior if lists have different lengths configurable
    * - `#4746`_
      - enhancement
      - high
      - Decide and document XDG media type
    * - `#4792`_
      - enhancement
      - high
      - Add Vietnamese translation
    * - `#4538`_
      - bug
      - medium
      - Libdoc doesn't handle parameterized types like `list[int]` properly
    * - `#4571`_
      - bug
      - medium
      - Suite setup and teardown are executed even if all tests are skipped
    * - `#4589`_
      - bug
      - medium
      - Remove unused attributes from `robot.running.Keyword` model object
    * - `#4604`_
      - bug
      - medium
      - Listeners do not get source information for keywords executed with `Run Keyword`
    * - `#4626`_
      - bug
      - medium
      - Inconsistent argument conversion when using `None` as default value with Python 3.11 and earlier
    * - `#4635`_
      - bug
      - medium
      - Dialogs created by `Dialogs` on Windows don't have focus
    * - `#4648`_
      - bug
      - medium
      - Argument conversion should be attempted with all possible types even if some type wouldn't be recognized
    * - `#4670`_
      - bug
      - medium
      - Parsing model: `Documentation.from_params(...).value` doesn't work
    * - `#4680`_
      - bug
      - medium
      - User Guide generation broken on Windows
    * - `#4689`_
      - bug
      - medium
      - Invalid sections are not represented properly in parsing model
    * - `#4692`_
      - bug
      - medium
      - `ELSE IF` condition not passed to listeners
    * - `#4695`_
      - bug
      - medium
      - Accessing `id` property of model objects may cause `ValueError`
    * - `#4716`_
      - bug
      - medium
      - Variable nodes with nested variables report a parsing error, but work properly in the runtime
    * - `#4754`_
      - bug
      - medium
      - Back navigation does not work properly in HTML outputs (log, report, Libdoc)
    * - `#4756`_
      - bug
      - medium
      - Failed keywords inside skipped tests are not expanded
    * - `#2717`_
      - enhancement
      - medium
      - `Dictionaries Should Be Equal` should support ignoring keys
    * - `#3579`_
      - enhancement
      - medium
      - Enhance performance of selecting tests using `--include` and `--exclude`
    * - `#4210`_
      - enhancement
      - medium
      - Enhance error detection at parsing time
    * - `#4547`_
      - enhancement
      - medium
      - Support long command line options with hyphens like `--pre-run-modifier`
    * - `#4567`_
      - enhancement
      - medium
      - Add optional typed base class for dynamic library API
    * - `#4568`_
      - enhancement
      - medium
      - Add optional typed base classes for listener API
    * - `#4569`_
      - enhancement
      - medium
      - Add type information to the visitor API
    * - `#4575`_
      - enhancement
      - medium
      - Add `on_limit_message` option to WHILE loops to control message used if loop limit is exceeded
    * - `#4576`_
      - enhancement
      - medium
      - Make the WHILE loop condition optional
    * - `#4583`_
      - enhancement
      - medium
      - Possibility to give a custom name to a suite using `Name` setting
    * - `#4601`_
      - enhancement
      - medium
      - Add `robot.running.TestSuite.from_string` method
    * - `#4609`_
      - enhancement
      - medium
      - If multiple keywords match, resolve conflict first using search order
    * - `#4627`_
      - enhancement
      - medium
      - Support custom converters that accept only `*varargs`
    * - `#4647`_
      - enhancement
      - medium
      - Add explicit argument converter for `Any` that does no conversion
    * - `#4660`_
      - enhancement
      - medium
      - Dynamic API: Support positional-only arguments
    * - `#4666`_
      - enhancement
      - medium
      - Add public API to query is Robot running and is dry-run active
    * - `#4676`_
      - enhancement
      - medium
      - Propose using `$var` syntax if evaluation IF or WHILE condition using `${var}` fails
    * - `#4683`_
      - enhancement
      - medium
      - Report syntax errors better in log file
    * - `#4684`_
      - enhancement
      - medium
      - Handle start index with `FOR IN ENUMERATE` loops already in parser
    * - `#4687`_
      - enhancement
      - medium
      - Add explicit command line option to limit which files are parsed
    * - `#4688`_
      - enhancement
      - medium
      - Do not exclude files during parsing if using `--suite` option
    * - `#4729`_
      - enhancement
      - medium
      - Leading and internal spaces should be preserved in documentation
    * - `#4740`_
      - enhancement
      - medium
      - Add type hints to parsing API
    * - `#4765`_
      - enhancement
      - medium
      - Add forward compatible `start_time`, `end_time` and `elapsed_time` propertys to result objects
    * - `#4777`_
      - enhancement
      - medium
      - Parse files with `.robot.rst` extension automatically
    * - `#4793`_
      - enhancement
      - medium
      - Enhance programmatic API to create resource files
    * - `#4611`_
      - bug
      - low
      - Some unit tests cannot be run independently
    * - `#4634`_
      - bug
      - low
      - Dialogs created by `Dialogs` are not centered and their minimum size is too small
    * - `#4638`_
      - bug
      - low
      - Using bare `Union` as annotation is not handled properly
    * - `#4646`_
      - bug
      - low
      - Bad error message when function is annotated with an empty tuple `()`
    * - `#4663`_
      - bug
      - low
      - `BuiltIn.Log` documentation contains a defect
    * - `#4736`_
      - bug
      - low
      - Backslash preventing newline in documentation can form escape sequence like `\n`
    * - `#4749`_
      - bug
      - low
      - Process: `Split/Join Command Line` do not work properly with `pathlib.Path` objects
    * - `#4780`_
      - bug
      - low
      - Libdoc crashes if it does not detect documentation format
    * - `#4781`_
      - bug
      - low
      - Libdoc: Type info for `TypedDict` doesn't list `Mapping` in converted types
    * - `#4522`_
      - enhancement
      - low
      - Deprecate `accept_plain_values` argument used by `timestr_to_secs`
    * - `#4596`_
      - enhancement
      - low
      - Make `TestSuite.source` attribute `pathlib.Path` instance
    * - `#4598`_
      - enhancement
      - low
      - Deprecate `name` argument of `TestSuite.from_model`
    * - `#4619`_
      - enhancement
      - low
      - Dialogs created by `Dialogs` should bind `Enter` key to `OK` button
    * - `#4636`_
      - enhancement
      - low
      - Buttons in dialogs created by `Dialogs` should get keyboard shortcuts
    * - `#4656`_
      - enhancement
      - low
      - Deprecate `Return` node in parsing model
    * - `#4709`_
      - enhancement
      - low
      - Add `__repr__()` method to NormalizedDict

Altogether 77 issues. View on the `issue tracker <https://github.com/robotframework/robotframework/issues?q=milestone%3Av6.1>`__.

.. _#1283: https://github.com/robotframework/robotframework/issues/1283
.. _#3902: https://github.com/robotframework/robotframework/issues/3902
.. _#4234: https://github.com/robotframework/robotframework/issues/4234
.. _#4771: https://github.com/robotframework/robotframework/issues/4771
.. _#4705: https://github.com/robotframework/robotframework/issues/4705
.. _#4744: https://github.com/robotframework/robotframework/issues/4744
.. _#4015: https://github.com/robotframework/robotframework/issues/4015
.. _#4089: https://github.com/robotframework/robotframework/issues/4089
.. _#4510: https://github.com/robotframework/robotframework/issues/4510
.. _#4532: https://github.com/robotframework/robotframework/issues/4532
.. _#4536: https://github.com/robotframework/robotframework/issues/4536
.. _#4546: https://github.com/robotframework/robotframework/issues/4546
.. _#4562: https://github.com/robotframework/robotframework/issues/4562
.. _#4570: https://github.com/robotframework/robotframework/issues/4570
.. _#4584: https://github.com/robotframework/robotframework/issues/4584
.. _#4613: https://github.com/robotframework/robotframework/issues/4613
.. _#4637: https://github.com/robotframework/robotframework/issues/4637
.. _#4682: https://github.com/robotframework/robotframework/issues/4682
.. _#4746: https://github.com/robotframework/robotframework/issues/4746
.. _#4792: https://github.com/robotframework/robotframework/issues/4792
.. _#4538: https://github.com/robotframework/robotframework/issues/4538
.. _#4571: https://github.com/robotframework/robotframework/issues/4571
.. _#4589: https://github.com/robotframework/robotframework/issues/4589
.. _#4604: https://github.com/robotframework/robotframework/issues/4604
.. _#4626: https://github.com/robotframework/robotframework/issues/4626
.. _#4635: https://github.com/robotframework/robotframework/issues/4635
.. _#4648: https://github.com/robotframework/robotframework/issues/4648
.. _#4670: https://github.com/robotframework/robotframework/issues/4670
.. _#4680: https://github.com/robotframework/robotframework/issues/4680
.. _#4689: https://github.com/robotframework/robotframework/issues/4689
.. _#4692: https://github.com/robotframework/robotframework/issues/4692
.. _#4695: https://github.com/robotframework/robotframework/issues/4695
.. _#4716: https://github.com/robotframework/robotframework/issues/4716
.. _#4754: https://github.com/robotframework/robotframework/issues/4754
.. _#4756: https://github.com/robotframework/robotframework/issues/4756
.. _#2717: https://github.com/robotframework/robotframework/issues/2717
.. _#3579: https://github.com/robotframework/robotframework/issues/3579
.. _#4210: https://github.com/robotframework/robotframework/issues/4210
.. _#4547: https://github.com/robotframework/robotframework/issues/4547
.. _#4567: https://github.com/robotframework/robotframework/issues/4567
.. _#4568: https://github.com/robotframework/robotframework/issues/4568
.. _#4569: https://github.com/robotframework/robotframework/issues/4569
.. _#4575: https://github.com/robotframework/robotframework/issues/4575
.. _#4576: https://github.com/robotframework/robotframework/issues/4576
.. _#4583: https://github.com/robotframework/robotframework/issues/4583
.. _#4601: https://github.com/robotframework/robotframework/issues/4601
.. _#4609: https://github.com/robotframework/robotframework/issues/4609
.. _#4627: https://github.com/robotframework/robotframework/issues/4627
.. _#4647: https://github.com/robotframework/robotframework/issues/4647
.. _#4660: https://github.com/robotframework/robotframework/issues/4660
.. _#4666: https://github.com/robotframework/robotframework/issues/4666
.. _#4676: https://github.com/robotframework/robotframework/issues/4676
.. _#4683: https://github.com/robotframework/robotframework/issues/4683
.. _#4684: https://github.com/robotframework/robotframework/issues/4684
.. _#4687: https://github.com/robotframework/robotframework/issues/4687
.. _#4688: https://github.com/robotframework/robotframework/issues/4688
.. _#4729: https://github.com/robotframework/robotframework/issues/4729
.. _#4740: https://github.com/robotframework/robotframework/issues/4740
.. _#4765: https://github.com/robotframework/robotframework/issues/4765
.. _#4777: https://github.com/robotframework/robotframework/issues/4777
.. _#4793: https://github.com/robotframework/robotframework/issues/4793
.. _#4611: https://github.com/robotframework/robotframework/issues/4611
.. _#4634: https://github.com/robotframework/robotframework/issues/4634
.. _#4638: https://github.com/robotframework/robotframework/issues/4638
.. _#4646: https://github.com/robotframework/robotframework/issues/4646
.. _#4663: https://github.com/robotframework/robotframework/issues/4663
.. _#4736: https://github.com/robotframework/robotframework/issues/4736
.. _#4749: https://github.com/robotframework/robotframework/issues/4749
.. _#4780: https://github.com/robotframework/robotframework/issues/4780
.. _#4781: https://github.com/robotframework/robotframework/issues/4781
.. _#4522: https://github.com/robotframework/robotframework/issues/4522
.. _#4596: https://github.com/robotframework/robotframework/issues/4596
.. _#4598: https://github.com/robotframework/robotframework/issues/4598
.. _#4619: https://github.com/robotframework/robotframework/issues/4619
.. _#4636: https://github.com/robotframework/robotframework/issues/4636
.. _#4656: https://github.com/robotframework/robotframework/issues/4656
.. _#4709: https://github.com/robotframework/robotframework/issues/4709
