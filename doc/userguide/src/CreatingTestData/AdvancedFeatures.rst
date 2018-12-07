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

1. Created as a user keyword in the same file where it is used. These
   keywords have the highest priority and they are always used, even
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
:name:`com.company.Library.Some Keyword`). If a custom name is given
to a library using the `WITH NAME syntax`_, the specified name must be
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

Keywords may be problematic in situations where they take
exceptionally long to execute or just hang endlessly. Robot Framework
allows you to set timeouts both for `test cases`_ and `user
keywords`_, and if a test or keyword is not finished within the
specified time, the keyword that is currently being executed is
forcefully stopped. Stopping keywords in this manner may leave the
library or system under test to an unstable state, and timeouts are
recommended only when there is no safer option available. In general,
libraries should be implemented so that keywords cannot hang or that
they have their own timeout mechanism, if necessary.

Test case timeout
~~~~~~~~~~~~~~~~~

The test case timeout can be set either by using the :setting:`Test
Timeout` setting in the Setting table or the :setting:`[Timeout]`
setting in the Test Case table. :setting:`Test Timeout` in the Setting
table defines a default test timeout value for all the test cases in
the test suite, whereas :setting:`[Timeout]` in the Test Case table
applies a timeout to an individual test case and overrides the
possible default value.

Using an empty :setting:`[Timeout]` means that the test has no
timeout even when :setting:`Test Timeout` is used. It is also possible
to use value `NONE` for this purpose.

Regardless of where the test timeout is defined, the first cell after
the setting name contains the duration of the timeout. The duration
must be given in Robot Framework's `time format`_, that is,
either directly in seconds or in a format like `1 minute
30 seconds`. It must be noted that there is always some overhead by the
framework, and timeouts shorter than one second are thus not
recommended.

The default error message displayed when a test timeout occurs is
`Test timeout <time> exceeded`. It is also possible to use custom
error messages, and these messages are written into the cells
after the timeout duration. The message can be split into multiple
cells, similarly as documentations. Both the timeout value and the
error message may contain variables.

If there is a timeout, the keyword running is stopped at the
expiration of the timeout and the test case fails. However, keywords
executed as `test teardown`_ are not interrupted if a test timeout
occurs, because they are normally engaged in important clean-up
activities. If necessary, it is possible to interrupt also these
keywords with `user keyword timeouts`_.

.. sourcecode:: robotframework

   *** Settings ***
   Test Timeout    2 minutes

   *** Test Cases ***
   Default Timeout
       [Documentation]    Timeout from the Setting table is used
       Some Keyword    argument

   Override
       [Documentation]    Override default, use 10 seconds timeout
       [Timeout]    10
       Some Keyword    argument

   Custom Message
       [Documentation]    Override default and use custom message
       [Timeout]    1min 10s    This is my custom error
       Some Keyword    argument

   Variables
       [Documentation]    It is possible to use variables too
       [Timeout]    ${TIMEOUT}
       Some Keyword    argument

   No Timeout
       [Documentation]    Empty timeout means no timeout even when Test Timeout has been used
       [Timeout]
       Some Keyword    argument

   No Timeout 2
       [Documentation]    Disabling timeout with NONE works too and is more explicit.
       [Timeout]    NONE
       Some Keyword    argument

User keyword timeout
~~~~~~~~~~~~~~~~~~~~

A timeout can be set for a user keyword using the :setting:`[Timeout]`
setting in the Keyword table. The syntax for setting it, including how
timeout values and possible custom messages are given, is
identical to the syntax used with `test case timeouts`_. If no custom
message is provided, the default error message `Keyword timeout
<time> exceeded` is used if a timeout occurs.

Starting from Robot Framework 3.0, timeout can be specified as a variable
so that the variable value is given as an argument. Using global variables
works already with previous versions.

.. sourcecode:: robotframework

   *** Keywords ***
   Timed Keyword
       [Documentation]    Set only the timeout value and not the custom message.
       [Timeout]    1 minute 42 seconds
       Do Something
       Do Something Else

   Wrapper With Timeout
       [Arguments]    @{args}
       [Documentation]    This keyword is a wrapper that adds a timeout to another keyword.
       [Timeout]    2 minutes    Original Keyword didn't finish in 2 minutes
       Original Keyword    @{args}

   Wrapper With Customizable Timeout
       [Arguments]    ${timeout}    @{args}
       [Documentation]    Same as the above but timeout given as an argument.
       [Timeout]    ${timeout}
       Original Keyword    @{args}

A user keyword timeout is applicable during the execution of that user
keyword. If the total time of the whole keyword is longer than the
timeout value, the currently executed keyword is stopped. User keyword
timeouts are applicable also during a test case teardown, whereas test
timeouts are not.

If both the test case and some of its keywords (or several nested
keywords) have a timeout, the active timeout is the one with the least
time left.

.. _for loop:

For loops
---------

Repeating same actions several times is quite a common need in test
automation. With Robot Framework, test libraries can have any kind of
loop constructs, and most of the time loops should be implemented in
them. Robot Framework also has its own for loop syntax, which is
useful, for example, when there is a need to repeat keywords from
different libraries.

For loops can be used with both test cases and user keywords. Except for
really simple cases, user keywords are better, because they hide the
complexity introduced by for loops. The basic for loop syntax,
`FOR item IN sequence`, is derived from Python, but similar
syntax is supported also by various other programming languages.

Simple for loop
~~~~~~~~~~~~~~~

In a normal for loop, one variable is assigned based on a list of values,
one value per iteration. The syntax starts with `FOR` (case-sensitive) as
a marker, then the loop variable, then a mandatory `IN` (case-sensitive) as
a separator, and finally the values to iterate. These values can contain
variables_, including `list variables`_.

The keywords used in the for loop are on the following rows and the loop
ends with `END` (case-sensitive) on its own row. Keywords inside the loop
do not need to be indented, but that is highly recommended to make the syntax
easier to read.

.. sourcecode:: robotframework

   *** Test Cases ***
   Example
       FOR    ${animal}    IN    cat    dog
           Log    ${animal}
           Log    2nd keyword
       END
       Log    Outside loop

   Second Example
       FOR    ${var}    IN    one    two    ${3}    four    ${five}
       ...    kuusi    7    eight    nine    ${last}
           Log    ${var}
       END

The for loop in :name:`Example` above is executed twice, so that first
the loop variable `${animal}` has the value `cat` and then
`dog`. The loop consists of two :name:`Log` keywords. In the
second example, loop values are `split into two rows`__ and the
loop is run altogether ten times.

It is often convenient to use for loops with `list variables`_. This is
illustrated by the example below, where `@{ELEMENTS}` contains
an arbitrarily long list of elements and keyword :name:`Start Element` is
used with all of them one by one.

.. sourcecode:: robotframework

   *** Test Cases ***
   Example
       FOR    ${element}    IN    @{ELEMENTS}
           Start Element    ${element}
       END

__ `Dividing test data to several rows`_

Old for loop syntax
~~~~~~~~~~~~~~~~~~~

For loop syntax was enhanced in various ways in Robot Framework 3.1.
The most noticeable change was that loops nowadays end with the explicit
`END` marker and keywords inside the loop do not need to be indented.
In the `space separated plain text format`_ indentation required
`escaping with a backslash`__ which resulted in quite ugly syntax:

.. sourcecode:: robotframework

   *** Test Cases ***
   Example
       :FOR    ${animal}    IN    cat    dog
       \    Log    ${animal}
       \    Log    2nd keyword
       Log    Outside loop

Another change, also visible in the example above, was that the for loop
marker used to be `:FOR` when nowadays just `FOR` is enough. Related to that,
the `:FOR` marker and also the `IN` separator were case-insensitive but
nowadays both `FOR` and `IN` are case-sensitive.

Old for loop syntax still works in Robot Framework 3.1 and only using
`IN` case-insensitively causes a deprecation warning. Not closing loops
with `END`, escaping keywords inside loops with :codesc:`\\`, and using
`:FOR` instead of `FOR` are all going to be deprecated in Robot Framework 3.2.
Users are advised to switch to the new syntax as soon as possible.

__ Escaping_

Nested for loops
~~~~~~~~~~~~~~~~

Having nested for loops is not supported directly, but it is possible to use
a user keyword inside a for loop and have another for loop there.

.. sourcecode:: robotframework

   *** Keywords ***
   Handle Table
       [Arguments]    @{table}
       FOR    ${row}    IN    @{table}
           Handle Row    @{row}
       END

   Handle Row
       [Arguments]    @{row}
       FOR    ${cell}    IN    @{row}
           Handle Cell    ${cell}
       END

Using several loop variables
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

It is also possible to use several loop variables. The syntax is the
same as with the normal for loop, but all loop variables are listed in
the cells between `FOR` and `IN`. There can be any number of loop
variables, but the number of values must be evenly dividable by the number of
variables.

If there are lot of values to iterate, it is often convenient to organize
them below the loop variables, as in the first loop of the example below:

.. sourcecode:: robotframework

   *** Test Cases ***
   Three loop variables
       FOR    ${index}    ${english}    ${finnish}    IN
       ...     1           cat           kissa
       ...     2           dog           koira
       ...     3           horse         hevonen
           Add to dictionary    ${english}    ${finnish}    ${index}
       END
       FOR    ${name}    ${id}    IN    @{EMPLOYERS}
           Create    ${name}    ${id}
       END

For-in-range loop
~~~~~~~~~~~~~~~~~

Earlier for loops always iterated over a sequence, and this is also the most
common use case. Sometimes it is still convenient to have a for loop
that is executed a certain number of times, and Robot Framework has a
special `FOR index IN RANGE limit` syntax for this purpose. This
syntax is derived from the similar Python idiom using the `built-in
range() function`__.

__ http://docs.python.org/library/functions.html#func-range

Similarly as other for loops, the for-in-range loop starts with
`FOR` and the loop variable is in the next cell. In this format
there can be only one loop variable and it contains the current loop
index. The next cell must contain `IN RANGE` (case-sensitive) and
the subsequent cells loop limits.

In the simplest case, only the upper limit of the loop is
specified. In this case, loop indexes start from zero and increase by one
until, but excluding, the limit. It is also possible to give both the
start and end limits. Then indexes start from the start limit, but
increase similarly as in the simple case. Finally, it is possible to give
also the step value that specifies the increment to use. If the step
is negative, it is used as decrement.

It is possible to use simple arithmetic such as addition and subtraction
with the range limits. This is especially useful when the limits are
specified with variables. Start, end and step are typically given as
integers, but using float values is possible as well.

.. sourcecode:: robotframework

   *** Test Cases ***
   Only upper limit
       [Documentation]    Loops over values from 0 to 9
       FOR    ${index}    IN RANGE    10
           Log    ${index}
       END

   Start and end
       [Documentation]    Loops over values from 1 to 10
       FOR    ${index}    IN RANGE    1    11
           Log    ${index}
       END

   Also step given
       [Documentation]    Loops over values 5, 15, and 25
       FOR    ${index}    IN RANGE    5    26    10
           Log    ${index}
       END

   Negative step
       [Documentation]    Loops over values 13, 3, and -7
       FOR    ${index}    IN RANGE    13    -13    -10
           Log    ${index}
       END

   Arithmetic
       [Documentation]    Arithmetic with variable
       FOR    ${index}    IN RANGE    ${var} + 1
           Log    ${index}
       END

   Float parameters
       [Documentation]    Loops over values 3.14, 4.34, and 5.54
       FOR    ${index}    IN RANGE    3.14    6.09    1.2
           Log    ${index}
       END

.. note:: Prior to Robot Framework 3.1, the `IN RANGE` separator was both
          case- and space-insensitive. Such usage is nowadays deprecated
          and exactly `IN RANGE` is required.

For-in-enumerate loop
~~~~~~~~~~~~~~~~~~~~~

Sometimes it is useful to loop over a list and also keep track of your location
inside the list. Robot Framework has a special
`FOR index ... IN ENUMERATE ...` syntax for this situation.
This syntax is derived from the `Python built-in enumerate() function`__.

__ http://docs.python.org/library/functions.html#enumerate

For-in-enumerate loops work just like regular for loops, except the cell
after its loop variables must say `IN ENUMERATE` (case-sensitive),
and they must have an additional index variable before any other loop-variables.
That index variable has a value of `0` for the first iteration, `1` for the
second, etc.

For example, the following two test cases do the same thing:

.. sourcecode:: robotframework

   *** Variables ***
   @{LIST}         a    b    c

   *** Test Cases ***
   Manage index manually
       ${index} =    Set Variable    -1
       FOR    ${item}    IN    @{LIST}
           ${index} =    Evaluate    ${index} + 1
           My Keyword    ${index}    ${item}
       END

   For-in-enumerate
       FOR    ${index}    ${item}    IN ENUMERATE    @{LIST}
           My Keyword    ${index}    ${item}
       END

Just like with regular for loops, you can loop over multiple values per loop
iteration as long as the number of values in your list is evenly divisible by
the number of loop-variables (excluding the first, index variable).

.. sourcecode:: robotframework

   *** Test Case ***
   For-in-enumerate with two values per iteration
       FOR    ${index}    ${en}    ${fi}    IN ENUMERATE
       ...    cat      kissa
       ...    dog      koira
       ...    horse    hevonen
           Log    "${en}" in English is "${fi}" in Finnish (index: ${index})
       END

.. note:: Prior to Robot Framework 3.1, the `IN ENUMERATE` separator was both
          case- and space-insensitive. Such usage is nowadays deprecated
          and exactly `IN ENUMERATE` is required.

For-in-zip loop
~~~~~~~~~~~~~~~

Some tests build up several related lists, then loop over them together.
Robot Framework has a shortcut for this case: `FOR ... IN ZIP ...`, which
is derived from the `Python built-in zip() function`__.

__ http://docs.python.org/library/functions.html#zip

This may be easiest to show with an example:

.. sourcecode:: robotframework

   *** Variables ***
   @{NUMBERS}      ${1}    ${2}    ${5}
   @{NAMES}        one     two     five

   *** Test Cases ***
   Iterate over two lists manually
       ${length}=    Get Length    ${NUMBERS}
       FOR    ${idx}    IN RANGE    ${length}
           Number Should Be Named    ${NUMBERS}[${idx}]    ${NAMES}[${idx}]
       END

   For-in-zip
       FOR    ${number}    ${name}    IN ZIP    ${NUMBERS}    ${NAMES}
           Number Should Be Named    ${number}    ${name}
       END

Similarly as for-in-range and for-in-enumerate loops, for-in-zip loops require
the cell after the loop variables to read `IN ZIP` (case-sensitive).

Values used with for-in-zip loops must be lists or list-like objects, and
there must be same number of loop variables as lists to loop over. Looping
will stop when the shortest list is exhausted.

Note that any lists used with for-in-zip should usually be given as `scalar
variables`_ like `${list}`. A `list variable`_ only works if its items
themselves are lists.

.. note:: Prior to Robot Framework 3.1, the `IN ZIP` separator was both
          case- and space-insensitive. Such usage is nowadays deprecated
          and exactly `IN ZIP` is required.

Exiting for loop
~~~~~~~~~~~~~~~~

Normally for loops are executed until all the loop values have been iterated
or a keyword used inside the loop fails. If there is a need to exit the loop
earlier, BuiltIn_ keywords :name:`Exit For Loop` and :name:`Exit For Loop If`
can be used to accomplish that. They works similarly as `break`
statement in Python, Java, and many other programming languages.

:name:`Exit For Loop` and :name:`Exit For Loop If` keywords can be used
directly inside a for loop or in a keyword that the loop uses. In both cases
test execution continues after the loop. It is an error to use these keywords
outside a for loop.

.. sourcecode:: robotframework

   *** Test Cases ***
   Exit Example
       ${text} =    Set Variable    ${EMPTY}
       FOR    ${var}    IN    one    two
           Run Keyword If    '${var}' == 'two'    Exit For Loop
           ${text} =    Set Variable    ${text}${var}
       END
       Should Be Equal    ${text}    one

In the above example it would be possible to use :name:`Exit For Loop If`
instead of using :name:`Exit For Loop` with :name:`Run Keyword If`.
For more information about these keywords, including more usage examples,
see their documentation in the BuiltIn_ library.

Continuing for loop
~~~~~~~~~~~~~~~~~~~

In addition to exiting a for loop prematurely, it is also possible to
continue to the next iteration of the loop before all keywords have been
executed. This can be done using BuiltIn_ keywords :name:`Continue For Loop`
and :name:`Continue For Loop If`, that work like `continue` statement
in many programming languages.

:name:`Continue For Loop` and :name:`Continue For Loop If` keywords can be used
directly inside a for loop or in a keyword that the loop uses. In both cases
rest of the keywords in that iteration are skipped and execution continues
from the next iteration. If these keywords are used on the last iteration,
execution continues after the loop. It is an error to use these keywords
outside a for loop.

.. sourcecode:: robotframework

   *** Test Cases ***
   Continue Example
       ${text} =    Set Variable    ${EMPTY}
       FOR    ${var}    IN    one    two    three
           Continue For Loop If    '${var}' == 'two'
           ${text} =    Set Variable    ${text}${var}
       END
       Should Be Equal    ${text}    onethree

For more information about these keywords, including usage examples, see their
documentation in the BuiltIn_ library.

Removing unnecessary keywords from outputs
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

For loops with multiple iterations often create lots of output and
considerably increase the size of the generated output_ and log_ files.
It is possible to `remove unnecessary keywords`__ from the outputs using
:option:`--RemoveKeywords FOR` command line option.

__ `Removing and flattening keywords`_

Repeating single keyword
~~~~~~~~~~~~~~~~~~~~~~~~

For loops can be excessive in situations where there is only a need to
repeat a single keyword. In these cases it is often easier to use
BuiltIn_ keyword :name:`Repeat Keyword`. This keyword takes a
keyword and how many times to repeat it as arguments. The times to
repeat the keyword can have an optional postfix `times` or `x`
to make the syntax easier to read.

.. sourcecode:: robotframework

   *** Test Cases ***
   Example
       Repeat Keyword    5    Some Keyword    arg1    arg2
       Repeat Keyword    42 times    My Keyword
       Repeat Keyword    ${var}    Another Keyword    argument

Conditional execution
---------------------

In general, it is not recommended to have conditional logic in test
cases, or even in user keywords, because it can make them hard to
understand and maintain. Instead, this kind of logic should be in test
libraries, where it can be implemented using natural programming
language constructs. However, some conditional logic can be useful at
times, and even though Robot Framework does not have an actual if/else
construct, there are several ways to get the same effect.

- The name of the keyword used as a setup or a teardown of both `test
  cases`__ and `test suites`__ can be specified using a
  variable. This facilitates changing them, for example, from
  the command line.

- The BuiltIn_ keyword :name:`Run Keyword` takes a keyword to actually
  execute as an argument, and it can thus be a variable. The value of
  the variable can, for example, be got dynamically from an earlier
  keyword or given from the command line.

- The BuiltIn_ keywords :name:`Run Keyword If` and :name:`Run Keyword
  Unless` execute a named keyword only if a certain expression is
  true or false, respectively. They are ideally suited to creating
  simple if/else constructs. For an example, see the documentation of
  the former.

- Another BuiltIn_ keyword, :name:`Set Variable If`, can be used to set
  variables dynamically based on a given expression.

- There are several BuiltIn_ keywords that allow executing a named
  keyword only if a test case or test suite has failed or passed.

__ `Test setup and teardown`_
__ `Suite setup and teardown`_


Parallel execution of keywords
------------------------------

When parallel execution is needed, it must be implemented in test library
level so that the library executes the code on background. Typically this
means that the library needs a keyword like :name:`Start Something` that
starts the execution and returns immediately, and another keyword like
:name:`Get Results From Something` that waits until the result is available
and returns it. See OperatingSystem_ library keywords :name:`Start Process`
and :name:`Read Process Output` for an example.
