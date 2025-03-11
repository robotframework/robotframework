==========================
Robot Framework 5.0 beta 1
==========================

.. default-role:: code

`Robot Framework`_ 5.0 is a big new major release with lot of interesting new
features that were prioritized based on the `community survey`__. Biggest
enhancements are `TRY/EXCEPT`, `WHILE`, inline `IF`, `RETURN`, `BREAK` and
`CONTINUE` syntax, support for custom argument conversion in libraries and
various enhancements to xUnit outputs. Robot Framework 5.0 only works with
Python 3.6 or newer.

__ https://github.com/pekkaklarck/rf5survey

Robot Framework 5.0 beta 1 is the second preview release and contains
majority of the planned new features.
All issues targeted for Robot Framework 5.0 can be found
from the `issue tracker milestone`_.

Questions and comments related to the release can be sent to the
`robotframework-users`_ mailing list or to `Robot Framework Slack`_,
and possible bugs submitted to the `issue tracker`_.

If you have pip_ installed, just run

::

   pip install --pre --upgrade robotframework

to install the latest available release or use

::

   pip install robotframework==5.0b1

to install exactly this version. Alternatively, you can download the source
distribution from PyPI_ and install it manually. For more details and other
installation approaches, see the `installation instructions`_.

Robot Framework 5.0 beta 1 was released on Friday February 11, 2022.

.. _Robot Framework: http://robotframework.org
.. _Robot Framework Foundation: http://robotframework.org/foundation
.. _pip: http://pip-installer.org
.. _PyPI: https://pypi.python.org/pypi/robotframework
.. _issue tracker milestone: https://github.com/robotframework/robotframework/issues?q=milestone%3Av5.0
.. _issue tracker: https://github.com/robotframework/robotframework/issues
.. _robotframework-users: http://groups.google.com/group/robotframework-users
.. _Robot Framework Slack: https://robotframework-slack-invite.herokuapp.com
.. _installation instructions: ../../INSTALL.rst

.. contents::
   :depth: 2
   :local:

Most important enhancements
===========================

Robot Framework 5.0 adds lot of new syntax to Robot Framework language, but
there are also many other big new enhancements.

`TRY/EXCEPT`
------------

Robot Framework 5.0 makes handling errors occurring during execution lot more
convenient than it used to be by adding native `TRY/EXCEPT` syntax (`#3075`_)
that is is inspired by Python's `exception handling`__ syntax. It has same
`TRY`, `EXCEPT`, `ELSE` and `FINALLY` branches as Python and they also mostly
work the same way. A difference is that Python uses lower case
`try`, `except`, etc. but with Robot Framework all this kind of syntax must use
upper case letters. A bigger difference is that with Python exceptions are objects
and with Robot Framework you are dealing with error messages as strings.

__ https://docs.python.org/tutorial/errors.html#handling-exceptions

Catching exceptions with `EXCEPT`
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The basic `TRY/EXCEPT` syntax can be used to handle failures based on
error messages:

.. code:: robotframework

    *** Test Cases ***
    First example
        TRY
            Some Keyword
        EXCEPT    Error message
            Error Handler Keyword
        END
        Keyword Outside

In the above example, if `Some Keyword` passes, the `EXCEPT` branch is not run
and execution continues after the `TRY/EXCEPT` structure. If the keyword fails
with a message `Error message` (case-sensitive), the `EXCEPT` branch is executed.
If the `EXCEPT` branch succeeds, execution continues after the `TRY/EXCEPT`
structure. If it fails, the test fails and remaining keywords are not executed.
If `Some Keyword` fails with any other exception, that failure is not handled
and the test fails without executing remaining keywords.

There can be more than one `EXCEPT` branch. In that case they are matched one
by one and the first matching branch is executed. One `EXCEPT` can also have
multiple messages to match, and such a branch is executed if any of its messages
match. In all these cases messages can be specified using variables in addition
to literal strings.

.. code:: robotframework

    *** Test Cases ***
    Multiple EXCEPT branches
        TRY
            Some Keyword
        EXCEPT    Error message    # Try matching this first.
            Error Handler 1
        EXCEPT    Another error    # Try this if above did not match.
            Error Handler 2
        EXCEPT    ${message}       # Last match attempt, this time using a variable.
            Error Handler 3
        END

    Multiple messages with one EXCEPT
        TRY
            Some Keyword
        EXCEPT    Error message    Another error    ${message}    # Match any of these.
            Error handler
        END

It is also possible to have an `EXCEPT` without messages, in which case it matches
any error. There can be only one such `EXCEPT` and it must follow possible
other `EXCEPT` branches:

.. code:: robotframework

    *** Test Cases ***
    Match any error
        TRY
            Some Keyword
        EXCEPT               # Match any error.
            Error Handler
        END

    Match any after testing more specific errors
        TRY
            Some Keyword
        EXCEPT    Error message    # Try matching this first
            Error Handler 1
        EXCEPT                     # Match any that did not match the above.
            Error Handler 2
        END

Matching errors using patterns
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

By default matching an error using `EXCEPT` requires an exact match. That can be
changed by prefixing the message with `GLOB:`, `REGEXP:` or `STARTS:` (case-sensitive)
to make the match a `glob pattern match`__, a `regular expression match`__, or
to match only the beginning of the error, respectively. Prefixing the message with
`EQUALS:` has the same effect as the default behavior. If an `EXCEPT` has multiple
messages, possible prefixes apply only to messages they are attached to, not to
other messages. The prefix must always be specified explicitly and cannot come
from a variable.

.. code:: robotframework

    *** Test Cases ***
    Glob pattern
        TRY
            Some Keyword
        EXCEPT    GLOB: ValueError: *
            Error Handler 1
        EXCEPT    GLOB: [Ee]rror ?? occurred    GLOB: ${pattern}
            Error Handler 2
        END

    Regular expression
        TRY
            Some Keyword
        EXCEPT    REGEXP: ValueError: .*
            Error Handler 1
        EXCEPT    REGEXP: [Ee]rror \\d+ occurred    # Backslash needs to be escaped.
            Error Handler 2
        END

    Match start
        TRY
            Some Keyword
        EXCEPT    STARTS: ValueError:    STARTS: ${beginning}
            Error Handler
        END

    Explicit exact match
        TRY
            Some Keyword
        EXCEPT    EQUALS: ValueError: invalid literal for int() with base 10: 'ooops'
            Error Handler
        EXCEPT    EQUALS: Error 13 occurred
            Error Handler 2
        END

.. note:: Remember that the backslash character often used with regular expressions
          is an escape character in Robot Framework data. It thus needs to be
          escaped with another backslash when using it in regular expressions.

__ https://en.wikipedia.org/wiki/Glob_(programming)
__ https://en.wikipedia.org/wiki/Regular_expression

Capturing error message
~~~~~~~~~~~~~~~~~~~~~~~

When `matching errors using patterns`_ and when using `EXCEPT` without any
messages to match any error, it is often useful to know the actual error that
occurred. Robot Framework supports that by making it possible to capture
the error message into a variable by adding `AS  ${var}` at the
end of the `EXCEPT` statement:

.. code:: robotframework

    *** Test Cases ***
    Capture error
        TRY
            Some Keyword
        EXCEPT    GLOB: ValueError: *    AS   ${error}
            Error Handler 1    ${error}
        EXCEPT    REGEXP: [Ee]rror \\d+    GLOB: ${pattern}    AS    ${error}
            Error Handler 2    ${error}
        EXCEPT    AS    ${error}
            Error Handler 3    ${error}
        END

Using `ELSE` to execute keywords when there are no errors
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Optional `ELSE` branches make it possible to execute keywords if there is no error.
There can be only one `ELSE` branch and it is allowed only after one or more
`EXCEPT` branches:

.. code:: robotframework

    *** Test Cases ***
    ELSE branch
        TRY
            Some Keyword
        EXCEPT    X
            Log    Error 'X' occurred!
        EXCEPT    Y
            Log    Error 'Y' occurred!
        ELSE
            Log    No error occurred!
        END
        Keyword Outside

In the above example, if `Some Keyword` passes, the `ELSE` branch is executed,
and if it fails with message `X` or `Y`, the appropriate `EXCEPT` branch run.
In all these cases execution continues after the whole `TRY/EXCEPT/ELSE` structure.
If `Some Keyword` fail any other way, `EXCEPT` and `ELSE` branches are not run
and the `TRY/EXCEPT/ELSE` structure fails.

To handle both the case when there is any error and when there is no error,
it is possible to use an `EXCEPT` without any message in combination with an `ELSE`:

.. code:: robotframework

    *** Test Cases ***
    Handle everything
        TRY
            Some Keyword
        EXCEPT    AS    ${err}
            Log    Error occurred: ${err}
        ELSE
            Log    No error occurred!
        END

Using `FINALLY` to execute keywords regardless are there errors or not
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Optional `FINALLY` branches make it possible to execute keywords both when there
is an error and when there is not. They are thus suitable for cleaning up
after a keyword execution somewhat similarly as teardowns. There can be only one
`FINALLY` branch and it must always be last. They can be used in combination with
`EXCEPT` and `ELSE` branches and having also `TRY/FINALLY` structure is possible:

.. code:: robotframework

    *** Test Cases ***
    TRY/EXCEPT/ELSE/FINALLY
        TRY
            Some keyword
        EXCEPT
            Log    Error occurred!
        ELSE
            Log    No error occurred.
        FINALLY
            Log    Always executed.
        END

    TRY/FINALLY
        Open Connection
        TRY
            Use Connection
        FINALLY
            Close Connection
        END

`WHILE`
-------

Robot Framework's new `WHILE` loops (`#4084`_) work the same way as such loops
in other languages. Basically the loop is executed as long as the loop condition
is true, the loop is exited explicitly using `BREAK` or `RETURN` (only works
inside keywords), or one of the keywords in the loop fails. In addition to
`BREAK` that exits the loop completely, it is possible to use `CONTINUE` to
skip the current loop iteration and to move the next one. These loop control
statements are often used in combination with the new `inline IF`_ syntax.

The loop condition is evaluated in Python same way as `IF` expressions are.
That means that normal variables like `${x}` are resolved before evaluating
the condition and that variables are available in the evaluation namespace
using the special `$x` syntax. Python builtins are also available and modules
are imported automatically. For more details see the `Evaluation expressions`__
appendix in the User Guide.

Examples:

.. code:: robotframework

    *** Variables ***
    ${x}              10

    *** Test Cases ***
    Loop as long as condition is True
        WHILE    ${x} > 0
            Log    ${x}
            ${x} =    Evaluate    ${x} - 1
        END

    BREAK and CONTINUE
        WHILE    True
            Log    ${x}
            ${x} =    Evaluate    ${x} - 1
            IF    ${x} == 0
                Log    We are done!
                BREAK
            END
            IF    ${x} % 2 == 0    CONTINUE    # New inline IF.
            Log    Only executed if ${x} is odd.
        END

__ http://robotframework.org/robotframework/latest/RobotFrameworkUserGuide.html#evaluating-expressions

Inline `IF`
-----------

Normal `IF/ELSE` structure, `introduced in Robot Framework 4.0`__, is a bit verbose
if there is a need to execute only a single statement. An alternative to it is
using the new inline `IF` syntax (`#4093`_) where the statement to execute follows
the `IF` marker and condition directly and no `END` marker is needed. For example,
the following two keywords are equivalent:

.. code:: robotframework

    *** Keyword ***
    Normal IF
        IF    $condition1
            Keyword    argument
        END
        IF    $condition2
            RETURN
        END

    Inline IF
        IF    $condition1    Keyword    argument
        IF    $condition2    RETURN

The inline `IF` syntax supports also `ELSE` and `ELSE IF` branches:

.. code:: robotframework

    *** Keyword ***
    Inline IF/ELSE
        IF    $condition    Keyword    argument    ELSE    Another Keyword

    Inline IF/ELSE IF/ELSE
        IF    $cond1    Keyword 1    ELSE IF    $cond2    Keyword 2    ELSE IF    $cond3    Keyword 3    ELSE    Keyword 4

As the latter example above demonstrates, inline `IF` with several `ELSE IF`
and `ELSE` branches starts to get hard to understand. Long inline `IF`
structures can be split into multiple lines using the common `...`
continuation syntax, but using a normal `IF/ELSE` structure or moving the logic
into a library is probably a better idea. Each inline `IF` branch can
contain only one statement. If more statements are needed, normal `IF/ELSE`
structure needs to be used instead.

If there is a need for an assignment with inline `IF`, the variable or variables
to assign must be before the starting `IF`. Otherwise the logic is exactly
the same as when assigning variables based on keyword return values. If
assignment is used and no branch is run, the variable gets value `None`.

.. code:: robotframework

    *** Keyword ***
    Inline IF/ELSE with assignment
        ${var} =    IF    $condition    Keyword    argument    ELSE    Another Keyword

    Inline IF/ELSE with assignment having multiple variables
        ${host}    ${port} =    IF    $production    Get Production Config    ELSE    Get Testing Config

__ https://github.com/robotframework/robotframework/blob/master/doc/releasenotes/rf-4.0.rst#native-if-else-syntax

`BREAK` and `CONTINUE`
----------------------

New `BREAK` and `CONTINUE` statements (`#4079`_) were already used in WHILE_
examples above. In addition to that they work with the old `FOR` loops and with
both loops they are often combined with `inline IF`_:

.. code:: robotframework

    *** Test Cases ***
    Example
        FOR    ${x}    IN RANGE    1000
            IF    ${x} > 10    BREAK
            Log    Executed only when ${x} < 11
            IF    ${x} % 2 == 0    CONTINUE
            Log    Executed only when ${x} is odd.
        END

Old `Exit For Loop` and `Continue For Loop` keywords along with their conditional
variants `Exit For Loop If` and `Continue For Loop If` still work, but they will
be deprecated and removed in the future.

`RETURN`
--------

New `RETURN` statement (`#4078`_) adds a uniform way to return from user keywords.
It can be used for returning values when the keyword has been executed like
when using the old `[Return]` setting, and also for returning prematurely like
the old `Return From Keyword` keyword supports:

.. code:: robotframework

    *** Keywords ***
    Return at the end
        Some Keyword
        ${result} =    Another Keyword
        RETURN    ${result}

    Return conditionally
        IF    ${condition}
            RETURN    Something
        ELSE
            RETURN    Something else
        END

    Early return
        IF    ${not applicable}    RETURN
        Some Keyword
        Another Keyword

The old `[Return]` setting and old keywords `Return From Keyword` and
`Return From Keyword If` continue to work. The plan is to deprecate and
remove them in the future.

Custom argument conversion
--------------------------

Robot Framework has supported `automatic argument conversion`_ for long time,
and now it is possible for libraries to register custom converters as well
(`#4088`_). This functionality has two main use cases:

- Overriding the standard argument converters provided by the framework.

- Adding argument conversion for custom types and for other types not supported
  out-of-the-box.

Argument converters are functions or other callables that get arguments used
in data and convert them to desired format before arguments are passed to
keywords. Converters are registered for libraries by setting
`ROBOT_LIBRARY_CONVERTERS` attribute (case-insensitive) to a dictionary mapping
desired types to converts. When implementing a library as a module, this
attribute must be set on the module level, and with class based libraries
it must be a class attribute. With libraries implemented as classes, it is
also possible to use the `converters` argument with the `@library` decorator.
Both of these approaches are illustrated by examples

.. _automatic argument conversion: https://github.com/robotframework/robotframework/blob/master/doc/releasenotes/rf-3.1.rst#automatic-argument-conversion

Overriding default converters
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Let's assume we wanted to create a keyword that accepts date_ objects for
users in Finland where the commonly used date format is `dd.mm.yyyy`.
The usage could look something like this:

.. code:: robotframework

    *** Test Cases ***
    Example
        Keyword    25.1.2022

Automatic argument conversion supports dates, but it expects them
to be in `yyyy-mm-dd` format so it will not work. A solution is creating
a custom converter and registering it to handle date_ conversion:

.. code:: python

    from datetime import date


    # Converter function.
    def parse_fi_date(value):
        day, month, year = value.split('.')
        return date(int(year), int(month), int(day))


    # Register converter function for the specified type.
    ROBOT_LIBRARY_CONVERTERS = {date: parse_fi_date}


    # Keyword using custom converter. Converter is got based on argument type.
    def keyword(arg: date):
        print(f'year: {arg.year}, month: {arg.month}, day: {arg.day}')

Conversion errors
~~~~~~~~~~~~~~~~~

If we try using the above keyword with invalid argument like `invalid`, it
fails with this error::

    ValueError: Argument 'arg' got value 'invalid' that cannot be converted to date: not enough values to unpack (expected 3, got 1)

This error is not too informative and does not tell anything about the expected
format. Robot Framework cannot provide more information automatically, but
the converter itself can be enhanced to validate the input. If the input is
invalid, the converter should raise a `ValueError` with an appropriate message.
In this particular case there would be several ways to validate the input, but
using `regular expressions`__ makes it possible to validate both that the input
has dots (`.`) in correct places and that date parts contain correct amount
of digits:

.. code:: python

    from datetime import date
    import re


    def parse_fi_date(value):
        # Validate input using regular expression and raise ValueError if not valid.
        match = re.match(r'(\d{1,2})\.(\d{1,2})\.(\d{4})$', value)
        if not match:
            raise ValueError(f"Expected date in format 'dd.mm.yyyy', got '{value}'.")
        day, month, year = match.groups()
        return date(int(year), int(month), int(day))


    ROBOT_LIBRARY_CONVERTERS = {date: parse_fi_date}


    def keyword(arg: date):
        print(f'year: {arg.year}, month: {arg.month}, day: {arg.day}')

With the above converter code, using the keyword with argument `invalid` fails
with a lot more helpful error message::

    ValueError: Argument 'arg' got value 'invalid' that cannot be converted to date: Expected date in format 'dd.mm.yyyy', got 'invalid'.

__ https://en.wikipedia.org/wiki/Regular_expression

Restricting value types
~~~~~~~~~~~~~~~~~~~~~~~

By default Robot Framework tries to use converters with all given arguments
regardless their type. This means that if the earlier example keyword would
be used with a variable containing something else than a string, conversion
code would fail in the `re.match` call. For example, trying to use it with
argument `${42}` would fail like this::

    ValueError: Argument 'arg' got value '42' (integer) that cannot be converted to date: TypeError: expected string or bytes-like object

This error situation could naturally handled in the converter code by checking
the value type, but if the converter only accepts certain types, it is typically
easier to just restrict the value to that type. Doing it requires only adding
appropriate type hint to the converter:

.. code:: python

    def parse_fi_date(value: str):
         # ...

Notice that this type hint *is not* used for converting the value before calling
the converter, it is used for strictly restricting which types can be used.
With the above addition calling the keyword with `${42}` would fail like this::

    ValueError: Argument 'arg' got value '42' (integer) that cannot be converted to date.

If the converter can accept multiple types, it is possible to specify types
as a Union_. For example, if we wanted to enhance our keyword to accept also
integers so that they would be considered seconds since the `Unix epoch`__,
we could change the converter like this:

.. code:: python

    from datetime import date
    import re
    from typing import Union


    # Accept both strings and integers.
    def parse_fi_date(value: Union[str, int]):
        # Integers are converted separately.
        if isinstance(value, int):
            return date.fromtimestamp(value)
        match = re.match(r'(\d{1,2})\.(\d{1,2})\.(\d{4})$', value)
        if not match:
            raise ValueError(f"Expected date in format 'dd.mm.yyyy', got '{value}'.")
        day, month, year = match.groups()
        return date(int(year), int(month), int(day))


    ROBOT_LIBRARY_CONVERTERS = {date: parse_fi_date}


    def keyword(arg: date):
        print(f'year: {arg.year}, month: {arg.month}, day: {arg.day}')

__ https://en.wikipedia.org/wiki/Unix_time

Converting custom types
~~~~~~~~~~~~~~~~~~~~~~~

A problem with the earlier example is that date_ objects could only be given
in `dd.mm.yyyy` format. It would would not work if there would be need to
support dates in different formats like in this example:

.. code:: robotframework

    *** Test Cases ***
    Example
        Finnish     25.1.2022
        US          1/25/2022
        ISO 8601    2022-01-22

A solution to this problem is creating custom types instead of overriding
the default date_ conversion:

.. code:: python

    from datetime import date
    import re
    from typing import Union

    from robot.api.deco import keyword, library


    # Custom type. Extends an existing type but that is not required.
    class FiDate(date):

        # Converter function implemented as a classmethod. It could be a normal
        # function as well, but this way all code is in the same class.
        @classmethod
        def from_string(cls, value: str):
            match = re.match(r'(\d{1,2})\.(\d{1,2})\.(\d{4})$', value)
            if not match:
                raise ValueError(f"Expected date in format 'dd.mm.yyyy', got '{value}'.")
            day, month, year = match.groups()
            return cls(int(year), int(month), int(day))


    # Another custom type.
    class UsDate(date):

        @classmethod
        def from_string(cls, value: str):
            match = re.match(r'(\d{1,2})/(\d{1,2})/(\d{4})$', value)
            if not match:
                raise ValueError(f"Expected date in format 'mm/dd/yyyy', got '{value}'.")
            month, day, year = match.groups()
            return cls(int(year), int(month), int(day))


    # Register converters using '@library' decorator.
    @library(converters={FiDate: FiDate.from_string, UsDate: UsDate.from_string})
    class Library:

        # Uses custom converter supporting 'dd.mm.yyyy' format.
        @keyword
        def finnish(self, arg: FiDate):
            print(f'year: {arg.year}, month: {arg.month}, day: {arg.day}')

        # Uses custom converter supporting 'mm/dd/yyyy' format.
        @keyword
        def us(self, arg: UsDate):
            print(f'year: {arg.year}, month: {arg.month}, day: {arg.day}')

        # Uses IS0-8601 compatible default conversion.
        @keyword
        def iso_8601(self, arg: date):
            print(f'year: {arg.year}, month: {arg.month}, day: {arg.day}')

        # Accepts date in different formats.
        @keyword
        def any(self, arg: Union[FiDate, UsDate, date]):
            print(f'year: {arg.year}, month: {arg.month}, day: {arg.day}')

Converter documentation
~~~~~~~~~~~~~~~~~~~~~~~

Information about converters is added to HTML and XML outputs produced by Libdoc
automatically. This information includes the name of the type, accepted values
(if specified using type hints) and documentation. Type information is
automatically linked to all keywords using these types.

Used documentation is got from the converter function by default. If it does
not have any documentation, documentation is got from the type. Both of these
approaches to add documentation to converters in the previous example thus
produce the same result:

.. code:: python

    class FiDate(date):

        @classmethod
        def from_string(cls, value: str):
            """Date in ``dd.mm.yyyy`` format."""
            # ...


    class UsDate(date):
        """Date in ``mm/dd/yyyy`` format."""

        @classmethod
        def from_string(cls, value: str):
            # ...

Adding documentation is in general recommended to provide users more
information about conversion. It is especially important to document
converter functions registered for existing types, because their own
documentation is likely not very useful in this context.

.. _date: https://docs.python.org/3/library/datetime.html#date-objects
.. _union: https://docs.python.org/3/library/typing.html#typing.Union

Automatic type conversion info added to Libdoc outputs
------------------------------------------------------

As already mentioned above when discussing about the new `custom argument conversion`_
functionality, Robot Framework has supported `automatic argument conversion`_ for
long time. So far library documentation generated using the Libdoc tool has
contained no information about what types are converted and how, but this
changes in Robot Framework 5.0. (`#4160`_)

Automatically converted types that are used by a library are included both in
the machine readable spec files and in the HTML output targeted for humans.
They are shown the same way as `Enums` and `TypedDicts` have been shown since
`Robot Framework 4.0`__. This is also how types supporting custom conversions
discussed above are shown.

To ease mapping types to their usages, type documentation in spec files
contains a list of keywords using them. In addition to that, arguments used by keywords
contain references to types they use. (`#4218`_)

__ https://github.com/robotframework/robotframework/blob/master/doc/releasenotes/rf-4.0.rst#libdoc-enhancements

Enhancements to xUnit compatible outputs
----------------------------------------

Robot Frameworks xUnit compatible outputs make it possible to provide information
about execution to external reporting systems that do not have native Robot Framework
support but support xUnit outputs produced also by many other tools like `jUnit`
and `pytest`. These outputs have been enhanced in different ways in Robot Framework 5.0:

- Each test suite gets its own `<testsuite>` element (`#2982`_). Earlier all
  tests in all suites were added under the root suite.
- `<testsuite>` elements gets `timestamp` attribute denoting the suite start time (`#4074`_).
- Suite documentation and metadata are added under each `<testsuite>` as
  properties (`#4199`_).

Backwards incompatible changes
==============================

Python 2 is not supported anymore
---------------------------------

Robot Framework 5.0 requires Python 3.6 or newer (`#3457`_). Unfortunately this
also means that `Jython <http://jython.org>`_ and `IronPython <http://ironpython.net>`_
are not supported anymore because they do not have Python 3 compatible releases
available. If you are using Python 2, Jython, or IronPython, you can continue
using Robot Framework 4 series.

Loop control keywords cannot be used inside keywords
----------------------------------------------------

`Exit For Loop` and `Continue For Loop` keywords can nowadays only be used
directly inside a FOR loop, not in keywords used by loops (`#4185`_). For example,
this is not anymore supported:

.. code:: robotframework

    *** Keywords ***
    Looping
        FOR    ${x}    IN    @{stuff}
            Keyword
        END

    Keyword
        Exit For Loop

Notice also that if there is no need to support older Robot Framework versions,
it is recommended to use the new `BREAK and CONTINUE`_ statements instead of these
keywords.

Other backwards incompatible changes
------------------------------------

- `Enhancements to xUnit compatible outputs`_, especially adding separate
  `<testsuite>` element for each suite (`#2982`_), may affect tools using these outputs.

- `Run Keyword And Expect Error` requires a full match when using it with regular
  expression patterns (`#4178`_). Earlier it accidentally required the pattern
  to match only the beginning.

- The built-in Tidy tool has been removed in favor of the external
  `RoboTidy <https://robotidy.readthedocs.io>`_ (`#4020`_).

- `FOR` loop iteration type passed to listeners has been changed from
  `FOR ITERATION` to `ITERATION` (`#4182`_).

- `Process.Start Process` keywords returns the created process object
  instead of a generic handle (`#4104`_).

- Unrecognized options passed to the `robot.run` and `robot.rebot` APIs are
  are not anymore ignored but instead cause an error (`#4212`_).

- Deprecated `--critical` and `--noncritical` options have been removed (`#4189`_).

- Deprecated `--xunitskipnoncritical` option has been removed (`#4192`_).

Deprecated features
===================

`dataTypes` section in Libdoc spec files has been deprecated
------------------------------------------------------------

The `dataTypes` section was added to spec files in `Robot Framework 4.0`__
to store information about `Enums` and `TypedDicts`. In Robot Framework 5.0,
also information about automatically converted types (`#4160`_) and custom
converters (`#4088`_) were added to spec files, and the structure of the
`dataTypes` section was not considered convenient.

Instead of changing the `dataTypes` section, a new `types` section was added
to contain information about all converted types. The old `dataTypes` section
is still created and it contains same information as earlier. It is, however,
deprecated and will be removed in the future.

Other deprecated features
-------------------------

- Old Python 2/3 compatibility layer has been deprecated (`#4150`_). It was not
  removed to avoid breaking libraries and tools using it, but it will be more
  loudly deprecated in the future and eventually removed.

- `BuiltIn.Log`: `repr` argument has been deprecated in favor of more generic
  `formatter` (`#4142`_)

- `BuiltIn.Run Keyword Unless` has been deprecated (`#4174`_). It can be replaced
  with `Run Keyword If`, but the native `IF/ELSE` syntax is generally recommended
  instead.

__ https://github.com/robotframework/robotframework/blob/master/doc/releasenotes/rf-4.0.rst#libdoc-enhancements

Acknowledgements
================

Robot Framework development is sponsored by the `Robot Framework Foundation`_
and its close to 50 member organizations. Robot Framework 5.0 team funded by
them consisted of `Pekka Klärck <https://github.com/pekkaklarck>`_ and
`Janne Härkönen <https://github.com/yanne>`_ (part time).
In addition to that, the wider open source community has provided several
great contributions:

- `@rikerfi <https://github.com/rikerfi>`__ added many enhancements to xUnit outputs:

  - Separate `<testsuite>` elements for each suite (`#2982`_).
  - `timestamp` attribute to `<testsuite>` elements (`#4074`_).
  - Suite documentation and metadata as properties (`#4199`_).

- Also `@makeevolution <https://github.com/makeevolution>`__ did various enhancements:

  - New built-in tags `robot:exclude`, `robot:skip` and `robot:skip-on-failure` (`#4161`_).
  - New `format` option to `BuiltIn.Log To Console` (`#4115`_).

- `Bharat Patel <https://github.com/bbpatel2001>`__ implemented new `BREAK` and
  `CONTINUE` statements (`#4079`_).

- `@onurcelep <https://github.com/onurcelep>`__ enhanced `Process.Start Process`
  so that it returns the created process object instead of a generic handle (`#4104`_).

- `Robert Thomas <https://github.com/Robtom5>`__ added support for formatters
  when when logging using the `logging` module (`#3208`_).

- `Brandon Wolfe <https://github.com/Wolfe1>`__ added `type` and `len`
  formatters to the `BuiltIn.Log` keyword (`#4095`_).

- `Richard Ludwig <https://github.com/JockeJarre>`__ added full regular expression
  support to `OperatingSystem.Grep File` (`#4132`_).

- `Aleksi Simell <https://github.com/asimell>`__ enhanced `String.Generate Random String`
  to support generating random strings in different lengths (`#4133`_).

- `Daniel Biehl <https://github.com/d-biehl>`__ fixed a crash that occurred if
  user keyword argument specification contained a line with only the `...` line
  continuation marker (`#4181`_).

Huge thanks to all sponsors, contributors and to everyone else who has reported
problems, participated in discussions on various forums, or otherwise helped to make
Robot Framework and its community and ecosystem better.

| `Pekka Klärck <https://github.com/pekkaklarck>`__
| Robot Framework Lead Developer

Full list of fixes and enhancements
===================================

.. list-table::
    :header-rows: 1

    * - ID
      - Type
      - Priority
      - Summary
      - Added
    * - `#3075`_
      - enhancement
      - critical
      - Native support for `TRY/EXCEPT` functionality
      - alpha 1
    * - `#3457`_
      - enhancement
      - critical
      - Remove Python 2 and Python 3.5 support
      - alpha 1
    * - `#4088`_
      - enhancement
      - critical
      - Ability to register custom converters for keyword arguments
      - alpha 1
    * - `#4181`_
      - high
      - medium
      - Parsing crashes if user keyword argument specification contains a line with only `...`
      - beta 1
    * - `#4195`_
      - bug
      - high
      - Log: Linking to warnings and `--expandkeywords` broken with IF/ELSE structures
      - alpha 1
    * - `#2982`_
      - enhancement
      - high
      - xUnit outputs: Add separate `<testsuite>` entries for each suite
      - alpha 1
    * - `#4078`_
      - enhancement
      - high
      - New `RETURN` statement for returning from user keywords
      - alpha 1
    * - `#4079`_
      - enhancement
      - high
      - New `BREAK` and `CONTINUE` statements for controlling `FOR` and `WHILE` loop execution
      - alpha 1
    * - `#4084`_
      - enhancement
      - high
      - `WHILE` loop
      - alpha 1
    * - `#4093`_
      - enhancement
      - high
      - Inline `IF` support
      - alpha 1
    * - `#4160`_
      - enhancement
      - high
      - Libdoc: Include automatic argument conversion info
      - beta 1
    * - `#3208`_
      - bug
      - medium
      - Formatters are not supported when logging using the `logging` module
      - alpha 1
    * - `#4143`_
      - bug
      - medium
      - "Get Time" keyword doesn't return accurate time delta if range includes daylight savings change
      - alpha 1
    * - `#4178`_
      - bug
      - medium
      - `Run Keyword And Expect Error` passes if regular expression matches only the beginning
      - alpha 1
    * - `#4212`_
      - bug
      - medium
      - Options passed to `robot.run` and `robot.rebot` are not verified
      - beta 1
    * - `#4221`_
      - bug
      - medium
      - Argument validation fails in dry-run if arguments contain `&{dict}` variables
      - beta 1
    * - `#4020`_
      - enhancement
      - medium
      - Remove built-in Tidy tool in favor of external Robotidy
      - alpha 1
    * - `#4039`_
      - enhancement
      - medium
      - Include information about chained exceptions in failure tracebacks
      - alpha 1
    * - `#4074`_
      - enhancement
      - medium
      - Add timestamp attribute testsuite element in xunit output
      - alpha 1
    * - `#4095`_
      - enhancement
      - medium
      - BuiltIn.Log: Add `type` and `len` formatters
      - alpha 1
    * - `#4104`_
      - enhancement
      - medium
      - Process: Change `Start Process` to return created process object instead of generic handle
      - alpha 1
    * - `#4115`_
      - enhancement
      - medium
      - New `format` option to `Log To Console` to control alignment, fill characters, and so on
      - alpha 1
    * - `#4132`_
      - enhancement
      - medium
      - Full regex syntax for Grep file
      - alpha 1
    * - `#4133`_
      - enhancement
      - medium
      - Support variable length in `Generate Random String`
      - alpha 1
    * - `#4150`_
      - enhancement
      - medium
      - Deprecate old Python 2/3 compatibility layer
      - alpha 1
    * - `#4161`_
      - enhancement
      - medium
      - Add new builtin tags `robot:exclude`, `robot:skip` and `robot:skip-on-failure`
      - alpha 1
    * - `#4166`_
      - enhancement
      - medium
      - Add `start/end_body_item` methods to Visitor interface to ease visiting all body items
      - alpha 1
    * - `#4177`_
      - enhancement
      - medium
      - `Set Test/Suite/Global/Local Variable`: Recommend using `$name`, not `${name}` more strongly
      - alpha 1
    * - `#4185`_
      - enhancement
      - medium
      - Prohibit using `Exit For Loop` and `Continue For Loop` in keywords
      - alpha 1
    * - `#4191`_
      - enhancement
      - medium
      - Increase the limit of started keywords and control structures
      - alpha 1
    * - `#4199`_
      - enhancement
      - medium
      - Add suite documentation and metadata to xUnit outputs
      - alpha 1
    * - `#4202`_
      - enhancement
      - medium
      - Add line number information for tests in output.xml
      - beta 1
    * - `#4214`_
      - enhancement
      - medium
      - Do not expland `NOT RUN` keywords even if they match `--expandkeywords`
      - beta 1
    * - `#4218`_
      - enhancement
      - medium
      - Libdoc: Include usage information to data types in spec files
      - beta 1
    * - `#4225`_
      - enhancement
      - medium
      - Better error reporting if whitespace between keywords and arguments is missing
      - beta 1
    * - `#4134`_
      - bug
      - low
      - Assigments can have extra `=` in log if executed keyword does not exist
      - alpha 1
    * - `#4159`_
      - bug
      - low
      - Libdoc: Minor problems in reading and writing XML specs
      - alpha 1
    * - `#4168`_
      - bug
      - low
      - Argument conversion error occurs if argument has annotation that is not hashable
      - alpha 1
    * - `#4171`_
      - bug
      - low
      - Bad error if task is empty or has no name
      - alpha 1
    * - `#4201`_
      - bug
      - low
      - Error message related to creating user keywords do not have line number information
      - alpha 1
    * - `#4213`_
      - bug
      - low
      - `stdout` and `stderr` passed to `robot.run` and `robot.rebot` are ignored if parsing options fails
      - beta 1
    * - `#4222`_
      - bug
      - low
      - Incorrect documentation for automatic Boolean conversion
      - beta 1
    * - `#4224`_
      - bug
      - low
      - Automatic list, tuple, dict and set conversion do not work correctly with all containers
      - beta 1
    * - `#4142`_
      - enhancement
      - low
      - BuiltIn.Log: Deprecate `repr` argument in favor of more generic `formatter`
      - alpha 1
    * - `#4174`_
      - enhancement
      - low
      - Deprecate `Run Keyword Unless`
      - alpha 1
    * - `#4182`_
      - enhancement
      - low
      - Listeners: Rename `FOR` loop iteration type from `FOR ITERATION` to `ITERATION`
      - alpha 1
    * - `#4184`_
      - enhancement
      - low
      - Show FOR loop body in log also if there is nothing to loop over
      - alpha 1
    * - `#4189`_
      - enhancement
      - low
      - Remove deprecated `--critical` and `--noncritical` options
      - alpha 1
    * - `#4192`_
      - enhancement
      - low
      - Remove deprecated `--xunitskipnoncritical` option
      - alpha 1

Altogether 49 issues. View on the `issue tracker <https://github.com/robotframework/robotframework/issues?q=milestone%3Av5.0>`__.

.. _#3075: https://github.com/robotframework/robotframework/issues/3075
.. _#3457: https://github.com/robotframework/robotframework/issues/3457
.. _#4088: https://github.com/robotframework/robotframework/issues/4088
.. _#4181: https://github.com/robotframework/robotframework/issues/4181
.. _#4195: https://github.com/robotframework/robotframework/issues/4195
.. _#2982: https://github.com/robotframework/robotframework/issues/2982
.. _#4078: https://github.com/robotframework/robotframework/issues/4078
.. _#4079: https://github.com/robotframework/robotframework/issues/4079
.. _#4084: https://github.com/robotframework/robotframework/issues/4084
.. _#4093: https://github.com/robotframework/robotframework/issues/4093
.. _#4160: https://github.com/robotframework/robotframework/issues/4160
.. _#3208: https://github.com/robotframework/robotframework/issues/3208
.. _#4143: https://github.com/robotframework/robotframework/issues/4143
.. _#4178: https://github.com/robotframework/robotframework/issues/4178
.. _#4212: https://github.com/robotframework/robotframework/issues/4212
.. _#4221: https://github.com/robotframework/robotframework/issues/4221
.. _#4020: https://github.com/robotframework/robotframework/issues/4020
.. _#4039: https://github.com/robotframework/robotframework/issues/4039
.. _#4074: https://github.com/robotframework/robotframework/issues/4074
.. _#4095: https://github.com/robotframework/robotframework/issues/4095
.. _#4104: https://github.com/robotframework/robotframework/issues/4104
.. _#4115: https://github.com/robotframework/robotframework/issues/4115
.. _#4132: https://github.com/robotframework/robotframework/issues/4132
.. _#4133: https://github.com/robotframework/robotframework/issues/4133
.. _#4150: https://github.com/robotframework/robotframework/issues/4150
.. _#4161: https://github.com/robotframework/robotframework/issues/4161
.. _#4166: https://github.com/robotframework/robotframework/issues/4166
.. _#4177: https://github.com/robotframework/robotframework/issues/4177
.. _#4185: https://github.com/robotframework/robotframework/issues/4185
.. _#4191: https://github.com/robotframework/robotframework/issues/4191
.. _#4199: https://github.com/robotframework/robotframework/issues/4199
.. _#4202: https://github.com/robotframework/robotframework/issues/4202
.. _#4214: https://github.com/robotframework/robotframework/issues/4214
.. _#4218: https://github.com/robotframework/robotframework/issues/4218
.. _#4225: https://github.com/robotframework/robotframework/issues/4225
.. _#4134: https://github.com/robotframework/robotframework/issues/4134
.. _#4159: https://github.com/robotframework/robotframework/issues/4159
.. _#4168: https://github.com/robotframework/robotframework/issues/4168
.. _#4171: https://github.com/robotframework/robotframework/issues/4171
.. _#4201: https://github.com/robotframework/robotframework/issues/4201
.. _#4213: https://github.com/robotframework/robotframework/issues/4213
.. _#4222: https://github.com/robotframework/robotframework/issues/4222
.. _#4224: https://github.com/robotframework/robotframework/issues/4224
.. _#4142: https://github.com/robotframework/robotframework/issues/4142
.. _#4174: https://github.com/robotframework/robotframework/issues/4174
.. _#4182: https://github.com/robotframework/robotframework/issues/4182
.. _#4184: https://github.com/robotframework/robotframework/issues/4184
.. _#4189: https://github.com/robotframework/robotframework/issues/4189
.. _#4192: https://github.com/robotframework/robotframework/issues/4192
