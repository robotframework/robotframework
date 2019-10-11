Creating test suites
====================

Robot Framework `test cases`__ are created in test case files, which can
be organized into directories. These files and directories create a
hierarchical test suite structure. Same concepts apply also when
`creating tasks`_, but the terminology differs.

__ `Creating test cases`_

.. contents::
   :depth: 2
   :local:

Test case files
---------------

Robot Framework test cases `are created`__ using test case tables in
test case files. Such a file automatically creates a test suite from
all the test cases it contains. There is no upper limit for how many
test cases there can be, but it is recommended to have less than ten,
unless the `data-driven approach`_ is used, where one test case consists of
only one high-level keyword.

The following settings in the Setting table can be used to customize the
test suite:

`Documentation`:setting:
   Used for specifying a `test suite documentation`_
`Metadata`:setting:
   Used for setting `free test suite metadata`_ as name-value
   pairs.
`Suite Setup`:setting:, `Suite Teardown`:setting:
   Specify `suite setup and teardown`_.

.. note:: All setting names can optionally include a colon at the end, for
      example :setting:`Documentation:`. This can make reading the settings easier
      especially when using the plain text format.

.. note:: Setting names are case-insensitive, but the format used above is
      recommended. Settings used to be also space-insensitive, but that was
      deprecated in Robot Framework 3.1 and trying to use something like
      `M e t a d a t a` causes an error in Robot Framework 3.2.

__ `Creating test cases`_

Test suite directories
----------------------

Test case files can be organized into directories, and these
directories create higher-level test suites. A test suite created from
a directory cannot have any test cases directly, but it contains
other test suites with test cases, instead. These directories can then be
placed into other directories creating an even higher-level suite. There
are no limits for the structure, so test cases can be organized
as needed.

When a test directory is executed, the files and directories it
contains are processed recursively as follows:

- Files and directories with names starting with a dot (:file:`.`) or an
  underscore (:file:`_`) are ignored.
- Directories with the name :file:`CVS` are ignored (case-sensitive).
- Files in `supported file formats`_ are processed.
- Other files are ignored.

If a file or directory that is processed does not contain any test
cases, it is silently ignored (a message is written to the syslog_)
and the processing continues.

Initialization files
~~~~~~~~~~~~~~~~~~~~

A test suite created from a directory can have similar settings as a suite
created from a test case file. Because a directory alone cannot have that
kind of information, it must be placed into a special test suite initialization
file. An initialization file name must always be of the format
:file:`__init__.ext`, where the extension must be one of the `supported
file formats`_ (typically :file:`__init__.robot`).
The name format is borrowed from Python, where files named in this manner
denote that a directory is a module.

Initialization files have the same structure and syntax as test case files,
except that they cannot have test case tables and not all settings are
supported. Variables and keywords created or imported in initialization files
*are not* available in the lower level test suites. If you need to share
variables or keywords, you can put them into `resource files`_ that can be
imported both by initialization and test case files.

The main usage for initialization files is specifying test suite related
settings similarly as in `test case files`_, but setting some `test case
related settings`__ is also possible. How to use different settings in the
initialization files is explained below.

`Documentation`:setting:, `Metadata`:setting:, `Suite Setup`:setting:, `Suite Teardown`:setting:
   These test suite specific settings work the same way as in test case files.
`Force Tags`:setting:
   Specified tags are unconditionally set to all test cases in all test case files
   this directory contains directly or recursively.
`Test Setup`:setting:, `Test Teardown`:setting:, `Test Timeout`:setting:
   Set the default value for test setup/teardown or test timeout to all test
   cases this directory contains. Can be overridden on lower level.
   Notice that keywords used as setups and teardowns must be available in
   test case files where tests using them are. Defining keywords in the
   initialization file itself is not enough.
`Task Setup`:setting:, `Task Teardown`:setting:, `Task Timeout`:setting:
   Aliases for `Test Setup`:setting:, `Test Teardown`:setting:,
   and `Test Timeout`:setting:, respectively, that can be used when
   `creating tasks`_, not tests.
`Default Tags`:setting:, `Test Template`:setting:
   Not supported in initialization files.

.. sourcecode:: robotframework

   *** Settings ***
   Documentation    Example suite
   Suite Setup      Do Something    ${MESSAGE}
   Force Tags       example
   Library          SomeLibrary

   *** Variables ***
   ${MESSAGE}       Hello, world!

   *** Keywords ***
   Do Something
       [Arguments]    ${args}
       Some Keyword    ${arg}
       Another Keyword

__ `Test case related settings in the Setting table`_

Test suite name and documentation
---------------------------------

The test suite name is constructed from the file or directory name. The name
is created so that the extension is ignored, possible underscores are
replaced with spaces, and names fully in lower case are title cased. For
example, :file:`some_tests.robot` becomes :name:`Some Tests` and
:file:`My_test_directory` becomes :name:`My test directory`.

The file or directory name can contain a prefix to control the `execution
order`_ of the suites. The prefix is separated from the base name by two
underscores and, when constructing the actual test suite name, both
the prefix and underscores are removed. For example files
:file:`01__some_tests.robot` and :file:`02__more_tests.robot` create test
suites :name:`Some Tests` and :name:`More Tests`, respectively, and
the former is executed before the latter.

The documentation for a test suite is set using the :setting:`Documentation`
setting in the Setting table. It can be used in test case files
or, with higher-level suites, in test suite initialization files. Test
suite documentation has exactly the same characteristics regarding to where
it is shown and how it can be created as `test case
documentation`_.

.. sourcecode:: robotframework

   *** Settings ***
   Documentation    An example test suite documentation with *some* _formatting_.
   ...              See test documentation for more documentation examples.

Both the name and documentation of the top-level test suite can be
overridden in test execution. This can be done with the command line
options :option:`--name` and :option:`--doc`, respectively, as
explained in section `Setting metadata`_.

Free test suite metadata
------------------------

Test suites can also have other metadata than the documentation. This metadata
is defined in the Setting table using the :setting:`Metadata` setting. Metadata
set in this manner is shown in test reports and logs.

The name and value for the metadata are located in the columns following
:setting:`Metadata`. The value is handled similarly as documentation, which means
that it can be split `into several cells`__ (joined together with spaces)
or `into several rows`__ (joined together with newlines),
simple `HTML formatting`_ works and even variables_ can be used.

__ `Dividing test data to several rows`_
__ `Newlines in test data`_

.. sourcecode:: robotframework

   *** Settings ***
   Metadata    Version        2.0
   Metadata    More Info      For more information about *Robot Framework* see http://robotframework.org
   Metadata    Executed At    ${HOST}

For top-level test suites, it is possible to set metadata also with the
:option:`--metadata` command line option. This is discussed in more
detail in section `Setting metadata`_.

Suite setup and teardown
------------------------

Not only `test cases`__ but also test suites can have a setup and
a teardown. A suite setup is executed before running any of the suite's
test cases or child test suites, and a test teardown is executed after
them. All test suites can have a setup and a teardown; with suites created
from a directory they must be specified in a `test suite
initialization file`_.

__ `Test setup and teardown`_

Similarly as with test cases, a suite setup and teardown are keywords
that may take arguments. They are defined in the Setting table with
:setting:`Suite Setup` and :setting:`Suite Teardown` settings,
respectively. Keyword names and possible arguments are located in
the columns after the setting name.

If a suite setup fails, all test cases in it and its child test suites
are immediately assigned a fail status and they are not actually
executed. This makes suite setups ideal for checking preconditions
that must be met before running test cases is possible.

A suite teardown is normally used for cleaning up after all the test
cases have been executed. It is executed even if the setup of the same
suite fails. If the suite teardown fails, all test cases in the
suite are marked failed, regardless of their original execution status.
Note that all the keywords in suite teardowns are executed even if one
of them fails.

The name of the keyword to be executed as a setup or a teardown can be
a variable. This facilitates having different setups or teardowns
in different environments by giving the keyword name as a variable
from the command line.
