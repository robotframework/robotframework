Advanced features
=================

.. contents::
   :depth: 2
   :local:

Handling keywords with same names
---------------------------------

Keywords that are used with Robot Framework are either `library
keywords`_ or `user keywords`_. The former come from `standard
libraries`_ or `external libraries`_, and the latter are either
created in the same file where they are used or then imported from
`resource files`_. When many keywords are in use, it is quite common
that some of them have the same name, and this section describes how to
handle possible conflicts in these situations.

Keyword scopes
~~~~~~~~~~~~~~

When only a keyword name is used and there are several keywords with
that name, Robot Framework attempts to determine which keyword has the
highest priority based on its scope. The keyword's scope is determined
on the basis of how the keyword in question is created:

1. Created as a user keyword in the currently executed `suite file`_.
   These keywords have the highest priority and they are always used, even
   if there are other keywords with the same name elsewhere.

2. Created in a resource file and imported either directly or
   indirectly from another resource file. This is the second-highest
   priority.

3. Created in an external test library. These keywords are used, if
   there are no user keywords with the same name. However, if there is
   a keyword with the same name in the standard library, a warning is
   displayed.

4. Created in a standard library. These keywords have the lowest
   priority.

Specifying a keyword explicitly
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Scopes alone are not a sufficient solution, because there can be
keywords with the same name in several libraries or resources, and
thus, they provide a mechanism to use only the keyword of the
highest priority. In such cases, it is possible to use *the full name
of the keyword*, where the keyword name is prefixed with the name of
the resource or library and a dot is a delimiter.

With library keywords, the long format means only using the format
:name:`LibraryName.Keyword Name`. For example, the keyword :name:`Run`
from the OperatingSystem_ library could be used as
:name:`OperatingSystem.Run`, even if there was another :name:`Run`
keyword somewhere else. If the library is in a module or package, the
full module or package name must be used (for example,
:name:`com.company.Library.Some Keyword`). If a `custom name`__ is given
to a library when importing it, the specified name must be
used also in the full keyword name.

Resource files are specified in the full keyword name, similarly as
library names. The name of the resource is derived from the basename
of the resource file without the file extension. For example, the
keyword :name:`Example` in a resource file :file:`myresources.html` can
be used as :name:`myresources.Example`. Note that this syntax does not
work, if several resource files have the same basename. In such
cases, either the files or the keywords must be renamed. The full name
of the keyword is case-, space- and underscore-insensitive, similarly
as normal keyword names.

__ `Setting custom name to library`_

.. _library search order:

Specifying explicit priority between libraries and resources
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If there are multiple conflicts between keywords, specifying all the keywords
in the long format can be quite a lot work. Using the long format also makes it
impossible to create dynamic test cases or user keywords that work differently
depending on which libraries or resources are available. A solution to both of
these problems is specifying the keyword priorities explicitly using the keyword
:name:`Set Library Search Order` from the BuiltIn_ library.

.. note:: Although the keyword has the word *library* in its name, it works
          also with resource files. As discussed above, keywords in resources
          always have higher priority than keywords in libraries, though.

The :name:`Set Library Search Order` accepts an ordered list or libraries and
resources as arguments. When a keyword name in the test data matches multiple
keywords, the first library or resource containing the keyword is selected and
that keyword implementation used. If the keyword is not found from any of the
specified libraries or resources, execution fails for conflict the same way as
when the search order is not set.

For more information and examples, see the documentation of the keyword.

Timeouts
--------

Sometimes keywords may take exceptionally long time to execute or just hang
endlessly. Robot Framework allows you to set timeouts both for `test cases`_
and `user keywords`_, and if a test or keyword is not finished within the
specified time, the keyword that is currently being executed is forcefully
stopped.

Stopping keywords in this manner may leave the library, the test environment
or the system under test to an unstable state, and timeouts are recommended
only when there is no safer option available. In general, libraries should be
implemented so that keywords cannot hang or that they have their own timeout
mechanism.

Test case timeout
~~~~~~~~~~~~~~~~~

The test case timeout can be set either by using the :setting:`Test Timeout`
setting in the Setting section or the :setting:`[Timeout]` setting with
individual test cases. :setting:`Test Timeout` defines a default timeout
for all the test cases in that suite, whereas :setting:`[Timeout]` applies
a timeout to a particular test case and overrides the possible default value.

Using an empty :setting:`[Timeout]` means that the test has no timeout even
when :setting:`Test Timeout` is used. It is also possible to use explicit
`NONE` value for this purpose. The timeout is effectively ignored also if
its value is zero or negative.

Regardless of where the test timeout is defined, the value given to it
contains the duration of the timeout. The duration must be given in Robot
Framework's `time format`_, that is, either directly in seconds like `10`
or in a format like `1 minute 30 seconds`. Timeouts can also be specified
as variables_ making it possible to give them, for example, from the command
line.

If there is a timeout and it expires, the keyword that is currently running
is stopped and the test case fails. Keywords executed as part of `test
teardown`_ are not interrupted if a test timeout occurs, though, but the test
is nevertheless marked failed. If a keyword in teardown may hang, it can be
stopped by using `user keyword timeouts`_.

.. sourcecode:: robotframework

   *** Settings ***
   Test Timeout       2 minutes

   *** Test Cases ***
   Default timeout
       [Documentation]    Default timeout from Settings is used.
       Some Keyword    argument

   Override
       [Documentation]    Override default, use 10 seconds timeout.
       [Timeout]    10
       Some Keyword    argument

   Variables
       [Documentation]    It is possible to use variables too.
       [Timeout]    ${TIMEOUT}
       Some Keyword    argument

   No timeout
       [Documentation]    Empty timeout means no timeout even when Test Timeout has been used.
       [Timeout]
       Some Keyword    argument

   No timeout 2
       [Documentation]    Disabling timeout with NONE works too and is more explicit.
       [Timeout]    NONE
       Some Keyword    argument

User keyword timeout
~~~~~~~~~~~~~~~~~~~~

Timeouts can be set for user keywords using the :setting:`[Timeout]` setting.
The syntax is exactly the same as with `test case timeout`_, but user keyword
timeouts do not have any default value. If a user keyword timeout is specified
using a variable, the value can be given also as a keyword argument.

.. sourcecode:: robotframework

   *** Keywords ***
   Hardcoded
       [Arguments]    ${arg}
       [Timeout]    1 minute 42 seconds
       Some Keyword    ${arg}

   Configurable
       [Arguments]    ${arg}    ${timeout}
       [Timeout]    ${timeout}
       Some Keyword    ${arg}

   Run Keyword with Timeout
       [Arguments]    ${keyword}    @{args}    &{kwargs}    ${timeout}=1 minute
       [Documentation]    Wrapper that runs another keyword with a configurable timeout.
       [Timeout]    ${timeout}
       Run Keyword    ${keyword}    @{args}    &{kwargs}

A user keyword timeout is applicable during the execution of that user
keyword. If the total time of the whole keyword is longer than the
timeout value, the currently executed keyword is stopped. User keyword
timeouts are applicable also during a test case teardown, whereas test
timeouts are not.

If both the test case and some of its keywords (or several nested
keywords) have a timeout, the active timeout is the one with the least
time left.

.. note:: With earlier Robot Framework versions it was possible to specify
          a custom error message to use if a timeout expires. This
          functionality was deprecated in Robot Framework 3.0.1 and removed
          in Robot Framework 3.2.


Parallel execution of keywords
------------------------------

When parallel execution is needed, it must be implemented in test library
level so that the library executes the code on background. Typically this
means that the library needs a keyword like :name:`Start Something` that
starts the execution and returns immediately, and another keyword like
:name:`Get Results From Something` that waits until the result is available
and returns it. See Process_ library keywords :name:`Start Process`
and :name:`Wait For Process` for an example.
