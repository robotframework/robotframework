Test execution
==============

This section describes how the test suite structure created from the parsed
test data is executed, how test status is determined, and how to continue
executing a test case if there are failures, and how to stop the whole test
execution gracefully.

.. contents::
   :depth: 2
   :local:

Execution flow
--------------

Executed suites and tests
~~~~~~~~~~~~~~~~~~~~~~~~~

Test cases are always executed within a test suite. A test suite
created from a `suite file`_ has tests directly, whereas suites
created from directories__ have child test suites which either have
tests or their own child suites. By default all the tests in an
executed suite are run, but it is possible to `select tests`__ using
options :option:`--test`, :option:`--suite`, :option:`--include` and
:option:`--exclude`. Suites containing no tests are ignored.

The execution starts from the top-level test suite. If the suite has
tests they are executed one-by-one, and if it has suites they are
executed recursively in depth-first order. When an individual test
case is executed, the keywords it contains are run in a
sequence. Normally the execution of the current test ends if any
of the keywords fails, but it is also possible to
`continue after failures`__. The exact `execution order`_ and how
possible `setups and teardowns`_ affect the execution are discussed
in the following sections.

__ `Suite directories`_
__ `Selecting test cases`_
__ `Continue on failure`_


Setups and teardowns
~~~~~~~~~~~~~~~~~~~~

Setups and teardowns can be used on `test suite`__, `test case`__ and
`user keyword`__ levels.

__ `Suite setup and teardown`_
__ `Test setup and teardown`_
__ `User keyword setup and teardown`_

Suite setup
'''''''''''

If a test suite has a setup, it is executed before its tests and child
suites. If the suite setup passes, test execution continues
normally. If it fails, all the test cases the suite and its child
suites contain are marked failed. The tests and possible suite setups
and teardowns in the child test suites are not executed.

Suite setups are often used for setting up the test environment.
Because tests are not run if the suite setup fails, it is easy to use
suite setups for verifying that the environment is in state in which the
tests can be executed.

Suite teardown
''''''''''''''

If a test suite has a teardown, it is executed after all its test
cases and child suites. Suite teardowns are executed regardless of the
test status and even if the matching suite setup fails. If the suite
teardown fails, all tests in the suite are marked failed afterwards in
reports and logs.

Suite teardowns are mostly used for cleaning up the test environment
after the execution. To ensure that all these tasks are done, `all the
keywords used in the teardown are executed`__ even if some of them
fail.

__ `Continue on failure`_

Test setup
''''''''''

Possible test setup is executed before the keywords of the test case.
If the setup fails, the keywords are not executed. The main use
for test setups is setting up the environment for that particular test
case.

Test teardown
'''''''''''''

Possible test teardown is executed after the test case has been
executed. It is executed regardless of the test status and also
if test setup has failed.

Similarly as suite teardown, test teardowns are used mainly for
cleanup activities. Also they are executed fully even if some of their
keywords fail.

User keyword setup
''''''''''''''''''

User keyword setup is executed before the keyword body. If the setup fails,
the body is not executed. There is not much difference between the keyword
setup and the first keyword in the body.

.. note:: User keyword setups are new in Robot Framework 7.0.

User keyword teardown
'''''''''''''''''''''

User keyword teardown is run after the keyword is executed otherwise, regardless
the status. User keyword teardowns are executed fully even if some of their
keywords would fail.

Execution order
~~~~~~~~~~~~~~~

Test cases in a test suite are executed in the same order as they are defined
in the test case file. Test suites inside a higher level test suite are
executed in case-insensitive alphabetical order based on the file or directory
name. If multiple files and/or directories are given from the command line,
they are executed in the order they are given.

If there is a need to use certain test suite execution order inside a
directory, it is possible to add prefixes like :file:`01` and
:file:`02` into file and directory names. Such prefixes are not
included in the generated test suite name if they are separated from
the base name of the suite with two underscores::

   01__my_suite.robot -> My Suite
   02__another_suite.robot -> Another Suite

If the alphabetical ordering of test suites inside suites is
problematic, a good workaround is giving them separately in the
required order. This easily leads to overly long start-up commands,
but `argument files`_ allow listing files nicely one file per line.

It is also possible to `randomize the execution order`__ using
the :option:`--randomize` option.

__ `Randomizing execution order`_

Test and suite statuses
-----------------------

This section explains how tests can get PASS_, FAIL_ or SKIP_ status and how the
`suite status`_ is determined based on test statuses.

.. note:: The SKIP status is new in Robot Framework 4.0.

PASS
~~~~

A test gets the PASS status if it is executed and none of the keywords it contains fails.

Prematurely passing tests
'''''''''''''''''''''''''

Normally all keywords are executed, but it is also possible to use
BuiltIn_ keywords :name:`Pass Execution` and :name:`Pass Execution If` to stop
execution with the PASS status and not run the remaining keywords.

How :name:`Pass Execution` and :name:`Pass Execution If` behave
in different situations is explained below:

- When used in any `setup or teardown`__ (suite, test or keyword), these
  keywords pass that setup or teardown. Possible teardowns of the started
  keywords are executed. Test execution or statuses are not affected otherwise.

- When used in a test case outside setup or teardown, the keywords pass that
  particular test case. Possible test and keyword teardowns are executed.

- Possible `continuable failures`__ that occur before these keyword are used,
  as well as failures in teardowns executed afterwards, will fail the execution.

- It is mandatory to give an explanation message
  why execution was interrupted, and it is also possible to
  modify test case tags. For more details, and usage examples, see the
  `documentation of these keywords`__.

Passing execution in the middle of a test, setup or teardown should be
used with care. In the worst case it leads to tests that skip all the
parts that could actually uncover problems in the tested application.
In cases where execution cannot continue do to external factors,
it is often safer to skip_ the test.

__ `Setups and teardowns`_
__ `Continue on failure`_
__ `BuiltIn`_

FAIL
~~~~

The most common reason for a test to get the FAIL status is that one of the keywords
it contains fails. The keyword itself can fail by `raising an exception`__ or the
keyword can be called incorrectly. Other reasons for failures include syntax errors
and the test being empty.

If a `suite setup`_ fails, tests in that suite are marked failed without running them.
If a `suite teardown`_ fails, tests are marked failed retroactively.

__ `Reporting keyword status`_

.. _skipped:

SKIP
~~~~

Starting from Robot Framework 4.0, tests can get also SKIP status in addition to
PASS and FAIL. There are many different ways to get this status.

Skipping before execution
'''''''''''''''''''''''''

The command line option :option:`--skip` can be used to skip specified tests without
running them at all. It works based on tags_ and supports `tag patterns`_ like
`examp??` and `tagANDanother`. If it is used multiple times, all tests matching any of
specified tags or tag patterns are skipped::

    --skip require-network
    --skip windowsANDversion9?
    --skip python2.* --skip python3.[0-6]

Starting from Robot Framework 5.0, a test case can also be skipped by tagging
the test with the reserved tag `robot:skip`:

.. sourcecode:: robotframework

   *** Test Cases ***
   Example
       [Tags]    robot:skip
       Log       This is not executed

The difference between :option:`--skip` and :option:`--exclude` is that with
the latter tests are `omitted from the execution altogether`__ and they will not
be shown in logs and reports. With the former they are included, but not actually
executed, and they will be visible in logs and reports.

__ `By tag names`_

Skipping dynamically during execution
'''''''''''''''''''''''''''''''''''''

Tests can get the skip status during execution in various ways:

- Using the BuiltIn_ keyword :name:`Skip` anywhere in the test case, including setup or
  teardown. Using :name:`Skip` keyword has two effects: the test gets the SKIP status
  and rest of the test is not executed. However, if the test has a teardown, it will be
  run.

- Using the BuiltIn_ keyword :name:`Skip If` which takes a condition and skips the test
  if the condition is true.

- `Library keywords`_ may also trigger skip behavior by using a special exceptions.
  This is explained the `Skipping tests`_ section in the `Creating test libraries`_
  chapter.

- If `suite setup`_ is skipped using any of the above means, all tests in the suite
  are skipped without executing them.

- If `suite teardown`_ is skipped, all tests will be marked skipped retroactively.

Automatically skipping failed tests
'''''''''''''''''''''''''''''''''''

The command line option :option:`--skiponfailure` can be used to automatically mark
failed tests skipped. It works based on tags_ and supports `tag patterns`_ like
the :option:`--skip` option discussed above::

    --skiponfailure not-ready
    --skiponfailure experimentalANDmobile

Starting from RF 5.0, the reserved tag `robot:skip-on-failure` can alternatively be used to
achieve the same effect as above:

.. sourcecode:: robotframework

   *** Test Cases ***
   Example
       [Tags]    robot:skip-on-failure
       Fail      this test will be marked as skipped instead of failed

The motivation for this functionality is allowing execution of tests that are not yet
ready or that are testing a functionality that is not yet ready. Instead of such tests
failing, they will be marked skipped and their tags can be used to separate them
from possible other skipped tests.

Migrating from criticality to SKIP
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Earlier Robot Framework versions supported criticality concept that allowed marking
tests critical or non-critical. By default all tests were critical, but the
:option:`--critical` and :option:`--noncritical` options could be used to configure that.
The difference between critical and non-critical tests was that non-critical tests
were not included when determining the final status for an executed test suite or
for the whole test run. In practice the test status was two dimensional having
PASS and FAIL in one axis and criticality on the other.

Non-critical failed tests were in many ways similar to the current skipped tests.
Because these features are similar and having both SKIP and criticality would
have created strange test statuses like non-critical SKIP, the criticality concept
was removed in Robot Framework 4.0 when the SKIP status was introduced. The problems
with criticality are explained in more detail in the `issue that proposed removing it`__.

__ https://github.com/robotframework/robotframework/issues/3624

The main use case for the criticality concept was being able to run tests that
are not yet ready or that are testing a functionality that is not yet ready. This
use case is nowadays covered by the skip-on-failure functionality discussed in
the previous section.

To ease migrating from criticality to skipping, the old :option:`--noncritical`
option worked as an alias for the new :option:`--skiponfailure` in Robot Framework 4.0
and also the old :option:`--critical` option was preserved. Both old options
were deprecated and they were removed in Robot Framework 5.0.

Suite status
~~~~~~~~~~~~

Suite status is determined solely based on statuses of the tests it contains:

- If any test has failed, suite status is FAIL.
- If there are no failures but at least one test has passed, suite status is PASS.
- If all tests have been skipped or the are no tests at all, suite status is SKIP.

.. _continue on failure:

Continuing on failure
---------------------

Normally test cases are stopped immediately when any of their keywords
fail. This behavior shortens test execution time and prevents
subsequent keywords hanging or otherwise causing problems if the
system under test is in unstable state. This has a drawback that often
subsequent keywords would give more information about the state of the
system, though, and in some cases those subsequent keywords would actually
take care of the needed cleanup activities. Hence Robot Framework offers
several features to continue even if there are failures.

Execution continues on teardowns automatically
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

To make it sure that all the cleanup activities are taken care of, the
continue-on-failure mode is automatically enabled in `suite, test and keyword
teardowns`__. In practice this means that in teardowns all the
keywords in all levels are always executed.

If this behavior is not desired, the special `robot:stop-on-failure` and
`robot:recursive-stop-on-failure` tags can be used to `disable it`__.

__ `Setups and teardowns`_
__ `Disabling continue-on-failure using tags`_

All top-level keywords are executed when tests have templates
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

When using `test templates`_, all the top-level keywords are executed to
make it sure that all the different combinations are covered. In this
usage continuing is limited to the top-level keywords, and inside them
the execution ends normally if there are non-continuable failures.

.. sourcecode:: robotframework

   *** Test Cases ***
   Continue with templates
       [Template]    Should be Equal
       this    fails
       this    is run

If this behavior is not desired, the special `robot:stop-on-failure` and
`robot:recursive-stop-on-failure` tags can be used to `disable it`__.

__ `Disabling continue-on-failure using tags`_

Special failures from keywords
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

`Library keywords`_ report failures using exceptions, and it is
possible to use special exceptions to tell Robot Framework that
execution can continue regardless the failure. How these exceptions
can be created is explained in the `Continuable failures`_ section in
the `Creating test libraries`_ section.

When a test ends and there have been continuable failures,
the test will be marked failed. If there are more than one failure,
all of them will be enumerated in the final error message::

  Several failures occurred:

  1) First error message.

  2) Second error message.

Test execution ends also if a normal failure occurs after a continuable
failure. Also in that case all the failures will be listed in the
final error message.

The return value from failed keywords, possibly assigned to a
variable, is always the Python `None`.

:name:`Run Keyword And Continue On Failure` keyword
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

BuiltIn_ keyword :name:`Run Keyword And Continue On Failure` allows
converting any failure into a continuable failure. These failures are
handled by the framework exactly the same way as continuable failures
originating from library keywords discussed above.

.. sourcecode:: robotframework

   *** Test Cases ***
   Example
       Run Keyword and Continue on Failure    Should be Equal    1    2
       Log    This is executed but test fails in the end

Enabling continue-on-failure using tags
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

All keywords executed as part of test cases or user keywords which are
tagged with the `robot:continue-on-failure` tag are considered continuable
by default. For example, the following two tests behave identically:

.. sourcecode:: robotframework

   *** Test Cases ***
   Test 1
       Run Keyword and Continue on Failure    Should be Equal    1    2
       User Keyword 1

   Test 2
       [Tags]    robot:continue-on-failure
       Should be Equal    1    2
       User Keyword 2

   *** Keywords ***
   User Keyword 1
       Run Keyword and Continue on Failure    Should be Equal    3    4
       Log    This is executed

   User Keyword 2
       [Tags]    robot:continue-on-failure
       Should be Equal    3    4
       Log    This is executed

These tags also affect the continue-on-failure mode with different `control
structures`_. For example, the below test case will execute the
:name:`Do Something` keyword ten times regardless does it succeed or not:

.. sourcecode:: robotframework

   *** Test Cases ***
   Example
       [Tags]    robot:continue-on-failure
       FOR    ${index}    IN RANGE    10
           Do Something
       END

Setting `robot:continue-on-failure` within a test case or a user keyword
will not propagate the continue-on-failure behavior into user keywords
they call. If such recursive behavior is needed, the
`robot:recursive-continue-on-failure` tag can be used. For example, all
keywords in the following example are executed:

.. sourcecode:: robotframework

   *** Test Cases ***
   Example
       [Tags]    robot:recursive-continue-on-failure
       Should be Equal    1    2
       User Keyword 1
       Log    This is executed

   *** Keywords ***
   User Keyword 1
       Should be Equal    3    4
       User Keyword 2
       Log    This is executed

   User Keyword 2
       Should be Equal    5    6
       Log    This is executed

Setting `robot:continue-on-failure` or `robot:recursive-continue-on-failure` in a
test case does NOT alter the behaviour of a failure in the keyword(s) executed
as part of the `[Setup]`:setting:: The test case is marked as failed and no
test case keywords are executed.

.. note:: The `robot:continue-on-failure` and `robot:recursive-continue-on-failure`
          tags are new in Robot Framework 4.1. They do not work properly with
          `WHILE` loops prior to Robot Framework 6.0.

Disabling continue-on-failure using tags
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Special tags `robot:stop-on-failure` and `robot:recursive-stop-on-failure`
can be used to disable the continue-on-failure mode if needed. They work
when `continue-on-failure has been enabled using tags`__ and also with
teardowns__ and templates__:

__ `Enabling continue-on-failure using tags`_
__ `Execution continues on teardowns automatically`_
__ `All top-level keywords are executed when tests have templates`_

.. sourcecode:: robotframework

   *** Test Cases ***
   Disable continue-in-failure set using tags
       [Tags]    robot:recursive-continue-on-failure
       Keyword
       Keyword    # This is executed

   Disable continue-in-failure in teardown
       No Operation
       [Teardown]    Keyword

   Disable continue-in-failure with templates
       [Tags]    robot:stop-on-failure
       [Template]    Should be Equal
       this    fails
       this    is not run

   *** Keywords ***
   Keyword
       [Tags]    robot:stop-on-failure
       Should be Equal    this    fails
       Should be Equal    this    is not run

The `robot:stop-on-failure` tag affects only test cases and user keywords
where it is used and does not propagate to user keywords they call nor to
their own teardowns. If recursive behavior affecting all called user keywords
and teardowns is desired, the `robot:recursive-stop-on-failure` tag can be
used instead. If there is a need, its effect can again be disabled in lower
level keywords by using `robot:continue-on-failure` or
`robot:recursive-continue-on-failure` tags.

The `robot:stop-on-failure` and `robot:recursive-stop-on-failure` tags do not
alter the behavior of continuable failures caused by `library keywords`__ or
by `Run Keyword And Continue On Failure`__. For example, both keywords in this
example are run even though `robot:stop-on-failure` is used:

.. sourcecode:: robotframework

   *** Test Cases ***
   Example
       [Tags]    robot:stop-on-failure
       Run Keyword and Continue on Failure    Should be Equal    1    2
       Log    This is executed regardless the tag

If `robot:recursive-stop-on-failure` and `robot:continue-on-failure` are used
together in the same test or keyword, execution is stopped in called keywords
if there are failures, but continues in the test or keyword using these tags.
If `robot:recursive-continue-on-failure` and `robot:stop-on-failure` are used
together in the same test or keyword, execution is continued in called keywords
if there are failures, but stopped in the test or keyword using these tags.

__ `Special failures from keywords`_
__ `Run Keyword And Continue On Failure keyword`_

.. note:: The `robot:stop-on-failure` and `robot:recursive-stop-on-failure`
          tags are new in Robot Framework 6.0.

.. note:: Using recursive and non-recursive tags together in same test or
          keyword is new in Robot Framework 7.0.

TRY/EXCEPT
~~~~~~~~~~

Robot Framework 5.0 introduced native `TRY/EXCEPT` syntax that can be used for
handling failures:

.. sourcecode:: robotframework

    *** Test Cases ***
    Example
        TRY
            Some Keyword
        EXCEPT    Expected error message
            Error Handler Keyword
        END

For more details see the separate `TRY/EXCEPT syntax`_ section.

BuiltIn keywords
~~~~~~~~~~~~~~~~

There are several BuiltIn_ keywords that can be used to execute other keywords
so that execution can continue after possible failures:

- :name:`Run Keyword And Expect Error` executes a keyword and expects it to fail
  with the specified error message. The aforementioned `TRY/EXCEPT` syntax is
  nowadays generally recommended instead.

- :name:`Run Keyword And Ignore Error` executes a keyword and silences possible
  error. It returns the status along with possible keyword return value or
  error message. The `TRY/EXCEPT` syntax generally works better in this case
  as well.

- :name:`Run Keyword And Warn On Failure` is a wrapper for
  :name:`Run Keyword And Ignore Error` that automatically logs a warning
  if the executed keyword fails.

- :name:`Run Keyword And Return Status` executes a keyword and returns Boolean
  `True` or `False` depending on did it pass or fail.

Stopping test execution gracefully
----------------------------------

Sometimes there is a need to stop the test execution before all the tests
have finished, but so that logs and reports are created. Different ways how
to accomplish this are explained below. In all these cases the remaining
test cases are marked failed.

The tests that are automatically failed get `robot:exit` tag and
the generated report will include `NOT robot:exit` `combined tag pattern`__
to easily see those tests that were not skipped. Note that the test in which
the exit happened does not get the `robot:exit` tag.

.. note:: Prior to Robot Framework 3.1, the special tag was named `robot-exit`.

__ `Generating combined tag statistics`_

Pressing `Ctrl-C`
~~~~~~~~~~~~~~~~~

The execution is stopped when `Ctrl-C` is pressed in the console
where the tests are running. The execution is stopped immediately,
but reports and logs are still generated.

If `Ctrl-C` is pressed again, the execution ends immediately and
reports and logs are not created.

Using signals
~~~~~~~~~~~~~

On UNIX-like machines it is possible to terminate test execution
using signals `INT` and `TERM`. These signals can be sent
from the command line using ``kill`` command, and sending signals can
also be easily automated.

Using keywords
~~~~~~~~~~~~~~

The execution can be stopped also by the executed keywords. There is a
separate :name:`Fatal Error` BuiltIn_ keyword for this purpose, and
custom keywords can use `fatal exceptions`__ when they fail.

__ `Stopping test execution`_

Stopping when first test case fails
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If option :option:`--exitonfailure (-X)` is used, test execution stops
immediately if any test fails. The remaining tests are marked
as failed without actually executing them.

Stopping on parsing or execution error
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Robot Framework separates *failures* caused by failing keywords from *errors*
caused by, for example, invalid settings or failed test library imports.
By default these errors are reported as `test execution errors`__, but errors
themselves do not fail tests or affect execution otherwise. If
:option:`--exitonerror` option is used, however, all such errors are considered
fatal and execution stopped so that remaining tests are marked failed. With
parsing errors encountered before execution even starts, this means that no
tests are actually run.

__ `Errors and warnings during execution`_

Handling teardowns
~~~~~~~~~~~~~~~~~~

By default teardowns of the tests and suites that have been started are
executed even if the test execution is stopped using one of the methods
above. This allows clean-up activities to be run regardless how execution
ends.

It is also possible to skip teardowns when execution is stopped by using
:option:`--skipteardownonexit` option. This can be useful if, for example,
clean-up tasks take a lot of time.
