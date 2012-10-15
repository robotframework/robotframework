Advanced features
-----------------

.. contents::
   :depth: 2
   :local:

Handling keywords with same names
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Keywords that are used with Robot Framework are either `library
keywords`_ or `user keywords`_. The former come from `standard
libraries`_ or `external libraries`_, and the latter are either
created in the same file where they are used or then imported from
`resource files`_. When many keywords are in use, it is quite common
that some of them have the same name, and this section describes how to
handle possible conflicts in these situations.

Keyword scopes
''''''''''''''

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
'''''''''''''''''''''''''''''''

Scopes alone are not a sufficient solution, because there can be
keywords with the same name in several libraries or resources, and
thus, they provide a mechanism to use only the keyword of the
highest priority. In such cases, it is possible to use *the full name
of the keyword*, where the keyword name is prefixed with the name of
the resource or library and a dot is a delimiter.

With library keywords, the long format means only using the format
:name:`LibraryName.Keyword Name`. For example, the keyword :name:`Run`
from the `OperatingSystem library`_ could be used as
:name:`OperatingSystem.Run`, even if there was another :name:`Run`
keyword somewhere else. If the library is in a module or package, the
full module or package name must be used (for example,
:name:`com.company.Library.Some Keyword`). If a custom name is given
to a library using the `WITH NAME syntax`_, the specified name must be
used also in the full keyword name.

Resource files are specified in the full keyword name, similarly as
library names. The name of the resource is derived from the basename
of the resource file without the file extension. For example, the
keyword :name:`Example` in a resource file :path:`myresources.html` can
be used as :name:`myresources.Example`. Note that this syntax does not
work, if several resource files have the same basename. In such
cases, either the files or the keywords must be renamed. The full name
of the keyword is case-, space- and underscore-insensitive, similarly
as normal keyword names.

Specifying explicit priority between libraries and resources
''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''

If there are multiple conflicts between keywords, specifying all the keywords
in the long format can be quite a lot work. Using the long format also makes it
impossible to create dynamic test cases or user keywords that work differently
depending on which libraries or resources are available. A solution to both of
these problems is specifying the keyword priorities explicitly using the keyword
:name:`Set Library Search Order` from the `BuiltIn library`_.

 .. note:: Although the keyword has the word `library` in its name, it works
           also with resource files starting from Robot Framework 2.6.2.
           As discussed above, keywords in resources always have higher
           priority than keywords in libraries, though.

The :name:`Set Library Search Order` accepts an ordered list or libraries and
resources as arguments. When a keyword name in the test data matches multiple
keywords, the first library or resource containing the keyword is selected and
that keyword implementation used. If the keyword is not found from any of the
specified libraries or resources, execution fails for conflict the same way as
when the search order is not set.

For more information and examples, see the documentation of the keyword.

Timeouts
~~~~~~~~

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
'''''''''''''''''

The test case timeout can be set either by using the :opt:`Test
Timeout` setting in the Setting table or the :opt:`[Timeout]`
setting in the Test Case table. :opt:`Test Timeout` in the Setting
table defines a default test timeout value for all the test cases in
the test suite, whereas :opt:`[Timeout]` in the Test Case table
applies a timeout to an individual test case and overrides the
possible default value.

Using an empty :opt:`[Timeout]` means that the test has no
timeout even when :opt:`Test Timeout` is used. Starting from Robot Framework
2.5.6, it is also possible to use value :misc:`NONE` for this purpose.

Regardless of where the test timeout is defined, the first cell after
the setting name contains the duration of the timeout. The duration
must be given in Robot Framework's `time format`_, that is,
either directly in seconds or in a format like :code:`1 minute
30 seconds`. It must be noted that there is always some overhead by the
framework, and timeouts shorter than one second are thus not
recommended.

The default error message displayed when a test timeout occurs is
:msg:`Test timeout <time> exceeded`. It is also possible to use custom
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

.. table:: Test timeout examples
   :class: example

   ============  =========  =======  =======
     Setting       Value     Value    Value
   ============  =========  =======  =======
   Test Timeout  2 minutes
   ============  =========  =======  =======

.. table::
   :class: example

   ===============  ===============  ========================================  ==========================  ==================
      Test Case         Action                      Argument                           Argument                 Argument
   ===============  ===============  ========================================  ==========================  ==================
   Default Timeout  [Documentation]  Timeout from the Setting table is used
   \                Some Keyword     argument
   \
   Override         [Documentation]  Override default, use 10 seconds timeout
   \                [Timeout]        10
   \                Some Keyword     argument
   \
   Custom Message   [Documentation]  Override default and use custom message
   \                [Timeout]        1min 10s                                  This is my custom error.    It continues here.
   \                Some Keyword     argument
   \
   Variables        [Documentation]  It is possible to use variables too
   \                [Timeout]        ${TIMEOUT}
   \                Some Keyword     argument
   \
   No Timeout       [Documentation]  Empty timeout means no timeout even when  Test Timeout has been used
   \                [Timeout]
   \                Some Keyword     argument
   \
   No Timeout 2     [Documentation]  Empty timeout using NONE, works with      2.5.6
   \                [Timeout]        NONE
   \                Some Keyword     argument
   ===============  ===============  ========================================  ==========================  ==================

User keyword timeout
''''''''''''''''''''

A timeout can be set for a user keyword using the :opt:`[Timeout]`
setting in the Keyword table. The syntax for setting it, including how
timeout values and possible custom messages are given, is
identical to the syntax used with `test case timeouts`_. If no custom
message is provided, the default error message :msg:`Keyword timeout
<time> exceeded` is used if a timeout occurs.

.. table:: User keyword timeout examples
   :class: example

   =================  =================  ==========================  ===========================================
        Keyword             Action                 Argument                           Argument
   =================  =================  ==========================  ===========================================
   Timed Keyword      [Documentation]    Set only the timeout value  and not the custom message.
   \                  [Timeout]          1 minute 42 seconds
   \                  Do Something
   \                  Do Something Else
   \
   Timed-out Wrapper  [Arguments]        @{args}
   \                  [Documentation]    This keyword is a wrapper   that adds a timeout to another keyword.
   \                  [Timeout]          2 minutes                   Original Keyword didn't finish in 2 minutes
   \                  Original Keyword   @{args}
   =================  =================  ==========================  ===========================================

A user keyword timeout is applicable during the execution of that user
keyword. If the total time of the whole keyword is longer than the
timeout value, the currently executed keyword is stopped. User keyword
timeouts are applicable also during a test case teardown, whereas test
timeouts are not.

If both the test case and some of its keywords (or several nested
keywords) have a timeout, the active timeout is the one with the least
time left.

.. warning:: Using timeouts might slow down test execution when using Python 2.5
             elsewhere than on Windows. Prior to Robot Framework 2.7 timeouts
             slowed down execution with all Python versions on all platforms.

For loops
~~~~~~~~~

Repeating same actions several times is quite a common need in test
automation. With Robot Framework, test libraries can have any kind of
loop constructs, and most of the time loops should be implemented in
them. Robot Framework also has its own For loop syntax, which is
useful, for example, when there is a need to repeat keywords from
different libraries.

For loops can be used with both test cases and user keywords. Except for
really simple cases, user keywords are better, because they hide the
complexity introduced by for loops. The basic for loop syntax,
:code:`FOR item IN sequence`, is derived from Python, but similar
syntax is possible also in shell scripts or Perl.

Normal for loop
'''''''''''''''

In a normal For loop, one variable is assigned from a list of values,
one value per iteration. The syntax starts with :name:`:FOR`, where
colon is required to separate the syntax from normal keywords. The
next cell contains the loop variable, the subsequent cell must have
:name:`IN`, and the final cells contain values over which to iterate.

The keywords used in the For loop are on the next rows and they must
be indented one cell to the right. The For loop ends when the indentation
returns back to normal or the table ends. Having nested For loops
directly is not supported, but it is possible to use a user keyword
inside a For loop and have another For loop there.

.. table:: Simple for loops
   :class: example

   ===========  ========  ============  ===========  ==========  ===========
    Test Case    Action     Argument     Argument     Argument    Arguments
   ===========  ========  ============  ===========  ==========  ===========
   Example 1    :FOR      ${animal}     IN           cat         dog
   \                      Log           ${animal}
   \                      Log           2nd keyword
   \            Log       Outside loop
   \
   Example 2    :FOR      ${var}        IN           one         two
   \            ...       three         four         five        six
   \            ...       seven
   \                      Log           ${var}
   ===========  ========  ============  ===========  ==========  ===========


The For loop in :name:`Example 1` above is executed twice, so that first
the loop variable :var:`${animal}` has the value :code:`cat` and then
:code:`dog`. The loop consists of two :name:`Log` keywords. In the
second example, loop values are `split into several rows`__ and the
loop is run altogether seven times.

.. tip:: If you use for loops in the `plain text format`_, remember to
         escape__ the indented cell using a backslash::

              *** Test Case ***
              Example 1
                  :FOR    ${animal}    IN    cat    dog
                  \    Log    ${animal}
                  \    Log    2nd keyword
                  Log    Outside loop

For loops are most useful and also clearest when they are used with
`list variables`_. This is illustrated by the example below, where
:var:`@{ELEMENTS}` contains an arbitrarily long list of element names
and keyword :name:`Start Element` is used with all of them.

.. table:: For loop with a list variable
   :class: example

   ===========  ========  =============  ==========  ===========  ===========
    Test Case    Action     Argument      Argument    Argument     Arguments
   ===========  ========  =============  ==========  ===========  ===========
   Example      :FOR      ${element}     IN          @{ELEMENTS}
   \                      Start Element  ${element}
   ===========  ========  =============  ==========  ===========  ===========

__ `Dividing test data to several rows`_
__ Escaping_

Using several loop variables
''''''''''''''''''''''''''''

It is also possible to use several loop variables. The syntax is the
same as with the normal For loop, but all loop variables are listed in
the cells between :name:`:FOR` and :name:`IN`. There can be any number of loop
variables, but the number of values must be evenly dividable by the number of
variables.

This syntax naturally works both with and without list variables. In
the former case, it is often possible to organize loop values below
loop variables, as in the first part of the example below:

.. table:: Using multiple loop variables
   :class: example

   ===========  ========  ===========  ==========  ==========  ============
    Test Case    Action     Argument    Argument    Argument    Arguments
   ===========  ========  ===========  ==========  ==========  ============
   Example      :FOR      ${index}     ${english}  ${finnish}  IN
   \            ...       1            cat         kissa
   \            ...       2            dog         koira
   \            ...       3            horse       hevonen
   \                      Do X         ${english}
   \                      Y Should Be  ${finnish}  ${index}
   \            :FOR      ${name}      ${id}       IN          @{EMPLOYERS}
   \                      Create       ${name}     ${id}
   ===========  ========  ===========  ==========  ==========  ============

For in range
''''''''''''

Earlier For loops always iterated over a sequence, and this is also the most
common use case. Sometimes it is still convenient to have a For loop
that is executed a certain number of times, and Robot Framework has a
special :code:`FOR index IN RANGE limit` syntax for this purpose. This
syntax is derived from the similar Python idiom.

Similarly as other For loops, the For in range loop starts with
:name:`:FOR` and the loop variable is in the next cell. In this format
there can be only one loop variable and it contains the current loop
index. The next cell must contain :name:`IN RANGE` and the subsequent
cells loop limits.

In the simplest case, only the upper limit of the loop is
specified. In this case, loop indexes start from zero and increase by one
until, but excluding, the limit. It is also possible to give both the
start and end limits. Then indexes start from the start limit, but
increase similarly as in the simple case. Finally, it is possible to give
also the step value that specifies the increment to use. If the step
is negative, it is used as decrement.

Starting from Robot Framework 2.5.5, it is possible to use simple arithmetics
such as addition and subtraction with the range limits. This is especially
useful when the limits are specified with variables.

.. table:: For in range examples
   :class: example

   ================  ===============  ===========  ==========  ========  ========  ========
      Test Case          Action        Argument     Argument     Arg       Arg       Arg
   ================  ===============  ===========  ==========  ========  ========  ========
   Only upper limit  [Documentation]  Loops over   values      from 0    to 9
   \                 :FOR             ${index}     IN RANGE    10
   \                                  Log          ${index}
   \
   Start and end     [Documentation]  Loops over   values      from 1    to 10
   \                 :FOR             ${index}     IN RANGE    1         11
   \                                  Log          ${index}
   \
   Also step given   [Documentation]  Loops over   values      5, 15,    and 25
   \                 :FOR             ${index}     IN RANGE    5         26        10
   \                                  Log          ${index}
   \
   Negative step     [Documentation]  Loops over   values      13, 3,    and -7
   \                 :FOR             ${index}     IN RANGE    13        -13       -10
   \                                  Log          ${index}
   \
   Arithmetics       [Documentation]  Arithmetics  with        variable
   \                 :FOR             ${index}     IN RANGE    ${var}+1
   \                                  Log          ${index}
   ================  ===============  ===========  ==========  ========  ========  ========

Exiting for loop
''''''''''''''''

Normally for loop is executed until all the elements of the loop have been
looped through or an error occurs and the test case or keyword fails. However
sometimes execution of a for loop needs to be stopped before all elements of
the loop have been gone through. `BuiltIn keyword`_ :name:`Exit For Loop` can be
used to exit the enclosing for loop.

:name:`Exit For Loop` keyword can be used directly in a for loop or in a keyword
that the for loop uses. In both cases the test execution continues after the
for loop. If executed outside of a for loop, the test fails.

.. table:: Exit for loop example
   :class: example

   =============  ========  ==============  ==================  ===============
      Test Case    Action    Argument        Argument            Argument
   =============  ========  ==============  ==================  ===============
   Exit Example   :FOR      ${var}          IN                  @{SOME LIST}
   \                        Run Keyword If  '${var}' == 'EXIT'  Exit For Loop
   \                        Do Something    ${var}
   =============  ========  ==============  ==================  ===============

Exiting a for loop can also be initiated from a keyword in a test library by
raising an exception with :code:`ROBOT_EXIT_FOR_LOOP` attribute. Please see
`Stopping test execution`_ for examples how to do this in Python and Java
libraries.

.. note:: Exit for loop functionality is new in Robot Framework 2.5.2.

Removing unnecessary keywords from outputs
''''''''''''''''''''''''''''''''''''''''''

For loops with multiple iterations often create lots of output and
considerably increase the size of the generated output_ and log_ files.
Starting from Robot Framework 2.7, it is possible to `remove unnecessary
keywords`__ from the outputs using :opt:`--RemoveKeywords FOR` command line
option.

__ `Removing keywords from outputs`_

Repeating single keyword
''''''''''''''''''''''''

For loops can be excessive in situations where there is only a need to
repeat a single keyword. In these cases it is often easier to use
`BuiltIn keyword`_ :name:`Repeat Keyword`.  This keyword takes a
keyword and how many times to repeat it as arguments. The times to
repeat the keyword can have an optional postfix `times` or `x` to make
the syntax easier to read.

.. table:: Repeat Keyword examples
   :class: example

   ===========  ==============  ============  ============  ========  ========
    Test Case       Action        Argument      Argument    Argument  Argument
   ===========  ==============  ============  ============  ========  ========
   Example      Repeat Keyword  5             Some Keyword  arg1      arg2
   \            Repeat Keyword  42 times      My Keyword
   \            Repeat Keyword  ${var}        Another KW    argument
   ===========  ==============  ============  ============  ========  ========

Robot Framework also had a special syntax for repeating a single
keyword. This syntax was deprecated in the 2.0.4 version in favor of
:name:`Repeat Keyword` and it was removed in the 2.5 version.

Conditional execution
~~~~~~~~~~~~~~~~~~~~~

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

- The `BuiltIn keyword`_ :name:`Run Keyword` takes a keyword to actually
  execute as an argument, and it can thus be a variable. The value of
  the variable can, for example, be got dynamically from an earlier
  keyword or given from the command line.

- The `BuiltIn keywords`_ :name:`Run Keyword If` and :name:`Run Keyword
  Unless` execute a named keyword only if a certain expression is
  true or false, respectively. They are ideally suited to creating
  simple if/else constructs. For an example, see the documentation of
  the former.

- Another `BuiltIn keyword`_, :name:`Set Variable If`, can be used to set
  variables dynamically based on a given expression.

- There are several `BuiltIn keywords`_ that allow executing a named
  keyword only if a test case or test suite has failed or passed.

__ `Test setup and teardown`_
__ `Suite setup and teardown`_


Parallel execution of keywords
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Prior to the 2.5 version Robot Framework a had special syntax for executing
keywords in parallel. This functionality was removed because it was rarely
used and it never worked fully.

When parallel execution is needed, it must be implemented in test library
level so that the library executes the code on background. Typically this
means that the library needs a keyword like :name:`Start Something` that
starts the execution and returns immediately, and another keyword like
:name:`Get Results From Something` that waits until the result is available
and returns it. See `OperatingSystem library`_ keywords :name:`Start Process`
and :name:`Read Process Output` for an example.
