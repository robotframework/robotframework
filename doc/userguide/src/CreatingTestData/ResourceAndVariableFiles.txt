Resource and variable files
---------------------------

User keywords and variables in `test case files`_ and `test suite
initialization files`_ can only be used in files where they are
created, but *resource files* provide a mechanism for sharing them. Since
the resource file structure is very close to test case files, it is
easy to create them.

*Variable files* provide a powerful mechanism for creating and sharing
variables. For example, they allow values other than strings and
enable creating variables dynamically. Their flexibility comes from
the fact that they are created using Python code, which also makes
them somewhat more complicated than `Variable tables`_.

.. contents::
   :depth: 2
   :local:

Resource files
~~~~~~~~~~~~~~

Taking resource files into use
''''''''''''''''''''''''''''''

Resource files are imported using the :opt:`Resource` setting in the
Settings table. The path to the resource file is given in the cell
after the setting name.

If the path is given in an absolute format, it is used directly. In other
cases, the resource file is first searched relatively to the directory
where the importing file is located. If the file is not found there,
it is then searched from the directories in PYTHONPATH. The path can
contain variables, and it is recommended to use them to make paths
system-independent (for example, :path:`${RESOURCES}/login_resources.html` or
:path:`${RESOURCE_PATH}`). Additionally, slashes ("/") in the path
are automatically changed to backslashes ("\\") on Windows.

.. table:: Importing resource files
   :class: example

   =========  =======================  =======
    Setting            Value            Value
   =========  =======================  =======
   Resource   myresources.html
   Resource   ../data/resources.html
   Resource   ${RESOURCES}/common.tsv
   =========  =======================  =======

The user keywords and variables defined in a resource file are
available in the file that takes that resource file into
use. Similarly available are also all keywords and variables from the
libraries, resource files and variable files imported by the said
resource file.

Resource file structure
'''''''''''''''''''''''

The higher-level structure of resource files is the same as that of
test case files otherwise, but, of course, they cannot contain Test
Case tables. Additionally, the Setting table in resource files can
contain only import settings (:opt:`Library`, :opt:`Resource`,
:opt:`Variables`) and :opt:`Documentation`. The Variable table and
Keyword table are used exactly the same way as in test case files.

If several resource files have a user keyword with the same name, they
must be used so that the `keyword name is prefixed with the resource
file name`__ without the extension (for example, :name:`myresources.Some
Keyword` and :name:`common.Some Keyword`). Moreover, if several resource
files contain the same variable, the one that is imported first is
taken into use.

__ `Handling keywords with same names`_

Documenting resource files
''''''''''''''''''''''''''

Keywords created in a resource file can be documented__ using
:opt:`[Documentation]` setting. Starting from Robot Framework 2.1 also
the resource file itself can have :opt:`Documentation` in the Setting
table similarly as `test suites`__.

Both `libdoc`_ and `RIDE`_ use these documentations, and they
are naturally available for anyone opening resource files.  The
first line of the documentation of a keyword is logged when it is run,
but otherwise resource file documentations are ignored during the test
execution.

__ `User keyword name and documentation`_
__ `Test suite name and documentation`_

Example resource file
'''''''''''''''''''''

.. table::
   :class: example

   =============  ========================  =======  =======
      Setting               Value            Value    Value
   =============  ========================  =======  =======
   Documentation  An example resource file
   Library        SeleniumLibrary
   Resource       ${RESOURCES}/common.html
   =============  ========================  =======  =======

.. table::
   :class: example

   ==============  ============================  =======  =======
      Variable                Value               Value    Value
   ==============  ============================  =======  =======
   ${HOST}         localhost:7272
   ${LOGIN_URL}    \http://${HOST}/
   ${WELCOME_URL}  \http://${HOST}/welcome.html
   ${BROWSER}      Firefox
   ==============  ============================  =======  =======

.. table::
   :class: example

   ===============  ===============  ==============  ==============  ========
       Keyword         Action           Argument        Argument     Argument
   ===============  ===============  ==============  ==============  ========
   Open Login Page  [Documentation]  Opens browser   to login page
   \                Open Browser     ${LOGIN_URL}    ${BROWSER}
   \                Title Should Be  Login Page
   \
   Input Name       [Arguments]      ${name}
   \                Input Text       username_field  ${name}
   \
   Input Password   [Arguments]      ${password}
   \                Input Text       password_field  ${password}
   ===============  ===============  ==============  ==============  ========

Variable files
~~~~~~~~~~~~~~

Variable files contain variables_ that can be used in the test
data. Variables can also be created using variable tables or set from
the command line, but variable files allow creating them dynamically
and their variables can contain any objects.

Variable files are typically implemented as Python modules and there are
two different approaches for creating variables:

`Creating variables directly`_
   Variables are specified as module attributes. In simple cases, the
   syntax is so simple that no real programming is needed. For example,
   :code:`MY_VAR = 'my value'` creates a variable
   :var:`${MY_VAR}` with the specified text as the value.

`Getting variables from a special function`_
   Variable files can have a special :code:`get_variables`
   (or :code:`getVariables`) method that returns variables as a mapping.
   Because the method can take arguments this approach is very flexible.

Alternatively variable files can be implemented as `Python or Java classes`__
that the framework will instantiate. Also in this case it is possible to create
variables as attributes or get them from a special method.

__ `Implementing variable file as Python or Java class`_

Taking variable files into use
''''''''''''''''''''''''''''''

Setting table
`````````````

All test data files can import variables using the
:opt:`Variables` setting in the Setting table, in the same way as
`resource files are imported`__ using the :opt:`Resource`
setting. Similarly to resource files, the path to the imported
variable file is considered relative to the directory where the
importing file is, and if not found, it is searched from the
directories in PYTHONPATH. The path can also contain variables, and
slashes are converted to backslashes on Windows. If an `argument file takes
arguments`__, they are specified in the cells after the path and also they
can contain variables.

__ `Taking resource files into use`_
__ `Getting variables from a special function`_

.. table:: Importing a variable file
   :class: example

   =========  =======================  =======  =======
    Setting             Value           Value    Value
   =========  =======================  =======  =======
   Variables  myvariables.py
   Variables  ../data/variables.py
   Variables   ${RESOURCES}/common.py
   Variables  taking_arguments.py      arg1     ${ARG2}
   =========  =======================  =======  =======

All variables from a variable file are available in the test data file
that imports it. If several variable files are imported and they
contain a variable with the same name, the one in the earliest imported file is
taken into use. Additionally, variables created in Variable tables and
set from the command line override variables from variable files.

Command line
````````````

Another way to take variable files into use is using the command line option
:opt:`--variablefile`. Variable files are referenced using a path to them, and
possible arguments are joined to the path with a colon (:opt:`:`)::

   --variablefile myvariables.py
   --variablefile path/variables.py
   --variablefile /absolute/path/common.py
   --variablefile taking_arguments.py:arg1:arg2

Variables in these files are globally available in all test data
files, similarly as `individual variables`__ set with the
:opt:`--variable` option. If both :opt:`--variablefile` and
:opt:`--variable` options are used and there are variables with same
names, those that are set individually with
:opt:`--variable` option take precedence.

__ `Setting variables in command line`_

Creating variables directly
'''''''''''''''''''''''''''

Basic syntax
````````````

When variable files are taken into use, they are imported as Python
modules and all their global attributes that do not start with an
underscore (:code:`_`) are considered to be variables. Because variable
names are case-insensitive, both lower- and upper-case names are
possible, but in general, capital letters are recommended for global
variables and attributes.

.. sourcecode:: python

   VARIABLE = "An example string"
   ANOTHER_VARIABLE = "This is pretty easy!"
   INTEGER = 42
   STRINGS = ["one", "two", "kolme", "four"]
   NUMBERS = [1, INTEGER, 3.14]

In the example above, variables :var:`${VARIABLE}`,
:var:`${ANOTHER VARIABLE}`, and so on, are created. The first two
variables are strings, the third one is an integer and the last two are lists.
All these variables are `scalar variables`_, even the ones containing
lists as values. To create `list variables`_, the variable name must
be prefixed with :code:`LIST__` (note the two underscores).

.. sourcecode:: python

   LIST__STRINGS = ["list", "of", "strings"]
   LIST__MIXED = ["first value", -1.1, None, True]

The variables in both the examples above could be created also using the
Variable table below.

.. table::
   :class: example

   ===================  ====================  ==========  =========  =========
         Variable              Value            Value       Value      Value
   ===================  ====================  ==========  =========  =========
   ${VARIABLE}          An example string
   ${ANOTHER_VARIABLE}  This is pretty easy!
   ${INTEGER}           ${42}
   ${STRINGS}           one                   two         kolme      four
   ${NUMBERS}           ${1}                  ${INTEGER}  ${3.14}
   @{STRINGS}           list                  of          strings
   @{MIXED}             first value           ${-1.1}     ${None}    ${True}
   ===================  ====================  ==========  =========  =========

Using objects as values
```````````````````````

Variables in variable files are not limited to having only strings or
other base types as values like variable tables. Instead, their
variables can contain any objects. In the example below, the variable
:var:`${MAPPING}` contains a Java Hashtable with two values (this
example works only when running tests on Jython).

.. sourcecode:: python

    from java.util import Hashtable

    MAPPING = Hashtable()
    MAPPING.put("one", 1)
    MAPPING.put("two", 2)

The second example creates :var:`${MAPPING}` as a Python dictionary
and also has two variables created from a custom object implemented in
the same file.

.. sourcecode:: python

    MAPPING = {'one': 1, 'two': 2}

    class MyObject:
        def __init__(self, name):
            self.name = name

    OBJ1 = MyObject('John')
    OBJ2 = MyObject('Jane')

Creating variables dynamically
``````````````````````````````

Because variable files are created using a real programming language,
they can have dynamic logic for setting variables.

.. sourcecode:: python

   import os
   import random
   import time

   USER = os.getlogin()                # current login name
   RANDOM_INT = random.randint(0, 10)  # random integer in range [0,10]
   CURRENT_TIME = time.asctime()       # timestamp like 'Thu Apr  6 12:45:21 2006'
   if time.localtime()[3] > 12:
       AFTERNOON = True
   else:
       AFTERNOON = False

The example above uses standard Python libraries to set different
variables, but you can use your own code to construct the values. The
example below illustrates the concept, but similarly, your code could
read the data from a database, from an external file or even ask it from
the user.

.. sourcecode:: python

    import math

    def get_area(diameter):
        radius = diameter / 2
        area = math.pi * radius * radius
        return area

    AREA1 = get_area(1)
    AREA2 = get_area(2)

Selecting which variables to include
````````````````````````````````````

When Robot Framework processes variable files, all their attributes
that do not start with an underscore are expected to be
variables. This means that even functions or classes created in the
variable file or imported from elsewhere are considered variables. For
example, the last example would contain the variables :var:`${math}`
and :var:`${get_area}` in addition to :var:`${AREA1}` and
:var:`${AREA2}`.

Normally the extra variables do not cause problems, but they
could override some other variables and cause hard-to-debug
errors. One possibility to ignore other attributes is prefixing them
with an underscore:

.. sourcecode:: python

    import math as _math

    def _get_area(diameter):
        radius = diameter / 2.0
        area = _math.pi * radius * radius
        return area

    AREA1 = _get_area(1)
    AREA2 = _get_area(2)

If there is a large number of other attributes, instead of prefixing
them all, it is often easier to use a special attribute
:code:`__all__` and give it a list of attribute names to be processed
as variables.

.. sourcecode:: python

    import math

    __all__ = ['AREA1', 'AREA2']

    def get_area(diameter):
        radius = diameter / 2.0
        area = math.pi * radius * radius
        return area

    AREA1 = get_area(1)
    AREA2 = get_area(2)

.. Note:: The :code:`__all__` attribute is also, and originally, used
          by Python to decide which attributes to import
          when using the syntax :code:`from modulename import *`.

Getting variables from a special function
'''''''''''''''''''''''''''''''''''''''''

An alternative approach for getting variables is having a special
:code:`get_variables` function (also camelCase syntax
:code:`getVariables` is possible) in a variable file. If such a function
exists, Robot Framework calls it and expects to receive variables as
a Python dictionary or a Java :code:`Map` with variable names as keys
and variable values as values. Variables are considered to be scalars,
unless prefixed with :code:`LIST__`, and values can contain
anything. The example below is functionally identical to the first examples of
`creating variables directly`_ above.

.. sourcecode:: python

    def get_variables():
        variables = {"VARIABLE ": "An example string",
                     "ANOTHER_VARIABLE": "This is pretty easy!",
                     "INTEGER": 42,
                     "STRINGS": ["one", "two", "kolme", "four"],
                     "NUMBERS": [1, 42, 3.14],
                     "LIST__STRINGS": ["list", "of", "strings"],
                     "LIST__MIXED": ["first value", -1.1, None, True]}
        return variables


:code:`get_variables` can also take arguments, which facilitates changing
what variables actually are created. Arguments to the function are set just
as any other arguments for a Python function. When `taking variable files
into use`_ in the test data, arguments are specified in cells after the path
to the variable file, and in the command line they are separated from the
path with a colon.

The dummy example below shows how to use arguments with variable files. In a
more realistic example, the argument could be a path to an external text file
or database where to read variables from.

.. sourcecode:: python

    variables1 = {'scalar': 'Scalar variable',
                  'LIST__list': ['List','variable']}
    variables2 = {'scalar' : 'Some other value',
                  'LIST__list': ['Some','other','value'],
                  'extra': 'variables1 does not have this at all'}

    def get_variables(arg):
        if arg == 'one':
            return variables1
        else:
            return variables2

Implementing variable file as Python or Java class
''''''''''''''''''''''''''''''''''''''''''''''''''

Starting from Robot Framework 2.7, it is possible to implement variables files
as Python or Java classes.

Implementation
``````````````

Because variable files are always imported using a file system path, creating
them as classes has some restrictions:

  - Python classes must have the same name as the module they are located.
  - Java classes must live in the default package.
  - Paths to Java classes must end with either :path:`.java` or :path:`.class`.
    The class file must exists in both cases.

Regardless the implementation language, the framework will create an instance
of the class using no arguments and variables will be gotten from the instance.
Similarly as with modules, variables can be defined as attributes directly
in the instance or gotten from a special :code:`get_variables`
(or :code:`getVariables`) method.

When variables are defined directly in an instance, all attributes containing
callable values are ignored to avoid creating variables from possible methods
the instance has. If you would actually need callable variables, you need
to use other approaches to create variable files.

Examples
````````

The first examples create variables from attributes using both Python and Java.
Both of them create variables :var:`${VARIABLE}` and :var:`@{LIST}` from class
attributes and :var:`${ANOTHER VARIABLE}` from an instance attribute.

.. sourcecode:: python

    class StaticPythonExample(object):
        variable = 'value'
        LIST__list = [1, 2, 3]
        _not_variable = 'starts with an underscore'

        def __init__(self):
            self.another_variable = 'another value'

.. sourcecode:: java

    public class StaticJavaExample {
        public static String variable = "value";
        public static String[] LIST__list = {1, 2, 3};
        private String notVariable = "is private";
        public String anotherVariable;

        public StaticJavaExample(String arg1, String arg2) {
            anotherVariable = "another value";
        }
    }

The second examples utilizes dynamic approach for getting variables. Both of
them create only one variable :var:`${DYNAMIC VARIABLE}`.

.. sourcecode:: python

    class DynamicPythonExample(object):

        def get_variables(self, *args):
            return {'dynamic variable': ' '.join(args)}

.. sourcecode:: java

    import java.util.Map;
    import java.util.HashMap;

    public class DynamicJavaExample {

        public Map<String, String> getVariables(String arg1, String arg2) {
            HashMap<String, String> variables = new HashMap<String, String>();
            variables.put("dynamic variable", arg1 + " " + arg2);
            return variables;
        }
    }
