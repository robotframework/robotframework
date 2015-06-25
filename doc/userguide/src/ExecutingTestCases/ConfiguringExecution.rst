Configuring execution
=====================

This section explains different command line options that can be used
for configuring the `test execution`_ or `post-processing
outputs`_. Options related to generated output files are discussed in
the `next section`__.

__ `Created outputs`_

.. contents::
   :depth: 2
   :local:

Selecting test cases
--------------------

Robot Framework offers several command line options for selecting
which test cases to execute. The same options also work when
post-processing outputs with the ``rebot`` tool.

By test suite and test case names
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Test suites and test cases can be selected by their names with the command
line options :option:`--suite (-s)` and :option:`--test (-t)`,
respectively.  Both of these options can be used several times to
select several test suites or cases. Arguments to these options are
case- and space-insensitive, and there can also be `simple
patterns`_ matching multiple names.  If both the :option:`--suite` and
:option:`--test` options are used, only test cases in matching suites
with matching names are selected.

::

  --test Example
  --test mytest --test yourtest
  --test example*
  --test mysuite.mytest
  --test *.suite.mytest
  --suite example-??
  --suite mysuite --test mytest --test your*

Using the :option:`--suite` option is more or less the same as executing only
the appropriate test case file or directory. One major benefit is the
possibility to select the suite based on its parent suite. The syntax
for this is specifying both the parent and child suite names separated
with a dot. In this case, the possible setup and teardown of the parent
suite are executed.

::

  --suite parent.child
  --suite myhouse.myhousemusic --test jack*

Selecting individual test cases with the :option:`--test` option is very
practical when creating test cases, but quite limited when running tests
automatically. The :option:`--suite` option can be useful in that
case, but in general, selecting test cases by tag names is more
flexible.

By tag names
~~~~~~~~~~~~

It is possible to include and exclude test cases by tag_ names with the
:option:`--include (-i)` and :option:`--exclude (-e)` options, respectively.
If the :option:`--include` option is used, only test cases having a matching
tag are selected, and with the :option:`--exclude` option test cases having a
matching tag are not. If both are used, only tests with a tag
matching the former option, and not with a tag matching the latter,
are selected.

::

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

Re-executing failed test cases
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Command line option :option:`--rerunfailed (-R)` can be used to select all failed
tests from an earlier `output file`_ for re-execution. This option is useful,
for example, if running all tests takes a lot of time and one wants to
iteratively fix failing test cases.

::

  pybot tests                             # first execute all tests
  pybot --rerunfailed output.xml tests    # then re-execute failing

Behind the scenes this option selects the failed tests as they would have been
selected individually with the :option:`--test` option. It is possible to further
fine-tune the list of selected tests by using :option:`--test`, :option:`--suite`,
:option:`--include` and :option:`--exclude` options.

Using an output not originating from executing the same tests that are run
now causes undefined results. Additionally, it is an error if the output
contains no failed tests. Using a special value `NONE` as the output
is same as not specifying this option at all.

.. tip:: Re-execution results and original results can be `merged together`__
         using the :option:`--merge` command line option.

.. note:: Re-executing failed tests is a new feature in Robot Framework 2.8.
          Prior Robot Framework 2.8.4 the option was named :option:`--runfailed`.
          The old name still works, but it will be removed in the future.

__ `Merging outputs`_

When no tests match selection
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

By default when no tests match the selection criteria test execution fails
with an error like::

    [ ERROR ] Suite 'Example' with includes 'xxx' contains no test cases.

Because no outputs are generated, this behavior can be problematic if tests
are executed and results processed automatically. Luckily a command line
option :option:`--RunEmptySuite` can be used to force the suite to be executed
also in this case. As a result normal outputs are created but show zero
executed tests. The same option can be used also to alter the behavior when
an empty directory or a test case file containing no tests is executed.

Similar situation can occur also when processing output files with rebot_.
It is possible that no test match the used filtering criteria or that
the output file contained no tests to begin with. By default executing
``rebot`` fails in these cases, but it has a separate
:option:`--ProcessEmptySuite` option that can be used to alter the behavior.
In practice this option works the same way as :option:`--RunEmptySuite` when
running tests.

.. note:: :option:`--ProcessEmptySuite` option was added in Robot Framework 2.7.2.

Setting criticality
-------------------

The final result of test execution is determined based on
critical tests. If a single critical test fails, the whole test run is
considered failed. On the other hand, non-critical test cases can
fail and the overall status is still considered passed.

All test cases are considered critical by default, but this can be changed
with the :option:`--critical (-c)` and :option:`--noncritical (-n)`
options. These options specify which tests are critical
based on tags_, similarly as :option:`--include` and
:option:`--exclude` are used to `select tests by tags`__.
If only :option:`--critical` is used, test cases with a
matching tag are critical. If only :option:`--noncritical` is used,
tests without a matching tag are critical. Finally, if both are
used, only test with a critical tag but without a non-critical tag are
critical.

Both :option:`--critical` and :option:`--noncritical` also support same `tag
patterns`_ as :option:`--include` and :option:`--exclude`. This means that pattern
matching is case, space, and underscore insensitive, `*` and `?`
are supported as wildcards, and `AND`, `OR` and `NOT`
operators can be used to create combined patterns.

::

  --critical regression
  --noncritical not_ready
  --critical iter-* --critical req-* --noncritical req-6??

The most common use case for setting criticality is having test cases
that are not ready or test features still under development in the
test execution. These tests could also be excluded from the
test execution altogether with the :option:`--exclude` option, but
including them as non-critical tests enables you to see when
they start to pass.

Criticality set when tests are
executed is not stored anywhere. If you want to keep same criticality
when `post-processing outputs`_ with ``rebot``, you need to
use :option:`--critical` and/or :option:`--noncritical` also with it::

  # Use rebot to create new log and report from the output created during execution
  pybot --critical regression --outputdir all my_tests.html
  rebot --name Smoke --include smoke --critical regression --outputdir smoke all/output.xml

  # No need to use --critical/--noncritical when no log or report is created
  jybot --log NONE --report NONE my_tests.html
  rebot --critical feature1 output.xml

__ `By tag names`_

Setting metadata
----------------

Setting the name
~~~~~~~~~~~~~~~~

When Robot Framework parses test data, `test suite names are created
from file and directory names`__. The name of the top-level test suite
can, however, be overridden with the command line option
:option:`--name (-N)`. Underscores in the given name are converted to
spaces automatically, and words in the name capitalized.

__ `Test suite name and documentation`_


Setting the documentation
~~~~~~~~~~~~~~~~~~~~~~~~~

In addition to `defining documentation in the test data`__, documentation
of the top-level suite can be given from the command line with the
option :option:`--doc (-D)`. Underscores in the given documentation
are converted to spaces, and it may contain simple `HTML formatting`_.

__ `Test suite name and documentation`_

Setting free metadata
~~~~~~~~~~~~~~~~~~~~~

`Free test suite metadata`_ may also be given from the command line with the
option :option:`--metadata (-M)`. The argument must be in the format
`name:value`, where `name` the name of the metadata to set and
`value` is its value. Underscores in the name and value are converted to
spaces, and the latter may contain simple `HTML formatting`_. This option may
be used several times to set multiple metadata.

Setting tags
~~~~~~~~~~~~

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
When importing Java based libraries or other extensions on Jython, Java
classpath is used in addition to the normal module search path.

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

``PYTHONPATH``, ``JYTHONPATH`` and ``IRONPYTHONPATH``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Python, Jython and IronPython read additional locations to be added to
the module search path from ``PYTHONPATH``, ``JYTHONPATH`` and
``IRONPYTHONPATH`` environment variables, respectively. If you want to
specify more than one location in any of them, you need to separate
the locations with a colon on UNIX-like machines (e.g.
`/opt/libs:$HOME/testlibs`) and with a semicolon on Windows (e.g.
`D:\libs;%HOMEPATH%\testlibs`).

Environment variables can be configured permanently system wide or so that
they affect only a certain user. Alternatively they can be set temporarily
before running a command, something that works extremely well in custom
`start-up scripts`_.

.. note:: Prior to Robot Framework 2.9, contents of ``PYTHONPATH`` environment
          variable were added to the module search path by the framework itself
          when running on Jython and IronPython. Nowadays that is not done
          anymore and ``JYTHONPATH`` and ``IRONPYTHONPATH`` must be used with
          these interpreters.

Using `--pythonpath` option
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Robot Framework has a separate command line option :option:`--pythonpath (-P)`
for adding locations to the module search path. Although the option name has
the word Python in it, it works also on Jython and IronPython.

Multiple locations can be given by separating them with a colon, regardless
the operating system, or by using this option several times. The given path
can also be a glob pattern matching multiple paths, but then it typically
needs to be escaped__.

__ `Escaping complicated characters`_

Examples::

   --pythonpath libs
   --pythonpath /opt/testlibs:mylibs.zip:yourlibs
   --pythonpath mylib.jar --pythonpath lib/STAR.jar --escape star:STAR

Configuring `sys.path` programmatically
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Python interpreters store the module search path they use as a list of strings
in `sys.path <https://docs.python.org/2/library/sys.html#sys.path>`__
attribute. This list can be updated dynamically during execution, and changes
are taken into account next time when something is imported.

Java classpath
~~~~~~~~~~~~~~

When libraries implemented in Java are imported with Jython, they can be
either in Jython's normal module search path or in `Java classpath`__. The most
common way to alter classpath is setting the ``CLASSPATH`` environment variable
similarly as ``PYTHONPATH``, ``JYTHONPATH`` or ``IRONPYTHONPATH``.
Alternatively it is possible to use Java's :option:`-cp` command line option.
This option is not exposed to the ``jybot`` `runner script`_, but it is
possible to use it with Jython by adding :option:`-J` prefix like
`jython -J-cp example.jar -m robot.run tests.robot`.

When using the standalone JAR distribution, the classpath has to be set a
bit differently, due to the fact that `java -jar` command does support
the ``CLASSPATH`` environment variable nor the :option:`-cp` option. There are
two different ways to configure the classpath::

  java -cp lib/testlibrary.jar:lib/app.jar:robotframework-2.9.jar org.robotframework.RobotFramework tests.robot
  java -Xbootclasspath/a:lib/testlibrary.jar:lib/app.jar -jar robotframework-2.9.jar tests.robot

__ https://docs.oracle.com/javase/8/docs/technotes/tools/findingclasses.html

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

.. note:: The dry run mode does not validate variables. This
          limitation may be lifted in the future releases.

__ `Errors and warnings during execution`_

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

Starting from Robot Framework 2.8.5, it is possible to give a custom seed
to initialize the random generator. This is useful if you want to re-run tests
using the same order as earlier. The seed is given as part of the value for
:option:`--randomize` in format `<what>:<seed>` and it must be an integer.
If no seed is given, it is generated randomly. The executed top level test
suite automatically gets metadata__ named :name:`Randomized` that tells both
what was randomized and what seed was used.

Examples::

    pybot --randomize tests my_test.txt
    pybot --randomize all:12345 path/to/tests

__ `Free test suite metadata`_

Programmatic modification of test data
--------------------------------------

If the provided built-in features to modify test data before execution
are not enough, Robot Framework 2.9 and newer provide a possible to do
custom modifications programmatically. This is accomplished by creating
a model modifier and activating it using the :option:`--prerunmodifier`
option.

Model modifiers should be implemented as visitors that can traverse through
the executable test suite structure and modify it as needed. The visitor
interface is explained as part of the `Robot Framework API documentation`__,
and the example below ought to give an idea of how it can be used and how
powerful this functionality is.

.. sourcecode:: python

   ../api/code_examples/select_every_xth_test.py

When a model modifier is taken into use on the command line using the
:option:`--prerunmodifier` option, it can be specified either as a name of
the modifier class or a path to the modifier file. If the modifier is given
as a class name, the module containing the class must be in the `module search
path`_, and if the module name is different than the class name, the given
name must include both like `module.ModifierClass`. If the modifier is given
as a path, the class name must be same as the file name. For most parts this
works exactly like when `specifying a test library to import`__.

If a modifier requires arguments, like the example above does, they can be
specified after the modifier name or path using either a colon (`:`) or a
semicolon (`;`) as a separator. If both are used in the value, the one first
is considered the actual separator.

For example, if the above model modifier would be in a file
:file:`SelectEveryXthTest.py`, it could be used like this::

    # Specify the modifier as a path. Run every second test.
    pybot --prerunmodifier path/to/SelectEveryXthTest.py:2 tests.robot

    # Specify the modifier as a name. Run every third test, starting from the second.
    # SelectEveryXthTest.py must be in the module search path.
    pybot --prerunmodifier SelectEveryXthTest:3:1 tests.robot

If more than one model modifier is needed, they can be specified by using
the :option:`--prerunmodifier` option multiple times. If similar modifying
is needed before creating results, `programmatic modification of results`_
can be enabled using the :option:`--prerebotmodifier` option.

__ https://robot-framework.readthedocs.org/en/latest/autodoc/robot.model.html#module-robot.model.visitor
__ `Specifying library to import`_

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
    Only show `.` for passed test, `f` for failed non-critical tests, `F`
    for failed critical tests, and `x` for tests which are skipped because
    `test execution exit`__. Failed critical tests are listed separately
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

    pybot --console quiet tests.robot
    jybot --dotted tests.robot

.. note:: :option:`--console`, :option:`--dotted` and :option:`--quiet`
          are new options in Robot Framework 2.9. Prior to that the output
          was always the same as in the current `verbose` mode.

Console width
~~~~~~~~~~~~~

The width of the test execution output in the console can be set using
the option :option:`--consolewidth (-W)`. The default width is 78 characters.

.. tip:: On many UNIX-like machines you can use handy `$COLUMNS`
         environment variable like `--consolewidth $COLUMNS`.

.. note:: Prior to Robot Framework 2.9 this functionality was enabled with
          :option:`--monitorwidth` option that is nowadays deprecated.
          The short option :option:`-W` works the same way in all versions.

Console colors
~~~~~~~~~~~~~~

The :option:`--consolecolors (-C)` option is used to control whether
colors should be used in the console output. Colors are implemented
using `ANSI colors`__ except on Windows where, by default, Windows
APIs are used instead. Accessing these APIs from Jython is not possible,
and as a result colors do not work with Jython on Windows.

This option supports the following case-insensitive values:

`auto`
    Colors are enabled when outputs are written into the console, but not
    when they are redirected into a file or elsewhere. This is the default.

`on`
    Colors are used also when outputs are redirected. Does not work on Windows.

`ansi`
    Same as `on` but uses ANSI colors also on Windows. Useful, for example,
    when redirecting output to a program that understands ANSI colors.
    New in Robot Framework 2.7.5.

`off`
    Colors are disabled.

.. note:: Prior to Robot Framework 2.9 this functionality was enabled with
          :option:`--monitorcolors` option that is nowadays deprecated.
          The short option :option:`-C` works the same way in all versions.

__ http://en.wikipedia.org/wiki/ANSI_escape_code

Console markers
~~~~~~~~~~~~~~~

Starting from Robot Framework 2.7, special markers `.` (success) and
`F` (failure) are shown on the console when using the `verbose output`__
and top level keywords in test cases end. The markers allow following
the test execution in high level, and they are erased when test cases end.

Starting from Robot Framework 2.7.4, it is possible to configure when markers
are used with :option:`--consolemarkers (-K)` option. It supports the following
case-insensitive values:

`auto`
    Markers are enabled when the standard output is written into the console,
    but not when it is redirected into a file or elsewhere. This is the default.

`on`
    Markers are always used.

`off`
    Markers are disabled.

.. note:: Prior to Robot Framework 2.9 this functionality was enabled with
          :option:`--monitormarkers` option that is nowadays deprecated.
          The short option :option:`-K` works the same way in all versions.

__ `Console output type`_

Setting listeners
-----------------

Listeners_ can be used to monitor the test execution. When they are taken into
use from the command line, they are specified using the :option:`--listener`
command line option. The value can either be a path to a listener or
a listener name. See the `Using listener interface`_ section for more details
about importing listeners and using them in general.
