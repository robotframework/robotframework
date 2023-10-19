Resource and variable files
===========================

User keywords and variables in `suite files`_ and `suite
initialization files`_ can only be used in files where they are
created, but *resource files* provide a mechanism for sharing them.
The high level syntax for creating resource files is exactly the same
as when creating suite files and `supported file formats`_ are the same
as well. The main difference is that resource files cannot have tests.

*Variable files* provide a powerful mechanism for creating and sharing
variables. For example, they allow values other than strings and
enable creating variables dynamically. Their flexibility comes from
the fact that they are created using Python or YAML, which
also makes them somewhat more complicated than `Variable sections`_.

.. contents::
   :depth: 2
   :local:

Resource files
--------------

Resource files are typically created using the plain text format, but also
`reStructuredText format`__ and `JSON format`__ are supported.

__ `Resource files using reStructured text format`_
__ `Resource files using JSON format`_

Taking resource files into use
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Resource files are imported using the :setting:`Resource` setting in the
Settings section so that the path to the resource file is given as an argument
to the setting. The recommended extension for resource files is :file:`.resource`.
For backwards compatibility reasons also :file:`.robot`, :file:`.txt` and
:file:`.tsv` work, but using :file:`.resource` may be mandated in the future.

If the resource file path is absolute, it is used directly. Otherwise,
the resource file is first searched relatively to the directory
where the importing file is located. If the file is not found there,
it is then searched from the directories in Python's `module search path`_.
Searching resource files from the module search path makes it possible to
bundle them into Python packages as `package data`__ and importing
them like :file:`package/example.resource`.

The resource file path can contain variables, and it is recommended to use
them to make paths system-independent (for example,
:file:`${RESOURCES}/login.resource` or just :file:`${RESOURCE_PATH}`).
Additionally, forward slashes (`/`) in the path
are automatically changed to backslashes (:codesc:`\\`) on Windows.

.. sourcecode:: robotframework

   *** Settings ***
   Resource    example.resource
   Resource    ../resources/login.resource
   Resource    package/example.resource
   Resource    ${RESOURCES}/common.resource

The user keywords and variables defined in a resource file are
available in the file that takes that resource file into
use. Similarly available are also all keywords and variables from the
libraries, resource files and variable files imported by the said
resource file.

.. note:: The :file:`.resource` extension is new in Robot Framework 3.1.

__ https://packaging.python.org/en/latest/guides/distributing-packages-using-setuptools/#package-data

Resource file structure
~~~~~~~~~~~~~~~~~~~~~~~

The higher-level structure of resource files is the same as that of
suite files otherwise, but they cannot contain tests or tasks.
Additionally, the Setting section in resource files can contain only imports
(:setting:`Library`, :setting:`Resource`, :setting:`Variables`),
:setting:`Documentation` and :setting:`Keyword Tags`.
The Variable section and Keyword section are used exactly the same way
as in suite files.

If several resource files have a user keyword with the same name, they
must be used so that the `keyword name is prefixed with the resource
file name`__ without the extension (for example, :name:`myresources.Some
Keyword` and :name:`common.Some Keyword`). Moreover, if several resource
files contain the same variable, the one that is imported first is
taken into use.

__ `Handling keywords with same names`_

Documenting resource files
~~~~~~~~~~~~~~~~~~~~~~~~~~

Keywords created in a resource file can be documented__ using
:setting:`[Documentation]` setting. The resource file itself can have
:setting:`Documentation` in the Setting section similarly as suites__.

Libdoc_ and various editors use these documentations, and they
are naturally available for anyone opening resource files.  The
first logical line of the documentation of a keyword, until the first
empty line, is logged when the keyword is run, but otherwise resource
file documentation is ignored during the test execution.

__ `User keyword name and documentation`_
__ `Suite name`_

Example resource file
~~~~~~~~~~~~~~~~~~~~~

.. sourcecode:: robotframework

   *** Settings ***
   Documentation     An example resource file
   Library           SeleniumLibrary
   Resource          ${RESOURCES}/common.resource

   *** Variables ***
   ${HOST}           localhost:7272
   ${LOGIN URL}      http://${HOST}/
   ${WELCOME URL}    http://${HOST}/welcome.html
   ${BROWSER}        Firefox

   *** Keywords ***
   Open Login Page
       [Documentation]    Opens browser to login page
       Open Browser    ${LOGIN URL}    ${BROWSER}
       Title Should Be    Login Page

   Input Name
       [Arguments]    ${name}
       Input Text    username_field    ${name}

   Input Password
       [Arguments]    ${password}
       Input Text    password_field    ${password}

Resource files using reStructured text format
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The `reStructuredText format`_ that can be used with `suite files`_  works
also with resource files. Such resource files can use either :file:`.rst`
or :file:`.rest` extension and they are otherwise imported exactly as
normal resource files:

.. sourcecode:: robotframework

   *** Settings ***
   Resource         example.rst

When parsing resource files using the reStructuredText format, Robot Framework
ignores all data outside code blocks containing Robot Framework data exactly
the same way as when parsing `reStructuredText suite files`__.
For example, the following resource file imports :name:`OperatingSystem` library,
defines `${MESSAGE}` variable and creates :name:`My Keyword` keyword:

.. sourcecode:: rest

    Resource file using reStructuredText
    ------------------------------------

    This text is outside code blocks and thus ignored.

    .. code:: robotframework

       *** Settings ***
       Library          OperatingSystem

       *** Variables ***
       ${MESSAGE}       Hello, world!

    Also this text is outside code blocks and ignored. Code blocks not
    containing Robot Framework data are ignored as well.

    .. code:: robotframework

       # Both space and pipe separated formats are supported.

       | *** Keywords ***  |                        |         |
       | My Keyword        | [Arguments]            | ${path} |
       |                   | Directory Should Exist | ${path} |

__ `reStructuredText format`_

Resource files using JSON format
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Resource files can be created using JSON_ the `same way as suite files`__.
Such JSON resource files must use either the standard :file:`.json` extension
or the custom :file:`.rsrc` extension. They are otherwise imported exactly as
normal resource files:

.. sourcecode:: robotframework

   *** Settings ***
   Resource         example.rsrc

Resource files can be converted to JSON using `ResourceFile.to_json`__ and
recreated using `ResourceFile.from_json`__:

.. sourcecode:: python

   from robot.running import ResourceFile


   # Create resource file based on data on the file system.
   resource = ResourceFile.from_file_system('example.resource')

   # Save JSON data to a file.
   resource.to_json('example.rsrc')

   # Recreate resource from JSON data.
   resource = ResourceFile.from_json('example.rsrc')

__ `JSON format`_
__ https://robot-framework.readthedocs.io/en/master/autodoc/robot.running.html#robot.running.model.ResourceFile.to_json
__ https://robot-framework.readthedocs.io/en/master/autodoc/robot.running.html#robot.running.model.ResourceFile.from_json

Variable files
--------------

Variable files contain variables_ that can be used in the test
data. Variables can also be created using `Variable sections`_ or `set from
the command line`__, but variable files allow creating them dynamically
and also make it easy to create other variable values than strings.

Variable files are typically implemented as modules and there are
two different approaches for creating variables:

`Getting variables directly from a module`_
   Variables are specified as module attributes. In simple cases, the
   syntax is so simple that no real programming is needed. For example,
   `MY_VAR = 'my value'` creates a variable `${MY_VAR}` with the specified
   text as its value. One limitation of this approach is that it does
   not allow using arguments.

`Getting variables from a special function`_
   Variable files can have a special `get_variables`
   (or `getVariables`) method that returns variables as a mapping.
   Because the method can take arguments this approach is very flexible.

Alternatively variable files can be implemented as `classes`__
that the framework will instantiate. Also in this case it is possible to create
variables as attributes or get them dynamically from the `get_variables`
method. Variable files can also be created as YAML__ and JSON__.

__ `Setting variables in command line`_
__ `Implementing variable file as a class`_
__ `Variable file as YAML`_
__ `Variable file as JSON`_

Taking variable files into use
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Setting section
'''''''''''''''

All test data files can import variable files using the :setting:`Variables`
setting in the Setting section. Variable files are typically imported using
a path to the file same way as `resource files are imported`__ using
the :setting:`Resource` setting. Similarly to resource files, the path to
the imported variable file is considered relative to the directory where the
importing file is, and if not found, it is searched from directories
in the `module search path`_. The path can also contain variables,
and slashes are converted to backslashes on Windows.

Examples:

.. sourcecode:: robotframework

   *** Settings ***
   Variables    myvariables.py
   Variables    ../data/variables.py
   Variables    ${RESOURCES}/common.yaml

Starting from Robot Framework 5.0, variable files implemented using Python
can also be imported using the module name `similarly as libraries`__.
When using this approach, the module needs to be in the `module search path`_.

Examples:

.. sourcecode:: robotframework

   *** Settings ***
   Variables    myvariables
   Variables    rootmodule.Variables

If a `variable file accepts arguments`__, they are specified after the path
or name of the variable file to import:

.. sourcecode:: robotframework

   *** Settings ***
   Variables    arguments.py    arg1    ${ARG2}
   Variables    arguments    argument

All variables from a variable file are available in the test data file
that imports it. If several variable files are imported and they
contain a variable with the same name, the one in the earliest imported file is
taken into use. Additionally, variables created in Variable sections and
set from the command line override variables from variable files.

__ `Taking resource files into use`_
__ `Specifying library to import`_
__ `Getting variables from a special function`_

Command line
''''''''''''

Another way to take variable files into use is using the command line option
:option:`--variablefile`. Variable files are referenced using a path or
module name similarly as when importing them using the :setting:`Variables`
setting. Possible arguments are joined to the path with a colon (`:`)::

   --variablefile myvariables.py
   --variablefile path/variables.py
   --variablefile /absolute/path/common.py
   --variablefile variablemodule
   --variablefile arguments.py:arg1:arg2
   --variablefile rootmodule.Variables:arg1:arg2

Variable files taken into use from the
command line are also searched from the `module search path`_ similarly as
variable files imported in the Setting section. Relative paths are considered
relative to the directory where execution is started from.

If a variable file is given as an absolute Windows path, the colon after the
drive letter is not considered a separator::

   --variablefile C:\path\variables.py

It is also possible to use a semicolon
(`;`) as an argument separator. This is useful if variable file arguments
themselves contain colons, but requires surrounding the whole value with
quotes on UNIX-like operating systems::

   --variablefile C:\path\variables.py;D:\data.xls
   --variablefile "myvariables.py;argument:with:colons"

Variables in variable files taken use on the command line are globally
available in all test data files, similarly as `individual variables`__
set with the :option:`--variable` option. If both :option:`--variablefile` and
:option:`--variable` options are used and there are variables with same
names, those that are set individually with
:option:`--variable` option take precedence.

__ `Setting variables in command line`_

Getting variables directly from a module
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Basic syntax
''''''''''''

When variable files are taken into use, they are imported as Python
modules and all their module level attributes that do not start with
an underscore (`_`) are, by default, considered to be variables. Because
variable names are case-insensitive, both lower- and upper-case names are
possible, but in general, capital letters are recommended for global
variables and attributes.

.. sourcecode:: python

   VARIABLE = "An example string"
   ANOTHER_VARIABLE = "This is pretty easy!"
   INTEGER = 42
   STRINGS = ["one", "two", "kolme", "four"]
   NUMBERS = [1, INTEGER, 3.14]
   MAPPING = {"one": 1, "two": 2, "three": 3}

In the example above, variables `${VARIABLE}`, `${ANOTHER VARIABLE}`, and
so on, are created. The first two variables are strings, the third one is
an integer, then there are two lists, and the final value is a dictionary.
All these variables can be used as a `scalar variable`_, lists and the
dictionary also a `list variable`_ like `@{STRINGS}` (in the dictionary's case
that variable would only contain keys), and the dictionary also as a
`dictionary variable`_ like `&{MAPPING}`.

To make creating a list variable or a dictionary variable more explicit,
it is possible to prefix the variable name with `LIST__` or `DICT__`,
respectively:

.. sourcecode:: python

   from collections import OrderedDict

   LIST__ANIMALS = ["cat", "dog"]
   DICT__FINNISH = OrderedDict([("cat", "kissa"), ("dog", "koira")])

These prefixes will not be part of the final variable name, but they cause
Robot Framework to validate that the value actually is list-like or
dictionary-like. With dictionaries the actual stored value is also turned
into a special dictionary that is used also when `creating dictionary
variables`_ in the Variable section. Values of these dictionaries are accessible
as attributes like `${FINNISH.cat}`. These dictionaries are also ordered, but
preserving the source order requires also the original dictionary to be
ordered.

The variables in both the examples above could be created also using the
Variable section below.

.. sourcecode:: robotframework

   *** Variables ***
   ${VARIABLE}            An example string
   ${ANOTHER VARIABLE}    This is pretty easy!
   ${INTEGER}             ${42}
   @{STRINGS}             one          two           kolme         four
   @{NUMBERS}             ${1}         ${INTEGER}    ${3.14}
   &{MAPPING}             one=${1}     two=${2}      three=${3}
   @{ANIMALS}             cat          dog
   &{FINNISH}             cat=kissa    dog=koira

.. note:: Variables are not replaced in strings got from variable files.
          For example, `VAR = "an ${example}"` would create
          variable `${VAR}` with a literal string value
          `an ${example}` regardless would variable `${example}`
          exist or not.

Using objects as values
'''''''''''''''''''''''

Variables in variable files are not limited to having only strings or
other base types as values like Variable sections. Instead, their
variables can contain any objects. In the example below, the variable
`${MAPPING}` contains a Python dictionary and also has two variables
created from a custom object implemented in the same file.

.. sourcecode:: python

    MAPPING = {'one': 1, 'two': 2}

    class MyObject:
        def __init__(self, name):
            self.name = name

    OBJ1 = MyObject('John')
    OBJ2 = MyObject('Jane')

Creating variables dynamically
''''''''''''''''''''''''''''''

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
''''''''''''''''''''''''''''''''''''

When Robot Framework processes variable files, all their attributes
that do not start with an underscore are expected to be
variables. This means that even functions or classes created in the
variable file or imported from elsewhere are considered variables. For
example, the last example would contain the variables `${math}`
and `${get_area}` in addition to `${AREA1}` and
`${AREA2}`.

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
`__all__` and give it a list of attribute names to be processed
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

.. Note:: The `__all__` attribute is also, and originally, used
          by Python to decide which attributes to import
          when using the syntax `from modulename import *`.

The third option to select what variables are actually created is using
a special `get_variables` function discussed below.

Getting variables from a special function
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

An alternative approach for getting variables is having a special
`get_variables` function (also camelCase syntax `getVariables` is possible)
in a variable file. If such a function exists, Robot Framework calls it and
expects to receive variables as a Python dictionary with variable names as keys
and variable values as values. Created variables can
be used as scalars, lists, and dictionaries exactly like when `getting
variables directly from a module`_, and it is possible to use `LIST__` and
`DICT__` prefixes to make creating list and dictionary variables more explicit.
The example below is functionally identical to the first example related to
`getting variables directly from a module`_.

.. sourcecode:: python

    def get_variables():
        variables = {"VARIABLE ": "An example string",
                     "ANOTHER VARIABLE": "This is pretty easy!",
                     "INTEGER": 42,
                     "STRINGS": ["one", "two", "kolme", "four"],
                     "NUMBERS": [1, 42, 3.14],
                     "MAPPING": {"one": 1, "two": 2, "three": 3}}
        return variables

`get_variables` can also take arguments, which facilitates changing
what variables actually are created. Arguments to the function are set just
as any other arguments for a Python function. When `taking variable files
into use`_, arguments are specified after the path
to the variable file, and in the command line they are separated from the
path with a colon or a semicolon.

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

Starting from Robot Framework 7.0, arguments to variable files support automatic
argument conversion as well as named argument syntax. For example, a variable
file with `get_variables(first: int = 0, second: str = '')` could be imported
like this:

.. sourcecode:: robotframework

   *** Settings ***
   Variables    example.py    42              # Converted to integer.
   Variables    example.py    second=value    # Named argument syntax.

Implementing variable file as a class
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

It is possible to implement variables files also as a class.

Implementation
''''''''''''''

Because variable files are always imported using a file system path,
the class must have the same name as the module it is located in.

The framework will create an instance of the class using no arguments and
variables will be gotten from the instance. Similarly as with modules,
variables can be defined as attributes directly
in the instance or gotten from a special `get_variables` method.

When variables are defined directly in an instance, all attributes containing
callable values are ignored to avoid creating variables from possible methods
the instance has. If you would actually need callable variables, you need
to use other approaches to create variable files.

Examples
''''''''

The first examples create variables from attributes.
It creates variables `${VARIABLE}` and `@{LIST}` from class
attributes and `${ANOTHER VARIABLE}` from an instance attribute.

.. sourcecode:: python

    class StaticExample:
        variable = 'value'
        LIST__list = [1, 2, 3]
        _not_variable = 'starts with an underscore'

        def __init__(self):
            self.another_variable = 'another value'


The second examples utilizes dynamic approach for getting variables. It
creates only one variable `${DYNAMIC VARIABLE}`.

.. sourcecode:: python

    class DynamicExample:

        def get_variables(self, *args):
            return {'dynamic variable': ' '.join(args)}


Variable file as YAML
~~~~~~~~~~~~~~~~~~~~~

Variable files can also be implemented as `YAML <https://yaml.org>`_ files.
YAML is a data serialization language with a simple and human-friendly syntax
that is nevertheless easy for machines to parse.
The following example demonstrates a simple YAML file:

.. sourcecode:: yaml

    string:   Hello, world!
    integer:  42
    list:
      - one
      - two
    dict:
      one: yksi
      two: kaksi
      with spaces: kolme

YAML variable files can be used exactly like normal variable files
from the command line using :option:`--variablefile` option, in the Settings
section using :setting:`Variables` setting, and dynamically using the
:name:`Import Variables` keyword. They are automatically recognized by their
extension that must be either :file:`.yaml` or :file:`.yml`.
If the above YAML file is imported, it will create exactly the same variables
as this Variable section:

.. sourcecode:: robotframework

   *** Variables ***
   ${STRING}     Hello, world!
   ${INTEGER}    ${42}
   @{LIST}       one         two
   &{DICT}       one=yksi    two=kaksi    with spaces=kolme

YAML files used as variable files must always be mappings on the top level.
As the above example demonstrates, keys and values in the mapping become
variable names and values, respectively. Variable values can be any data
types supported by YAML syntax. If names or values contain non-ASCII
characters, YAML variables files must be UTF-8 encoded.

Mappings used as values are automatically converted to special dictionaries
that are used also when `creating dictionary variables`_ in the Variable section.
Most importantly, values of these dictionaries are accessible as attributes
like `${DICT.one}`, assuming their names are valid as Python attribute names.
If the name contains spaces or is otherwise not a valid attribute name, it is
always possible to access dictionary values using syntax like
`${DICT}[with spaces]` syntax.

.. note:: Using YAML files with Robot Framework requires `PyYAML
          <http://pyyaml.org>`_ module to be installed. You can typically
          install it with pip_ like `pip install pyyaml`.

Variable file as JSON
~~~~~~~~~~~~~~~~~~~~~

Variable files can also be implemented as `JSON <https://json.org>`_ files.
Similarly as YAML discussed in the previous section, JSON is a data
serialization format targeted both for humans and machines. It is based on
JavaScript syntax and it is not as human-friendly as YAML, but it still
relatively easy to understand and modify. The following example contains
exactly the same data as the earlier YAML example:

.. sourcecode:: json

    {
        "string": "Hello, world!",
        "integer": 42,
        "list": [
            "one",
            "two"
        ],
        "dict": {
            "one": "yksi",
            "two": "kaksi",
            "with spaces": "kolme"
        }
    }

JSON variable files are automatically recognized by their :file:`.json`
extension and they can be used exactly like YAML variable files. They
also have exactly same requirements for structure, encoding, and so on.
Unlike YAML, Python supports JSON out-of-the-box so no extra modules need
to be installed.

.. note:: Support for JSON variable files is new in Robot Framework 6.1.
