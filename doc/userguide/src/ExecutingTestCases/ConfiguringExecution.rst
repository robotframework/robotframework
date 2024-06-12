Configuring execution
=====================

This section explains different command line options that can be used
for configuring the `test execution`_ or `post-processing
outputs`_. Options related to generated `output files`_ are discussed in
the next section.

.. contents::
   :depth: 2
   :local:

Selecting files to parse
------------------------

Executing individual files
~~~~~~~~~~~~~~~~~~~~~~~~~~

When executing individual files, Robot Framework tries to parse and run them
regardless the name or the file extension. What parser to use depends
on the extension:

- :file:`.robot` files and files that are not recognized are parsed using
  the normal `Robot Framework parser`__.
- :file:`.rst` and :file:`.rest` files are parsed using the `reStructuredText parser`__.
- :file:`.rbt` and :file:`.json` files are parsed using the `JSON parser`__.
- Files supported by `custom parsers`__ are parsed by a matching parser.

Examples::

    robot example.robot    # Standard Robot Framework parser.
    robot example.tsv      # Must be compatible with the standard parser.
    robot example.rst      # reStructuredText parser.
    robot x.robot y.rst    # Parse both files using an appropriate parser.

__ `Supported file formats`_
__ `reStructuredText format`_
__ `JSON format`_
__ `Using custom parsers`_

Included and excluded files
~~~~~~~~~~~~~~~~~~~~~~~~~~~

When executing a directory__, files and directories are parsed using
the following rules:

- All files and directories starting with a dot (:file:`.`) or an underscore
  (:file:`_`) are ignored.
- :file:`.robot` files are parsed using the normal `Robot Framework parser`__.
- :file:`.robot.rst` files are parsed using the `reStructuredText parser`__.
- :file:`.rbt` files are parsed using the `JSON parser`__.
- Files supported by `custom parsers`__ are parsed by a matching parser.
- Other files are ignored unless parsing them has been enabled by using
  the :option:`--parseinclude` or :option:`--extension` options discussed
  in the subsequent sections.

__ `Suite directories`_
__ `Supported file formats`_
__ `reStructuredText format`_
__ `JSON format`_
__ `Using custom parsers`_

Selecting files by name or path
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

When executing a directory, it is possible to parse only certain files based on
their name or path by using the :option:`--parseinclude (-I)` option. This option
has slightly different semantics depending on the value it is used with:

- If the value is just a file name like `example.robot`, files matching
  the name in all directories will be parsed.

- To match only a certain file in a certain directory, files can be given
  as relative or absolute paths like `path/to/tests.robot`.

- If the value is a path to a directory, all files inside that directory are parsed,
  recursively.

Examples::

    robot --parseinclude example.robot tests       # Parse `example.robot` files anywhere under `tests`.
    robot -I example_*.robot -I ???.robot tests    # Parse files matching `example_*.robot` or `???.robot` under `tests`.
    robot -I tests/example.robot tests             # Parse only `tests/example.robot`.
    robot --parseinclude tests/example tests       # Parse files under `tests/example` directory, recursively.

Values used with :option:`--parseinclude` are case-insensitive and support
`glob patterns <Simple patterns_>`__ like `example_*.robot`. There are, however,
two small differences compared to how patterns typically work with Robot Framework:

- `*` matches only a single path segment. For example, `path/*/tests.robot`
  matches :file:`path/to/tests.robot` but not :file:`path/to/nested/tests.robot`.

- `**` can be used to enable recursive matching. For example, `path/**/tests.robot`
  matches both :file:`path/to/tests.robot` and :file:`path/to/nested/tests.robot`.

If the pattern contains an extension, files with that extension are parsed
even if they by `default would not be`__. What parser to use depends on
the used extension:

- :file:`.rst` and :file:`.rest` files are parsed using the `reStructuredText parser`__.
- :file:`.json` files are parsed using the `JSON parser`__.
- Other files are parsed using the normal `Robot Framework parser`__.

Notice that when you use a pattern like `*.robot` and there exists a file that
matches the pattern in the execution directory, the shell may resolve
the pattern before Robot Framework is called and the value passed to
it is the file name, not the original pattern. In such cases you need
to quote or escape the pattern like `'*.robot'` or `\*.robot`.

__ `Included and excluded files`_
__ `reStructuredText format`_
__ `JSON format`_
__ `Supported file formats`_

.. note:: `--parseinclude` is new in Robot Framework 6.1.

Selecting files by extension
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

In addition to using the :option:`--parseinclude` option discussed in the
previous section, it is also possible to enable parsing files that are `not
parsed by default`__ by using the :option:`--extension (-F)` option.
Matching extensions is case insensitive and the leading dot can be omitted.
If there is a need to parse more than one kind of files, it is possible to
use a colon `:` to separate extensions::

    robot --extension rst path/to/tests    # Parse only *.rst files.
    robot -F robot:rst path/to/tests       # Parse *.robot and *.rst files.

The above is equivalent to the following :option:`--parseinclude` usage::

    robot --parseinclude *.rst path/to/tests
    robot -I *.robot -I *.rst path/to/tests

Because the :option:`--parseinclude` option is more powerful and covers all
same use cases as the :option:`--extension` option, the latter is likely to be
deprecated in the future. Users are recommended to use :option:`--parseinclude`
already now.

__ `Included and excluded files`_

Using custom parsers
~~~~~~~~~~~~~~~~~~~~

External parsers can parse files that Robot Framework does not recognize
otherwise. For more information about creating and using such parsers see
the `Parser interface`_ section.

Selecting test cases
--------------------

Robot Framework offers several command line options for selecting
which test cases to execute. The same options work also when `executing
tasks`_ and when post-processing outputs with Rebot_.

By test names
~~~~~~~~~~~~~

The easiest way to select only some tests to be run is using the
:option:`--test (-t)` option. As the name implies, it can be used for
selecting tests by their names. Given names are case, space and underscore
insensitive and they also support `simple patterns`_. The option can be
used multiple times to match multiple tests::

  --test Example                   # Match only tests with name 'Example'.
  --test example*                  # Match tests starting with 'example'.
  --test first --test second       # Match tests with name 'first' or 'second'.

To pinpoint a test more precisely, it is possible to prefix the test name
with a suite name::

  --test mysuite.mytest            # Match test 'mytest' in suite 'mysuite'.
  --test root.sub.test             # Match test 'test' in suite 'sub' in suite 'root'.
  --test *.sub.test                # Match test 'test' in suite 'sub' anywhere.

Notice that when the given name includes a suite name, it must match the whole
suite name starting from the root suite. Using a wildcard as in the last example
above allows matching tests with a parent suite anywhere.

Using the :option:`--test` option is convenient when only a few tests needs
to be selected. A common use case is running just the test that is currently
being worked on. If a bigger number of tests needs to be selected,
it is typically easier to select them `by suite names`_ or `by tag names`_.

When `executing tasks`_, it is possible to use the :option:`--task` option
as an alias for :option:`--test`.

By suite names
~~~~~~~~~~~~~~

Tests can be selected also by suite names with the :option:`--suite (-s)`
option that selects all tests in matching suites. Similarly
as with :option:`--test`, given names are case, space and underscore
insensitive and support `simple patterns`_. To pinpoint a suite
more precisely, it is possible to prefix the name with the parent suite
name::

  --suite Example                  # Match only suites with name 'Example'.
  --suite example*                 # Match suites starting with 'example'.
  --suite first --suite second     # Match suites with name 'first' or 'second'.
  --suite root.child               # Match suite 'child' in root suite 'root'.
  --suite *.parent.child           # Match suite 'child' with parent 'parent' anywhere.

If the name contains a parent suite name, it must match the whole suite name
the same way as with :option:`--test`. Using a wildcard as in the last example
above allows matching suites with a parent suite anywhere.

.. note:: Prior to Robot Framework 7.0, :option:`--suite` with a parent suite
          did not need to match the whole suite name. For example, `parent.child`
          would match suite `child` with parent `parent` anywhere. The name must
          be prefixed with a wildcard if this behavior is desired nowadays.

If both :option:`--suite` and :option:`--test` options are used, only the
specified tests in specified suites are selected::

  --suite mysuite --test mytest    # Match test 'mytest' if its inside suite 'mysuite'.

Using the :option:`--suite` option is more or less the same as executing
the appropriate suite file or directory directly. The main difference is
that if a file or directory is run directly, possible suite setups and teardowns
on higher level are not executed::

  # Root suite is 'Tests' and its possible setup and teardown are run.
  robot --suite example path/to/tests

  # Root suite is 'Example' and possible higher level setups and teardowns are ignored.
  robot path/to/tests/example.robot

Prior to Robot Framework 6.1, files not matching the :option:`--suite` option
were not parsed at all for performance reasons. This optimization was not
possible anymore after suites got a new :setting:`Name` setting that can override
the default suite name that is got from the file or directory name. New
:option:`--parseinclude` option has been added to `explicitly select which
files are parsed`__ if this kind of parsing optimization is needed.

__ `Selecting files by name or path`_

By tag names
~~~~~~~~~~~~

It is possible to include and exclude test cases by tag_ names with the
:option:`--include (-i)` and :option:`--exclude (-e)` options, respectively.
If the :option:`--include` option is used, only test cases having a matching
tag are selected, and with the :option:`--exclude` option test cases having a
matching tag are not. If both are used, only tests with a tag
matching the former option, and not with a tag matching the latter,
are selected::

   --include example
   --exclude not_ready
   --include regression --exclude long_lasting

Both :option:`--include` and :option:`--exclude` can be used several
times to match multiple tags. In that case a test is selected
if it has a tag that matches any included tags, and also has no tag
that matches any excluded tags.

In addition to specifying a tag to match fully, it is possible to use
`tag patterns`_ where `*` and `?` are wildcards and
`AND`, `OR`, and `NOT` operators can be used for
combining individual tags or patterns together::

   --include feature-4?
   --exclude bug*
   --include fooANDbar
   --exclude xxORyyORzz
   --include fooNOTbar

Starting from RF 5.0, it is also possible to use the reserved
tag `robot:exclude` to achieve
the same effect as with using the `--exclude` option:

.. sourcecode:: robotframework

   *** Test Cases ***
   Example
      [Tags]    robot:exclude
      Fail      This is not executed

Selecting test cases by tags is a very flexible mechanism and allows
many interesting possibilities:

- A subset of tests to be executed before other tests, often called smoke
  tests, can be tagged with `smoke` and executed with `--include smoke`.

- Unfinished test can be committed to version control with a tag such as
  `not_ready` and excluded from the test execution with
  `--exclude not_ready`.

- Tests can be tagged with `sprint-<num>`, where
  `<num>` specifies the number of the current sprint, and
  after executing all test cases, a separate report containing only
  the tests for a certain sprint can be generated (for example, `rebot
  --include sprint-42 output.xml`).

Options :option:`--include` and :option:`--exclude` can be used in combination
with :option:`--suite` and :option:`--test` discussed in the previous section.
In that case tests that are selected must match all selection criteria::

  --suite example --include tag    # Match test if it is in suite 'example' and has tag 'tag'.
  --suite example --exclude tag    # Match test if it is in suite 'example' and does not have tag 'tag'.
  --test ex* --include tag         # Match test if its name starts with 'ex' and it has tag 'tag'.
  --test ex* --exclude tag         # Match test if its name starts with 'ex' and it does not have tag 'tag'.

.. note:: In Robot Framework 7.0 `--include` and `--test` were cumulative and
          selected tests needed to match only either of these options. That behavior
          caused `backwards incompatibility problems`__ and it was changed
          back to the original already in Robot Framework 7.0.1.

__ https://github.com/robotframework/robotframework/issues/5023

Re-executing failed test cases
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Command line option :option:`--rerunfailed (-R)` can be used to select all failed
tests from an earlier `output file`_ for re-execution. This option is useful,
for example, if running all tests takes a lot of time and one wants to
iteratively fix failing test cases.

::

  robot tests                             # first execute all tests
  robot --rerunfailed output.xml tests    # then re-execute failing

Behind the scenes this option selects the failed tests as they would have been
selected individually using the :option:`--test` option. It is possible to further
fine-tune the list of selected tests by using :option:`--test`, :option:`--suite`,
:option:`--include` and :option:`--exclude` options.

It is an error if the output contains no failed tests, but this behavior can be
changed by using the :option:`--runemptysuite` option `discussed below`__.
Using an output not originating from executing the same tests that are run
now causes undefined results. Using a special value `NONE` as the output is
same as not specifying this option at all.

.. tip:: Re-execution results and original results can be `merged together`__
         using the :option:`--merge` command line option.

__ `When no tests match selection`_
__ `Merging outputs`_

Re-executing failed test suites
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Command line option :option:`--rerunfailedsuites (-S)` can be used to select all
failed suites from an earlier `output file`_ for re-execution. Like
:option:`--rerunfailed (-R)`, this option is useful when full test execution
takes a lot of time. Note that all tests from a failed test suite will be
re-executed, even passing ones. This option is useful when the tests in
a test suite depends on each other.

Behind the scenes this option selects the failed suites as they would have been
selected individually with the :option:`--suite` option. It is possible to further
fine-tune the list of selected tests by using :option:`--test`, :option:`--suite`,
:option:`--include` and :option:`--exclude` options.

When no tests match selection
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

By default when no tests match the selection criteria test execution fails
with an error like::

    [ ERROR ] Suite 'Example' contains no tests matching tag 'xxx'.

Because no outputs are generated, this behavior can be problematic if tests
are executed and results processed automatically. Luckily a command line
option :option:`--RunEmptySuite` (case-insensitive) can be used to force
the suite to be executed also in this case. As a result normal outputs are
created but show zero executed tests. The same option can be used also to
alter the behavior when an empty directory or a test case file containing
no tests is executed.

Similar situation can occur also when processing output files with Rebot_.
It is possible that no test match the used filtering criteria or that
the output file contained no tests to begin with. By default executing
Rebot fails in these cases, but it has a separate
:option:`--ProcessEmptySuite` option that can be used to alter the behavior.
In practice this option works the same way as :option:`--RunEmptySuite` when
running tests.

.. note:: Using :option:`--RunEmptySuite` with :option:`--ReRunFailed`
          or :option:`--ReRunFailedSuites` requires Robot Framework 5.0.1
          or newer.

Setting metadata
----------------

Setting suite name
~~~~~~~~~~~~~~~~~~

When Robot Framework parses test data, `suite names`__ are created
from file and directory names. The name of the top-level test suite
can, however, be overridden with the command line option
:option:`--name (-N)`::

    robot --name "Custom name" tests.robot

__ `Suite name`_

Setting suite documentation
~~~~~~~~~~~~~~~~~~~~~~~~~~~

In addition to `defining documentation in the test data`__, documentation
of the top-level suite can be given from the command line with the
option :option:`--doc (-D)`. The value can contain simple `HTML formatting`_
and must be quoted if it contains spaces.

If the given documentation is a relative or absolute path pointing to an existing
file, the actual documentation will be read from that file. This is especially
convenient if the externally specified documentation is long or contains multiple
lines.

Examples::

    robot --doc "Example documentation" tests.robot
    robot --doc doc.txt tests.robot    # Documentation read from doc.txt if it exits.

.. note:: Reading documentation from an external file is new in Robot Framework 4.1.

          Prior to Robot Framework 3.1, underscores in documentation were
          converted to spaces same way as with the :option:`--name` option.

__ `Suite documentation`_

Setting free suite metadata
~~~~~~~~~~~~~~~~~~~~~~~~~~~

`Free suite metadata`_ may also be given from the command line with the
option :option:`--metadata (-M)`. The argument must be in the format
`name:value`, where `name` the name of the metadata to set and
`value` is its value. The value can contain simple `HTML formatting`_ and
the whole argument must be quoted if it contains spaces.
This option may be used several times to set multiple metadata values.

If the given value is a relative or absolute path pointing to an existing
file, the actual value will be read from that file. This is especially
convenient if the value is long or contains multiple lines.
If the value should be a path to an existing file, not read from that file,
the value must be separated with a space from the `name:` part.

Examples::

    robot --metadata Name:Value tests.robot
    robot --metadata "Another Name:Another value, now with spaces" tests.robot
    robot --metadata "Read From File:meta.txt" tests.robot    # Value read from meta.txt if it exists.
    robot --metadata "Path As Value: meta.txt" tests.robot    # Value always used as-is.

.. note:: Reading metadata value from an external file is new in Robot Framework 4.1.

          Prior to Robot Framework 3.1, underscores in the value were
          converted to spaces same way as with the :option:`--name` option.

Setting test tags
~~~~~~~~~~~~~~~~~

The command line option :option:`--settag (-G)` can be used to set
the given tag to all executed test cases. This option may be used
several times to set multiple tags.

.. _module search path:

Configuring where to search libraries and other extensions
----------------------------------------------------------

When Robot Framework imports a `test library`__, `listener`__, or some other
Python based extension, it uses the Python interpreter to import the module
containing the extension from the system. The list of locations where modules
are looked for is called *the module search path*, and its contents can be
configured using different approaches explained in this section.

Robot Framework uses Python's module search path also when importing `resource
and variable files`_ if the specified path does not match any file directly.

The module search path being set correctly so that libraries and other
extensions are found is a requirement for successful test execution. If
you need to customize it using approaches explained below, it is often
a good idea to create a custom `start-up script`_.

__ `Specifying library to import`_
__ `Setting listeners`_

Locations automatically in module search path
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Python interpreters have their own standard library as well as a directory
where third party modules are installed automatically in the module search
path. This means that test libraries `packaged using Python's own packaging
system`__ are automatically installed so that they can be imported without
any additional configuration.

__ `Packaging libraries`_

``PYTHONPATH``
~~~~~~~~~~~~~~

Python reads additional locations to be added to
the module search path from ``PYTHONPATH`` environment variables.
If you want to specify more than one location in any of them, you
need to separate the locations with a colon on UNIX-like machines (e.g.
`/opt/libs:$HOME/testlibs`) and with a semicolon on Windows (e.g.
`D:\libs;%HOMEPATH%\testlibs`).

Environment variables can be configured permanently system wide or so that
they affect only a certain user. Alternatively they can be set temporarily
before running a command, something that works extremely well in custom
`start-up scripts`_.

Using `--pythonpath` option
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Robot Framework has a separate command line option :option:`--pythonpath (-P)`
for adding locations to the module search path.

Multiple locations can be given by separating them with a colon (`:`) or
a semicolon (`;`) or by using this option multiple times. If the value
contains both colons and semicolons, it is split from semicolons. Paths
can also be `glob patterns`__ matching multiple paths, but they typically
need to be escaped when used on the console.

Examples::

   --pythonpath libs
   --pythonpath /opt/testlibs:mylibs.zip:yourlibs
   --pythonpath /opt/testlibs --pythonpath mylibs.zip --pythonpath yourlibs
   --pythonpath c:\temp;d:\resources
   --pythonpath  lib/\*.zip    # '*' is escaped

.. note:: Both colon and semicolon work regardless the operating system.
          Using semicolon is new in Robot Framework 5.0.

__ https://en.wikipedia.org/wiki/Glob_(programming)

Configuring `sys.path` programmatically
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Python interpreters store the module search path they use as a list of strings
in `sys.path`__
attribute. This list can be updated dynamically during execution, and changes
are taken into account next time when something is imported.

__ http://docs.python.org/library/sys.html#sys.path


Setting variables
-----------------

Variables_ can be set from the command line either individually__
using the :option:`--variable (-v)` option or through `variable files`_
with the :option:`--variablefile (-V)` option. Variables and variable
files are explained in separate chapters, but the following examples
illustrate how to use these options::

  --variable name:value
  --variable OS:Linux --variable IP:10.0.0.42
  --variablefile path/to/variables.py
  --variablefile myvars.py:possible:arguments:here
  --variable ENVIRONMENT:Windows --variablefile c:\resources\windows.py

__ `Setting variables in command line`_

Dry run
-------

Robot Framework supports so called *dry run* mode where the tests are
run normally otherwise, but the keywords coming from the test libraries
are not executed at all. The dry run mode can be used to validate the
test data; if the dry run passes, the data should be syntactically
correct. This mode is triggered using option :option:`--dryrun`.

The dry run execution may fail for following reasons:

  * Using keywords that are not found.
  * Using keywords with wrong number of arguments.
  * Using user keywords that have invalid syntax.

In addition to these failures, normal `execution errors`__ are shown,
for example, when test library or resource file imports cannot be
resolved.

It is possible to disable dry run validation of specific `user keywords`_
by adding a special `robot:no-dry-run` `keyword tag`__ to them. This is useful
if a keyword fails in the dry run mode for some reason, but work fine when
executed normally.

.. note:: The dry run mode does not validate variables.

__ `Errors and warnings during execution`_
__ `User keyword tags`_

Randomizing execution order
---------------------------

The test execution order can be randomized using option
:option:`--randomize <what>[:<seed>]`, where `<what>` is one of the following:

`tests`
    Test cases inside each test suite are executed in random order.

`suites`
    All test suites are executed in a random order, but test cases inside
    suites are run in the order they are defined.

`all`
    Both test cases and test suites are executed in a random order.

`none`
    Neither execution order of test nor suites is randomized.
    This value can be used to override the earlier value set with
    :option:`--randomize`.

It is possible to give a custom seed
to initialize the random generator. This is useful if you want to re-run tests
using the same order as earlier. The seed is given as part of the value for
:option:`--randomize` in format `<what>:<seed>` and it must be an integer.
If no seed is given, it is generated randomly. The executed top level test
suite automatically gets metadata__ named :name:`Randomized` that tells both
what was randomized and what seed was used.

Examples::

    robot --randomize tests my_test.robot
    robot --randomize all:12345 path/to/tests

__ `Free suite metadata`_

.. _pre-run modifier:

Programmatic modification of test data
--------------------------------------

If the provided built-in features to modify test data before execution
are not enough, Robot Framework makes it possible to do
custom modifications programmatically. This is accomplished by creating
a so called *pre-run modifier* and activating it using the
:option:`--prerunmodifier` option.

Pre-run modifiers should be implemented as visitors that can traverse through
the executable test suite structure and modify it as needed. The visitor
interface is explained as part of the `Robot Framework API documentation
<visitor interface_>`_, and it possible to modify executed `test suites
<running.TestSuite_>`_, `test cases <running.TestCase_>`_ and `keywords
<running.Keyword_>`_ using it. The examples below ought to give an idea of
how pre-run modifiers can be used and how powerful this functionality is.

When a pre-run modifier is taken into use on the command line using the
:option:`--prerunmodifier` option, it can be specified either as a name of
the modifier class or a path to the modifier file. If the modifier is given
as a class name, the module containing the class must be in the `module search
path`_, and if the module name is different than the class name, the given
name must include both like `module.ModifierClass`. If the modifier is given
as a path, the class name must be same as the file name. For most parts this
works exactly like when `importing a test library`__.

If a modifier requires arguments, like the examples below do, they can be
specified after the modifier name or path using either a colon (`:`) or a
semicolon (`;`) as a separator. If both are used in the value, the one used
first is considered to be the actual separator. Starting from Robot Framework
4.0, arguments also support the `named argument syntax`_ as well as `argument
conversion`__ based on `type hints`__ and `default values`__ the same way
as keywords do.

If more than one pre-run modifier is needed, they can be specified by using
the :option:`--prerunmodifier` option multiple times. If similar modifying
is needed before creating logs and reports, `programmatic modification of
results`_ can be enabled using the :option:`--prerebotmodifier` option.

Pre-run modifiers are executed before other configuration affecting the
executed test suite and test cases. Most importantly, options related to
`selecting test cases`_ are processed after modifiers, making it possible to
use options like :option:`--include` also with possible dynamically added
tests.

.. tip:: Modifiers are taken into use from the command line exactly the same
         way as listeners_. See the `Registering listeners from command line`_
         section for more information and examples.

__ `Specifying library to import`_
__ `Supported conversions`_
__ `Specifying argument types using function annotations`_
__ `Implicit argument types based on default values`_

Example: Select every Xth test
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The first example shows how a pre-run modifier can remove tests from the
executed test suite structure. In this example only every Xth tests is
preserved, and the X is given from the command line along with an optional
start index.

.. sourcecode:: python

   ../api/code_examples/SelectEveryXthTest.py

If the above pre-run modifier is in a file :file:`SelectEveryXthTest.py` and
the file is in the `module search path`_, it could be used like this::

    # Specify the modifier as a path. Run every second test.
    robot --prerunmodifier path/to/SelectEveryXthTest.py:2 tests.robot

    # Specify the modifier as a name. Run every third test, starting from the second.
    robot --prerunmodifier SelectEveryXthTest:3:1 tests.robot

.. note:: Argument conversion based on type hints like `x: int` in the above
          example is new in Robot Framework 4.0 and requires Python 3.

Example: Exclude tests by name
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Also the second example removes tests, this time based on a given name pattern.
In practice it works like a negative version of the built-in :option:`--test`
option.

.. sourcecode:: python

   ../api/code_examples/ExcludeTests.py

Assuming the above modifier is in a file named :file:`ExcludeTests.py`, it
could be used like this::

  # Exclude test named 'Example'.
  robot --prerunmodifier path/to/ExcludeTests.py:Example tests.robot

  # Exclude all tests ending with 'something'.
  robot --prerunmodifier path/to/ExcludeTests.py:*something tests.robot

Example: Disable setups and teardowns
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Sometimes when debugging tests it can be useful to disable setups or teardowns.
This can be accomplished by editing the test data, but pre-run modifiers make
it easy to do that temporarily for a single run:

.. sourcecode:: python

  ../api/code_examples/disable.py

Assuming that the above modifiers are all in a file named :file:`disable.py`
and this file is in the `module search path`_, setups and teardowns could be
disabled, for example, as follows::

  # Disable suite teardowns.
  robot --prerunmodifier disable.SuiteTeardown tests.robot

  # Disable both test setups and teardowns by using '--prerunmodifier' twice.
  robot --prerunmodifier disable.TestSetup --prerunmodifier disable.TestTeardown tests.robot

.. note::  Prior to Robot Framework 4.0 `setup` and `teardown` were accessed via
           the intermediate `keywords` attribute and, for example, suite setup
           was disabled like `suite.keywords.setup = None`.

Controlling console output
--------------------------

There are various command line options to control how test execution is
reported on the console.

Console output type
~~~~~~~~~~~~~~~~~~~

The overall console output type is set with the :option:`--console` option.
It supports the following case-insensitive values:

`verbose`
    Every test suite and test case is reported individually. This is
    the default.

`dotted`
    Only show `.` for passed test, `F` for failed tests, `s` for skipped
    tests and `x` for tests which are skipped because
    `test execution exit`__. Failed tests are listed separately
    after execution. This output type makes it easy to see are there any
    failures during execution even if there would be a lot of tests.

`quiet`
    No output except for `errors and warnings`_.

`none`
    No output whatsoever. Useful when creating a custom output using,
    for example, listeners_.

__ `Stopping test execution gracefully`_

Separate convenience options :option:`--dotted (-.)` and :option:`--quiet`
are shortcuts for `--console dotted` and `--console quiet`, respectively.

Examples::

    robot --console quiet tests.robot
    robot --dotted tests.robot

Console width
~~~~~~~~~~~~~

The width of the test execution output in the console can be set using
the option :option:`--consolewidth (-W)`. The default width is 78 characters.

.. tip:: On many UNIX-like machines you can use handy `$COLUMNS`
         environment variable like `--consolewidth $COLUMNS`.

Console colors
~~~~~~~~~~~~~~

The :option:`--consolecolors (-C)` option is used to control whether
colors should be used in the console output. Colors are implemented
using `ANSI colors`__ except on Windows where, by default, Windows
APIs are used instead.

This option supports the following case-insensitive values:

`auto`
    Colors are enabled when outputs are written into the console, but not
    when they are redirected into a file or elsewhere. This is the default.

`on`
    Colors are used also when outputs are redirected. Does not work on Windows.

`ansi`
    Same as `on` but uses ANSI colors also on Windows. Useful, for example,
    when redirecting output to a program that understands ANSI colors.

`off`
    Colors are disabled.

__ http://en.wikipedia.org/wiki/ANSI_escape_code

Console markers
~~~~~~~~~~~~~~~

Special markers `.` (success) and
`F` (failure) are shown on the console when using the `verbose output`__
and top level keywords in test cases end. The markers allow following
the test execution in high level, and they are erased when test cases end.

It is possible to configure when markers
are used with :option:`--consolemarkers (-K)` option. It supports the following
case-insensitive values:

`auto`
    Markers are enabled when the standard output is written into the console,
    but not when it is redirected into a file or elsewhere. This is the default.

`on`
    Markers are always used.

`off`
    Markers are disabled.

__ `Console output type`_

Setting listeners
-----------------

Listeners_ can be used to monitor the test execution. When they are taken into
use from the command line, they are specified using the :option:`--listener`
command line option. The value can either be a path to a listener or
a listener name. See the `Listener interface`_ section for more details
about importing listeners and using them in general.
