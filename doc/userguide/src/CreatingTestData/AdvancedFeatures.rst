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

1. Created as a user keyword in the currently executed `test case file`_.
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

.. _for:
.. _for loop:

`FOR` loops
-----------

Repeating same actions several times is quite a common need in test
automation. With Robot Framework, test libraries can have any kind of
loop constructs, and most of the time loops should be implemented in
them. Robot Framework also has its own `FOR` loop syntax, which is
useful, for example, when there is a need to repeat keywords from
different libraries.

`FOR` loops can be used with both test cases and user keywords. Except for
really simple cases, user keywords are better, because they hide the
complexity introduced by `FOR` loops. The basic `FOR` loop syntax,
`FOR item IN sequence`, is derived from Python, but similar
syntax is supported also by various other programming languages.

Simple `FOR` loop
~~~~~~~~~~~~~~~~~

In a normal `FOR` loop, one variable is assigned based on a list of values,
one value per iteration. The syntax starts with `FOR` (case-sensitive) as
a marker, then the loop variable, then a mandatory `IN` (case-sensitive) as
a separator, and finally the values to iterate. These values can contain
variables_, including `list variables`_.

The keywords used in the `FOR` loop are on the following rows and the loop
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

The `FOR` loop in :name:`Example` above is executed twice, so that first
the loop variable `${animal}` has the value `cat` and then
`dog`. The loop consists of two :name:`Log` keywords. In the
second example, loop values are `split into two rows`__ and the
loop is run altogether ten times.

It is often convenient to use `FOR` loops with `list variables`_. This is
illustrated by the example below, where `@{ELEMENTS}` contains
an arbitrarily long list of elements and keyword :name:`Start Element` is
used with all of them one by one.

.. sourcecode:: robotframework

   *** Test Cases ***
   Example
       FOR    ${element}    IN    @{ELEMENTS}
           Start Element    ${element}
       END

__ `Dividing data to several rows`_

Old `FOR` loop syntax
~~~~~~~~~~~~~~~~~~~~~

Prior to Robot Framework 3.1 the `FOR` loop syntax was different than nowadays.
The marker to start the loop was `:FOR` instead of `FOR` and loop contents needed
to be explicitly marked with a backslash instead of using the `END` marker to end
the loop. The first example above would look like this using the old syntax:

.. sourcecode:: robotframework

   *** Test Cases ***
   Example
       :FOR    ${animal}    IN    cat    dog
       \    Log    ${animal}
       \    Log    2nd keyword
       Log    Outside loop

The old syntax was deprecated in Robot Framework 3.2 and the support for it was
removed altogether in Robot Framework 4.0.

Nested `FOR` loops
~~~~~~~~~~~~~~~~~~

Starting from Robot Framework 4.0, it is possible to use nested `FOR` loops
simply by adding another loop inside a loop:

.. sourcecode:: robotframework

   *** Keywords ***
   Handle Table
       [Arguments]    @{table}
       FOR    ${row}    IN    @{table}
           FOR    ${cell}    IN    @{row}
               Handle Cell    ${cell}
           END
       END

There can be multiple nesting levels and one loop can contain several loops:

.. sourcecode:: robotframework

   *** Test Cases ***
   Example
       FOR    ${root}    IN    r1    r2
           FOR    ${child}    IN    c1   c2    c3
               FOR    ${grandchild}    IN    g1    g2
                   Log Many    ${root}    ${child}    ${grandchild}
               END
           END
           FOR    ${sibling}    IN    s1    s2    s3
                   Log Many    ${root}    ${sibling}
           END
       END

With earlier Robot Framework versions nesting `FOR` loops was not supported directly,
but it was possible to have a user keyword inside a loop and have another loop there.

Using several loop variables
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

It is also possible to use several loop variables. The syntax is the
same as with the normal `FOR` loop, but all loop variables are listed in
the cells between `FOR` and `IN`. There can be any number of loop
variables, but the number of values must be evenly dividable by the number of
variables.

If there are lot of values to iterate, it is often convenient to organize
them below the loop variables, as in the first loop of the example below:

.. sourcecode:: robotframework

   *** Test Cases ***
   Multiple loop variables
       FOR    ${index}    ${english}    ${finnish}    IN
       ...     1           cat           kissa
       ...     2           dog           koira
       ...     3           horse         hevonen
           Add Translation    ${english}    ${finnish}    ${index}
       END
       FOR    ${name}    ${id}    IN    @{EMPLOYERS}
           Create    ${name}    ${id}
       END

`FOR-IN-RANGE` loop
~~~~~~~~~~~~~~~~~~~

All `FOR` loops in the previous section iterated over a sequence. That is the most
common use case, but sometimes it is convenient to have a loop that is executed
a certain number of times. For this purpose Robot Framework has a special
`FOR index IN RANGE limit` loop syntax that is derived from the similar Python
idiom using the `built-in range() function`__.

__ http://docs.python.org/library/functions.html#func-range

Similarly as other `FOR` loops, the `FOR-IN-RANGE` loop starts with
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

`FOR-IN-ENUMERATE` loop
~~~~~~~~~~~~~~~~~~~~~~~

Sometimes it is useful to loop over a list and also keep track of your location
inside the list. Robot Framework has a special
`FOR index ... IN ENUMERATE ...` syntax for this situation.
This syntax is derived from the `Python built-in enumerate() function`__.

__ http://docs.python.org/library/functions.html#enumerate

`FOR-IN-ENUMERATE` loops work just like regular `FOR` loops, except the cell
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

   FOR-IN-ENUMERATE
       FOR    ${index}    ${item}    IN ENUMERATE    @{LIST}
           My Keyword    ${index}    ${item}
       END

Starting from Robot Framework 4.0, it is possible to specify a custom start index
by using `start=<index>` syntax as the last item of the `FOR ... IN ENUMERATE`
header:

.. sourcecode:: robotframework

   *** Variables ***
   @{LIST}         a    b    c
   ${START}        10

   *** Test Cases ***
   For-in-enumerate with start
       FOR    ${index}    ${item}    IN ENUMERATE    @{LIST}    start=1
           My Keyword    ${index}    ${item}
       END

   Start as variable
       FOR    ${index}    ${item}    IN ENUMERATE    @{LIST}    start=${start}
           My Keyword    ${index}    ${item}
       END

The `start=<index>` syntax must be explicitly used in the `FOR` header and it cannot
itself come from a variable. If the last actual item to enumerate would start with
`start=`, it needs to be escaped like `start\=`.

Just like with regular `FOR` loops, you can loop over multiple values per loop
iteration as long as the number of values in your list is evenly divisible by
the number of loop-variables (excluding the first, index variable):

.. sourcecode:: robotframework

   *** Test Case ***
   FOR-IN-ENUMERATE with two values per iteration
       FOR    ${index}    ${en}    ${fi}    IN ENUMERATE
       ...    cat      kissa
       ...    dog      koira
       ...    horse    hevonen
           Log    "${en}" in English is "${fi}" in Finnish (index: ${index})
       END

If you only use one loop variable with FOR-IN-ENUMERATE loops, that variable
will become a Python tuple containing the index and the iterated value:

.. sourcecode:: robotframework

   *** Test Case ***
   FOR-IN-ENUMERATE with one loop variable
       FOR    ${x}    IN ENUMERATE    @{LIST}
           Length Should Be    ${x}    2
           Log    Index is ${x}[0] and item is ${x}[1].
       END

.. note:: FOR-IN-ENUMERATE loops with only one loop variable is a new
          feature in Robot Framework 3.2.

`FOR-IN-ZIP` loop
~~~~~~~~~~~~~~~~~

Some tests build up several related lists, then loop over them together.
Robot Framework has a shortcut for this case: `FOR ... IN ZIP ...`, which
is derived from the `Python built-in zip() function`__.

__ http://docs.python.org/library/functions.html#zip

This may be easiest to show with an example:

.. sourcecode:: robotframework

   *** Variables ***
   @{NUMBERS}       ${1}    ${2}    ${5}
   @{NAMES}         one     two     five

   *** Test Cases ***
   Iterate over two lists manually
       ${length}=    Get Length    ${NUMBERS}
       FOR    ${index}    IN RANGE    ${length}
           Log Many    ${NUMBERS}[${index}]    ${NAMES}[${index}]
       END

   FOR-IN-ZIP
       FOR    ${number}    ${name}    IN ZIP    ${NUMBERS}    ${NAMES}
           Log Many    ${number}    ${name}
       END

Similarly as FOR-IN-RANGE and FOR-IN-ENUMERATE loops, FOR-IN-ZIP loops require
the cell after the loop variables to read `IN ZIP` (case-sensitive).
Values used with FOR-IN-ZIP loops must be lists or list-like objects. Looping
will stop when the shortest list is exhausted.

Lists to iterate over must always be given either as `scalar variables`_ like
`${items}` or as `list variables`_ like `@{lists}` that yield the actual
iterated lists. The former approach is more common and it was already
demonstrated above. The latter approach works like this:

.. sourcecode:: robotframework

   *** Variables ***
   @{NUMBERS}       ${1}    ${2}    ${5}
   @{NAMES}         one     two     five
   @{LISTS}         ${NUMBERS}    ${NAMES}

   *** Test Cases ***
   FOR-IN-ZIP with lists from variable
       FOR    ${number}    ${name}    IN ZIP    @{LISTS}
           Log Many    ${number}    ${name}
       END

The number of lists to iterate over is not limited, but it must match
the number of loop variables. Alternatively there can be just one loop
variable that then becomes a Python tuple getting items from all lists.

.. sourcecode:: robotframework

   *** Variables ***
   @{ABC}           a    b    c
   @{XYZ}           x    y    z
   @{NUM}           1    2    3    4    5

   *** Test Cases ***
   FOR-IN-ZIP with multiple lists
       FOR    ${a}    ${x}    ${n}    IN ZIP    ${ABC}    ${XYZ}    ${NUM}
           Log Many    ${a}    ${x}    ${n}
       END

   FOR-IN-ZIP with one variable
       FOR    ${items}    IN ZIP    ${ABC}    ${XYZ}    ${NUM}
           Length Should Be    ${items}    3
           Log Many    ${items}[0]    ${items}[1]    ${items}[2]
       END

If lists have an unequal number of items, the shortest list defines how
many iterations there are and values at the end of longer lists are ignored.
For example, the above examples loop only three times and values `4` and `5`
in the `${NUM}` list are ignored.

.. note:: Getting lists to iterate over from list variables and using
          just one loop variable are new features in Robot Framework 3.2.

Dictionary iteration
~~~~~~~~~~~~~~~~~~~~

Normal `FOR` loops and `FOR-IN-ENUMERATE` loops support iterating over keys
and values in dictionaries. This syntax requires at least one of the loop
values to be a `dictionary variable`_.
It is possible to use multiple dictionary variables and to give additional
items in `key=value` syntax. Items are iterated in the order they are defined
and if same key gets multiple values the last value will be used.

.. sourcecode:: robotframework

   *** Variables ***
   &{DICT}          a=1    b=2    c=3

   *** Test Cases ***
   Dictionary iteration with FOR loop
       FOR    ${key}    ${value}    IN    &{DICT}
           Log    Key is '${key}' and value is '${value}'.
       END

   Dictionary iteration with FOR-IN-ENUMERATE loop
       FOR    ${index}    ${key}    ${value}    IN ENUMERATE    &{DICT}
           Log    On round ${index} key is '${key}' and value is '${value}'.
       END

   Multiple dictionaries and extra items in 'key=value' syntax
       &{more} =    Create Dictionary    e=5    f=6
       FOR    ${key}    ${value}    IN    &{DICT}    d=4    &{more}    g=7
           Log    Key is '${key}' and value is '${value}'.
       END

Typically it is easiest to use the dictionary iteration syntax so that keys
and values get separate variables like in the above examples. With normal `FOR`
loops it is also possible to use just a single variable that will become
a tuple containing the key and the value. If only one variable is used with
`FOR-IN-ENUMERATE` loops, it becomes a tuple containing the index, the key and
the value. Two variables with `FOR-IN-ENUMERATE` loops means assigning the index
to the first variable and making the second variable a tuple containing the key
and the value.

.. sourcecode:: robotframework

   *** Test Cases ***
   One loop variable
       FOR    ${item}    IN    &{DICT}
           Log    Key is '${item}[0]' and value is '${item}[1]'.
       END

   One loop variable with FOR-IN-ENUMERATE
       FOR    ${item}    IN ENUMERATE    &{DICT}
           Log    On round ${item}[0] key is '${item}[1]' and value is '${item}[2]'.
       END

   Two loop variables with FOR-IN-ENUMERATE
       FOR    ${index}    ${item}    IN ENUMERATE    &{DICT}
           Log    On round ${index} key is '${item}[0]' and value is '${item}[1]'.
       END

In addition to iterating over names and values in dictionaries, it is possible
to iterate over keys and then possibly fetch the value based on it. This syntax
requires using dictionaries as `list variables`_:

.. sourcecode:: robotframework

   *** Test Cases ***
   One loop variable
       FOR    ${key}    IN    @{DICT}
           Log    Key is '${key}' and value is '${DICT}[${key}]'.
       END

.. note:: Iterating over keys and values in dictionaries is a new feature in
          Robot Framework 3.2. With earlier version it is possible to iterate
          over dictionary keys like the last example above demonstrates.

Exiting `FOR` loop
~~~~~~~~~~~~~~~~~~

Normally `FOR` loops are executed until all the loop values have been iterated
or a keyword used inside the loop fails. If there is a need to exit the loop
earlier, BuiltIn_ keywords :name:`Exit For Loop` and :name:`Exit For Loop If`
can be used to accomplish that. They works similarly as `break`
statement in Python, Java, and many other programming languages.

:name:`Exit For Loop` and :name:`Exit For Loop If` keywords can be used
directly inside a `FOR` loop or in a keyword that the loop uses. In both cases
test execution continues after the loop. It is an error to use these keywords
outside a `FOR` loop.

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

Continuing `FOR`` loop
~~~~~~~~~~~~~~~~~~~~~~

In addition to exiting a `FOR` loop prematurely, it is also possible to
continue to the next iteration of the loop before all keywords have been
executed. This can be done using BuiltIn_ keywords :name:`Continue For Loop`
and :name:`Continue For Loop If`, that work like `continue` statement
in many programming languages.

:name:`Continue For Loop` and :name:`Continue For Loop If` keywords can be used
directly inside a `FOR` loop or in a keyword that the loop uses. In both cases
rest of the keywords in that iteration are skipped and execution continues
from the next iteration. If these keywords are used on the last iteration,
execution continues after the loop. It is an error to use these keywords
outside a `FOR` loop.

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

`FOR` loops with multiple iterations often create lots of output and
considerably increase the size of the generated output_ and log_ files.
It is possible to `remove unnecessary keywords`__ from the outputs using
:option:`--RemoveKeywords FOR` command line option.

__ `Removing and flattening keywords`_

Repeating single keyword
~~~~~~~~~~~~~~~~~~~~~~~~

`FOR` loops can be excessive in situations where there is only a need to
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

.. _if:
.. _if/else structures:

`WHILE loops`
-------------

TODO

`IF/ELSE` syntax
----------------

Sometimes there is a need to execute some keywords conditionally. Starting
from Robot Framework 4.0 there is a separate `IF/ELSE` syntax, but
there are also `other ways to execute keywords conditionally`_. Notice that if
the logic gets complicated, it is typically better to move it into a `test library`_.

Basic `IF` syntax
~~~~~~~~~~~~~~~~~

Robot Framework's native `IF` syntax starts with `IF` (case-sensitive) and
ends with `END` (case-sensitive). The `IF` marker requires exactly one value that is
the condition to evaluate. Keywords to execute if the condition is true are on their
own rows between the `IF` and `END` markers. Indenting keywords in the `IF` block is
highly recommended but not mandatory.

In the following example keywords :name:`Some keyword` and :name:`Another keyword`
are executed if `${rc}` is greater than zero:

.. sourcecode:: robotframework

    *** Test Cases ***
    Example
       IF    ${rc} > 0
           Some keyword
           Another keyword
       END

The condition is evaluated in Python so that Python builtins like
`len()` are available and modules are imported automatically to support usages like
`platform.system() == 'Linux'` and `math.ceil(${x}) == 1`.
Normal variables like `${rc}` in the above example are replaced before evaluation, but
variables are also available in the evaluation namespace using the special `$rc` syntax.
The latter approach is handy when the string representation of the variable cannot be
used in the condition directly. For example, strings require quoting and multiline
strings and string themselves containing quotes cause additional problems. For more
information and examples related the evaluation syntax see the `Evaluating expressions`_
appendix.

`ELSE` branches
~~~~~~~~~~~~~~~

Like most other languages supporting conditional execution, Robot Framework `IF`
syntax also supports `ELSE` branches that are executed if the `IF` condition is
not true.

In this example :name:`Some keyword` is executed if `${rc}` is greater than
zero and :name:`Another keyword` is executed otherwise:

.. sourcecode:: robotframework

    *** Test Cases ***
    Example
        IF    ${rc} > 0
            Some keyword
        ELSE
            Another keyword
        END

`ELSE IF` branches
~~~~~~~~~~~~~~~~~~

Robot Framework also supports `ELSE IF` branches that have their own condition
that is evaluated if the initial condition is not true. There can be any number
of `ELSE IF` branches and they are gone through in the order they are specified.
If one of the `ELSE IF` conditions is true, the block following it is executed
and remaining `ELSE IF` branches are ignored. An optional `ELSE` branch can follow
`ELSE IF` branches and it is executed if all conditions are false.

In the following example different keyword is executed depending on is `${rc}` positive,
negative, zero, or something else like a string or `None`:

.. sourcecode:: robotframework

    *** Test Cases ***
    Example
        IF    $rc > 0
            Positive keyword
        ELSE IF    $rc < 0
            Negative keyword
        ELSE IF    $rc == 0
            Zero keyword
        ELSE
            Fail    Unexpected rc: ${rc}
        END

Notice that this example uses the `${rc}` variable in the special `$rc` format to
avoid evaluation failures if it is not a number. See the aforementioned
`Evaluating expressions`_ appendix for more information about this syntax.

.. _inline if:

Inline `IF`
~~~~~~~~~~~

Normal `IF/ELSE` structure is a bit verbose if there is a need to execute only
a single statement. An alternative to it is using inline `IF` syntax where
the statement to execute follows the `IF` marker and condition directly and
no `END` marker is needed. For example, the following two keywords are
equivalent:

.. sourcecode:: robotframework

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

.. sourcecode:: robotframework

    *** Keyword ***
    Inline IF/ELSE
        IF    $condition    Keyword    argument    ELSE    Another Keyword

    Inline IF/ELSE IF/ELSE
        IF    $cond1    Keyword 1    ELSE IF    $cond2    Keyword 2    ELSE IF    $cond3    Keyword 3    ELSE    Keyword 4

As the latter example above demonstrates, inline `IF` with several `ELSE IF`
and `ELSE` branches starts to get hard to understand. Long inline `IF`
structures can be `split into multiple lines`__ using the common `...`
continuation syntax, but using a normal `IF/ELSE` structure or moving the logic
into a `test library`_ is probably a better idea. Each inline `IF` branch can
contain only one statement. If more statements are needed, normal `IF/ELSE`
structure needs to be used instead.

If there is a need for an assignment with inline `IF`, the variable or variables
to assign must be before the starting `IF`. Otherwise the logic is exactly
the same as when `assigning variables`__ based on keyword return values. If
assignment is used and no branch is run, the variable gets value `None`.

.. sourcecode:: robotframework

    *** Keyword ***
    Inline IF/ELSE with assignment
        ${var} =    IF    $condition    Keyword    argument    ELSE    Another Keyword

    Inline IF/ELSE with assignment having multiple variables
        ${host}    ${port} =    IF    $production    Get Production Config    ELSE    Get Testing Config

__ `Dividing data to several rows`_
__ `Return values from keywords`_

.. note:: Inline `IF` syntax is new in Robot Framework 5.0.

Nested `IF` structures
~~~~~~~~~~~~~~~~~~~~~~

`IF` structures can be nested with each others and with `FOR loops`_.
This is illustrated by the following example using advanced features such
as `FOR-IN-ENUMERATE loop`_, `named-only arguments with user keywords`_ and
`inline Python evaluation`_ syntax (`${{len(${items})}}`):

.. sourcecode:: robotframework

    *** Keyword ***
    Log items
        [Arguments]    @{items}    ${log_values}=True
        IF    not ${items}
            Log to console    No items.
        ELSE IF    len(${items}) == 1
            IF    ${log_values}
                Log to console    One item: ${items}[0]
            ELSE
                Log to console    One item.
            END
        ELSE
            Log to console    ${{len(${items})}} items.
            IF    ${log_values}
                FOR    ${index}    ${item}    IN ENUMERATE    @{items}    start=1
                    Log to console    Item ${index}: ${item}
                END
            END
        END

    *** Test Cases ***
    No items
        Log items

    One item without logging value
        Log items    xxx    log_values=False

    Multiple items
        Log items    a    b    c

Other ways to execute keywords conditionally
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

There are also other methods to execute keywords conditionally:

- The name of the keyword used as a setup or a teardown with tests__, suites__ or
  keywords__ can be specified using a variable. This facilitates changing them,
  for example, from the command line.

- The BuiltIn_ keyword :name:`Run Keyword` takes a keyword to actually
  execute as an argument and it can thus be a variable. The value of
  the variable can, for example, be got dynamically from an earlier
  keyword or given from the command line.

- The BuiltIn_ keywords :name:`Run Keyword If` and :name:`Run Keyword Unless`
  execute a named keyword only if a certain expression is true or false, respectively.
  The new `IF/ELSE` syntax explained above is generally recommended, though.

- Another BuiltIn_ keyword, :name:`Set Variable If`, can be used to set
  variables dynamically based on a given expression.

- There are several BuiltIn_ keywords that allow executing a named
  keyword only if a test case or test suite has failed or passed.

__ `Test setup and teardown`_
__ `Suite setup and teardown`_
__ `Keyword teardown`_

`TRY/EXCEPT` syntax
-------------------

When a keyword fails, Robot Framework's default behavior is to stop the current
test and executes its possible teardown_. There can, however, be needs to handle
these failures during execution as well. Robot Framework 5.0 introduces native
`TRY/EXCEPT` syntax for this purpose, but there also `other ways to handle errors`_.

Robot Framework's `TRY/EXCEPT` syntax is inspired by Python's `exception handling`__
syntax. It has same `TRY`, `EXCEPT`, `ELSE` and `FINALLY` branches as Python and
they also mostly work the same way. A difference is that Python uses lower case
`try`, `except`, etc. but with Robot Framework all this kind of syntax must use
upper case letters. A bigger difference is that with Python exceptions are objects
and with Robot Framework you are dealing with error messages as strings.

__ https://docs.python.org/tutorial/errors.html#handling-exceptions

Catching exceptions with `EXCEPT`
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The basic `TRY/EXCEPT` syntax can be used to handle failures based on
error messages:

.. sourcecode:: robotframework

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

.. sourcecode:: robotframework

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

.. sourcecode:: robotframework

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

.. sourcecode:: robotframework

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
          is an `escape character`__ in Robot Framework data. It thus needs to be
          escaped with another backslash when using it in regular expressions.

__ https://en.wikipedia.org/wiki/Glob_(programming)
__ https://en.wikipedia.org/wiki/Regular_expression
__ Escaping_

Capturing error message
~~~~~~~~~~~~~~~~~~~~~~~

When `matching errors using patterns`_ and when using `EXCEPT` without any
messages to match any error, it is often useful to know the actual error that
occurred. Robot Framework supports that by making it possible to capture
the error message into a variable by adding `AS  ${var}` at the
end of the `EXCEPT` statement:

.. sourcecode:: robotframework

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

.. sourcecode:: robotframework

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

.. sourcecode:: robotframework

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
after a keyword execution somewhat similarly as teardowns_. There can be only one
`FINALLY` branch and it must always be last. They can be used in combination with
`EXCEPT` and `ELSE` branches and having also `TRY/FINALLY` structure is possible:

.. sourcecode:: robotframework

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

Other ways to handle errors
~~~~~~~~~~~~~~~~~~~~~~~~~~~

There are also other methods to execute keywords conditionally:

- The BuiltIn_ keyword :name:`Run Keyword And Expect Error` executes a named
  keyword and expects that it fails with a specified error message. It is basically
  the same as using `TRY/EXCEPT` with a specified message. The syntax to specify
  the error message is also identical except that this keyword uses glob pattern
  matching, not exact match, by default. Using the native `TRY/EXCEPT` functionality
  is generally recommended unless there is a need to support older Robot Framework
  versions that do not support it.

- The BuiltIn_ keyword :name:`Run Keyword And Ignore Error` executes a named keyword
  and returns its status as string `PASS` or `FAIL` along with possible return value
  or error message. It is basically the same as using `TRY/EXCEPT/ELSE` so that
  `EXCEPT` catches all errors. Using the native syntax is recommended unless
  old Robot Framework versions need to be supported.

- The BuiltIn_ keyword :name:`Run Keyword And Return Status` executes a named keyword
  and returns its status as a Boolean true or false. It is a wrapper for the
  aforementioned :name:`Run Keyword And Ignore Error`. The native syntax is
  nowadays recommended instead.

- `Test teardowns`_ and `keyword teardowns`_ can be used for cleaning up activities
  similarly as `FINALLY` branches.

- When keywords are implemented in Python based libraries_, all Python's error
  handling features are readily available. This is the recommended approach
  especially if needed logic gets more complicated.

Parallel execution of keywords
------------------------------

When parallel execution is needed, it must be implemented in test library
level so that the library executes the code on background. Typically this
means that the library needs a keyword like :name:`Start Something` that
starts the execution and returns immediately, and another keyword like
:name:`Get Results From Something` that waits until the result is available
and returns it. See Process_ library keywords :name:`Start Process`
and :name:`Wait For Process` for an example.
