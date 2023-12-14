Control structures
==================

This section describes various structures that can be used to control the test
execution flow. These structures are familiar from most programming languages
and they allow conditional execution, repeatedly executing a block of keywords
and fine-grained error handling. For readability reasons these structures should
be used judiciously, and more complex use cases should be preferably
implemented in `test libraries`__.

__ `Creating test libraries`_

.. contents::
   :depth: 2
   :local:

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

Prior to Robot Framework 3.1, the `FOR` loop syntax was different than nowadays.
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

Nesting `FOR` loops
~~~~~~~~~~~~~~~~~~~

Starting from Robot Framework 4.0, it is possible to use nested `FOR` loops
simply by adding a loop inside another loop:

.. sourcecode:: robotframework

   *** Keywords ***
   Handle Table
       [Arguments]    @{table}
       FOR    ${row}    IN    @{table}
           FOR    ${cell}    IN    @{row}
               Handle Cell    ${cell}
           END
       END

There can be multiple nesting levels and loops can also be combined with
other control structures:

.. sourcecode:: robotframework

   *** Test Cases ***
   Multiple nesting levels
       FOR    ${root}    IN    r1    r2
           FOR    ${child}    IN    c1   c2    c3
               FOR    ${grandchild}    IN    g1    g2
                   Log Many    ${root}    ${child}    ${grandchild}
               END
           END
           FOR    ${sibling}    IN    s1    s2    s3
               IF    '${sibling}' != 's2'
                   Log Many    ${root}    ${sibling}
               END
           END
       END

Using several loop variables
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

It is possible to iterate over multiple values in one iteration by using
multiple loop variables between the `FOR` and `IN` markers. There can be
any number of loop variables, but the number of values must be evenly
dividable by the number of variables. Each iteration consumes as many
values as there are variables.

If there are lot of values to iterate, it is often convenient to organize
them below the loop variables, as in the first loop of the example below:

.. sourcecode:: robotframework

   *** Test Cases ***
   Multiple loop variables
       FOR    ${index}    ${english}    ${finnish}    IN
       ...    1           cat           kissa
       ...    2           dog           koira
       ...    3           horse         hevonen
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
`FOR` that is followed by a loop variable. In this format
there can be only one loop variable and it contains the current loop
index. After the variable there must be `IN RANGE` marker (case-sensitive)
that is followed by loop limits.

In the simplest case, only the upper limit of the loop is
specified. In this case, loop indices start from zero and increase by one
until, but excluding, the limit. It is also possible to give both the
start and end limits. Then indices start from the start limit, but
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
       [Documentation]    Loops over values from 0 to 9.
       FOR    ${index}    IN RANGE    10
           Log    ${index}
       END

   Start and end
       [Documentation]    Loops over values from 1 to 10.
       FOR    ${index}    IN RANGE    1    11
           Log    ${index}
       END

   Also step given
       [Documentation]    Loops over values 5, 15, and 25.
       FOR    ${index}    IN RANGE    5    26    10
           Log    ${index}
       END

   Negative step
       [Documentation]    Loops over values 13, 3, and -7.
       FOR    ${index}    IN RANGE    13    -13    -10
           Log    ${index}
       END

   Arithmetic
       [Documentation]    Arithmetic with variable.
       FOR    ${index}    IN RANGE    ${var} + 1
           Log    ${index}
       END

   Float parameters
       [Documentation]    Loops over values 3.14, 4.34, and 5.54.
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

`FOR-IN-ENUMERATE` loops syntax is just like the regular `FOR` loop syntax,
except that the separator between variables and values is `IN ENUMERATE`
(case-sensitive). Typically they are used so that there is an additional index
variable before any other loop-variables. By default the index has a value `0`
on the first iteration, `1` on the second, and so on.

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
by using `start=<index>` syntax as the last item of the `FOR ... IN ENUMERATE ...`
header:

.. sourcecode:: robotframework

   *** Variables ***
   @{LIST}         a    b    c
   ${START}        10

   *** Test Cases ***
   FOR-IN-ENUMERATE with start
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
the number of loop-variables (excluding the index variable):

.. sourcecode:: robotframework

   *** Test Cases ***
   FOR-IN-ENUMERATE with two values per iteration
       FOR    ${index}    ${en}    ${fi}    IN ENUMERATE
       ...    cat      kissa
       ...    dog      koira
       ...    horse    hevonen
           Log    "${en}" in English is "${fi}" in Finnish (index: ${index})
       END

If you only use one loop variable with `FOR-IN-ENUMERATE` loops, that variable
will become a Python tuple containing the index and the iterated value:

.. sourcecode:: robotframework

   *** Test Cases ***
   FOR-IN-ENUMERATE with one loop variable
       FOR    ${x}    IN ENUMERATE    @{LIST}
           Length Should Be    ${x}    2
           Log    Index is ${x}[0] and item is ${x}[1].
       END

.. note:: `FOR-IN-ENUMERATE` loops with only one loop variable is a new
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

As the example above illustrates, `FOR-IN-ZIP` loops require their own custom
separator `IN ZIP` (case-sensitive) between loop variables and values.
Values used with `FOR-IN-ZIP` loops must be lists or list-like objects.

Items to iterate over must always be given either as `scalar variables`_ like
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
the number of loop variables. Alternatively, there can be just one loop
variable that then becomes a Python tuple getting items from all lists.

.. sourcecode:: robotframework

   *** Variables ***
   @{ABC}           a    b    c
   @{XYZ}           x    y    z
   @{NUM}           1    2    3

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

Starting from Robot Framework 6.1, it is possible to configure what to do if
lengths of the iterated items differ. By default, the shortest item defines how
many iterations there are and values at the end of longer ones are ignored.
This can be changed by using the `mode` option that has three possible values:

- `STRICT`: Items must have equal lengths. If not, execution fails. This is
  the same as using `strict=True` with Python's zip__ function.
- `SHORTEST`: Items in longer items are ignored. Infinite iterators are supported
  in this mode as long as one of the items is exhausted. This is the default
  behavior.
- `LONGEST`: The longest item defines how many iterations there are. Missing
  values in shorter items are filled-in with value specified using the `fill`
  option or `None` if it is not used. This is the same as using Python's
  zip_longest__ function except that it has `fillvalue` argument instead of
  `fill`.

All these modes are illustrated by the following examples:

.. sourcecode:: robotframework

   *** Variables ***
   @{CHARACTERS}     a    b    c    d    f
   @{NUMBERS}        1    2    3

   *** Test Cases ***
   STRICT mode
       [Documentation]    This loop fails due to lists lengths being different.
       FOR    ${c}    ${n}    IN ZIP    ${CHARACTERS}    ${NUMBERS}    mode=STRICT
           Log    ${c}: ${n}
       END

   SHORTEST mode
       [Documentation]    This loop executes three times.
       FOR    ${c}    ${n}    IN ZIP    ${CHARACTERS}    ${NUMBERS}    mode=SHORTEST
           Log    ${c}: ${n}
       END

   LONGEST mode
       [Documentation]    This loop executes five times.
       ...                On last two rounds `${n}` has value `None`.
       FOR    ${c}    ${n}    IN ZIP    ${CHARACTERS}    ${NUMBERS}    mode=LONGEST
           Log    ${c}: ${n}
       END

   LONGEST mode with custom fill value
       [Documentation]    This loop executes five times.
       ...                On last two rounds `${n}` has value `0`.
       FOR    ${c}    ${n}    IN ZIP    ${CHARACTERS}    ${NUMBERS}    mode=LONGEST    fill=0
           Log    ${c}: ${n}
       END

.. note:: The behavior if list lengths differ will change in the future
          so that the `STRICT` mode will be the default. If that is not desired,
          the `SHORTEST` mode needs to be used explicitly.

__ https://docs.python.org/library/functions.html#zip
__ https://docs.python.org/library/itertools.html#itertools.zip_longest

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
   Iterate over keys
       FOR    ${key}    IN    @{DICT}
           Log    Key is '${key}' and value is '${DICT}[${key}]'.
       END

.. note:: Iterating over keys and values in dictionaries is a new feature in
          Robot Framework 3.2. With earlier version it is possible to iterate
          over dictionary keys like the last example above demonstrates.

Removing unnecessary keywords from outputs
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

`FOR` loops with multiple iterations often create lots of output and
considerably increase the size of the generated output_ and log_ files.
It is possible to `remove or flatten unnecessary keywords`__ using
:option:`--removekeywords` and :option:`--flattenkeywords` command line options.

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

.. _WHILE:

`WHILE loops`
-------------

`WHILE` loops combine features of `FOR loops`_ and `IF/ELSE structures`_.
They specify a condition and repeat the loop body as long as the condition
remains true. This can be utilised, for example, to repeat a nondeterministic sequence
until the desired outcome happens, or in some cases they can be used as an
alternative to `FOR loops`_.

.. note:: `WHILE` loops are new in Robot Framework 5.0.

Basic `WHILE` syntax
~~~~~~~~~~~~~~~~~~~~

.. sourcecode:: robotframework

    *** Test Cases ***
    Example
        VAR    ${rc}   1
        WHILE    ${rc} != 0
            ${rc} =    Keyword that returns zero on success
        END

The `WHILE` loop condition is evaluated in Python so that Python builtins like
`len()` are available and modules are imported automatically to support usages
like `math.pi * math.pow(${radius}, 2) < 10`.
Normal variables like `${rc}` in the above example are replaced before evaluation, but
variables are also available in the evaluation namespace using the special `$rc` syntax.
The latter approach is handy when the string representation of the variable cannot be
used in the condition directly. For example, strings require quoting and multiline
strings and string themselves containing quotes cause additional problems. See the
`Evaluating expressions`_ appendix for more information and examples related to
the evaluation syntax.

Starting from Robot Framework 6.1, the condition in a `WHILE` statement can be omitted.
This is interpreted as the condition always being true, which may be useful with the
`limit` option described below.

Limiting `WHILE` loop iterations
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

With `WHILE` loops, there is always a possibility to achieve an infinite loop,
either by intention or by mistake. This happens when the loop condition never
becomes false. While infinite loops have some utility in application programming,
in automation an infinite loop is rarely a desired outcome. If such a loop occurs
with Robot Framework, the execution must be forcefully stopped and no log or report
can be created. For this reason, `WHILE` loops in Robot Framework have a default
limit of 10 000 iterations. If the limit is exceeded, the loop fails.

The limit can be set with the `limit` configuration parameter either as a maximum
iteration count or as a maximum time for the whole loop. When the limit is an
iteration count, it is possible to use just integers like `100` and to add `times`
or `x` suffix after the value like `100 times`. When the limit is a timeout,
it is possible to use `time strings`__ like `10 s` or `1 hour 10 minutes`.
The limit can also be disabled altogether by using `NONE` (case-insensitive).
All these options are illustrated by the examples below.

.. sourcecode:: robotframework

    *** Test Cases ***
    Limit as iteration count
        WHILE    True    limit=100
            Log    This is run 100 times.
        END
        WHILE    True    limit=10 times
            Log    This is run 10 times.
        END
        WHILE    True    limit=42x
            Log    This is run 42 times.
        END

    Limit as time
        WHILE    True    limit=10 seconds
            Log    This is run 10 seconds.
        END

    No limit
        WHILE    True    limit=NONE
            Log    This runs forever.
        END

.. note:: Support for using `times` and `x` suffixes with iteration counts
          is new in Robot Framework 7.0.

Keywords in a loop are not forcefully stopped if the limit is exceeded. Instead
the loop is exited similarly as if the loop condition would have become false.
A major difference is that the loop status will be `FAIL` in this case.

Starting from Robot Framework 6.1, it is possible to use `on_limit` parameter to
configure the behaviour when the limit is exceeded. It supports two values `pass`
and `fail`, case insensitively. If the value is `pass`, the execution will continue
normally when the limit is reached and the status of the `WHILE` loop will be `PASS`.
The value `fail` works similarly as the default behaviour, e.g. the loop and the
test will fail if the limit is exceeded.

.. sourcecode:: robotframework

    *** Test Cases ***
    Continue when iteration limit is reached
        WHILE    True    limit=5    on_limit=pass
            Log    Loop will be executed five times
        END
        Log    This will be executed normally.

    Continue when time limit is reached
        WHILE    True    limit=10s    on_limit=pass
            Log    Loop will be executed for 10 seconds.
            Sleep   0.5s
        END
        Log    This will be executed normally.


By default, the error message raised when the limit is reached is
`WHILE loop was aborted because it did not finish within the limit of 0.5
seconds. Use the 'limit' argument to increase or remove the limit if
needed.`. Starting from Robot Framework 6.1, the error message can be changed
with the `on_limit_message` configuration parameter.

.. sourcecode:: robotframework

    *** Test Cases ***
    Limit as iteration count
        WHILE    True    limit=0.5s    on_limit_message=Custom While loop error message
            Log    This is run 0.5 seconds.
        END

.. note:: `on_limit_message` configuration parameter is new in Robot Framework 6.1.

__ `Time format`_

Nesting `WHILE` loops
~~~~~~~~~~~~~~~~~~~~~

`WHILE` loops can be nested and also combined with other control structures:

.. sourcecode:: robotframework

    *** Test Cases ***
    Nesting WHILE
        ${x} =   Set Variable    10
        WHILE    ${x} > 0
            ${y} =   Set Variable    ${x}
            WHILE    ${y} > 0
                ${y} =    Evaluate    ${y} - 1
            END
            IF    ${x} > 5
                ${x} =    Evaluate    ${x} - 1
            ELSE
                ${x} =    Evaluate    ${x} - 2
            END
        END

Removing unnecessary keywords from outputs
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

`WHILE` loops with multiple iterations often create lots of output and
considerably increase the size of the generated output_ and log_ files.
It is possible to `remove or flatten unnecessary keywords`__ using
:option:`--removekeywords` and :option:`--flattenkeywords` command line options.

__ `Removing and flattening keywords`_

.. _if:
.. _if/else:
.. _if/else structures:


.. _BREAK:
.. _CONTINUE:

Loop control using `BREAK` and `CONTINUE`
-----------------------------------------

Both FOR_ and WHILE_ loop execution can be controlled with `BREAK` and `CONTINUE`
statements. The former exits the whole loop prematurely and the latter stops
executing the current loop iteration and continues to the next one. In practice
they have the same semantics as `break` and `continue` statements in Python, Java,
and many other programming languages.

Both `BREAK` and `CONTINUE` are typically used conditionally with `IF/ELSE`_
or `TRY/EXCEPT`_ structures, and especially the `inline IF`_ syntax is often
convenient with them. These statements must be used in the loop body,
possibly inside the aforementioned control structures, and using them in
keyword called in the loop body is invalid.

.. sourcecode:: robotframework

   *** Test Cases ***
   BREAK with FOR
       ${text} =    Set Variable    zero
       FOR    ${var}    IN    one    two    three
           IF    '${var}' == 'two'    BREAK
           ${text} =    Set Variable    ${text}-${var}
       END
       Should Be Equal    ${text}    zero-one

   CONTINUE with FOR
       ${text} =    Set Variable    zero
       FOR    ${var}    IN    one    two    three
           IF    '${var}' == 'two'    CONTINUE
           ${text} =    Set Variable    ${text}-${var}
       END
       Should Be Equal    ${text}    zero-one-three

   CONTINUE and BREAK with WHILE
       WHILE    True
           TRY
                ${value} =    Do Something
           EXCEPT
               CONTINUE
           END
           Do something with value    ${value}
           BREAK
       END

   Invalid BREAK usage
       [Documentation]    BREAK and CONTINUE can only be used in the loop body,
       ...                not in keywords used in the loop.
       FOR    ${var}    IN    one    two    three
           Invalid BREAK
       END

   *** Keywords ***
   Invalid BREAK
       [Documentation]    This keyword fails due to invalid syntax.
       BREAK

.. note:: `BREAK` and `CONTINUE` statements are new in Robot Framework 5.0 similarly
          as `WHILE`. Earlier versions supported controlling `FOR` loops using
          BuiltIn_ keywords :name:`Exit For Loop`, :name:`Exit For Loop If`,
          :name:`Continue For Loop` and :name:`Continue For Loop If`. These
          keywords still continue to work, but they will be deprecated and removed
          in the future.

.. note:: Also the RETURN_ statement can be used to a exit loop. It only works
          when loops are used inside a `user keyword`_.

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

    *** Keywords ***
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

    *** Keywords ***
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

    *** Keywords ***
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

    *** Keywords ***
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

- The name of the keyword used as a setup or a teardown with suites__, tests__ and
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

__ `Suite setup and teardown`_
__ `Test setup and teardown`_
__ `User keyword setup and teardown`_

.. _try/except:

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

.. note:: It is not possible to catch exceptions caused by invalid syntax.

Matching errors using patterns
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

By default matching an error using `EXCEPT` requires an exact match. That can be
changed using a configuration option `type=` as an argument to the except clause.
Valid values for the option are `GLOB`, `REGEXP` or `START` (case-insensitive)
to make the match a `glob pattern match`__, a `regular expression match`__, or
to match only the beginning of the error, respectively. Using value
`LITERAL` has the same effect as the default behavior. If an `EXCEPT` has multiple
messages, this option applies to all of them. The value of the option
can be defined with a variable as well.

.. sourcecode:: robotframework

    *** Variables ***
    ${MATCH TYPE}     regexp

    *** Test Cases ***
    Glob pattern
        TRY
            Some Keyword
        EXCEPT    ValueError: *    type=GLOB
            Error Handler 1
        EXCEPT    [Ee]rror ?? occurred    ${pattern}    type=glob
            Error Handler 2
        END

    Regular expression
        TRY
            Some Keyword
        EXCEPT    ValueError: .*    type=${MATCH TYPE}
            Error Handler 1
        EXCEPT    [Ee]rror \\d+ occurred    type=Regexp    # Backslash needs to be escaped.
            Error Handler 2
        END

    Match start
        TRY
            Some Keyword
        EXCEPT    ValueError:    ${beginning}    type=start
            Error Handler
        END

    Explicit exact match
        TRY
            Some Keyword
        EXCEPT    ValueError: invalid literal for int() with base 10: 'ooops'    type=LITERAL
            Error Handler
        EXCEPT    Error 13 occurred    type=LITERAL
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
        EXCEPT    ValueError: *    type=GLOB    AS   ${error}
            Error Handler 1    ${error}
        EXCEPT    [Ee]rror \\d+    (Invalid|Bad) usage    type=REGEXP    AS    ${error}
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

- `Test teardowns`__ and `keyword teardowns`__ can be used for cleaning up activities
  similarly as `FINALLY` branches.

- When keywords are implemented in Python based libraries_, all Python's error
  handling features are readily available. This is the recommended approach
  especially if needed logic gets more complicated.

__ `Test teardown`_
__ `User keyword teardown`_
