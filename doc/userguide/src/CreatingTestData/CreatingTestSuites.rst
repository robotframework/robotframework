Creating test suites
--------------------

Robot Framework test cases are created in test case files, which can
be organized into directories. These files and directories create a
hierarchical test suite structure.

.. contents::
   :depth: 2
   :local:

Test case files
~~~~~~~~~~~~~~~

Robot Framework test cases `are created`__ using test case tables in
test case files. Such a file automatically creates a test suite from
all the test cases it contains. There is no upper limit for how many
test cases there can be, but it is recommended to have less than ten,
unless the `data-driven approach`_ is used, where one test case consists of
only one high-level keyword.

The following settings in the Setting table can be used to customize the
test suite:

`Documentation`:opt:
   Used for specifying a `test suite documentation`_
`Metadata`:opt:
   Used for setting `free test suite metadata`_ as name-value
   pairs.
`Suite Setup`:opt:, `Suite Teardown`:opt:
   Specify `suite setup and teardown`_. Have also synonyms
   :opt:`Suite Precondition` and :opt:`Suite Postcondition`, respectively.

.. note:: All setting names can optionally include a colon at the end, for
      example :opt:`Documentation:`. This can make reading the settings easier
      especially when using the plain text format. This is a
      new feature in Robot Framework 2.5.5.

__ `Test case syntax`_

Test suite directories
~~~~~~~~~~~~~~~~~~~~~~

Test case files can be organized into directories, and these
directories create higher-level test suites. A test suite created from
a directory cannot have any test cases directly, but it contains
other test suites with test cases, instead. These directories can then be
placed into other directories creating an even higher-level suite. There
are no limits for the structure, so test cases can be organized
as needed.

When a test directory is executed, the files and directories it
contains are processed recursively as follows:

- Files and directories with names starting with a dot (:path:`.`) or an
  underscore (:path:`_`) are ignored.
- Directories with the name :path:`CVS` are ignored (case-sensitive).
- Files not having one of the `recognized extensions`__ (:path:`.html`,
  :path:`.xhtml`, :path:`.htm`, :path:`.tsv`, :path:`.txt`, :path:`.rst`,
  or :path:`.rest`) are ignored (case-insensitive).
- Other files and directories are processed.

If a file or directory that is processed does not contain any test
cases, it is silently ignored (a message is written to the syslog_)
and the processing continues.

__ `Supported file formats`_

Warning on invalid files
''''''''''''''''''''''''

Normally files that do not have a valid test case table are silently ignored
with a message written to the syslog_. As of Robot Framework 2.5.5 it is
possible to use a command line option :opt:`--warnonskippedfiles`, which turns
the message into a warning shown in `test execution errors`__.

__ `Errors and warnings during execution`_

Initialization files
''''''''''''''''''''

A test suite created from a directory can have similar settings as a suite
created from a test case file. Because a directory alone cannot have that
kind of information, it must be placed into a special test suite initialization
file. Initialization files have the same structure and syntax as
test case files, except that they cannot have test case tables and not all
settings are supported.

An initialization file name must always be of the format :path:`__init__.ext`,
where the extension must match one of the `supported file formats`_ (for example,
:path:`__init__.html` or :path:`__init__.txt`). The name format is borrowed
from Python, where files named in this manner denote that a directory is a module.

The main usage for initialization files is specifying test suite related
settings similarly as in `test case files`_, but setting some `test case
related settings`__ is also possible. Variables and keywords created or
imported in initialization files *are not* available in the lower level
test suites, but `resource files`_ can be used if there is a need to
share them.

How to use different settings in the initialization files:

`Documentation`:opt:, `Metadata`:opt:, `Suite Setup`:opt:, `Suite Teardown`:opt:
   These test suite specific settings work the same way as in test case files.
`Force Tags`:opt:
   Specified tags are unconditionally set to all test cases in all test case files
   this directory contains directly or recursively.
`Test Setup`:opt:, `Test Teardown`:opt:, `Test Timeout`:opt:
   Set the default value for test setup/teardown or test timeout to all test
   cases this directory contains. Can be overridden on lower level.
   Support for defining test timeout in initialization files was added in
   Robot Framework 2.7.
`Default Tags`:opt:, `Test Template`:opt:
   Not supported in initialization files.

.. table:: An example test suite initialization file
   :class: example

   =============  =============  =============
      Setting         Value          Value
   =============  =============  =============
   Documentation  Example suite
   Suite Setup    Do Something   ${MESSAGE}
   Force Tags     example
   Library        SomeLibrary
   =============  =============  =============

.. table::
   :class: example

   =============  =============  =============
      Variable        Value          Value
   =============  =============  =============
   ${MESSAGE}     Hello, world!
   =============  =============  =============

.. table::
   :class: example

   =============  ===============  ================  ================
      Keyword          Action          Argument          Argument
   =============  ===============  ================  ================
   Do Something   [Arguments]      ${arg}
   \              Some Keyword     ${arg}
   \              Another Keyword
   =============  ===============  ================  ================

__ `Test case related settings in the Setting table`_

Test suite name and documentation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The test suite name is constructed from the file or directory name. The name
is created so that the extension is ignored, possible underscores are
replaced with spaces, and names fully in lower case are title cased. For
example, :path:`some_tests.html` becomes :name:`Some Tests` and
:path:`My_test_directory` becomes :name:`My test directory`.

.. note:: The rules for creating test suite names changed slightly in
   	  Robot Framework 2.5.

The file or directory name can contain a prefix to control the `execution
order`_ of the suites. The prefix is separated from the base name by two
underscores and, when constructing the actual test suite name, both
the prefix and underscores are removed. For example files
:path:`01__some_tests.txt` and :path:`02__more_tests.txt` create test
suites :name:`Some Tests` and :name:`More Tests`, respectively, and
the former is executed before the latter.

The documentation for a test suite is set using the :opt:`Documentation`
setting in the Setting table. It can be used in test case files
or, with higher-level suites, in test suite initialization files. Test
suite documentation has exactly the same characteristics regarding to where
it is shown and how it can be created as `test case
documentation`_.

.. table:: Test suite documentation example
   :class: example

   =============  ======================  ======================  ======================
      Setting             Value                   Value                   Value
   =============  ======================  ======================  ======================
   Documentation  An example test suite   documentation with      \*some\* _formatting_.
   ...            See test documentation  for more documentation  examples.
   =============  ======================  ======================  ======================

Both the name and documentation of the top-level test suite can be
overridden in test execution. This can be done with the command line
options :opt:`--name` and :opt:`--doc`, respectively, as
explained in section `Setting metadata`_.

Free test suite metadata
~~~~~~~~~~~~~~~~~~~~~~~~

Test suites can also have other metadata than the documentation. This metadata
is defined in the Setting table using the :opt:`Metadata` setting. Metadata
set in this manner is shown in test reports and logs.

The name and value for the metadata are located in the columns following
:opt:`Metadata`. The value is handled similarly as documentation, which means
that it can be split `into several cells`__ (joined together with spaces)
or `into several rows`__ (joined together with newlines),
simple `HTML formatting`_ works and even variables_ can be used.

__ `Dividing test data to several rows`_
__ `Automatic newlines in test data`_

.. table:: Metadata examples
   :class: example

   =========  ===========  ====================  =========================  ==============================
    Setting      Value            Value                   Value                          Value
   =========  ===========  ====================  =========================  ==============================
   Metadata   Version      2.0
   Metadata   More Info    For more information  about \*Robot Framework\*  see \http://robotframework.org
   Metadata   Executed At  ${HOST}
   =========  ===========  ====================  =========================  ==============================

For top-level test suites, it is possible to set metadata also with the
:opt:`--metadata` command line option. This is discussed in more
detail in section `Setting metadata`_.

Prior to Robot Framework 2.5 the free metadata was specified with syntax like
:opt:`Meta: <name>`, where :opt:`<name>` was the metadata name and the value
was defined in subsequent column. Robot Framework 2.5 still supports this old
format but it will be deprecated in the future.

Suite setup and teardown
~~~~~~~~~~~~~~~~~~~~~~~~

Not only `test cases`__ but also test suites can have a setup and
a teardown. A suite setup is executed before running any of the suite's
test cases or child test suites, and a test teardown is executed after
them. All test suites can have a setup and a teardown; with suites created
from a directory they must be specified in a `test suite
initialization file`_.

__ `Test setup and teardown`_

Similarly as with test cases, a suite setup and teardown are keywords
that may take arguments. They are defined in the Setting table with
:opt:`Suite Setup` and :opt:`Suite Teardown` settings,
respectively. They also have similar synonyms, :opt:`Suite
Precondition` and :opt:`Suite Postcondition`, as a test case setup
and teardown have. Keyword names and possible arguments are located in
the columns after the setting name.

If a suite setup fails, all test cases in it and its child test suites
are immediately assigned a fail status and they are not actually
executed. This makes suite setups ideal for checking preconditions
that must be met before running test cases is possible.

A suite teardown is normally used for cleaning up after all the test
cases have been executed. It is executed even if the setup of the same
suite fails. If the suite teardown fails, all test cases in the
suite are marked failed, regardless of their original execution status.
Starting from Robot Framework 2.5, all the keywords in suite teardowns
are executed even if one of them fails.

The name of the keyword to be executed as a setup or a teardown can be
a variable. This facilitates having different setups or teardowns
in different environments by giving the keyword name as a variable
from the command line.
