.. _Creating tests:

Creating test cases
===================

This section describes the overall test case syntax. Organizing test
cases into `test suites`_ using `suite files`_ and `suite
directories`_ is discussed in the next section.

When using Robot Framework for other automation purposes than test
automation, it is recommended to create *tasks* instead of tests.
The task syntax is for most parts identical to the test syntax,
and the differences are explained in the `Creating tasks`_ section.

.. contents::
   :depth: 2
   :local:

Test case syntax
----------------

Basic syntax
~~~~~~~~~~~~

Test cases are constructed in test case sections from the available
keywords. Keywords can be imported from `test libraries`_ or `resource
files`_, or created in the `keyword section`_ of the test case file
itself.

.. _keyword section: `user keywords`_

The first column in the test case section contains test case names. A
test case starts from the row with something in this column and
continues to the next test case name or to the end of the section. It is
an error to have something between the section headers and the first
test.

The second column normally has keyword names. An exception to this rule
is `setting variables from keyword return values`_, when the second and
possibly also the subsequent columns contain variable names and a keyword
name is located after them. In either case, columns after the keyword name
contain possible arguments to the specified keyword.

.. _setting variables from keyword return values: `User keyword return values`_

.. _example-tests:
.. sourcecode:: robotframework

   *** Test Cases ***
   Valid Login
       Open Login Page
       Input Username    demo
       Input Password    mode
       Submit Credentials
       Welcome Page Should Be Open

   Setting Variables
       Do Something    first argument    second argument
       ${value} =    Get Some Value
       Should Be Equal    ${value}    Expected value

.. note:: Although test case names can contain any character, using `?` and
          especially `*` is not generally recommended because they are
          considered to be `wildcards`_ when `selecting test cases`_.
          For example, trying to run only a test with name :name:`Example *`
          like `--test 'Example *'` will actually run any test starting with
          :name:`Example`.

Settings in the Test Case section
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Test cases can also have their own settings. Setting names are always
in the second column, where keywords normally are, and their values
are in the subsequent columns. Setting names have square brackets around
them to distinguish them from keywords. The available settings are listed
below and explained later in this section.

`[Documentation]`:setting:
    Used for specifying a `test case documentation`_.

`[Setup]`:setting:, `[Teardown]`:setting:
   Specify `test setup and teardown`_.

`[Tags]`:setting:
    Used for `tagging test cases`_.

`[Template]`:setting:
   Specifies the `template keyword`_ to use. The test itself will contain only
   data to use as arguments to that keyword.

`[Timeout]`:setting:
   Used for setting a `test case timeout`_. Timeouts_ are discussed in
   their own section.

.. note:: Setting names are case-insensitive, but the format used above is
      recommended. Settings used to be also space-insensitive, but that was
      deprecated in Robot Framework 3.1 and trying to use something like
      `[T a g s]` causes an error in Robot Framework 3.2. Possible spaces
      between brackets and the name (e.g. `[ Tags ]`) are still allowed.

Example test case with settings:

.. sourcecode:: robotframework

   *** Test Cases ***
   Test With Settings
       [Documentation]    Another dummy test
       [Tags]    dummy    owner-johndoe
       Log    Hello, world!

Test case related settings in the Setting section
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The Setting section can have the following test case related
settings. These settings are mainly default values for the
test case specific settings listed earlier.

`Test Setup`:setting:, `Test Teardown`:setting:
   The default values for `test setup and teardown`_.

`Test Tags`:setting:
   Tags_ all tests in the suite will get in addition to their possible own tags.

`Test Template`:setting:
   The default `template keyword`_ to use.

`Test Timeout`:setting:
   The default value for `test case timeout`_. Timeouts_ are discussed in
   their own section.

Using arguments
---------------

The earlier examples have already demonstrated keywords taking
different arguments, and this section discusses this important
functionality more thoroughly. How to actually implement `user
keywords`__ and `library keywords`__ with different arguments is
discussed in separate sections.

Keywords can accept zero or more arguments, and some arguments may
have default values. What arguments a keyword accepts depends on its
implementation, and typically the best place to search this
information is keyword's documentation. In the examples in this
section the documentation is expected to be generated using the
Libdoc_ tool, but the same information is available on
documentation generated by generic documentation tools such as
``pydoc``.

__ `User keyword arguments`_
__ `Keyword arguments`_

.. _positional argument:

Positional arguments
~~~~~~~~~~~~~~~~~~~~

Most keywords have a certain number of arguments that must always be
given.  In the keyword documentation this is denoted by specifying the
argument names separated with a comma like `first, second,
third`. The argument names actually do not matter in this case, except
that they should explain what the argument does, but it is important
to have exactly the same number of arguments as specified in the
documentation. Using too few or too many arguments will result in an
error.

The test below uses keywords :name:`Create Directory` and :name:`Copy
File` from the OperatingSystem_ library. Their arguments are
specified as `path` and `source, destination`, which means
that they take one and two arguments, respectively. The last keyword,
:name:`No Operation` from BuiltIn_, takes no arguments.

.. sourcecode:: robotframework

   *** Test Cases ***
   Example
       Create Directory    ${TEMPDIR}/stuff
       Copy File    ${CURDIR}/file.txt    ${TEMPDIR}/stuff
       No Operation

Default values
~~~~~~~~~~~~~~

Arguments often have default values which can either be given or
not. In the documentation the default value is typically separated
from the argument name with an equal sign like `name=default
value`. It is possible that all the arguments have default
values, but there cannot be any positional arguments after arguments
with default values.

Using default values is illustrated by the example below that uses
:name:`Create File` keyword which has arguments `path, content=,
encoding=UTF-8`. Trying to use it without any arguments or more than
three arguments would not work.

.. sourcecode:: robotframework

   *** Test Cases ***
   Example
       Create File    ${TEMPDIR}/empty.txt
       Create File    ${TEMPDIR}/utf-8.txt         Hyvä esimerkki
       Create File    ${TEMPDIR}/iso-8859-1.txt    Hyvä esimerkki    ISO-8859-1

.. _varargs-usage:

Variable number of arguments
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

It is also possible that a keyword accepts any number of arguments.
These so called *varargs* can be combined with mandatory arguments
and arguments with default values, but they are always given after
them. In the documentation they have an asterisk before the argument
name like `*varargs`.

For example, :name:`Remove Files` and :name:`Join Paths` keywords from
the OperatingSystem_ library have arguments `*paths` and `base, *parts`,
respectively. The former can be used with any number of arguments, but
the latter requires at least one argument.

.. sourcecode:: robotframework

   *** Test Cases ***
   Example
       Remove Files    ${TEMPDIR}/f1.txt    ${TEMPDIR}/f2.txt    ${TEMPDIR}/f3.txt
       @{paths} =    Join Paths    ${TEMPDIR}    f1.txt    f2.txt    f3.txt    f4.txt

.. _named argument:
.. _named argument syntax:

Named arguments
~~~~~~~~~~~~~~~

The named argument syntax makes using arguments with `default values`_ more
flexible, and allows explicitly labeling what a certain argument value means.
Technically named arguments work exactly like `keyword arguments`__ in Python.

__ http://docs.python.org/tutorial/controlflow.html#keyword-arguments

Basic syntax
''''''''''''

It is possible to name an argument given to a keyword by prefixing the value
with the name of the argument like `arg=value`. This is especially
useful when multiple arguments have default values, as it is
possible to name only some the arguments and let others use their defaults.
For example, if a keyword accepts arguments `arg1=a, arg2=b, arg3=c`,
and it is called with one argument `arg3=override`, arguments
`arg1` and `arg2` get their default values, but `arg3`
gets value `override`. If this sounds complicated, the `named arguments
example`_ below hopefully makes it more clear.

The named argument syntax is both case and space sensitive. The former
means that if you have an argument `arg`, you must use it like
`arg=value`, and neither `Arg=value` nor `ARG=value`
works.  The latter means that spaces are not allowed before the `=`
sign, and possible spaces after it are considered part of the given value.

When the named argument syntax is used with `user keywords`_, the argument
names must be given without the `${}` decoration. For example, user
keyword with arguments `${arg1}=first, ${arg2}=second` must be used
like `arg2=override`.

Using normal positional arguments after named arguments like, for example,
`| Keyword | arg=value | positional |`, does not work.
The relative order of the named arguments does not matter.

Named arguments with variables
''''''''''''''''''''''''''''''

It is possible to use `variables`_ in both named argument names and values.
If the value is a single `scalar variable`_, it is passed to the keyword as-is.
This allows using any objects, not only strings, as values also when using
the named argument syntax. For example, calling a keyword like `arg=${object}`
will pass the variable `${object}` to the keyword without converting it to
a string.

If variables are used in named argument names, variables are resolved before
matching them against argument names.

The named argument syntax requires the equal sign to be written literally
in the keyword call. This means that variable alone can never trigger the
named argument syntax, not even if it has a value like `foo=bar`. This is
important to remember especially when wrapping keywords into other keywords.
If, for example, a keyword takes a `variable number of arguments`_ like
`@{args}` and passes all of them to another keyword using the same `@{args}`
syntax, possible `named=arg` syntax used in the calling side is not recognized.
This is illustrated by the example below.

.. sourcecode:: robotframework

   *** Test Cases ***
   Example
       Run Program    shell=True    # This will not come as a named argument to Run Process

   *** Keywords ***
   Run Program
       [Arguments]    @{args}
       Run Process    program.py    @{args}    # Named arguments are not recognized from inside @{args}

If keyword needs to accept and pass forward any named arguments, it must be
changed to accept `free named arguments`_. See `free named argument examples`_
for a wrapper keyword version that can pass both positional and named
arguments forward.

Escaping named arguments syntax
'''''''''''''''''''''''''''''''

The named argument syntax is used only when the part of the argument
before the equal sign matches one of the keyword's arguments. It is possible
that there is a positional argument with a literal value like `foo=quux`,
and also an unrelated argument with name `foo`. In this case the argument
`foo` either incorrectly gets the value `quux` or, more likely,
there is a syntax error.

In these rare cases where there are accidental matches, it is possible to
use the backslash character to escape__ the syntax like `foo\=quux`.
Now the argument will get a literal value `foo=quux`. Note that escaping
is not needed if there are no arguments with name `foo`, but because it
makes the situation more explicit, it may nevertheless be a good idea.

__ Escaping_

Where named arguments are supported
'''''''''''''''''''''''''''''''''''

As already explained, the named argument syntax works with keywords. In
addition to that, it also works when `importing libraries`_.

Naming arguments is supported by `user keywords`_ and by most `test libraries`_.
The only exceptions are Python keywords explicitly using `positional-only arguments`_.

Named arguments example
'''''''''''''''''''''''

The following example demonstrates using the named arguments syntax with
library keywords, user keywords, and when importing the Telnet_ test library.

.. sourcecode:: robotframework

   *** Settings ***
   Library    Telnet    prompt=$    default_log_level=DEBUG

   *** Test Cases ***
   Example
       Open connection    10.0.0.42    port=${PORT}    alias=example
       List files    options=-lh
       List files    path=/tmp    options=-l

   *** Keywords ***
   List files
       [Arguments]    ${path}=.    ${options}=
       Execute command    ls ${options} ${path}

.. _kwargs-usage:

Free named arguments
~~~~~~~~~~~~~~~~~~~~

Robot Framework supports *free named arguments*, often also called *free
keyword arguments* or *kwargs*, similarly as `Python supports **kwargs`__.
What this means is that a keyword can receive all arguments that use
the `named argument syntax`_ (`name=value`) and do not match any arguments
specified in the signature of the keyword.

Free named arguments are supported by same keyword types than `normal named
arguments`__. How keywords specify that they accept free named arguments
depends on the keyword type. For example, `Python based keywords`__ simply use
`**kwargs` and `user keywords`__ use `&{kwargs}`.

Free named arguments support variables similarly as `named arguments
<Named arguments with variables_>`__. In practice that means that variables
can be used both in names and values, but the escape sign must always be
visible literally. For example, both `foo=${bar}` and `${foo}=${bar}` are
valid, as long as the variables that are used exist. An extra limitation is
that free argument names must always be strings.

__ http://docs.python.org/tutorial/controlflow.html#keyword-arguments
__ `Where named arguments are supported`_
__ `Free keyword arguments (**kwargs)`_
__ `Free named arguments with user keywords`_

.. _free named argument examples:

Examples
''''''''

As the first example of using free named arguments, let's take a look at
:name:`Run Process` keyword in the Process_ library. It has a signature
`command, *arguments, **configuration`, which means that it takes the command
to execute (`command`), its arguments as `variable number of arguments`_
(`*arguments`) and finally optional configuration parameters as free named
arguments (`**configuration`). The example below also shows that variables
work with free keyword arguments exactly like when `using the named argument
syntax`__.

.. sourcecode:: robotframework

   *** Test Cases ***
   Free Named Arguments
       Run Process    program.py    arg1    arg2    cwd=/home/user
       Run Process    program.py    argument    shell=True    env=${ENVIRON}

See `Free keyword arguments (**kwargs)`_ section under `Creating test
libraries`_ for more information about using the free named arguments syntax
in your custom test libraries.

As the second example, let's create a wrapper `user keyword`_ for running the
`program.py` in the above example. The wrapper keyword :name:`Run Program`
accepts all positional and named arguments and passes them forward to
:name:`Run Process` along with the name of the command to execute.

.. sourcecode:: robotframework

   *** Test Cases ***
   Free Named Arguments
       Run Program    arg1    arg2    cwd=/home/user
       Run Program    argument    shell=True    env=${ENVIRON}

   *** Keywords ***
   Run Program
       [Arguments]    @{args}    &{config}
       Run Process    program.py    @{args}    &{config}

__ `Named arguments with variables`_

Named-only arguments
~~~~~~~~~~~~~~~~~~~~

Starting from Robot Framework 3.1, keywords can accept argument that must
always be named using the `named argument syntax`_. If, for example,
a keyword would accept a single named-only argument `example`, it would
always need to be used like `example=value` and using just `value` would
not work. This syntax is inspired by the `keyword-only arguments`__
syntax supported by Python 3.

For most parts named-only arguments work the same way as `named arguments`_.
The main difference is that libraries implemented with Python 2 using
the `static library API`_ `do not support this syntax`__.

As an example of using the `named-only arguments with user keywords`_, here
is a variation of the :name:`Run Program` in the above `free named argument
examples`_ that only supports configuring `shell`:

.. sourcecode:: robotframework

   *** Test Cases ***
   Named-only Arguments
       Run Program    arg1    arg2              # 'shell' is False (default)
       Run Program    argument    shell=True    # 'shell' is True

   *** Keywords ***
   Run Program
       [Arguments]    @{args}    ${shell}=False
       Run Process    program.py    @{args}    shell=${shell}

__ https://www.python.org/dev/peps/pep-3102
__ `Keyword-only arguments`_

Arguments embedded to keyword names
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

A totally different approach to specify arguments is embedding them
into keyword names. This syntax is supported by both `test library keywords`__
and `user keywords`__.

__ `Embedding arguments into keyword names`_
__ `Embedding arguments into keyword name`_

Failures
--------

When test case fails
~~~~~~~~~~~~~~~~~~~~

A test case fails if any of the keyword it uses fails. Normally this means that
execution of that test case is stopped, possible `test teardown`_ is executed,
and then execution continues from the next test case. It is also possible to
use special `continuable failures`__ if stopping test execution is not desired.

__ `Continue on failure`_

Error messages
~~~~~~~~~~~~~~

The error message assigned to a failed test case is got directly from the
failed keyword. Often the error message is created by the keyword itself, but
some keywords allow configuring them.

In some circumstances, for example when continuable failures are used,
a test case can fail multiple times. In that case the final error message
is got by combining the individual errors. Very long error messages are
`automatically cut from the middle`__ to keep reports_ easier to read, but
full error messages are always visible in `log files`_ as messages of
the failed keywords.

By default error messages are normal text, but
they can `contain HTML formatting`__. This
is enabled by starting the error message with marker string `*HTML*`.
This marker will be removed from the final error message shown in reports
and logs. Using HTML in a custom message is shown in the second example below.

.. sourcecode:: robotframework

   *** Test Cases ***
   Normal Error
       Fail    This is a rather boring example...

   HTML Error
       ${number} =    Get Number
       Should Be Equal    ${number}    42    *HTML* Number is not my <b>MAGIC</b> number.

__ `Limiting error message length in reports`_
__ `HTML in error messages`_

Test case name and documentation
--------------------------------

The test case name comes directly from the Test Case section: it is
exactly what is entered into the test case column. Test cases in one
test suite should have unique names.  Pertaining to this, you can also
use the `automatic variable`_ `${TEST_NAME}` within the test
itself to refer to the test name. It is available whenever a test is
being executed, including all user keywords, as well as the test setup
and the test teardown.

Starting from Robot Framework 3.2, possible variables_ in the test case name
are resolved so that the final name will contain the variable value. If
the variable does not exist, its name is left unchanged.

.. sourcecode:: robotframework

    *** Variables ***
    ${MAX AMOUNT}      ${5000000}

    *** Test Cases ***
    Amount cannot be larger than ${MAX AMOUNT}
        # ...

The :setting:`[Documentation]` setting allows setting free form
documentation for a test case. That text is shown in the command line
output and in the resulting logs and reports.
If documentation gets long, it can be `split into multiple rows`__.
It is possible to use simple `HTML formatting`_ and variables_ can
be used to make the documentation dynamic. Possible non-existing
variables are left unchanged.

__ `Dividing data to several rows`_

.. sourcecode:: robotframework

   *** Test Cases ***
   Simple
       [Documentation]    Simple and short documentation.
       No Operation

   Multiple lines
       [Documentation]    First row of the documentation.
       ...
       ...                Documentation continues here. These rows form
       ...                a paragraph when shown in HTML outputs.
       No Operation

   Formatting
       [Documentation]
       ...    This list has:
       ...    - *bold*
       ...    - _italics_
       ...    - link: http://robotframework.org
       No Operation

   Variables
       [Documentation]    Executed at ${HOST} by ${USER}
       No Operation

It is important that test cases have clear and descriptive names, and
in that case they normally do not need any documentation. If the logic
of the test case needs documenting, it is often a sign that keywords
in the test case need better names and they are to be enhanced,
instead of adding extra documentation. Finally, metadata, such as the
environment and user information in the last example above, is often
better specified using tags_.

.. _test case tags:

Tagging test cases
------------------

Using tags in Robot Framework is a simple, yet powerful mechanism for
classifying test cases and also `user keywords`_. Tags are free text and
Robot Framework itself has no special meaning for them except for the
`reserved tags`_ discussed below. Tags can be used at least for the following
purposes:

- They are shown in test reports_, logs_ and, of course, in the test
  data, so they provide metadata to test cases.
- Statistics__ about test cases (total, passed, failed and skipped) are
  automatically collected based on them.
- They can be used to `include and exclude`__ as well as to skip_ test cases.

__ `Configuring statistics`_
__ `By tag names`_

There are multiple ways how to specify tags for test cases explained below:

`Test Tags`:setting: setting in the Settings section
   All tests in a test case file with this setting always get specified tags.
   If this setting is used in a `suite initialization file`_, all tests
   in child suites get these tags.

`[Tags]`:setting: setting with each test case
   Tests get these tags in addition to tags specified using the :setting:`Test Tags`
   setting. The :setting:`[Tags]` setting also allows removing tags set with
   :setting:`Test Tags` by using the `-tag` syntax.

`--settag`:option: command line option
   All tests get tags set with this option in addition to tags they got elsewhere.

`Set Tags`:name:, `Remove Tags`:name:, `Fail`:name: and `Pass Execution`:name: keywords
   These BuiltIn_ keywords can be used to manipulate tags dynamically
   during the test execution.

Example:

.. sourcecode:: robotframework

   *** Settings ***
   Test Tags       requirement: 42    smoke

   *** Variables ***
   ${HOST}         10.0.1.42

   *** Test Cases ***
   No own tags
       [Documentation]    Test has tags 'requirement: 42' and 'smoke'.
       No Operation

   Own tags
       [Documentation]    Test has tags 'requirement: 42', 'smoke' and 'not ready'.
       [Tags]    not ready
       No Operation

   Own tags with variable
       [Documentation]    Test has tags 'requirement: 42', 'smoke' and 'host: 10.0.1.42'.
       [Tags]    host: ${HOST}
       No Operation

   Remove common tag
       [Documentation]    Test has only tag 'requirement: 42'.
       [Tags]    -smoke
       No Operation

   Remove common tag using a pattern
       [Documentation]    Test has only tag 'smoke'.
       [Tags]    -requirement: *
       No Operation

   Set Tags and Remove Tags keywords
       [Documentation]    This test has tags 'smoke', 'example' and 'another'.
       Set Tags    example    another
       Remove Tags    requirement: *

As the example shows, tags can be created using variables, but otherwise they
preserve the exact name used in the data. When tags are compared, for example,
to collect statistics, to select test to be executed, or to remove duplicates,
comparisons are case, space and underscore insensitive.

As demonstrated by the above examples, removing tags using `-tag` syntax supports
`simple patterns`_ like `-requirement: *`. Tags starting with a hyphen have no
special meaning otherwise than with the :setting:`[Tags]` setting. If there is
a need to set a tag starting with a hyphen with :setting:`[Tags]`, it is possible
to use the escaped__ format like `\-tag`.

.. note:: The :setting:`Test Tags` setting is new in Robot Framework 6.0.
          Earlier versions support :setting:`Force Tags` and :setting:`Default Tags`
          settings discussed in the next section.

.. note:: The `-tag` syntax for removing common tags is new in Robot Framework 7.0.

__ escaping_

Deprecation of :setting:`Force Tags` and :setting:`Default Tags`
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Prior to Robot Framework 6.0, tags could be specified to tests in the Setting section
using two different settings:

:setting:`Force Tags`
    All tests unconditionally get these tags. This is exactly the same as
    :setting:`Test Tags` nowadays.

:setting:`Default Tags`
    All tests get these tags by default. If a test has :setting:`[Tags]`,
    it will not get these tags.

Both of these settings still work, but they are considered deprecated.
A visible deprecation warning will be added in the future, most likely
in Robot Framework 8.0, and eventually these settings will be removed.
Tools like Tidy__ can be used to ease transition.

Updating :setting:`Force Tags` requires only renaming it to :setting:`Test Tags`.
The :setting:`Default Tags` setting will be removed altogether, but the `-tag`
functionality introduced in Robot Framework 7.0 provides same underlying
functionality. The following examples demonstrate the needed changes.

Old syntax:

.. sourcecode:: robotframework

    *** Settings ***
    Force Tags      all
    Default Tags    default

    *** Test Cases ***
    Common only
        [Documentation]    Test has tags 'all' and 'default'.
        No Operation

    No default
        [Documentation]    Test has only tag 'all'.
        [Tags]
        No Operation

    Own and no default
        [Documentation]    Test has tags 'all' and 'own'.
        [Tags]    own
        No Operation

New syntax:

.. sourcecode:: robotframework

    *** Settings ***
    Test Tags      all    default

    *** Test Cases ***
    Common only
        [Documentation]    Test has tags 'all' and 'default'.
        No Operation

    No default
        [Documentation]    Test has only tag 'all'.
        [Tags]    -default
        No Operation

    Own and no default
        [Documentation]    Test has tags 'all' and 'own'.
        [Tags]    own    -default
        No Operation

__ https://robotidy.readthedocs.io

Reserved tags
~~~~~~~~~~~~~

Users are generally free to use whatever tags that work in their context.
There are, however, certain tags that have a predefined meaning for Robot
Framework itself, and using them for other purposes can have unexpected
results. All special tags Robot Framework has and will have in the future
have the `robot:` prefix. To avoid problems, users should thus not use any
tag with this prefixes unless actually activating the special functionality.
The current reserved tags are listed below, but more such tags are likely
to be added in the future.

`robot:continue-on-failure` and `robot:recursive-continue-on-failure`
    Used for `enabling the continue-on-failure mode`__.

`robot:stop-on-failure` and `robot:recursive-stop-on-failure`
    Used for `disabling the continue-on-failure mode`__.

`robot:skip-on-failure`
    Mark test to be `skipped if it fails`__.

`robot:skip`
    Mark test to be `unconditionally skipped`__.

`robot:exclude`
    Mark test to be `unconditionally excluded`__.

`robot:private`
    Mark keyword to be private__.

`robot:no-dry-run`
    Mark keyword not to be executed in the `dry run`_ mode.

`robot:exit`
    Added to tests automatically when `execution is stopped gracefully`__.

`robot:flatten`
    Enable `flattening keyword during execution time`_.

__ `Enabling continue-on-failure using tags`_
__ `Disabling continue-on-failure using tags`_
__ `Automatically skipping failed tests`_
__ `Skipping before execution`_
__ `By tag names`_
__ `Private user keywords`_
__ `stopping test execution gracefully`_

As of RobotFramework 4.1, reserved tags are suppressed by default in
`tag statistics`__. They will be shown when they are explicitly
included via the `--tagstatinclude robot:*` command line option.

__ `Configuring statistics`_

Test setup and teardown
-----------------------

Robot Framework has similar test setup and teardown functionality as many
other test automation frameworks. In short, a test setup is something
that is executed before a test case, and a test teardown is executed
after a test case. In Robot Framework setups and teardowns are just
normal keywords with possible arguments.

A setup and a teardown are always a single keyword. If they need to take care
of multiple separate tasks, it is possible to create higher-level `user
keywords`_ for that purpose. An alternative solution is executing multiple
keywords using the BuiltIn_ keyword :name:`Run Keywords`.

The test teardown is special in two ways. First of all, it is executed also
when a test case fails, so it can be used for clean-up activities that must be
done regardless of the test case status. In addition, all the keywords in the
teardown are also executed even if one of them fails. This `continue on failure`_
functionality can be used also with normal keywords, but inside teardowns it is
on by default.

The easiest way to specify a setup or a teardown for test cases in a
test case file is using the :setting:`Test Setup` and :setting:`Test
Teardown` settings in the Setting section. Individual test cases can
also have their own setup or teardown. They are defined with the
:setting:`[Setup]` or :setting:`[Teardown]` settings in the test case
section and they override possible :setting:`Test Setup` and
:setting:`Test Teardown` settings. Having no keyword after a
:setting:`[Setup]` or :setting:`[Teardown]` setting means having no
setup or teardown. It is also possible to use value `NONE` to indicate that
a test has no setup/teardown.

.. sourcecode:: robotframework

   *** Settings ***
   Test Setup       Open Application    App A
   Test Teardown    Close Application

   *** Test Cases ***
   Default values
       [Documentation]    Setup and teardown from setting section
       Do Something

   Overridden setup
       [Documentation]    Own setup, teardown from setting section
       [Setup]    Open Application    App B
       Do Something

   No teardown
       [Documentation]    Default setup, no teardown at all
       Do Something
       [Teardown]

   No teardown 2
       [Documentation]    Setup and teardown can be disabled also with special value NONE
       Do Something
       [Teardown]    NONE

   Using variables
       [Documentation]    Setup and teardown specified using variables
       [Setup]    ${SETUP}
       Do Something
       [Teardown]    ${TEARDOWN}

The name of the keyword to be executed as a setup or a teardown can be a
variable. This facilitates having different setups or teardowns in
different environments by giving the keyword name as a variable from
the command line.

.. note:: `Test suites can have a setup and teardown of their
           own`__. A suite setup is executed before any test cases or sub test
           suites in that test suite, and similarly a suite teardown is
           executed after them.

__  `Suite setup and teardown`_

Test templates
--------------

Test templates convert normal `keyword-driven`_ test cases into
`data-driven`_ tests. Whereas the body of a keyword-driven test case
is constructed from keywords and their possible arguments, test cases with
template contain only the arguments for the template keyword.
Instead of repeating the same keyword multiple times per test and/or with all
tests in a file, it is possible to use it only per test or just once per file.

Template keywords can accept both normal positional and named arguments, as
well as arguments embedded to the keyword name. Unlike with other settings,
it is not possible to define a template using a variable.

Basic usage
~~~~~~~~~~~

How a keyword accepting normal positional arguments can be used as a template
is illustrated by the following example test cases. These two tests are
functionally fully identical.

.. sourcecode:: robotframework

   *** Test Cases ***
   Normal test case
       Example keyword    first argument    second argument

   Templated test case
       [Template]    Example keyword
       first argument    second argument

As the example illustrates, it is possible to specify the
template for an individual test case using the :setting:`[Template]`
setting. An alternative approach is using the :setting:`Test Template`
setting in the Setting section, in which case the template is applied
for all test cases in that test case file. The :setting:`[Template]`
setting overrides the possible template set in the Setting section, and
an empty value for :setting:`[Template]` means that the test has no
template even when :setting:`Test Template` is used. It is also possible
to use value `NONE` to indicate that a test has no template.

If a templated test case has multiple data rows in its body, the template
is applied for all the rows one by one. This
means that the same keyword is executed multiple times, once with data
on each row. Templated tests are also special so that all the rounds
are executed even if one or more of them fails. It is possible to use this
kind of `continue on failure`_ mode with normal tests too, but with
the templated tests the mode is on automatically.

.. sourcecode:: robotframework

   *** Settings ***
   Test Template    Example keyword

   *** Test Cases ***
   Templated test case
       first round 1     first round 2
       second round 1    second round 2
       third round 1     third round 2

Using keywords with `default values`_ or accepting `variable number of arguments`_,
as well as using `named arguments`_ and `free named arguments`_, work with templates
exactly like they work otherwise. Using variables_ in arguments is also
supported normally.

Templates with embedded arguments
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Templates support a variation of
the `embedded argument syntax`_. With templates this syntax works so
that if the template keyword has variables in its name, they are considered
placeholders for arguments and replaced with the actual arguments
used with the template. The resulting keyword is then used without positional
arguments. This is best illustrated with an example:

.. sourcecode:: robotframework

   *** Test Cases ***
   Normal test case with embedded arguments
       The result of 1 + 1 should be 2
       The result of 1 + 2 should be 3

   Template with embedded arguments
       [Template]    The result of ${calculation} should be ${expected}
       1 + 1    2
       1 + 2    3

   *** Keywords ***
   The result of ${calculation} should be ${expected}
       ${result} =    Calculate    ${calculation}
       Should Be Equal    ${result}     ${expected}

When embedded arguments are used with templates, the number of arguments in
the template keyword name must match the number of arguments it is used with.
The argument names do not need to match the arguments of the original keyword,
though, and it is also possible to use different arguments altogether:

.. sourcecode:: robotframework

   *** Test Cases ***
   Different argument names
       [Template]    The result of ${foo} should be ${bar}
       1 + 1    2
       1 + 2    3

   Only some arguments
       [Template]    The result of ${calculation} should be 3
       1 + 2
       4 - 1

   New arguments
       [Template]    The ${meaning} of ${life} should be 42
       result    21 * 2

The main benefit of using embedded arguments with templates is that
argument names are specified explicitly. When using normal arguments,
the same effect can be achieved by naming the columns that contain
arguments. This is illustrated by the `data-driven style`_ example in
the next section.

Templates with `FOR` loops
~~~~~~~~~~~~~~~~~~~~~~~~~~

If templates are used with `FOR loops`_, the template is applied for
all the steps inside the loop. The continue on failure mode is in use
also in this case, which means that all the steps are executed with
all the looped elements even if there are failures.

.. sourcecode:: robotframework

   *** Test Cases ***
   Template with FOR loop
       [Template]    Example keyword
       FOR    ${item}    IN    @{ITEMS}
           ${item}    2nd arg
       END
       FOR    ${index}    IN RANGE    42
           1st arg    ${index}
       END

Templates with `IF/ELSE` structures
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

`IF/ELSE structures`_ can be also used together with templates.
This can be useful, for example, when used together with `FOR loops`_ to
filter executed arguments.

.. sourcecode:: robotframework

   *** Test Cases ***
   Template with FOR and IF
       [Template]    Example keyword
       FOR    ${item}    IN    @{ITEMS}
           IF  ${item} < 5
               ${item}    2nd arg
           END
       END

Different test case styles
--------------------------

There are several different ways in which test cases may be written. Test
cases that describe some kind of *workflow* may be written either in
keyword-driven or behavior-driven style. Data-driven style can be used to test
the same workflow with varying input data.

Keyword-driven style
~~~~~~~~~~~~~~~~~~~~

Workflow tests, such as the :name:`Valid Login` test described
earlier_, are constructed from several keywords and their possible
arguments. Their normal structure is that first the system is taken
into the initial state (:name:`Open Login Page` in the :name:`Valid
Login` example), then something is done to the system (:name:`Input
Name`, :name:`Input Password`, :name:`Submit Credentials`), and
finally it is verified that the system behaved as expected
(:name:`Welcome Page Should Be Open`).

.. _earlier: example-tests_

Data-driven style
~~~~~~~~~~~~~~~~~

Another style to write test cases is the *data-driven* approach where
test cases use only one higher-level keyword, often created as a
`user keyword`_, that hides the actual test workflow. These tests are
very useful when there is a need to test the same scenario with
different input and/or output data. It would be possible to repeat the
same keyword with every test, but the `test template`_ functionality
allows specifying the keyword to use only once.

.. sourcecode:: robotframework

   *** Settings ***
   Test Template    Login with invalid credentials should fail

   *** Test Cases ***                USERNAME         PASSWORD
   Invalid User Name                 invalid          ${VALID PASSWORD}
   Invalid Password                  ${VALID USER}    invalid
   Invalid User Name and Password    invalid          invalid
   Empty User Name                   ${EMPTY}         ${VALID PASSWORD}
   Empty Password                    ${VALID USER}    ${EMPTY}
   Empty User Name and Password      ${EMPTY}         ${EMPTY}

.. tip:: Naming columns like in the example above makes tests easier to
         understand. This is possible because on the header row other
         cells except the first one `are ignored`__.

The above example has six separate tests, one for each invalid
user/password combination, and the example below illustrates how to
have only one test with all the combinations. When using `test
templates`_, all the rounds in a test are executed even if there are
failures, so there is no real functional difference between these two
styles. In the above example separate combinations are named so it is
easier to see what they test, but having potentially large number of
these tests may mess-up statistics. Which style to use depends on the
context and personal preferences.

.. sourcecode:: robotframework

   *** Test Cases ***
   Invalid Password
       [Template]    Login with invalid credentials should fail
       invalid          ${VALID PASSWORD}
       ${VALID USER}    invalid
       invalid          whatever
       ${EMPTY}         ${VALID PASSWORD}
       ${VALID USER}    ${EMPTY}
       ${EMPTY}         ${EMPTY}

__ `Test data sections`_

Behavior-driven style
~~~~~~~~~~~~~~~~~~~~~

It is also possible to write test cases as requirements that also non-technical
project stakeholders must understand. These *executable requirements* are a
corner stone of a process commonly called `Acceptance Test Driven Development`__
(ATDD) or `Specification by Example`__.

One way to write these requirements/tests is *Given-When-Then* style
popularized by `Behavior Driven Development`__ (BDD). When writing test cases in
this style, the initial state is usually expressed with a keyword starting with
word :name:`Given`, the actions are described with keyword starting with
:name:`When` and the expectations with a keyword starting with :name:`Then`.
Keyword starting with :name:`And` or :name:`But` may be used if a step has more
than one action.

.. sourcecode:: robotframework

   *** Test Cases ***
   Valid Login
       Given login page is open
       When valid username and password are inserted
       and credentials are submitted
       Then welcome page should be open

__ https://en.wikipedia.org/wiki/Acceptance_test-driven_development
__ http://en.wikipedia.org/wiki/Specification_by_example
__ http://en.wikipedia.org/wiki/Behavior_Driven_Development

Ignoring :name:`Given/When/Then/And/But` prefixes
'''''''''''''''''''''''''''''''''''''''''''''''''

Prefixes :name:`Given`, :name:`When`, :name:`Then`, :name:`And` and :name:`But`
are dropped when matching keywords are searched, if no match with the full name
is found. This works for both user keywords and library keywords. For example,
:name:`Given login page is open` in the above example can be implemented as
user keyword either with or without the word :name:`Given`. Ignoring prefixes
also allows using the same keyword with different prefixes. For example
:name:`Welcome page should be open` could also used as :name:`And welcome page
should be open`.

.. note:: These prefixes can be localized_. See the Translations_ appendix
          for supported translations.

Embedding data to keywords
''''''''''''''''''''''''''

When writing concrete examples it is useful to be able to pass actual data to
keyword implementations. User keywords support this by allowing `embedding
arguments into keyword name`_.
