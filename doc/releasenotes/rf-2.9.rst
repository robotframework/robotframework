===================
Robot Framework 2.9
===================

.. default-role:: code

Robot Framework 2.9 is a new major version with nearly 100 fixed issues.
It contains, for example, high priority enhancements related to variables,
support for creating keywords with embedded arguments in test libraries, and
possibility to tag keywords. The most visible enhancement is the new fresh
look in logs and reports. All issues targeted for RF 2.9 can be found from
the `issue tracker <https://github.com/robotframework/robotframework/issues?q=milestone%3A2.9>`_.

Questions and comments related to this release can be sent to the
`robotframework-users <http://groups.google.com/group/robotframework-users>`_
mailing list and possible bugs `submitted to the issue tracker
<https://github.com/robotframework/robotframework/issues>`_.

Source distribution and Windows installers are available at `PyPI
<https://pypi.python.org/pypi/robotframework/2.9>`_ and the standalone JAR
with Jython 2.7 at `Maven central
<http://search.maven.org/#search%7Cga%7C1%7Ca%3Arobotframework>`_.

If you have `pip <http://pip-installer.org>`_ installed, just run
`pip install --upgrade robotframework` to install or upgrade to the latest
version or use `pip install robotframework==2.9` to install exactly this
version. For more details and other installation approaches, see
`installation instructions <../../INSTALL.rst>`_.

Robot Framework 2.9 was released on Friday July 31, 2015.

.. contents::
   :depth: 2
   :local:

Compatibility with other projects
=================================

Robot Framework 2.9 should, for most parts, be compatible with other projects
in the larger Robot Framework ecosystem. It may, however, take some time before
tools support new syntax like dictionary variables and keyword tags.
Additionally, big internal changes may affect libraries and tools that have
used the internal APIs. Libraries and tools know not to be compatible with
Robot Framework 2.9 will be listed here.

- RIDE 1.4 and older are not compatible with new syntax added in Robot
  Framework 2.9. Updated version is to be released shortly.

- Selenium2Library 1.7.0 and older `use an internal API
  <https://github.com/robotframework/Selenium2Library/issues/429>`__
  that has been removed. Selenium2Library 1.7.1 and newer are compatible with
  Robot Framework 2.9.

- RemoteSwingLibrary 2.0.2 and older use the same `removed internal API
  <https://github.com/robotframework/remoteswinglibrary/issues/24>`__ as
  Selenium2Library. RemoteSwingLibrary 2.0.3 and newer are compatible with
  Robot Framework 2.9.

- Robot Framework Jenkins plugin 1.6.0 and older `can not parse the new
  output.xml <https://issues.jenkins-ci.org/browse/JENKINS-29178>`__.
  Jenkins plugin 1.6.1 and newer are compatible with Robot Framework 2.9.

Most important enhancements
===========================

Dictionary variable type
------------------------

The biggest new feature in RF 2.9 is the syntax to create and use dictionary
variables (`#1450`_). Dictionaries can be returned from keywords or created
in variable files, but they can also be created in the variable table:

.. code:: robotframework

    *** Variables ***
    &{DICT}    key=value    second=2    third=${3}

The above example will create a dictionary variable `&{DICT}` with Python
dictionary `{'key': 'value', 'second': '2', 'third': 3}` as the value. If
a dictionary variable is used as a scalar variable like `${DICT}`, it will be
passed forward as a single argument containing the whole dictionary. If it
used like `&{DICT}`, individual items are passed as named arguments. For
example, these two examples are equivalent:

.. code:: robotframework

    *** Test Cases ***
    Example 1
        My Keyword    key=value    second=2    third=${3}
    Example 2
        My Keyword    &{DICT}

Individual dictionary variable items can be accessed either using special
`&{DICT}[key]` syntax similarly as individual list variable items can be
accessed like `@{LIST}[0]`. As a special feature, dictionary variables allow
accessing values also using attribute access like `${DICT.key}`. For more
information about dictionary variables, see Variables section in the
`User Guide`_.

Python style `**kwargs` support with user keywords using `&{kwargs}` syntax
---------------------------------------------------------------------------

New dictionary variable syntax can be used with user keywords to accept free
keyword arguments similarly as Python based keywords can accept `**kwargs`
(`#1561`_). This can be accomplished simply by having a dictionary variable
like `&{kwargs}` as the last argument in user keyword argument specification:

.. code:: robotframework

    *** Keywords ***
    Run My Process
        [Arguments]    @{arguments}    &{configuration}
        Run Process    myproc.exe    @{arguments}    &{configuration}

Also this new functionality is explained with further examples in the
`User Guide`_.

Embedded arguments in keywords defined in test libraries
--------------------------------------------------------

User keywords have supported embedded arguments since RF 2.1.1 (`#370`_), and
finally this functionality is supported also by library keywords (`#1818`_).
This is accomplished by giving a custom name to a keyword by setting
`robot_name` attribute manually or by using `robot.api.deco.keyword` decorator
(`#1835`_), and using `${args}` in the name similarly as with user keywords.
The implementing method or function must also accept same number of arguments
as there are embedded argument.

.. code:: python

    from robot.api.deco import keyword

    @keyword(name='User "${user}" selects "${item}" from webshop')
    def select_item(user, item):
        # ...

The `User Guide`_ is, again, the place where to find more information and
examples.

Keyword categorization (i.e. tagging) support
---------------------------------------------

Keywords can now have tags (`#925`_). The tags can be added to user keywords
either by using the new `[Tags]` setting, or by adding them to the last line
of documentation.

.. code:: robotframework

    *** Keywords ***
    My keyword
        [Tags]    tag1    tag2
        No Operation
    My other keyword
        [Documentation]    Tags can also be added as last line of documentation.
        ...                Tags: tag1, tag2
        No Operation

Library keywords can also use the last line of their documentation to specify
tag. Alternatively the method or function implementing a keyword can itself
have `robot_tags` attribute that contains a list of tags. The `keyword`
decorator provides a handy shortcut to set `robot_tags` attribute:

.. code:: python

    from robot.api.deco import keyword

    @keyword(tags=['tag1', 'tag2'])
    def select_item(user, item):
        # ...

Libdoc will show keywords by tags (`#1840`_) and tags can also be used to
specify keywords for `--removekeywords` and `--flattenkeywords` commandline
options (`#1935`_).

Programmatic modifications of test data and results as part of normal execution
-------------------------------------------------------------------------------

It is now possible to specify modifiers to pre-process the test data before
the test run and to modify the results before generation of log and report.
The modifiers can be taken into use with `--prerunmodifier` and
`--prerebotmodifier`. See the issue `#1976`_ and the `User Guide`_ for examples
and more details about these very powerful new extension APIs.

Lighter and more neutral colors for logs and reports
----------------------------------------------------

Logs and reports have a new fresh look (`#1943`_). Go run some tests and see
yourself!

Less verbose and quiet console outputs
--------------------------------------

New option `--console` allows changing the console output type (`#317`_).
Possible values are `verbose` (default), `dotted` (x-unit like output where
each passing test prints only a dot), `quiet` (no output except warnings and
errors) and `none` (no output whatsoever). Dotted and quiet outputs can also
be enabled with separate options `--dotted` and `--quiet`, respectively.

Variables are added to evaluation namespace of `Evaluate`, `Run Keyword If`, etc.
---------------------------------------------------------------------------------

Robot Framework´s variables are now available with a `$` prefix as Python
variables in evaluation namespace of various BuiltIn library keywords
(`#2040`_).

The two rows below are now equivalent (assuming value of `${my var}` is
a string):

.. code:: robotframework

    *** Keywords ***
    My keyword
        Run keyword if    "${my var}" != "Foo"   ...   # old syntax
        Run keyword if     $my_var != "Foo"    ...   # new syntax in 2.9

`FOR ... IN ZIP ...` and `FOR ... IN ENUMERATE`
-----------------------------------------------

New for loop syntax allows use of for-in-zip and for-in-enumerate loops
(`#1952`_).

.. code:: robotframework

    *** Keywords ***
    For in zip example    # take elements from both lists
        :FOR    ${number}    ${name}    IN ZIP    ${NUMBERS}    ${NAMES}
            \     Number Should Be Named    ${number}    ${name}
    For in enumerate example    # take an item and an increasing index number
        :FOR    ${index}    ${item}    IN ENUMERATE    @{LIST}
         \     My Keyword    ${index}    ${item}

See the `User Guide`_ for more details and examples.

Contribution guidelines
-----------------------

We have written guidelines helping to submit issue and contribute code
(`#1805`_). A link to them appears when submitting and issue or creating
a pull request, and `CONTRIBUTING.rst <../../CONTRIBUTING.rst>`__ is also
directly available. We plan to enhance the guidelines in the future, so all
kind of comments and enhancement ideas are highly appreciated.

Other high priority enhancements and fixes
------------------------------------------

- Scalar and list variables stored in same namespace (`#1905`_)
- Standard libraries do not mask third party Python modules (`#1737`_)
- Fixed sporadic failures with timeouts on IronPython (`#1931`_)
- `--ExitOnFailure` fixed when test/suite setup/teardown fails  (`#2004`_)
- YAML files supported as first class variable files  (`#1965`_)
- `Run Keyword If Test (Failed / Passed)` detects failure in teardown  (`#1270`_)
- DateTime: Fixed DST problems when calculating with dates  (`#2018`_)

Backwards incompatible changes
==============================

Being a major release, RF 2.9 contains lot of changes and some of them are
backwards incompatible.

List and scalar variables stored in same namespace
--------------------------------------------------

It has been possible to use a list variable `@{list}` as a scalar variable
`${list}` since RF 2.0.3 (`#117`_), and scalar variables containing lists have
been usable as list variables since RF 2.8 (`#483`_). It has been possible,
however, to also create scalar and list variables with same base name, for
example, in the variable table:

.. code:: robotframework

    *** Variables ***
    ${VAR}    Scalar variable
    @{VAR}    List    variable

This caused a lot of confusion, and the addition of `&{dictionary}` variables
(`#1450`_) would have made situation even more complicated. As a result it was
decided to store all variables in the same namespace (`#1905`_) and decide
how they are used depending on the format (e.g. `${var}` for scalar, `@{var}`
for list, and `&{var}` for dictionary).

As a result of this change, tests using scalar and list variables with same
base name will need to be updated. Unfortunately there is no other good way
to detect these problems than running tests with the new version and seeing
does anything break.

Variables no longer leak to lower level keywords
------------------------------------------------

Local variables used to leak from test to keywords and from keywords to lower
level keywords (`#532`_). The example below shows variable leaking from test
to keyword:

.. code:: robotframework

    *** Test Case ***
    Example
        ${x}=    Set Variable    hello
        My keyword

    *** Keywords ***
    My keyword
        Should be equal    ${x}    hello

This behavior was never intended, but fixing the bug can break tests where
this was used either intentionally or by accident.

Python and Jython 2.5 support dropped
-------------------------------------

With the official `Jython 2.7 <http://jython.org>`__ version out, we dropped
the support for Python and Jython 2.5 series (`#1928`_). The standalone JAR
distribution contains Jython 2.7 from now on. The main motivation of this
change was to ease supporting Python 3 in the (near) future.

Empty elements or attributes are not written to output.xml
----------------------------------------------------------


For example, every suite, test and keyword used to have `<doc></doc>` element
even if they did not have any documentation. Nowadays such empty elements are
not written to the output.xml at all (`#2020`_). This change may affect tools
processing output.xml files, but it also reduced output.xml size up to 10% in
our tests.

PYTHONPATH environment variable is not processed with Jython or IronPython
--------------------------------------------------------------------------

Robot Framework used to process `PYTHONPATH` environment variable regardless
the interpreter. In RF 2.9 no such processing is done (`#1983`_), and you need
to use `JYTHONPATH` or `IRONPYTHONPATH` with Jython and IronPython,
respectively.

Execution directory not added automatically to module search path
-----------------------------------------------------------------

The directory where execution is started from is not anymore added to the
module search path (`#2019`_). If it is needed, `PYTHONPATH`, `JYTHONPATH`
or `IRONPYTHONPATH` environment variable can be explicitly set to `.` before
execution.

Standard libraries not importable in Python without `robot.libraries` prefix
----------------------------------------------------------------------------

It used to be possible to import Robot Framework's standard libraries in Python
code by just using the library name like `import DateTime`. This caused
problems in with standard libraries having same name as third party Python
modules like `DateTime <https://pypi.python.org/pypi/DateTime/4.0.1>`__.

To avoid these problems, standard libraries are not anymore directly importable
in Python code (`#1737`_). They are still importable with the `robot.libraries`
prefix like `from robot.libraries import DateTime`. This has also always been
the recommended way and the one used in examples in the `User Guide`_.

Disabling command line options accepting no values by using same option again not supported
-------------------------------------------------------------------------------------------

Earlier it was possible to disable options accepting no values like `--dryrun`
by giving the option again like `--dryrun --other options --dryrun`. This was
rather confusing, and nowadays it is possible to do that by using the same
option with `no` prefix like `--nodryrun` instead (`#1865`_). If an option is
used with and without the `no` prefix, the last used value has precedence.
Having same option multiple times has no special functionality anymore.

Possible equal signs in arguments to `BuiltIn.Call Method` need to be escaped
-----------------------------------------------------------------------------

`Call Method` nowadays supports `**kwags` and thus possible equal signs in
normal arguments need to be escaped with a backslash like `hello\=world`
(`#1603`_).

Unused internal functions, classes, etc. removed
------------------------------------------------

See issue `#1924`_ for a detailed list of changes to internal APIs. These
changes should not affect libraries or tools using Robot Framework's public
APIs.

Other backwards incompatible changes
------------------------------------

These changes should generally not cause problems in real life. See linked
issues for more details if you think you may be affected.

- Not possible to use keyword with embedded arguments as a normal keyword
  (`#1962`_)
- When assigning keyword return values to multiple scalar variables, an exact
  number of values is required (`#1910`_)
- `Create Dictionary` keyword moved from Collections to BuiltIn (`#1913`_)
- Keyword name conflict involving Remote library keyword causes failure and
  not warning (`#1815`_)
- Possibility to set scalar variables with lists value using
  `Set Test/Suite/Global Variable` keyword removed (`#1919`_)
- Variable assignment is not anymore part of the keyword name in logs, in
  listener interface, or when using `--removekeywords` (`#1611`_)
- Deprecated syntax for repeating single keyword removed (`#1775`_)
- Deprecated `--runmode` option removed (`#1923`_)
- Deprecated `--xunitfile` option removed in favor of `--xunit` (`#1925`_)
- Deprecated way to exit for loops using custom exception with
  `ROBOT_EXIT_FOR_LOOP` attribute has been removed (`#1440`_)
- `Run Keyword If Test (Failed / Passed)` detects failures also in teardown
  (`#1270`_)
- DateTime: DST fixes when calculating with dates (`#2018`_)
- `FAIL` is no longer usable as a normal log level (`#2016`_)
- Console colors and markers: Fail if given value is invalid and remove
  outdated `FORCE` color value (`#2031`_)
- OperatingSystem and Dialogs: Remove partial support for running without
  Robot Framework itself (`#2039`_)

Deprecated features
===================

Robot Framework 2.9 also deprecates some features that will be removed in the
future releases. See the issues below for more details:

- `OperatingSystem.Start Process` keyword deprecated in favor of much more
  flexible `Process.Start Process` (`#1773`_)
- Listener interface version 1.0 deprecated (`#1841`_)
- `--runfailed` and `--rerunmerge` options deprecated in favor of
  `--rerunfailed` and `--merge`, respectively (`#1642`_)
- Old `Meta: Name` syntax for specifying test suite metadata deprecated
  (`#1918`_)
- Using same setting multiple times deprecated (`#2063`_)
- `DeprecatedBuiltIn` and `DeprecatedOperatingSystem` officially deprecated
  (`#1774`_)
- Deprecate `--monitorxxx` options in favor of `--consolexxx` (`#2027`_)

Acknowledgements
================

Robot Framework 2.9 got more contributions than any earlier release. Big
thanks for the following contributors as well for anyone who has tested the
preview releases, submitted issues, or otherwise helped to make RF 2.9 a great
release!

- Jared Hellman (@hellmanj)  implemented support for embedded arguments with
  library keywords (`#1818`_) and custom library keyword names (`#1835`_)
  required by it.
- Vinicius K. Ruoso (@vkruoso) implemented support for multiple listeners per
  library (`#1970`_).
- Joseph Lorenzini (@jaloren) exposed `ERROR` log level for keywords (`#1916`_).
- Guillaume Grossetie (@Mogztter) contributed initial versions of log and
  report styles (`#1943`_).
- Ed Brannin (@edbrannin) implemented `FOR ... IN ZIP` and `FOR ... IN
  ENUMERATE` syntax (`#1954`_).
- Moon SungHoon (@MoonSungHoon) added new `Get Regexp Matches` keyword to
  the String library (`#1985`_).
- Hélio Guilherme (@HelioGuilherme66) added support for partial match for
  `Get Lines Matching Regexp` in the String library (`#1836`_).
- Jean-Charles Deville (@jcdevil) made variable errors not exit `runner
  keywords` (`#1869`_).
- Guy Kisel (@guykisel) wrote the initial contribution guidelines (`#1805`_).
- Laurent Bristiel (@laurentbristiel) converted examples in `User Guide`_ to
  plain text format (`#1972`_).

Full list of fixes and enhancements
===================================

.. list-table::
    :header-rows: 1

    * - ID
      - Type
      - Priority
      - Summary
    * - `#532`_
      - bug
      - critical
      - Variables should not leak to lower level keywords
    * - `#1450`_
      - enhancement
      - critical
      - Dictionary variable type
    * - `#1561`_
      - enhancement
      - critical
      - Support Python style `**kwargs` with user keywords using `&{kwargs}` syntax
    * - `#1905`_
      - enhancement
      - critical
      - Store list and scalar variables in same namespace
    * - `#925`_
      - enhancement
      - critical
      - Keyword categorization (i.e. tagging) support
    * - `#1270`_
      - bug
      - high
      - Run Keyword If Test (Failed / Passed) does not detect failure in teardown
    * - `#1737`_
      - bug
      - high
      - Standard libraries should not be importable in Python w/o `robot.libraries` prefix
    * - `#1931`_
      - bug
      - high
      - Timeouts can cause sporadic failures with IronPython
    * - `#2004`_
      - bug
      - high
      - `--ExitOnFailure` does not work if test/suite setup/teardown fails
    * - `#2018`_
      - bug
      - high
      - DateTime: DST problems when calculating with dates
    * - `#1805`_
      - enhancement
      - high
      - Contribution instructions
    * - `#1818`_
      - enhancement
      - high
      - Embedded arguments in keywords defined in test libraries
    * - `#1840`_
      - enhancement
      - high
      - Libdoc: Show keywords by tags
    * - `#1928`_
      - enhancement
      - high
      - Drop Python/Jython 2.5 support to ease adding support for Python 3
    * - `#1943`_
      - enhancement
      - high
      - Use lighter and more neutral colors for report and log html page
    * - `#1952`_
      - enhancement
      - high
      - `FOR ... IN ZIP ...` and `FOR ... IN ENUMERATE`
    * - `#1965`_
      - enhancement
      - high
      - Support yaml files as first class variable file
    * - `#1976`_
      - enhancement
      - high
      - Support programmatic modifications of test data and results as part of normal execution
    * - `#1991`_
      - enhancement
      - high
      - Include Jython 2.7 in standalone jar
    * - `#2040`_
      - enhancement
      - high
      - Add variables to evaluation namespace of `Evaluate`, `Run Keyword If`, ...
    * - `#293`_
      - enhancement
      - high
      - BuiltIn: New `Reload Library` keyword
    * - `#317`_
      - enhancement
      - high
      - Less verbose and quiet console outputs
    * - `#1611`_
      - bug
      - medium
      - Variable assignment should not be part of keyword name with `--removekeywords`, in logs, in listener interface, or in other APIs
    * - `#1900`_
      - bug
      - medium
      - Log messages lost if library `__init__` imports or initializes other libraries
    * - `#1908`_
      - bug
      - medium
      - Telnet option negotiation loop
    * - `#1992`_
      - bug
      - medium
      - Listeners are not unregistered when using `TestSuite.run` API
    * - `#2062`_
      - bug
      - medium
      - Not possible to print to stdout/stderr by listeners or otherwise inside `Run Keyword` variants
    * - `#1440`_
      - enhancement
      - medium
      - Remove attribute ROBOT_EXIT_FOR_LOOP deprecated in 2.8
    * - `#1603`_
      - enhancement
      - medium
      - Support `**kwargs` with `BuiltIn.Call Method` keywords
    * - `#1728`_
      - enhancement
      - medium
      - Support setting child suite variables with `Set Suite Variable`
    * - `#1743`_
      - enhancement
      - medium
      - Make keyword prefix (library name) less visible than keywords in HTML reports
    * - `#1773`_
      - enhancement
      - medium
      - Deprecate `OperatingSystem.Start Process` keyword
    * - `#1774`_
      - enhancement
      - medium
      - Officially deprecate `DeprecatedBuiltIn` and `DeprecatedOperatingSystem`
    * - `#1826`_
      - enhancement
      - medium
      - Process: Better support on Jython 2.7 (termination, signals, pid)
    * - `#1834`_
      - enhancement
      - medium
      - String: Support partial match with `Get Lines Matching RegExp`
    * - `#1835`_
      - enhancement
      - medium
      - Allow giving a custom name to keywords implemented using the static and the hybrid APIs
    * - `#1841`_
      - enhancement
      - medium
      - Deprecate old listener API
    * - `#1865`_
      - enhancement
      - medium
      - Support disabling command line options accepting no values using `no` prefix (e.g. `--dryrun` -> `--nodryrun`)
    * - `#1869`_
      - enhancement
      - medium
      - Variable errors should not exit `Wait Until Keyword Succeeds`, `Run Keyword And Expect Error`, etc.
    * - `#1910`_
      - enhancement
      - medium
      - Require exact number of keyword return value when assigning multiple scalar variables
    * - `#1911`_
      - enhancement
      - medium
      - Accept list variable as a wildcard anywhere when assigning variables
    * - `#1913`_
      - enhancement
      - medium
      - Move `Create Dictionary` to BuiltIn and enhance to preserve order, allow accessing keys as attributes, etc.
    * - `#1914`_
      - enhancement
      - medium
      - Catenate cell values when creating scalar variable in variable table
    * - `#1916`_
      - enhancement
      - medium
      - Expose `ERROR` log level to custom libraries
    * - `#1927`_
      - enhancement
      - medium
      - Remote: Support accessing keys of returned dicts using attribute access
    * - `#1935`_
      - enhancement
      - medium
      - Support keyword tags with `--flattenkeywords` and `--removekeywords`
    * - `#1958`_
      - enhancement
      - medium
      - `Log Many`: Support logging `&{dictionary}` variable items
    * - `#1959`_
      - enhancement
      - medium
      - `Wait Until Keyword Succeeds`: Support giving wait time as number of times to retry
    * - `#1962`_
      - enhancement
      - medium
      - Disallow using keyword with embedded arguments as normal keywords
    * - `#1969`_
      - enhancement
      - medium
      - Allow giving listener and model modifier instances to `robot.run` and `TestSuite.run`
    * - `#1970`_
      - enhancement
      - medium
      - Enhance ROBOT_LIBRARY_LISTENER to accept a list of listeners
    * - `#1972`_
      - enhancement
      - medium
      - User Guide: Switch examples to use plain text format instead of HTML format
    * - `#1983`_
      - enhancement
      - medium
      - PYTHONPATH environment variable should not be processed with Jython or IronPython
    * - `#1985`_
      - enhancement
      - medium
      - String: New `Get Regexp Matches` keyword
    * - `#1990`_
      - enhancement
      - medium
      - Avoid Python 3 incompatible type checks
    * - `#1998`_
      - enhancement
      - medium
      - Pass keyword and library names separately to listeners
    * - `#2020`_
      - enhancement
      - medium
      - Do not write empty elements or attributes to output.xml
    * - `#2027`_
      - enhancement
      - medium
      - Deprecate `--monitorxxx` options in favor of `--consolexxx`
    * - `#2028`_
      - enhancement
      - medium
      - Tag patterns starting with `NOT`
    * - `#2029`_
      - enhancement
      - medium
      - When exiting gracefully, skipped tests should get automatic `robot-exit` tag
    * - `#2030`_
      - enhancement
      - medium
      - Notify listeners about library, resource and variable file imports
    * - `#2032`_
      - enhancement
      - medium
      - Document that test and keyword tags with `robot-` prefix are reserved
    * - `#2036`_
      - enhancement
      - medium
      - `BuiltIn.Get Variables`: Support getting variables without `${}` decoration
    * - `#2038`_
      - enhancement
      - medium
      - Consistent usage of Boolean arguments in standard libraries
    * - `#2063`_
      - enhancement
      - medium
      - Deprecate using same setting multiple times
    * - `#1815`_
      - bug
      - low
      - Keyword name conflict involving Remote keyword should cause failure, not warning
    * - `#1906`_
      - bug
      - low
      - Free keyword arguments (`**kwargs`) names cannot contain equal signs or trailing backslashes
    * - `#1922`_
      - bug
      - low
      - Screenshot library causes deprecation warning with wxPython 3.x
    * - `#1997`_
      - bug
      - low
      - User Guide has outdated links to test templates
    * - `#2002`_
      - bug
      - low
      - Keyword and test names with urls or quotes create invalid html on log and report
    * - `#2003`_
      - bug
      - low
      - Checking is stdout/stderr stream terminal causes exception if stream's buffer is detached
    * - `#2016`_
      - bug
      - low
      - `FAIL` should not be useable as a normal log level
    * - `#2019`_
      - bug
      - low
      - Execution directory should not be added to module search path (`PYTHONPATH`)
    * - `#2043`_
      - bug
      - low
      - BuiltIn: Some `Should` keyword only consider Python `True` true and other values false
    * - `#1642`_
      - enhancement
      - low
      - Deprecate `--runfailed` and `--rerunmerge` options
    * - `#1775`_
      - enhancement
      - low
      - Remove deprecated syntax for repeating single keyword
    * - `#1897`_
      - enhancement
      - low
      - Clean-up reference to RF 2.6 and older from User Guide and other documentation
    * - `#1898`_
      - enhancement
      - low
      - Improve error message for "Else" instead of "ELSE"
    * - `#1918`_
      - enhancement
      - low
      - Deprecate old `Meta: Name` syntax for specifying test suite metadata
    * - `#1919`_
      - enhancement
      - low
      - Remove possibility to setting scalar variables with lists value using `Set Test/Suite/Global Variable` keyword
    * - `#1921`_
      - enhancement
      - low
      - More flexible syntax to deprecate keywords
    * - `#1923`_
      - enhancement
      - low
      - Remove deprecated `--runmode` option
    * - `#1924`_
      - enhancement
      - low
      - Remove unused internal functions, classes, etc.
    * - `#1925`_
      - enhancement
      - low
      - Remove deprecated `--xunitfile` option
    * - `#1929`_
      - enhancement
      - low
      - OperatingSystem: Enhance documentation about path separators
    * - `#1945`_
      - enhancement
      - low
      - Enhance documentation of `Run Keyword If` return values
    * - `#2021`_
      - enhancement
      - low
      - Update XSD schemas
    * - `#2022`_
      - enhancement
      - low
      - Document that preformatted text with spaces in Robot data requires escaping
    * - `#2031`_
      - enhancement
      - low
      - Console colors and markers: Fail if given value is invalid and remove outdated `FORCE` color value
    * - `#2033`_
      - enhancement
      - low
      - Use `setuptools` for installation when available
    * - `#2037`_
      - enhancement
      - low
      - `BuiltIn.Evaluate`: Support any mapping as a custom namespace
    * - `#2039`_
      - enhancement
      - low
      - OperatingSystem and Dialogs: Remove partial support for running without Robot Framework itself
    * - `#2041`_
      - enhancement
      - low
      - Collections: New keyword `Convert To Dictionary`
    * - `#2045`_
      - enhancement
      - low
      - BuiltIn: Log argument types in DEBUG level not INFO

Altogether 94 issues. View on `issue tracker <https://github.com/robotframework/robotframework/issues?q=milestone%3A2.9>`__.

.. _User Guide: http://robotframework.org/robotframework/#user-guide
.. _#117: https://github.com/robotframework/robotframework/issues/117
.. _#370: https://github.com/robotframework/robotframework/issues/370
.. _#483: https://github.com/robotframework/robotframework/issues/483
.. _#1836: https://github.com/robotframework/robotframework/issues/1836
.. _#1954: https://github.com/robotframework/robotframework/issues/1954
.. _#532: https://github.com/robotframework/robotframework/issues/532
.. _#1450: https://github.com/robotframework/robotframework/issues/1450
.. _#1561: https://github.com/robotframework/robotframework/issues/1561
.. _#1905: https://github.com/robotframework/robotframework/issues/1905
.. _#925: https://github.com/robotframework/robotframework/issues/925
.. _#1270: https://github.com/robotframework/robotframework/issues/1270
.. _#1737: https://github.com/robotframework/robotframework/issues/1737
.. _#1931: https://github.com/robotframework/robotframework/issues/1931
.. _#2004: https://github.com/robotframework/robotframework/issues/2004
.. _#2018: https://github.com/robotframework/robotframework/issues/2018
.. _#1805: https://github.com/robotframework/robotframework/issues/1805
.. _#1818: https://github.com/robotframework/robotframework/issues/1818
.. _#1840: https://github.com/robotframework/robotframework/issues/1840
.. _#1928: https://github.com/robotframework/robotframework/issues/1928
.. _#1943: https://github.com/robotframework/robotframework/issues/1943
.. _#1952: https://github.com/robotframework/robotframework/issues/1952
.. _#1965: https://github.com/robotframework/robotframework/issues/1965
.. _#1976: https://github.com/robotframework/robotframework/issues/1976
.. _#1991: https://github.com/robotframework/robotframework/issues/1991
.. _#2040: https://github.com/robotframework/robotframework/issues/2040
.. _#293: https://github.com/robotframework/robotframework/issues/293
.. _#317: https://github.com/robotframework/robotframework/issues/317
.. _#1611: https://github.com/robotframework/robotframework/issues/1611
.. _#1900: https://github.com/robotframework/robotframework/issues/1900
.. _#1908: https://github.com/robotframework/robotframework/issues/1908
.. _#1992: https://github.com/robotframework/robotframework/issues/1992
.. _#2062: https://github.com/robotframework/robotframework/issues/2062
.. _#1440: https://github.com/robotframework/robotframework/issues/1440
.. _#1603: https://github.com/robotframework/robotframework/issues/1603
.. _#1728: https://github.com/robotframework/robotframework/issues/1728
.. _#1743: https://github.com/robotframework/robotframework/issues/1743
.. _#1773: https://github.com/robotframework/robotframework/issues/1773
.. _#1774: https://github.com/robotframework/robotframework/issues/1774
.. _#1826: https://github.com/robotframework/robotframework/issues/1826
.. _#1834: https://github.com/robotframework/robotframework/issues/1834
.. _#1835: https://github.com/robotframework/robotframework/issues/1835
.. _#1841: https://github.com/robotframework/robotframework/issues/1841
.. _#1865: https://github.com/robotframework/robotframework/issues/1865
.. _#1869: https://github.com/robotframework/robotframework/issues/1869
.. _#1910: https://github.com/robotframework/robotframework/issues/1910
.. _#1911: https://github.com/robotframework/robotframework/issues/1911
.. _#1913: https://github.com/robotframework/robotframework/issues/1913
.. _#1914: https://github.com/robotframework/robotframework/issues/1914
.. _#1916: https://github.com/robotframework/robotframework/issues/1916
.. _#1927: https://github.com/robotframework/robotframework/issues/1927
.. _#1935: https://github.com/robotframework/robotframework/issues/1935
.. _#1958: https://github.com/robotframework/robotframework/issues/1958
.. _#1959: https://github.com/robotframework/robotframework/issues/1959
.. _#1962: https://github.com/robotframework/robotframework/issues/1962
.. _#1969: https://github.com/robotframework/robotframework/issues/1969
.. _#1970: https://github.com/robotframework/robotframework/issues/1970
.. _#1972: https://github.com/robotframework/robotframework/issues/1972
.. _#1983: https://github.com/robotframework/robotframework/issues/1983
.. _#1985: https://github.com/robotframework/robotframework/issues/1985
.. _#1990: https://github.com/robotframework/robotframework/issues/1990
.. _#1998: https://github.com/robotframework/robotframework/issues/1998
.. _#2020: https://github.com/robotframework/robotframework/issues/2020
.. _#2027: https://github.com/robotframework/robotframework/issues/2027
.. _#2028: https://github.com/robotframework/robotframework/issues/2028
.. _#2029: https://github.com/robotframework/robotframework/issues/2029
.. _#2030: https://github.com/robotframework/robotframework/issues/2030
.. _#2032: https://github.com/robotframework/robotframework/issues/2032
.. _#2036: https://github.com/robotframework/robotframework/issues/2036
.. _#2038: https://github.com/robotframework/robotframework/issues/2038
.. _#2063: https://github.com/robotframework/robotframework/issues/2063
.. _#1815: https://github.com/robotframework/robotframework/issues/1815
.. _#1906: https://github.com/robotframework/robotframework/issues/1906
.. _#1922: https://github.com/robotframework/robotframework/issues/1922
.. _#1997: https://github.com/robotframework/robotframework/issues/1997
.. _#2002: https://github.com/robotframework/robotframework/issues/2002
.. _#2003: https://github.com/robotframework/robotframework/issues/2003
.. _#2016: https://github.com/robotframework/robotframework/issues/2016
.. _#2019: https://github.com/robotframework/robotframework/issues/2019
.. _#2043: https://github.com/robotframework/robotframework/issues/2043
.. _#1642: https://github.com/robotframework/robotframework/issues/1642
.. _#1775: https://github.com/robotframework/robotframework/issues/1775
.. _#1897: https://github.com/robotframework/robotframework/issues/1897
.. _#1898: https://github.com/robotframework/robotframework/issues/1898
.. _#1918: https://github.com/robotframework/robotframework/issues/1918
.. _#1919: https://github.com/robotframework/robotframework/issues/1919
.. _#1921: https://github.com/robotframework/robotframework/issues/1921
.. _#1923: https://github.com/robotframework/robotframework/issues/1923
.. _#1924: https://github.com/robotframework/robotframework/issues/1924
.. _#1925: https://github.com/robotframework/robotframework/issues/1925
.. _#1929: https://github.com/robotframework/robotframework/issues/1929
.. _#1945: https://github.com/robotframework/robotframework/issues/1945
.. _#2021: https://github.com/robotframework/robotframework/issues/2021
.. _#2022: https://github.com/robotframework/robotframework/issues/2022
.. _#2031: https://github.com/robotframework/robotframework/issues/2031
.. _#2033: https://github.com/robotframework/robotframework/issues/2033
.. _#2037: https://github.com/robotframework/robotframework/issues/2037
.. _#2039: https://github.com/robotframework/robotframework/issues/2039
.. _#2041: https://github.com/robotframework/robotframework/issues/2041
.. _#2045: https://github.com/robotframework/robotframework/issues/2045
