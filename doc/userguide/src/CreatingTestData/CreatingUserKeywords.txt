Creating user keywords
----------------------

Keyword tables are used to create new higher-level keywords by
combining existing keywords together. These keywords are called *user
keywords* to differentiate them from lowest level *library keywords*
that are implemented in test libraries. The syntax for creating user
keywords is very close to the syntax for creating test cases, which
makes it easy to learn.

.. contents::
   :depth: 2
   :local:

User keyword syntax
~~~~~~~~~~~~~~~~~~~

Basic syntax
''''''''''''

In many ways, the overall user keyword syntax is identical to the
`test case syntax`_.  User keywords are created in keyword tables
which differ from test case tables only by the name that is used to
identify them. User keyword names are in the first column similarly as
test cases names. Also user keywords are created from keywords, either
from keywords in test libraries or other user keywords. Keyword names
are normally in the second column, but when setting variables from
keyword return values, they are in the subsequent columns.

.. table:: User keyword examples
   :class: example

   =======================  =================  =======================  ===========
           Keyword               Action               Argument           Argument
   =======================  =================  =======================  ===========
   Open Login Page          Open Browser       \http://host/login.html
   \                        Title Should Be    Login Page
   \
   Title Should Start With  [Arguments]        ${expected}
   \                        ${title} =         Get Title
   \                        Should Start With  ${title}                 ${expected}
   =======================  =================  =======================  ===========

Most user keywords take some arguments. This important feature is used
already in the second example above, and it is explained in detail
`later in this section`__, similarly as `user keyword return
values`_.

__ `User keyword arguments`_

User keywords can be created in `test case files`_, `resource files`_,
and `test suite initialization files`_. Keywords created in resource
files are available for files using them, whereas other keywords are
only available in the files where they are created.

Settings in the Keyword table
'''''''''''''''''''''''''''''

User keywords can have similar settings as `test cases`__, and they
have the same square bracket syntax separating them from keyword
names. All available settings are listed below and explained later in
this section.

`[Documentation]`:opt:
   Used for setting a `user keyword documentation`_.

`[Arguments]`:opt:
   Specifies `user keyword arguments`_.

`[Return]`:opt:
   Specifies `user keyword return values`_.

`[Teardown]`:opt:
   Specify `keyword teardown`_. Available from Robot Framework 2.6 onwards.

`[Timeout]`:opt:
   Sets the possible `user keyword timeout`_. Timeouts_ are discussed
   in a section of their own.

__ `Settings in the test case table`_

.. _User keyword documentation:

User keyword name and documentation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The user keyword name is defined in the first column of the user
keyword table. Of course, the name should be descriptive, and it is
acceptable to have quite long keyword names. Actually, when creating
use-case-like test cases, the highest-level keywords are often
formulated as sentences or even paragraphs.

User keywords can have a documentation that is set with the
:opt:`[Documentation]` setting, exactly as `test case
documentation`_. This setting documents the user keyword in the test
data. It is also shown in a more formal keyword documentation, which
the `libdoc`_ tool can create from `resource files`_. Finally, the
first row of the documentation is shown as a keyword documentation in
`test logs`_.

Sometimes keywords need to be removed, replaced with new ones, or
deprecated for other reasons.  User keywords can be marked deprecated
by starting the documentation with :code:`*DEPRECATED*`, which will
cause a warning when the keyoword is used. For more information, see
`Deprecating keywords`_ section.

User keyword arguments
~~~~~~~~~~~~~~~~~~~~~~

Most user keywords need to take some arguments. The syntax for
specifying them is probably the most complicated feature normally
needed with Robot Framework, but even that is relatively easy,
particularly in most common cases. Arguments are normally specified with
the :opt:`[Arguments]` setting, and argument names use the same
syntax as variables_, for example :var:`${arg}`.

Positional arguments
''''''''''''''''''''

The simplest way to specify arguments (apart from not having them at all)
is using only positional arguments. In most cases, this is all
that is needed.

The syntax is such that first the :opt:`[Arguments]` setting is
given and then argument names are defined in the subsequent
cells. Each argument is in its own cell, using the same syntax as with
variables. The keyword must be used with as many arguments as there
are argument names in its signature. The actual argument names do not
matter to the framework, but from users' perspective they should should
be as descriptive as possible. It is recommended
to use lower-case letters in variable names, either as
:var:`${my_arg}`, :var:`${my arg}` or :var:`${myArg}`.

.. table:: User keyword taking different number of arguments
   :class: example

   ===============  ===========  ========================  ==========  ==========
       Keyword        Action             Argument           Argument    Argument
   ===============  ===========  ========================  ==========  ==========
   One Argument     [Arguments]  ${arg_name}
   \                Log          Got argument ${arg_name}
   \
   Three Arguments  [Arguments]  ${arg1}                   ${arg2}     ${arg3}
   \                Log          1st argument: ${arg1}
   \                Log          2nd argument: ${arg2}
   \                Log          3rd argument: ${arg3}
   ===============  ===========  ========================  ==========  ==========

Default values
''''''''''''''

Positional arguments are probably sufficient in most
situations. However, sometimes it is useful to be able to have a
keyword that takes a different number of arguments and has default
values for those that are not given. User keywords also allow this,
and the needed new syntax does not add very much to the already
discussed basic syntax. In short, default values are added to
arguments, so that first there is the equals sign (:code:`=`) and then
the value, for example :var:`${arg}=default`. There can be many
arguments with defaults, but they all must be given after the normal
positional arguments.

.. note:: The syntax for default values is space sensitive. Spaces
          before the :code:`=` sign are not allowed, and possible spaces
          after it are considered part of the default value itself.

.. table:: User keyword with default values for arguments
   :class: example

   =================================  ===============  =====================  ===================
                 Keyword                   Action             Argument              Argument
   =================================  ===============  =====================  ===================
   One Argument With Default Value    [Arguments]      ${arg}=default value
   \                                  [Documentation]  This keyword takes     0-1 arguments
   \                                  Log              Got argument ${arg}
   \
   Two Arguments With Defaults        [Arguments]      ${arg1}=default 1      ${arg2}=default 2
   \                                  [Documentation]  This keyword takes     0-2 arguments
   \                                  Log              1st argument ${arg1}
   \                                  Log              2nd argument ${arg2}
   \
   One Required And One With Default  [Arguments]      ${required}            ${optional}=default
   \                                  [Documentation]  This keyword takes     1-2 arguments
   \                                  Log              Required: ${required}
   \                                  Log              Optional: ${optional}
   =================================  ===============  =====================  ===================

When a keyword accepts several arguments with default values and only
some of them needs to be overridden, it is often handy to use the
`named arguments`_ syntax. When this syntax is used with user
keywords, the arguments are specified without the :var:`${}`
decoration. For example, the second keyword above could be used like
below and :var:`${arg1}` would still get its default value.

.. table:: User keyword and named arguments syntax
   :class: example

   =============  ===========================  ==============  ============
     Test Case               Action               Argument       Argument
   =============  ===========================  ==============  ============
   Example        Two Arguments With Defaults  arg2=new value
   =============  ===========================  ==============  ============

As all Pythonistas must have already noticed, the syntax for
specifying default arguments is heavily inspired by Python syntax for
function default values.

Variable number of arguments
''''''''''''''''''''''''''''

Sometimes even default values are not enough and there is a need
for a keyword accepting any number of arguments. User keywords
support also this. All that is needed is having `list variable`__
such as :var:`@{varargs}` as the last argument in the keyword signature.
This syntax can be combined with the previously described positional
arguments and default values, and at the end the list variable gets all
the leftover arguments that do not match other arguments. The list
variable can thus have any number of items, even zero.

__ `list variables`_

.. table:: User keywords accepting variable number of arguments
   :class: example

   ===========================  ===========  ================  ==========  ==========
              Keyword             Action         Argument       Argument    Argument
   ===========================  ===========  ================  ==========  ==========
   Any Number Of Arguments      [Arguments]  @{varargs}
   \                            Log Many     @{varargs}
   \
   One Or More Arguments        [Arguments]  ${required}       @{rest}
   \                            Log Many     ${required}       @{rest}
   \
   Required, Default, Varargs   [Arguments]  ${req}            ${opt}=42   @{others}
   \                            Log          Required: ${req}
   \                            Log          Optional: ${opt}
   \                            Log          Others:
   \                            : FOR        ${item}           IN          @{others}
   \                                         Log               ${item}
   ===========================  ===========  ================  ==========  ==========

Notice that if the last keyword above is used with more than one
argument, the second argument :var:`${opt}` always gets the given
value instead of the default value. This happens even if the given
value is empty. The last example also illustrates how a variable
number of arguments accepted by a user keyword can be used in a `for
loop`__. This combination of two rather advanced functions can
sometimes be very useful.

Again, Pythonistas probably notice that the variable number of
arguments syntax is very close to the one in Python.

__ `for loops`_

Embedding arguments into keyword name
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Robot Framework has also another approach to pass arguments to user
keywords than specifying them in cells after the keyword name as
explained in the previous section. This method is based on embedding
the arguments directly into the keyword name, and its main benefit is
making it easier to use real and clear sentences as keywords.

Basic syntax
''''''''''''

It has always been possible to use keywords like :name:`Select dog
from list` and :name:`Selects cat from list`, but all such keywords
must have been implemented separately. The idea of embedding arguments
into the keyword name is that all you need is a keyword with name like
:name:`Select ${animal} from list`.

.. table:: An example keyword with arguments embedded into its name
   :class: example

   ===========================  =====================  =============  ============
              Keyword                   Action            Argument      Argument
   ===========================  =====================  =============  ============
   Select ${animal} from list   Open Page              Pet Selection
   \                            Select Item From List  animal_list    ${animal}
   ===========================  =====================  =============  ============

Keywords using embedded arguments cannot take any "normal" arguments
(specified with :opt:`[Arguments]` setting) but otherwise they are
created just like other user keywords. The arguments used in the name
will naturally be available inside the keyword and they have different
value depending on how the keyword is called. For example,
:var:`${animal}` in the previous has value :code:`dog` if the keyword
is used like :name:`Select dog from list`. Obviously it is not
mandatory to use all these arguments inside the keyword, and they can
thus be used as wildcards.

These kind of keywords are also used the same way as other keywords
except that spaces and underscores are not ignored in their
names. They are, however, case-insensitive like other keywords. For
example, the keyword in the example above could be used like
:name:`select x from list`, but not like :name:`Select x fromlist`.

Embedded arguments do not support default values or variable number of
arguments like normal arguments do. Using variables when
calling these keywords is possible but that can reduce readability.
Notice also that embedded arguments only work with user keywords.

Embedded arguments matching too much
''''''''''''''''''''''''''''''''''''

One tricky part in using embedded arguments is making sure that the
values used when calling the keyword match the correct arguments. This
is a problem especially if there are multiple arguments and characters
separating them may also appear in the given values. For example,
keyword :name:`Select ${city} ${team}` does not work correctly if used
with city containing too parts like :name:`Select Los Angeles Lakers`.

An easy solution to this problem is quoting the arguments (e.g.
:name:`Select "${city}" "${team}"`) and using the keyword in quoted
format (e.g. :name:`Select "Los Angeles" "Lakers"`). This approach is
not enough to resolve all this kind of conflicts, though, but it is
still highly recommended because it makes arguments stand out from
rest of the keyword. A more powerful but also more complicated
solution, `using custom regular expressions`_ when defining variables,
is explained in the next section. Finally, if things get complicated,
it might be a better idea to use normal positional arguments instead.

The problem of arguments matching too much occurs often when creating
keywords that `ignore given/when/then/and prefixes`__ . For example,
:name:`${name} goes home` matches :name:`Given Janne goes home` so
that :var:`${name}` gets value :code:`Given Janne`. Quotes around the
argument, like in :name:`"${name}" goes home`, resolve this problem
easily.

__ `Ignoring Given/When/Then/And prefixes`_

Using custom regular expressions
''''''''''''''''''''''''''''''''
When keywords with embedded arguments are called, the values are
matched internally using `regular expressions`__
(regexps for short). The default logic goes so that every argument in
the name is replaced with a pattern :code:`.*?` that basically matches
any string. This logic works fairly well normally, but as just
discussed above, sometimes keywords `match more than
intended`__. Quoting or otherwise separating arguments from the other
text can help but, for example, the test below fails because keyword
:name:`I execute "ls" with "-lh"` matches both of the defined
keywords.

.. table:: Embedded arguments match too much
   :class: example

   ============================  ===============================
             Test Case                         Step
   ============================  ===============================
   Example                       I execute "ls"
   \                             I execute "ls" with "-lh"
   ============================  ===============================

.. table::
   :class: example

   =================================  ==========  ==============  ==========
                Keyword                  Action      Argument      Argument
   =================================  ==========  ==============  ==========
   I execute "${cmd}"                 Run         ${cmd}
   I execute "${cmd}" with "${opts}"  Run         ${cmd} ${opts}
   =================================  ==========  ==============  ==========

A solution to this problem is using a custom regular expression that
makes sure that the keyword matches only what it should in that
particular context. To be able to use this feature, and to fully
understand the examples in this section, you need to understand at
least the basics of the regular expression syntax.

A custom embedded argument regular expression is defined after the
base name of the argument so that the argument and the regexp are
separated with a colon. For example, an argument that should match
only numbers can be defined like :var:`${arg:\\d+}`. Using custom
regular expressions is illustrated by the examples below.

.. table:: Using custom regular expressions with embedded arguments
   :class: example

   ============================  ===============================
             Test Case                         Step
   ============================  ===============================
   Example                       I execute "ls"
   \                             I execute "ls" with "-lh"
   \                             I type 1 + 2
   \                             I type 53 - 11
   \                             Today is 2011-06-27
   ============================  ===============================

.. table::
   :class: example

   ===========================================  ============  ==============  ===========  ==========
                Keyword                            Action        Argument      Argument     Argument
   ===========================================  ============  ==============  ===========  ==========
   I execute "${cmd:[^"]+}"                     Run           ${cmd}
   I execute "${cmd}" with "${opts}"            Run           ${cmd} ${opts}
   I type ${a:\\d+} ${operator:[+-]} ${b:\\d+}  Calculate     ${a}            ${operator}  ${b}
   Today is ${date:\\d{4\\}-\\d{2\\}-\\d{2\\}}  Log           ${date}
   ===========================================  ============  ==============  ===========  ==========

In the above example keyword :name:`I execute "ls" with "-lh"` matches
only :name:`I execute "${cmd}" with "${opts}"`. That is guaranteed
because the custom regular expression :code:`[^"]+` in :name:`I execute
"${cmd:[^"]}"` means that a matching argument cannot contain any
quotes. In this case there is no need to add custom regexps to the
other :name:`I execute` variant.

.. tip:: If you quote arguments, using regular expression :code:`[^"]+`
         guarantees that the argument matches only until the first
         closing quote.

Supported regular expression syntax
```````````````````````````````````

Being implemented with Python, Robot Framework naturally uses Python's
:name:`re` module that has pretty standard `regular expressions
syntax`__. This syntax is otherwise fully supported with embedded
arguments, but regexp extensions in format :code:`(?...)` cannot be
used. Notice also that matching embedded arguments is done
case-insensitively. If the regular expression syntax is invalid,
creating the keyword fails with an error visible in `test execution
errors`__.

Escaping special characters
```````````````````````````

There are some special characters that need to be escaped when used in
the custom embedded arguments regexp. First of all, possible closing
curly braces (:code:`}`) in the pattern need to be escaped with a
single backslash (:code:`\\}`) because otherwise the argument would
end already there. Escaping closing burly braces is illustrated in the
previous example with keyword :name:`Today is
${date:\\d{4\\}-\\d{2\\}-\\d{2\\}}`.

Backslash (:code:`\\`) is a special character in Python regular
expression syntax and thus needs to be escaped if you want to have a
literal backslash character. The safest escape sequence in this case
is four backslashes (:code:`\\\\\\\\`) but, depending on the next
character, also two backslashes may be enough.

Notice also that keyword names and possible embedded arguments in them
should *not* be escaped using the normal `test data escaping
rules`__. This means that, for example, backslashes in expressions
like :var:`${name:\\w+}` should not be escaped.

Using variables with custom embedded argument regular expressions
`````````````````````````````````````````````````````````````````

Whenever custom embedded argument regular expressions are used, Robot
Framework automatically enhances the specified regexps so that they
match variables in addition to the text matching the pattern. This
means that it is always possible to use variables with keywords having
embedded arguments. For example, the following test case would pass
using the keywords from the earlier example.

.. table:: Using variables with custom regular expressions
   :class: example

   =================  =================
        Variable            Value
   =================  =================
   ${DATE}            2011-06-27
   =================  =================

.. table::
   :class: example

   ============================  ===============================
             Test Case                         Step
   ============================  ===============================
   Example                       I type ${1} + ${2}
   \                             Today is ${DATE}
   ============================  ===============================

A drawback of variables automatically matching custom regular
expressions is that it is possible that the value the keyword gets
does not actually match the specified regexp. For example, variable
:var:`${DATE}` in the above example could contain any value and
:name:`Today is ${DATE}` would still match the same keyword.

__ http://en.wikipedia.org/wiki/Regular_expression
__ `Embedded arguments matching too much`_
__ http://docs.python.org/library/re.html
__ `Errors and warnings during execution`_
__ Escaping_

Behavior-driven development example
'''''''''''''''''''''''''''''''''''

The biggest benefit of having arguments as part of the keyword name is that it
makes it easier to use higher-level sentence-like keywords when writing test
cases in `behavior-driven style`_. The example below illustrates this. Notice
also that prefixes :name:`Given`, :name:`When` and :name:`Then` are `left out
of the keyword definitions`__.

.. table:: Embedded arguments used by BDD style tests
   :class: example

   ============================  ===============================
             Test Case                         Step
   ============================  ===============================
   Add two numbers               Given I have Calculator open
   \                             When I add 2 and 40
   \                             Then result should be 42
   \
   Add negative numbers          Given I have Calculator open
   \                             When I add 1 and -2
   \                             Then result should be -1
   ============================  ===============================

.. table::
   :class: example

   ======================================  ===============  ============  ============
                  Keyword                       Action        Argument      Argument
   ======================================  ===============  ============  ============
   I have ${program} open                  Start Program    ${program}
   \
   I add ${number 1} and ${number 2}       Input Number     ${number 1}
   \                                       Push Button      \+
   \                                       Input Number     ${number 2}
   \                                       Push Button      \=
   \
   Result should be ${expected}            ${result} =      Get Result
   \                                       Should Be Equal  ${result}     ${expected}
   ======================================  ===============  ============  ============

.. note:: Embedded arguments feature in Robot Framework is inspired by
          how `step definitions` are created in a popular BDD tool
          called Cucumber__.

__ `Ignoring Given/When/Then/And prefixes`_
__ http://cukes.info

User keyword return values
~~~~~~~~~~~~~~~~~~~~~~~~~~

Similarly as library keywords, also user keywords can return
values. Return values are defined with the :opt:`[Return]`
setting. The values can then be `assigned to variables`__ in test
cases or other user keywords.

__ `Return values from keywords`_

In a typical case, a user keyword returns one value and it can be set
to a scalar variable. This is done by having the return value in the
next cell after the :opt:`[Return]` setting. User keywords can
also return several values, which can then be assigned into several
scalar variables at once, to a list variable, or to scalar variables
and a list variable. Several values can be returned simply by
specifying those values in different cells after the
:opt:`[Return]` setting.

.. table:: User keywords returning values
   :class: example

   ================  ============  ===================  ===================  ===================
       Test Case        Action         Argument              Argument            Argument
   ================  ============  ===================  ===================  ===================
   One Return Value  ${ret} =      Return One Value     argument
   \                 Some Keyword  ${ret}
   \
   Multiple Values   ${a}          ${b}                 ${c} =               Return Three Values
   \                 @{list} =     Return Three Values
   \                 ${scalar}     @{rest} =            Return Three Values
   ================  ============  ===================  ===================  ===================

.. table::
   :class: example

   ===================  ============  ==============  ===========  ==========
         Keyword           Action        Argument       Argument    Argument
   ===================  ============  ==============  ===========  ==========
   Return One Value     [Arguments]   ${arg}
   \                    Do Something  ${arg}
   \                    ${value} =    Get Some Value
   \                    [Return]      ${value}
   \
   Return Three Values  [Return]      foo             bar          zap
   ===================  ============  ==============  ===========  ==========

Keyword teardown
~~~~~~~~~~~~~~~~

Starting from Robot Framework 2.6, also user keywords may have a teardown.
It is defined using :opt:`[Teardown]` setting.

Keyword teardown works much in the same way as a `test case
teardown`__.  Most importantly, the teardown is always a single
keyword, although it can be another user keyword, and it gets executed
also when the user keyword fails. In addition, all steps of the
teardown are executed even if one of them fails. However, a failure in
keyword teardown will fail the test case and subsequent steps in the
test are not run. The name of the keyword to be executed as a teardown
can also be a variable.

.. table::
   :class: example

   ==================  ===============  ===================  ==================
     User Keyword           Action            Argument            Argument
   ==================  ===============  ===================  ==================
   With Teardown       Do Something
   \                   [Teardown]       Log                  keyword teardown
   \
   Using variables     [Documentation]  Teardown given as    variable
   \                   Do Something
   \                   [Teardown]       ${TEARDOWN}
   ==================  ===============  ===================  ==================

__ `test setup and teardown`_
