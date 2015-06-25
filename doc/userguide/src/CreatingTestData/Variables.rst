Variables
=========

.. contents::
   :depth: 2
   :local:

Introduction
------------

Variables are an integral feature of Robot Framework, and they can be
used in most places in test data. Most commonly, they are used in
arguments for keywords in test case tables and keyword tables, but
also all settings allow variables in their values. A normal keyword
name *cannot* be specified with a variable, but the BuiltIn_ keyword
:name:`Run Keyword` can be used to get the same effect.

Robot Framework has its own variables that can be used as scalars__, lists__
or `dictionaries`__ using syntax `${SCALAR}`, `@{LIST}` and `&{DICT}`,
respectively. In addition to this, `environment variables`_ can be used
directly with syntax `%{ENV_VAR}`.

Variables are useful, for example, in these cases:

- When strings change often in the test data. With variables you only
  need to make these changes in one place.

- When creating system-independent and operating-system-independent test
  data. Using variables instead of hard-coded strings eases that considerably
  (for example, `${RESOURCES}` instead of `c:\resources`, or `${HOST}`
  instead of `10.0.0.1:8080`). Because variables can be `set from the
  command line`__ when tests are started, changing system-specific
  variables is easy (for example, `--variable HOST:10.0.0.2:1234
  --variable RESOURCES:/opt/resources`). This also facilitates
  localization testing, which often involves running the same tests
  with different strings.

- When there is a need to have objects other than strings as arguments
  for keywords. This is not possible without variables.

- When different keywords, even in different test libraries, need to
  communicate. You can assign a return value from one keyword to a
  variable and pass it as an argument to another.

- When values in the test data are long or otherwise complicated. For
  example, `${URL}` is shorter than
  `http://long.domain.name:8080/path/to/service?foo=1&bar=2&zap=42`.

If a non-existent variable is used in the test data, the keyword using
it fails. If the same syntax that is used for variables is needed as a
literal string, it must be `escaped with a backslash`__ as in `\${NAME}`.

__ `Scalar variables`_
__ `List variables`_
__ `Dictionary variables`_
__ `Setting variables in command line`_
__ Escaping_

Variable types
--------------

Different variable types are explained in this section. How variables
can be created is discussed in subsequent sections.

Robot Framework variables, similarly as keywords, are
case-insensitive, and also spaces and underscores are
ignored. However, it is recommended to use capital letters with
global variables (for example, `${PATH}` or `${TWO WORDS}`)
and small letters with variables that are only available in certain
test cases or user keywords (for example, `${my var}` or
`${myVar}`). Much more importantly, though, cases should be used
consistently.

Variable name consists of the variable type identifier (`$`, `@`, `&`, `%`),
curly braces (`{`, `}`) and actual variable name between the braces.
Unlike in some programming languages where similar variable syntax is
used, curly braces are always mandatory. Variable names can basically have
any characters between the curly braces. However, using only alphabetic
characters from a to z, numbers, underscore and space is recommended, and
it is even a requirement for using the `extended variable syntax`_.

.. _scalar variable:

Scalar variables
~~~~~~~~~~~~~~~~

When scalar variables are used in the test data, they are replaced
with the value they are assigned to. While scalar variables are most
commonly used for simple strings, you can assign any objects,
including lists, to them. The scalar variable syntax, for example
`${NAME}`, should be familiar to most users, as it is also used,
for example, in shell scripts and Perl programming language.

The example below illustrates the usage of scalar variables. Assuming
that the variables `${GREET}` and `${NAME}` are available
and assigned to strings `Hello` and `world`, respectively,
both the example test cases are equivalent.

.. table:: Scalar variables with string values
   :class: example

   ============  ========  ====================  ==========
    Test Case     Action        Argument          Argument
   ============  ========  ====================  ==========
   Constants     Log       Hello
   \             Log       Hello, world!!
   Variables     Log       ${GREET}
   \             Log       ${GREET}, ${NAME}!!
   ============  ========  ====================  ==========

When a scalar variable is used as the only value in a test data cell,
the scalar variable is replaced with the value it has. The value may
be any object. When a scalar variable is used in a test data cell with
anything else (constant strings or other variables), its value is
first converted into a Unicode string and then catenated to whatever is in
that cell. Converting the value into a string means that the object's
method `__unicode__` (in Python, with `__str__` as a fallback)
or `toString` (in Java) is called.

.. note:: Variable values are used as-is without conversions also when
          passing arguments to keywords using the `named arguments`_
          syntax like `argname=${var}`.

The example below demonstrates the difference between having a
variable in a cell alone or with other content. First, let us assume
that we have a variable `${STR}` set to a string `Hello,
world!` and `${OBJ}` set to an instance of the following Java
object:

.. sourcecode:: java

 public class MyObj {

     public String toString() {
         return "Hi, tellus!";
     }
 }

With these two variables set, we then have the following test data:

.. table:: Scalar variables with objects as values
   :class: example

   ===========  ========  =================  ==========
    Test Case    Action        Argument       Argument
   ===========  ========  =================  ==========
   Objects      KW 1      ${STR}
   \            KW 2      ${OBJ}
   \            KW 3      I said "${STR}"
   \            KW 4      You said "${OBJ}"
   ===========  ========  =================  ==========

Finally, when this test data is executed, different keywords receive
the arguments as explained below:

- :name:`KW 1` gets a string `Hello, world!`
- :name:`KW 2` gets an object stored to variable `${OBJ}`
- :name:`KW 3` gets a string `I said "Hello, world!"`
- :name:`KW 4` gets a string `You said "Hi, tellus!"`

.. Note:: Converting variables to Unicode obviously fails if the variable
          cannot be represented as Unicode. This can happen, for example,
          if you try to use byte sequences as arguments to keywords so that
          you catenate the values together like `${byte1}${byte2}`.
          A workaround is creating a variable that contains the whole value
          and using it alone in the cell (e.g. `${bytes}`) because then
          the value is used as-is.

.. _list variable:

List variables
~~~~~~~~~~~~~~

When a variable is used as a scalar like `${EXAMPLE}`, its value will be
used as-is. If a variable value is a list or list-like, it is also possible
to use as a list variable like `@{EXAMPLE}`. In this case individual list
items are passed in as arguments separately. This is easiest to explain with
an example. Assuming that a variable `@{USER}` has value `['robot','secret']`,
the following two test cases are equivalent:

.. table:: Using list variables
   :class: example

   =============  ========  ===========  ==========
     Test Case     Action    User Name    Password
   =============  ========  ===========  ==========
   Constants      Login     robot        secret
   List Variable  Login     @{USER}
   =============  ========  ===========  ==========

Robot Framework stores its own variables in one internal storage and allows
using them as scalars, lists or dictionaries. Using a variable as a list
requires its value to be a Python list or list-like object. Robot Framework
does not allow strings to be used as lists, but other iterable objects such
as tuples or dictionaries are accepted.

Prior to Robot Framework 2.9, scalar and list variables were stored separately,
but it was possible to use list variables as scalars and scalar variables as
lists. This caused lot of confusion when there accidentally was a scalar
variable and a list variable with same name but different value.

Using list variables with other data
''''''''''''''''''''''''''''''''''''

It is possible to use list variables with other arguments, including
other list variables.

.. table:: Using list variables with other data
   :class: example

   =============  ==========  ==========  ==========  ===========
     Test Case      Action     Argument    Argument    Argument
   =============  ==========  ==========  ==========  ===========
   Example        Keyword     @{LIST}     more        args
   \              Keyword     ${SCALAR}   @{LIST}     constant
   \              Keyword     @{LIST}     @{ANOTHER}  @{ONE MORE}
   =============  ==========  ==========  ==========  ===========

If a list variable is used in a cell with other data (constant strings or other
variables), the final value will contain a string representation of the
variable value. The end result is thus exactly the same as when using the
variable as a scalar with other data in the same cell.

Accessing individual list items
'''''''''''''''''''''''''''''''

It is possible to access a certain value of a list variable
with the syntax `@{NAME}[index]`, where `index` is the index of the
selected value. Indexes start from zero, and trying to access a value
with too large an index causes an error. Indices are automatically converted
to integers, and it is also possible to use variables as indices.
List items accessed in this manner can be used similarly as scalar variables.

.. table:: Accessing list variable items
   :class: example

   ===============  ===============  ===================  ==========
      Test Case         Action            Argument         Argument
   ===============  ===============  ===================  ==========
   Constants        Login            robot                secret
   \                Title Should Be  Welcome robot!
   List Variable    Login            @{USER}
   \                Title Should Be  Welcome @{USER}[0]!
   Variable Index   Log              @{LIST}[${INDEX}]
   ===============  ===============  ===================  ==========

Using list variables with settings
''''''''''''''''''''''''''''''''''

List variables can be used only with some of the settings__. They can
be used in arguments to imported libraries and variable files, but
library and variable file names themselves cannot be list
variables. Also with setups and teardowns list variable can not be used
as the name of the keyword, but can be used in arguments. With tag related
settings they can be used freely. Using scalar variables is possible in
those places where list variables are not supported.

.. table:: Using list variables with settings
   :class: example

   ==============  ================  ===============  ====================
      Settings          Value            Value             Comment
   ==============  ================  ===============  ====================
   Library         ExampleLibrary    @{LIB ARGS}      # This works
   Library         ${LIBRARY}        @{LIB ARGS}      # This works
   Library         @{NAME AND ARGS}                   # This does not work
   Suite Setup     Some Keyword      @{KW ARGS}       # This works
   Suite Setup     ${KEYWORD}        @{KW ARGS}       # This works
   Suite Setup     @{KEYWORD}                         # This does not work
   Default Tags    @{TAGS}                            # This works
   ==============  ================  ===============  ====================

__ `All available settings in test data`_

.. _dictionary variable:

Dictionary variables
~~~~~~~~~~~~~~~~~~~~

As discussed above, a variable containing a list can be used as a `list
variable`_ to pass list items to a keyword as individual arguments.
Similarly a variable containing a Python dictionary or a dictionary-like
object can be used as a dictionary variable like `&{EXAMPLE}`. In practice
this means that individual items of the dictionary are passed as
`named arguments`_ to the keyword. Assuming that a variable `&{USER}` has
value `{'name': 'robot', 'password': 'secret'}`, the following two test cases
are equivalent.

.. table:: Using dictionary variables
   :class: example

   =============  ========  ===========  ===============
     Test Case     Action    User Name      Password
   =============  ========  ===========  ===============
   Strings        Login     name=robot   password=secret
   List Variable  Login     &{USER}
   =============  ========  ===========  ===============

Dictionary variables are new in Robot Framework 2.9.

Using dictionary variables with other data
''''''''''''''''''''''''''''''''''''''''''

It is possible to use dictionary variables with other arguments, including
other dictionary variables. Because `named argument syntax`_ requires positional
arguments to be before named argument, dictionaries can only be followed by
named arguments or other dictionaries.

.. table:: Using dictionary variables with other data
   :class: example

   =============  ==========  ==========  ==========  ===========
     Test Case      Action     Argument    Argument    Argument
   =============  ==========  ==========  ==========  ===========
   Example        Keyword     &{DICT}     named=arg
   \              Keyword     positional  @{LIST}     &{DICT}
   \              Keyword     &{DICT}     &{ANOTHER}  &{ONE MORE}
   =============  ==========  ==========  ==========  ===========

If a dictionary variable is used in a cell with other data (constant strings or
other variables), the final value will contain a string representation of the
variable value. The end result is thus exactly the same as when using the
variable as a scalar with other data in the same cell.

Accessing individual dictionary items
'''''''''''''''''''''''''''''''''''''

It is possible to access a certain value of a dictionary variable
with the syntax `&{NAME}[key]`, where `key` is the name of the
selected value. Keys are considered to be strings, but non-strings
keys can be used as variables. Dictionary items accessed in this
manner can be used similarly as scalar variables:

.. table:: Accessing dictionary variable items
   :class: example

   ===============  ===============  ======================  ===============
      Test Case         Action              Argument             Argument
   ===============  ===============  ======================  ===============
   Constants        Login            name=robot              password=secret
   \                Title Should Be  Welcome robot!
   Dict Variable    Login            &{USER}
   \                Title Should Be  Welcome &{USER}[name]!
   Variable Key     Log Many         &{DICT}[${KEY}]         &{DICT}[${42}]
   ===============  ===============  ======================  ===============

Using dictionary variables with settings
''''''''''''''''''''''''''''''''''''''''

Dictionary variables cannot generally be used with settings. The only exception
are imports, setups and teardowns where dictionaries can be used as arguments.

.. table:: Using list variables with settings
   :class: example

   ==============  ================  =============  =============
      Settings          Value            Value          Value
   ==============  ================  =============  =============
   Library         ExampleLibrary    &{LIB ARGS}
   Suite Setup     Some Keyword      &{KW ARGS}     named=arg
   ==============  ================  =============  =============

.. _environment variable:

Environment variables
~~~~~~~~~~~~~~~~~~~~~

Robot Framework allows using environment variables in the test
data using the syntax `%{ENV_VAR_NAME}`. They are limited to string
values.

Environment variables set in the operating system before the test execution are
available during it, and it is possible to create new ones with the keyword
:name:`Set Environment Variable` or delete existing ones with the
keyword :name:`Delete Environment Variable`, both available in the
OperatingSystem_ library. Because environment variables are global,
environment variables set in one test case can be used in other test
cases executed after it. However, changes to environment variables are
not effective after the test execution.

.. table:: Using environment variables
   :class: example

   =============  ========  =====================  ==========
     Test Case     Action          Argument         Argument
   =============  ========  =====================  ==========
   Env Variables  Log       Current user: %{USER}
   \              Run       %{JAVA_HOME}${/}javac
   =============  ========  =====================  ==========

Java system properties
~~~~~~~~~~~~~~~~~~~~~~

When running tests with Jython, it is possible to access `Java system properties`__
using same syntax as `environment variables`_. If an environment variable and a
system property with same name exist, the environment variable will be used.

.. table:: Using Java system properties
   :class: example

   =================  ========  ========================================  ==========
     Test Case         Action          Argument                            Argument
   =================  ========  ========================================  ==========
   System Properties   Log      %{user.name} running tests on %{os.name}
   =================  ========  ========================================  ==========

__ http://docs.oracle.com/javase/tutorial/essential/environment/sysprop.html

Creating variables
------------------

Variables can spring into existence from different sources.

Variable table
~~~~~~~~~~~~~~

The most common source for variables are Variable tables in `test case
files`_ and `resource files`_. Variable tables are convenient, because they
allow creating variables in the same place as the rest of the test
data, and the needed syntax is very simple. Their main disadvantages are
that values are always strings and they cannot be created dynamically.
If either of these is a problem, `variable files`_ can be used instead.

Creating scalar variables
'''''''''''''''''''''''''

The simplest possible variable assignment is setting a string into a
scalar variable. This is done by giving the variable name (including
`${}`) in the first column of the Variable table and the value in
the second one. If the second column is empty, an empty string is set
as a value. Also an already defined variable can be used in the value.

.. table:: Creating scalar variables
   :class: example

   ============  ==================  =========
     Variable           Value          Value
   ============  ==================  =========
   ${NAME}       Robot Framework
   ${VERSION}    2.0
   ${ROBOT}      ${NAME} ${VERSION}
   ============  ==================  =========

It is also possible, but not obligatory,
to use the equals sign `=` after the variable name to make assigning
variables slightly more explicit.

.. table:: Creating scalar variables using the equals sign
   :class: example

   ============  ===============  =========
     Variable         Value         Value
   ============  ===============  =========
   ${NAME} =     Robot Framework
   ${VERSION} =  2.0
   ============  ===============  =========

If a scalar variable has a long value, it can be split to multiple columns and
rows__. By default cells are catenated together using a space, but this
can be changed by having `SEPARATOR=<sep>` in the first cell.

.. table:: Creating long scalar variables
   :class: example

   ============  ====================  =====================
     Variable           Value                  Value
   ============  ====================  =====================
   ${EXAMPLE}    This value is joined  together with a space
   ${MULTILINE}  SEPARATOR=\\n         First line
   ...           Second line           Third line
   ============  ====================  =====================

Joining long values like above is a new feature in Robot Framework 2.9.
Creating a scalar variable with multiple values was a syntax error in
Robot Framework 2.8 and with earlier versions it created a variable with
a list value.

__ `Dividing test data to several rows`_

Creating list variables
'''''''''''''''''''''''

Creating list variables is as easy as creating scalar variables. Again, the
variable name is in the first column of the Variable table and
values in the subsequent columns. A list variable can have any number
of values, starting from zero, and if many values are needed, they
can be `split into several rows`__.

__ `Dividing test data to several rows`_

.. table:: Creating list variables
   :class: example

   ============  =========  =========  =========
     Variable      Value      Value      Value
   ============  =========  =========  =========
   @{NAMES}      Matti      Teppo
   @{NAMES2}     @{NAMES}   Seppo
   @{NOTHING}
   @{MANY}       one        two        three
   ...           four       five       six
   ...           seven
   ============  =========  =========  =========

Creating dictionary variables
'''''''''''''''''''''''''''''

Dictionary variables can be created in the variable table similarly as
list variables. The difference is that items need to be created using
`name=value` syntax or existing dictionary variables. If there are multiple
items with same name, the last value has precedence. If a name contains
an equal sign, it can be escaped__ with a backslash like `\=`.

.. table:: Creating dictionary variables
   :class: example

   ===============  ===============  ================  ===============
       Variable          Value             Value            Value
   ===============  ===============  ================  ===============
   &{USER 1}        name=Matti       address=xxx       phone=123
   &{USER 2}        name=Teppo       address=yyy       phone=456
   &{MANY}          first=1          second=${2}       ${3}=third
   &{EVEN MORE}     &{MANY}          first=override    empty=
   ...              =empty           key\\=here=value
   ===============  ===============  ================  ===============

Dictionary variables created in variable table have two extra properties
compared to normal Python dictionaries. First of all, values of these
dictionaries can be accessed like attributes, which means that it is possible
to use `extended variable syntax`_ like `${VAR.key}`. This only works if the
key is a valid attribute name and does not match any normal attribute
Python dictionaries have. For example, individual value `&{USER}[name]` can
also be accessed like `${USER.name}` (notice that `$` is needed in this
context), but `&{MANY}[${3}]` does not work as `${MANY.3}`.

Another special property of dictionaries created in the variable table is
that they are ordered. This means that if these dictionaries are iterated,
their items always come in the order they are defined. This can be useful
if dictionaries are used as `list variables`_ with `for loops`_ or otherwise.
When a dictionary is used as a list variable, the actual value contains
dictionary keys. For example, `@{MANY}` variable would have value `['first',
'second', 3]`.

__ Escaping_

Variable file
~~~~~~~~~~~~~

Variable files are the most powerful mechanism for creating different
kind of variables. It is possible to assign variables to any object
using them, and they also enable creating variables dynamically. The
variable file syntax and taking variable files into use is explained
in section `Resource and variable files`_.

Setting variables in command line
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Variables can be set from the command line either individually with
the :option:`--variable (-v)` option or using a variable file with the
:option:`--variablefile (-V)` option. Variables set from the command line
are globally available for all executed test data files, and they also
override possible variables with the same names in the Variable table and in
variable files imported in the test data.

The syntax for setting individual variables is :option:`--variable
name:value`, where `name` is the name of the variable without
`${}` and `value` is its value. Several variables can be
set by using this option several times. Only scalar variables can be
set using this syntax and they can only get string values. Many
special characters are difficult to represent in the
command line, but they can be escaped__ with the :option:`--escape`
option.

__ `Escaping complicated characters`_

.. sourcecode:: bash

   --variable EXAMPLE:value
   --variable HOST:localhost:7272 --variable USER:robot
   --variable ESCAPED:Qquotes_and_spacesQ --escape quot:Q --escape space:_

In the examples above, variables are set so that

- `${EXAMPLE}` gets the value `value`
- `${HOST}` and `${USER}` get the values
  `localhost:7272` and `robot`
- `${ESCAPED}` gets the value `"quotes and spaces"`

The basic syntax for taking `variable files`_ into use from the command line
is :option:`--variablefile path/to/variables.py`, and `Taking variable files into
use`_ section has more details. What variables actually are created depends on
what variables there are in the referenced variable file.

If both variable files and individual variables are given from the command line,
the latter have `higher priority`__.

__ `Variable priorities and scopes`_

Return values from keywords
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Return values from keywords can also be set into variables. This
allows communication between different keywords even in different test
libraries.

Variables set in this manner are otherwise similar to any other
variables, but they are available only in the `local scope`_
where they are created. Thus it is not possible, for example, to set
a variable like this in one test case and use it in another. This is
because, in general, automated test cases should not depend on each
other, and accidentally setting a variable that is used elsewhere
could cause hard-to-debug errors. If there is a genuine need for
setting a variable in one test case and using it in another, it is
possible to use BuiltIn_ keywords as explained in the next section.

Assigning scalar variables
''''''''''''''''''''''''''

Any value returned by a keyword can be assigned to a `scalar variable`_.
As illustrated by the example below, the required syntax is very simple.

.. table:: Assigning return value to scalar variable
   :class: example

   ============  ===============  ============  ============
     Test Case        Action        Argument      Argument
   ============  ===============  ============  ============
   Returning     ${x} =           Get X         an argument
   \             Log              We got ${x}!
   ============  ===============  ============  ============

In the above example the value returned by the :name:`Get X` keyword
is first set into the variable `${x}` and then used by the :name:`Log`
keyword. Having the equals sign `=` after the variable name is
not obligatory, but it makes the assignment more explicit. Creating
local variables like this works both in test case and user keyword level.

Notice that although a value is assigned to a scalar variable, it can
be used as a `list variable`_ if it has a list-like value and as a `dictionary
variable`_ if it has a dictionary-like value.

.. table:: Assigning list to scalar variable
   :class: example

   ============  ================  ============  ==========  ==========  ==========
     Test Case        Action         Argument     Argument    Argument    Argument
   ============  ================  ============  ==========  ==========  ==========
   Example       ${list} =         Create List   first       second      third
   \             Length Should Be  ${list}       3
   \             Log Many          @{list}
   ============  ================  ============  ==========  ==========  ==========

Assigning list variables
''''''''''''''''''''''''

If a keyword returns a list or any list-like object, it is possible to
assign it to a `list variable`_.

.. table:: Assigning list variable
   :class: example

   ============  ================  ============  ==========  ==========  ==========
     Test Case        Action         Argument     Argument    Argument    Argument
   ============  ================  ============  ==========  ==========  ==========
   Example       @{list} =         Create List   first       second      third
   \             Length Should Be  ${list}       3
   \             Log Many          @{list}
   ============  ================  ============  ==========  ==========  ==========

Because all Robot Framework variables are stored in same namespace, there is
not much difference between assigning a value to a scalar variable or list
variable. This can be seen by comparing the above example with the example at
the end of the previous section. Actually the only difference is that when
creating a list variable, Robot Framework automatically verifies that the value
is a list or list-like.

Assigning dictionary variables
''''''''''''''''''''''''''''''

If a keyword returns a dictionary or any dictionary-like object, it is possible
to assign it to a `dictionary variable`_.

.. table:: Assigning dictionary variable
   :class: example

   ============  ================  =================  ==========  ===========  ==========
     Test Case        Action            Argument       Argument    Argument     Argument
   ============  ================  =================  ==========  ===========  ==========
   Example       &{dict} =         Create Dictionary  first=1     second=${2}  ${3}=third
   \             Length Should Be  ${dict}            3
   \             Do Something      &{dict}
   \             Log               ${dict.first}
   ============  ================  =================  ==========  ===========  ==========

Because all Robot Framework variables are stored in same namespace, it would
also be possible to assign a dictionary into a scalar variable and use it
later as a dictionary when needed. There are, however, some actual benefits
in creating a dictionary variable explicitly. First of all, Robot Framework
verifies that the returned value is a dictionary or dictionary-like similarly
as it verifies that list variables can only get a list-like value.
Another benefit is that Robot Framework converts the value into a special
dictionary it uses also when `creating dictionary variables`_ in the variable
table. These dictionaries are sortable and their values can be accessed using
attribute access like `${dict.first}` in the above example.

Assigning multiple variables
''''''''''''''''''''''''''''

If a keyword returns a list or a list-like object, it is possible to assign
individual values into multiple scalar variables or into scalar variables and
a list variable.

.. table:: Assigning multiple values at once
   :class: example

   ===============  ============  ==========  ==========  ==========
      Test Case        Action      Argument    Argument    Argument
   ===============  ============  ==========  ==========  ==========
   Assign Multiple  ${a}          ${b}        ${c} =      Get Three
   \                ${first}      @{rest} =   Get Three
   \                @{before}     ${last} =   Get Three
   \                ${begin}      @{middle}   ${end} =    Get Three
   ===============  ============  ==========  ==========  ==========

Assuming that the keyword :name:`Get Three` returns a list `[1, 2, 3]`,
the following variables are created:

- `${a}`, `${b}` and `${c}` with values `1`, `2`, and `3`, respectively.
- `${first}` with value `1`, and `@{rest}` with value `[2, 3]`.
- `@{before}` with value `[1, 2]` and `${last}` with value `3`.
- `${begin}` with value `1`, `@{middle}` with value `[2]` and ${end} with
  value `3`.

It is an error if the returned list has more or less values than there are
scalar variables to assign. Additionally, only one list variable is allowed
and dictionary variables can only be assigned alone.

The support for assigning multiple variables was slightly changed in
Robot Framework 2.9. Prior to it a list variable was only allowed as
the last assigned variable, but nowadays it can be used anywhere.
Additionally, it was possible to return more values than scalar variables.
In that case the last scalar variable was magically turned into a list
containing the extra values.

Using :name:`Set Test/Suite/Global Variable` keywords
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The BuiltIn_ library has keywords :name:`Set Test Variable`,
:name:`Set Suite Variable` and :name:`Set Global Variable` which can
be used for setting variables dynamically during the test
execution. If a variable already exists within the new scope, its
value will be overwritten, and otherwise a new variable is created.

Variables set with :name:`Set Test Variable` keyword are available
everywhere within the scope of the currently executed test case. For
example, if you set a variable in a user keyword, it is available both
in the test case level and also in all other user keywords used in the
current test. Other test cases will not see variables set with this
keyword.

Variables set with :name:`Set Suite Variable` keyword are available
everywhere within the scope of the currently executed test
suite. Setting variables with this keyword thus has the same effect as
creating them using the `Variable table`_ in the test data file or
importing them from `variable files`_. Other test suites, including
possible child test suites, will not see variables set with this
keyword.

Variables set with :name:`Set Global Variable` keyword are globally
available in all test cases and suites executed after setting
them. Setting variables with this keyword thus has the same effect as
`creating from the command line`__ using the options :option:`--variable` or
:option:`--variablefile`. Because this keyword can change variables
everywhere, it should be used with care.

.. note:: :name:`Set Test/Suite/Global Variable` keywords set named
          variables directly into `test, suite or global variable scope`__
          and return nothing. On the other hand, another BuiltIn_ keyword
          :name:`Set Variable` sets local variables using `return values`__.

__ `Setting variables in command line`_
__ `Variable scopes`_
__ `Return values from keywords`_

.. _built-in variable:

Built-in variables
------------------

Robot Framework provides some built-in variables that are available
automatically.

Operating-system variables
~~~~~~~~~~~~~~~~~~~~~~~~~~

Built-in variables related to the operating system ease making the test data
operating-system-agnostic.

.. table:: Available operating-system-related built-in variables
   :class: tabular

   +------------+------------------------------------------------------------------+
   |  Variable  |                      Explanation                                 |
   +============+==================================================================+
   | ${CURDIR}  | An absolute path to the directory where the test data            |
   |            | file is located. This variable is case-sensitive.                |
   +------------+------------------------------------------------------------------+
   | ${TEMPDIR} | An absolute path to the system temporary directory. In UNIX-like |
   |            | systems this is typically :file:`/tmp`, and in Windows           |
   |            | :file:`c:\\Documents and Settings\\<user>\\Local Settings\\Temp`.|
   +------------+------------------------------------------------------------------+
   | ${EXECDIR} | An absolute path to the directory where test execution was       |
   |            | started from.                                                    |
   +------------+------------------------------------------------------------------+
   | ${/}       | The system directory path separator. `/` in UNIX-like            |
   |            | systems and :codesc:`\\` in Windows.                             |
   +------------+------------------------------------------------------------------+
   | ${:}       | The system path element separator. `:` in UNIX-like              |
   |            | systems and `;` in Windows.                                      |
   +------------+------------------------------------------------------------------+
   | ${\\n}     | The system line separator. :codesc:`\\n` in UNIX-like systems and|
   |            | :codesc:`\\r\\n` in Windows. New in version 2.7.5.               |
   +------------+------------------------------------------------------------------+

.. table:: Using operating-system-related built-in variables
   :class: example

   =============  ========================  =======================  ==================================
     Test Case             Action                   Argument                       Argument
   =============  ========================  =======================  ==================================
   Example        Create Binary File        ${CURDIR}${/}input.data  Some text here${\\n}on two lines
   \              Set Environment Variable  CLASSPATH                ${TEMPDIR}${:}${CURDIR}${/}foo.jar
   =============  ========================  =======================  ==================================

Number variables
~~~~~~~~~~~~~~~~

The variable syntax can be used for creating both integers and
floating point numbers, as illustrated in the example below. This is
useful when a keyword expects to get an actual number, and not a
string that just looks like a number, as an argument.

.. table:: Using number variables
   :class: example

   ===========  ========  ===========  ==========  ===================================================
    Test Case    Action    Argument     Argument                   Comment
   ===========  ========  ===========  ==========  ===================================================
   Example 1A   Connect   example.com  80          # Connect gets two strings as arguments
   Example 1B   Connect   example.com  ${80}       # Connect gets a string and an integer
   Example 2    Do X      ${3.14}      ${-1e-4}    # Do X gets floating point numbers 3.14 and -0.0001
   ===========  ========  ===========  ==========  ===================================================

It is possible to create integers also from binary, octal, and
hexadecimal values using `0b`, `0o` and `0x` prefixes, respectively.
The syntax is case insensitive.

.. table:: Using integer variables with base
   :class: example

   ===========  ===============  ==========  ==========
    Test Case        Action       Argument    Argument
   ===========  ===============  ==========  ==========
   Example      Should Be Equal  ${0b1011}   ${11}
   \            Should Be Equal  ${0o10}     ${8}
   \            Should Be Equal  ${0xff}     ${255}
   \            Should Be Equal  ${0B1010}   ${0XA}
   ===========  ===============  ==========  ==========

Boolean and None/null variables
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Also Boolean values and Python `None` and Java `null` can
be created using the variable syntax similarly as numbers.

.. table:: Using Boolean and None/null variables
   :class: example

   ===========  ===============  ==========  ==========  =============================================
    Test Case        Action       Argument    Argument                      Comment
   ===========  ===============  ==========  ==========  =============================================
   Boolean      Set Status       ${true}                 # Set Status gets Boolean true as an argument
   \            Create Y         something   ${false}    # Create Y gets a string and Boolean false
   None         Do XYZ           ${None}                 # Do XYZ gets Python None as an argument
   Null         ${ret} =         Get Value   arg         # Checking that Get Value returns Java null
   \            Should Be Equal  ${ret}      ${null}
   ===========  ===============  ==========  ==========  =============================================

These variables are case-insensitive, so for example `${True}` and
`${true}` are equivalent. Additionally, `${None}` and
`${null}` are synonyms, because when running tests on the Jython
interpreter, Jython automatically converts `None` and
`null` to the correct format when necessary.

Space and empty variables
~~~~~~~~~~~~~~~~~~~~~~~~~

It is possible to create spaces and empty strings using variables
`${SPACE}` and `${EMPTY}`, respectively. These variables are
useful, for example, when there would otherwise be a need to `escape
spaces or empty cells`__ with a backslash. If more than one space is
needed, it is possible to use the `extended variable syntax`_ like
`${SPACE * 5}`.  In the following example, :name:`Should Be
Equal` keyword gets identical arguments but those using variables are
easier to understand than those using backslashes.

.. table:: Using `${SPACE}` and `${EMPTY}` variables
   :class: example

   =============   =================  ================  ================================
     Test Case          Action            Argument                Argument
   =============   =================  ================  ================================
   One Space       Should Be Equal    ${SPACE}          \\ \\
   Four Spaces     Should Be Equal    ${SPACE * 4}      \\ \\ \\ \\ \\
   Ten Spaces      Should Be Equal    ${SPACE * 10}     \\ \\ \\ \\ \\ \\ \\ \\ \\ \\ \\
   Quoted Space    Should Be Equal    "${SPACE}"        " "
   Quoted Spaces   Should Be Equal    "${SPACE * 2}"    " \\ "
   Empty           Should Be Equal    ${EMPTY}          \\
   =============   =================  ================  ================================

There is also an empty `list variable`_ `@{EMPTY}` and an empty `dictionary
variable`_ `&{EMPTY}`. Because they have no content, they basically
vanish when used somewhere in the test data. They are useful, for example,
with `test templates`_ when the `template keyword is used without
arguments`__ or when overriding list or dictionary variables in different
scopes. Modifying the value of `@{EMPTY}` or `&{EMPTY}` is not possible.

.. table:: Using `@{EMPTY}` and `&{EMPTY}` variable
   :class: example

   =============   ===================  ============  ============
     Test Case           Action           Argument      Argument
   =============   ===================  ============  ============
   Template        [Template]           Some keyword
   \               @{EMPTY}
   \
   Override        Set Global Variable  @{LIST}       @{EMPTY}
                   Set Suite Variable   &{DICT}       &{EMPTY}
   =============   ===================  ============  ============

.. note:: `@{EMPTY}` is new in Robot Framework 2.7.4 and `&{EMPTY}` in
          Robot Framework 2.9.

__ Escaping_
__ https://groups.google.com/group/robotframework-users/browse_thread/thread/ccc9e1cd77870437/4577836fe946e7d5?lnk=gst&q=templates#4577836fe946e7d5

Automatic variables
~~~~~~~~~~~~~~~~~~~

Some automatic variables can also be used in the test data. These
variables can have different values during the test execution and some
of them are not even available all the time. Altering the value of
these variables does not affect the original values, but some values
can be changed dynamically using keywords from the `BuiltIn`_ library.

.. table:: Available automatic variables
   :class: tabular

   +------------------------+-------------------------------------------------------+------------+
   |        Variable        |                    Explanation                        | Available  |
   +========================+=======================================================+============+
   | ${TEST NAME}           | The name of the current test case.                    | Test case  |
   +------------------------+-------------------------------------------------------+------------+
   | @{TEST TAGS}           | Contains the tags of the current test case in         | Test case  |
   |                        | alphabetical order. Can be modified dynamically using |            |
   |                        | :name:`Set Tags` and :name:`Remove Tags` keywords.    |            |
   +------------------------+-------------------------------------------------------+------------+
   | ${TEST DOCUMENTATION}  | The documentation of the current test case. Can be set| Test case  |
   |                        | dynamically using using :name:`Set Test Documentation`|            |
   |                        | keyword. New in Robot Framework 2.7.                  |            |
   +------------------------+-------------------------------------------------------+------------+
   | ${TEST STATUS}         | The status of the current test case, either PASS or   | `Test      |
   |                        | FAIL.                                                 | teardown`_ |
   +------------------------+-------------------------------------------------------+------------+
   | ${TEST MESSAGE}        | The message of the current test case.                 | `Test      |
   |                        |                                                       | teardown`_ |
   +------------------------+-------------------------------------------------------+------------+
   | ${PREV TEST NAME}      | The name of the previous test case, or an empty string| Everywhere |
   |                        | if no tests have been executed yet.                   |            |
   +------------------------+-------------------------------------------------------+------------+
   | ${PREV TEST STATUS}    | The status of the previous test case: either PASS,    | Everywhere |
   |                        | FAIL, or an empty string when no tests have been      |            |
   |                        | executed.                                             |            |
   +------------------------+-------------------------------------------------------+------------+
   | ${PREV TEST MESSAGE}   | The possible error message of the previous test case. | Everywhere |
   +------------------------+-------------------------------------------------------+------------+
   | ${SUITE NAME}          | The full name of the current test suite.              | Everywhere |
   +------------------------+-------------------------------------------------------+------------+
   | ${SUITE SOURCE}        | An absolute path to the suite file or directory.      | Everywhere |
   +------------------------+-------------------------------------------------------+------------+
   | ${SUITE DOCUMENTATION} | The documentation of the current test suite. Can be   | Everywhere |
   |                        | set dynamically using using :name:`Set Suite          |            |
   |                        | Documentation` keyword. New in Robot Framework 2.7.   |            |
   +------------------------+-------------------------------------------------------+------------+
   | &{SUITE METADATA}      | The free metadata of the current test suite. Can be   | Everywhere |
   |                        | set using :name:`Set Suite Metadata` keyword.         |            |
   |                        | New in Robot Framework 2.7.4.                         |            |
   +------------------------+-------------------------------------------------------+------------+
   | ${SUITE STATUS}        | The status of the current test suite, either PASS or  | `Suite     |
   |                        | FAIL.                                                 | teardown`_ |
   +------------------------+-------------------------------------------------------+------------+
   | ${SUITE MESSAGE}       | The full message of the current test suite, including | `Suite     |
   |                        | statistics.                                           | teardown`_ |
   +------------------------+-------------------------------------------------------+------------+
   | ${KEYWORD STATUS}      | The status of the current keyword, either PASS or     | `User      |
   |                        | FAIL. New in Robot Framework 2.7                      | keyword    |
   |                        |                                                       | teardown`_ |
   +------------------------+-------------------------------------------------------+------------+
   | ${KEYWORD MESSAGE}     | The possible error message of the current keyword.    | `User      |
   |                        | New in Robot Framework 2.7.                           | keyword    |
   |                        |                                                       | teardown`_ |
   +------------------------+-------------------------------------------------------+------------+
   | ${LOG LEVEL}           | Current `log level`_. New in Robot Framework 2.8.     | Everywhere |
   +------------------------+-------------------------------------------------------+------------+
   | ${OUTPUT FILE}         | An absolute path to the `output file`_.               | Everywhere |
   +------------------------+-------------------------------------------------------+------------+
   | ${LOG FILE}            | An absolute path to the `log file`_ or string NONE    | Everywhere |
   |                        | when no log file is created.                          |            |
   +------------------------+-------------------------------------------------------+------------+
   | ${REPORT FILE}         | An absolute path to the `report file`_ or string NONE | Everywhere |
   |                        | when no report is created.                            |            |
   +------------------------+-------------------------------------------------------+------------+
   | ${DEBUG FILE}          | An absolute path to the `debug file`_ or string NONE  | Everywhere |
   |                        | when no debug file is created.                        |            |
   +------------------------+-------------------------------------------------------+------------+
   | ${OUTPUT DIR}          | An absolute path to the `output directory`_.          | Everywhere |
   +------------------------+-------------------------------------------------------+------------+

Suite related variables `${SUITE SOURCE}`, `${SUITE NAME}`,
`${SUITE DOCUMENTATION}` and `&{SUITE METADATA}` are
available already when test libraries and variable files are imported,
except to Robot Framework 2.8 and 2.8.1 where this support was broken.
Possible variables in these automatic variables are not yet resolved
at the import time, though.

Variable priorities and scopes
------------------------------

Variables coming from different sources have different priorities and
are available in different scopes.

Variable priorities
~~~~~~~~~~~~~~~~~~~

*Variables from the command line*

   Variables `set in the command line`__ have the highest priority of all
   variables that can be set before the actual test execution starts. They
   override possible variables created in Variable tables in test case
   files, as well as in resource and variable files imported in the
   test data.

   Individually set variables (:option:`--variable` option) override the
   variables set using `variable files`_ (:option:`--variablefile` option).
   If you specify same individual variable multiple times, the one specified
   last will override earlier ones. This allows setting default values for
   variables in a `start-up script`_ and overriding them from the command line.
   Notice, though, that if multiple variable files have same variables, the
   ones in the file specified first have the highest priority.

__ `Setting variables in command line`_

*Variable table in a test case file*

   Variables created using the `Variable table`_ in a test case file
   are available for all the test cases in that file. These variables
   override possible variables with same names in imported resource and
   variable files.

   Variables created in the variable tables are available in all other tables
   in the file where they are created. This means that they can be used also
   in the Setting table, for example, for importing more variables from
   resource and variable files.

*Imported resource and variable files*

   Variables imported from the `resource and variable files`_ have the
   lowest priority of all variables created in the test data.
   Variables from resource files and variable files have the same
   priority. If several resource and/or variable file have same
   variables, the ones in the file imported first are taken into use.

   If a resource file imports resource files or variable files,
   variables in its own Variable table have a higher priority than
   variables it imports. All these variables are available for files that
   import this resource file.

   Note that variables imported from resource and variable files are not
   available in the Variable table of the file that imports them. This
   is due to the Variable table being processed before the Setting table
   where the resource files and variable files are imported.

*Variables set during test execution*

   Variables set during the test execution either using `return values
   from keywords`_ or `using Set Test/Suite/Global Variable keywords`_
   always override possible existing
   variables in the scope where they are set. In a sense they thus
   have the highest priority, but on the other hand they do not affect
   variables outside the scope they are defined.

*Built-in variables*

   `Built-in variables`_ like `${TEMPDIR}` and `${TEST_NAME}`
   have the highest priority of all variables. They cannot be overridden
   using Variable table or from command line, but even they can be reset during
   the test execution. An exception to this rule are `number variables`_, which
   are resolved dynamically if no variable is found otherwise. They can thus be
   overridden, but that is generally a bad idea. Additionally `${CURDIR}`
   is special because it is replaced already during the test data processing time.

Variable scopes
~~~~~~~~~~~~~~~

Depending on where and how they are created, variables can have a
global, test suite, test case or local scope.

Global scope
''''''''''''

Global variables are available everywhere in the test data. These
variables are normally `set from the command line`__ with the
:option:`--variable` and :option:`--variablefile` options, but it is also
possible to create new global variables or change the existing ones
with the BuiltIn_ keyword :name:`Set Global Variable` anywhere in
the test data. Additionally also `built-in variables`_ are global.

It is recommended to use capital letters with all global variables.

Test suite scope
''''''''''''''''

Variables with the test suite scope are available anywhere in the
test suite where they are defined or imported. They can be created
in Variable tables, imported from `resource and variable files`_,
or set during the test execution using the BuiltIn_ keyword
:name:`Set Suite Variable`.

The test suite scope *is not recursive*, which means that variables
available in a higher-level test suite *are not available* in
lower-level suites. If necessary, `resource and variable files`_ can
be used for sharing variables.

Since these variables can be considered global in the test suite where
they are used, it is recommended to use capital letters also with them.

Test case scope
'''''''''''''''

Variables with the test case scope are visible in a test case and in
all user keywords the test uses. Initially there are no variables in
this scope, but it is possible to create them by using the BuiltIn_
keyword :name:`Set Test Variable` anywhere in a test case.

Also variables in the test case scope are to some extend global. It is
thus generally recommended to use capital letters with them too.

Local scope
'''''''''''

Test cases and user keywords have a local variable scope that is not
seen by other tests or keywords. Local variables can be created using
`return values`__ from executed keywords and user keywords also get
them as arguments__.

It is recommended to use lower-case letters with local variables.

.. note:: Prior to Robot Framework 2.9 variables in the local scope
          `leaked to lower level user keywords`__. This was never an
          intended feature, and variables should be set or passed
          explicitly also with earlier versions.

__ `Setting variables in command line`_
__ `Return values from keywords`_
__ `User keyword arguments`_
__ https://github.com/robotframework/robotframework/issues/532

Advanced variable features
--------------------------

Extended variable syntax
~~~~~~~~~~~~~~~~~~~~~~~~

Extended variable syntax allows accessing attributes of an object assigned
to a variable (for example, `${object.attribute}`) and even calling
its methods (for example, `${obj.getName()}`). It works both with
scalar and list variables, but is mainly useful with the former

Extended variable syntax is a powerful feature, but it should
be used with care. Accessing attributes is normally not a problem, on
the contrary, because one variable containing an object with several
attributes is often better than having several variables. On the
other hand, calling methods, especially when they are used with
arguments, can make the test data pretty complicated to understand.
If that happens, it is recommended to move the code into a test library.

The most common usages of extended variable syntax are illustrated
in the example below. First assume that we have the following `variable file`_
and test case:

.. sourcecode:: python

   class MyObject:

       def __init__(self, name):
           self.name = name

       def eat(self, what):
           return '%s eats %s' % (self.name, what)

       def __str__(self):
           return self.name

   OBJECT = MyObject('Robot')
   DICTIONARY = {1: 'one', 2: 'two', 3: 'three'}

.. table::
   :class: example

   ===========  ========  =========================  ==========
    Test Case    Action          Argument             Argument
   ===========  ========  =========================  ==========
   Example      KW 1      ${OBJECT.name}
   \            KW 2      ${OBJECT.eat('Cucumber')}
   \            KW 3      ${DICTIONARY[2]}
   ===========  ========  =========================  ==========

When this test data is executed, the keywords get the arguments as
explained below:

- :name:`KW 1` gets string `Robot`
- :name:`KW 2` gets string `Robot eats Cucumber`
- :name:`KW 3` gets string `two`

The extended variable syntax is evaluated in the following order:

1. The variable is searched using the full variable name. The extended
   variable syntax is evaluated only if no matching variable
   is found.

2. The name of the base variable is created. The body of the name
   consists of all the characters after the opening `{` until
   the first occurrence of a character that is not an alphanumeric character
   or a space. For example, base variables of `${OBJECT.name}`
   and `${DICTIONARY[2]}`) are `OBJECT` and `DICTIONARY`,
   respectively.

3. A variable matching the body is searched. If there is no match, an
   exception is raised and the test case fails.

4. The expression inside the curly brackets is evaluated as a Python
   expression, so that the base variable name is replaced with its
   value. If the evaluation fails because of an invalid syntax or that
   the queried attribute does not exist, an exception is raised and
   the test fails.

5. The whole extended variable is replaced with the value returned
   from the evaluation.

If the object that is used is implemented with Java, the extended
variable syntax allows you to access attributes using so-called bean
properties. In essence, this means that if you have an object with the
`getName`  method set into a variable `${OBJ}`, then the
syntax `${OBJ.name}` is equivalent to but clearer than
`${OBJ.getName()}`. The Python object used in the previous example
could thus be replaced with the following Java implementation:

.. sourcecode:: java

 public class MyObject:

     private String name;

     public MyObject(String name) {
         name = name;
     }

     public String getName() {
         return name;
     }

     public String eat(String what) {
         return name + " eats " + what;
     }

     public String toString() {
         return name;
     }
 }

Many standard Python objects, including strings and numbers, have
methods that can be used with the extended variable syntax either
explicitly or implicitly. Sometimes this can be really useful and
reduce the need for setting temporary variables, but it is also easy
to overuse it and create really cryptic test data. Following examples
show few pretty good usages.

.. table:: Using methods of strings and numbers
   :class: example

   ===========  ============  ===================  ===============
    Test Case      Action           Argument          Argument
   ===========  ============  ===================  ===============
   String       ${string} =   Set Variable         abc
   \            Log           ${string.upper()}    # Logs 'ABC'
   \            Log           ${string * 2}        # Logs 'abcabc'
   Number       ${number} =   Set Variable         ${-2}
   \            Log           ${number * 10}       # Logs -20
   \            Log           ${number.__abs__()}  # Logs 2
   ===========  ============  ===================  ===============

Note that even though `abs(number)` is recommended over
`number.__abs__()` in normal Python code, using
`${abs(number)}` does not work. This is because the variable name
must be in the beginning of the extended syntax. Using `__xxx__`
methods in the test data like this is already a bit questionable, and
it is normally better to move this kind of logic into test libraries.

Extended variable syntax works also in `list variable`_ context.
If, for example, an object assigned to a variable `${EXTENDED}` has
an attribute `attribute` that contains a list as a value, it can be
used as a list variable `@{EXTENDED.attribute}`.

Extended variable assignment
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Starting from Robot Framework 2.7, it is possible to set attributes of
objects stored to scalar variables using `keyword return values`__ and
a variation of the `extended variable syntax`_. Assuming we have
variable `${OBJECT}` from the previous examples, attributes could
be set to it like in the example below.

__ `Return values from keywords`_

.. table:: Extended variable assignment
   :class: example

   ===========  ====================  ==============  ===============
    Test Case          Action            Argument         Argument
   ===========  ====================  ==============  ===============
   Example      ${OBJECT.name} =      Set Variable    New name
   \            ${OBJECT.new_attr} =  Set Variable    New attribute
   ===========  ====================  ==============  ===============

The extended variable assignment syntax is evaluated using the
following rules:

1. The assigned variable must be a scalar variable and have at least
   one dot. Otherwise the extended assignment syntax is not used and
   the variable is assigned normally.

2. If there exists a variable with the full name
   (e.g. `${OBJECT.name}` in the example above) that variable
   will be assigned a new value and the extended syntax is not used.

3. The name of the base variable is created. The body of the name
   consists of all the characters between the opening `${` and
   the last dot, for example, `OBJECT` in `${OBJECT.name}`
   and `foo.bar` in `${foo.bar.zap}`. As the second example
   illustrates, the base name may contain normal extended variable
   syntax.

4. The name of the attribute to set is created by taking all the
   characters between the last dot and the closing `}`, for
   example, `name` in `${OBJECT.name}`. If the name does not
   start with a letter or underscore and contain only these characters
   and numbers, the attribute is considered invalid and the extended
   syntax is not used. A new variable with the full name is created
   instead.

5. A variable matching the base name is searched. If no variable is
   found, the extended syntax is not used and, instead, a new variable
   is created using the full variable name.

6. If the found variable is a string or a number, the extended syntax
   is ignored and a new variable created using the full name. This is
   done because you cannot add new attributes to Python strings or
   numbers, and this way the new syntax is also less
   backwards-incompatible.

7. If all the previous rules match, the attribute is set to the base
   variable. If setting fails for any reason, an exception is raised
   and the test fails.

.. note:: Unlike when assigning variables normally using `return
          values from keywords`_, changes to variables done using the
          extended assign syntax are not limited to the current
          scope. Because no new variable is created but instead the
          state of an existing variable is changed, all tests and
          keywords that see that variable will also see the changes.

Variables inside variables
~~~~~~~~~~~~~~~~~~~~~~~~~~

Variables are allowed also inside variables, and when this syntax is
used, variables are resolved from the inside out. For example, if you
have a variable `${var${x}}`, then `${x}` is resolved
first. If it has the value `name`, the final value is then the
value of the variable `${varname}`. There can be several nested
variables, but resolving the outermost fails, if any of them does not
exist.

In the example below, :name:`Do X` gets the value `${JOHN HOME}`
or `${JANE HOME}`, depending on if :name:`Get Name` returns
`john` or `jane`. If it returns something else, resolving
`${${name} HOME}` fails.

.. table:: Using a variable inside another variable
   :class: example

   ============  ==========  =======  =======
     Variable       Value     Value    Value
   ============  ==========  =======  =======
   ${JOHN HOME}  /home/john
   ${JANE HOME}  /home/jane
   ============  ==========  =======  =======

.. table::
   :class: example

   ===========  ============  ========================  ==========
    Test Case      Action             Argument           Argument
   ===========  ============  ========================  ==========
   Example      ${name} =     Get Name
   \            Do X          ${${name} HOME}
   ===========  ============  ========================  ==========
