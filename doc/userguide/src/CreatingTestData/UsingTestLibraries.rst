Using test libraries
--------------------

Test libraries contain those lowest-level keywords, often called
*library keywords*, which actually interact with the system under
test. All test cases always use keywords from some library, often
through higher-level `user keywords`_. This section explains how to
take test libraries into use and how to use the keywords they
provide. `Creating test libraries`_ is described in a separate
section.

.. contents::
   :depth: 2
   :local:


Taking test libraries into use
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Instructions for taking test libraries into use are given in the
subsections below.

Using Library setting
'''''''''''''''''''''

Test libraries are normally imported using the :opt:`Library`
setting in the Setting table and having the library name in the
subsequent column. The library name is case-sensitive (it is the name
of the module or class implementing the library and must be exactly
correct), but any spaces in it are ignored. With Python libraries in
modules or Java libraries in packages, the full name including the
module or package name must be used.

In those cases where the library needs arguments, they are listed in
the columns after the library name. It is possible to use default
values, variable number of arguments, and named arguments in test
library imports similarly as with `arguments to keywords`__.  Both the
library name and arguments can be set using variables.

__ `Using arguments`_


.. table:: Importing test libraries
   :class: example

   =========  ===================  =======  =======
    Setting          Value          Value    Value
   =========  ===================  =======  =======
   Library    OperatingSystem      \        \
   Library    com.company.TestLib  \        \
   Library    MyLibrary            arg1     arg2
   Library    ${LIBRARY}           \        \
   =========  ===================  =======  =======

It is possible to import test libraries in `test case files`_,
`resource files`_ and `test suite initialization files`_. In all these
cases, all the keywords in the imported library are available in that
file. With resource files, those keywords are also available in other
files using them.

Using Import Library keyword
''''''''''''''''''''''''''''

Another possibility to take a test library into use is using the
keyword :name:`Import Library` from the BuiltIn_ library. This keyword
takes the library name and possible arguments similarly as the
:opt:`Library` setting. Keywords from the imported library are
available in the test suite where the :name:`Import Library` keyword was
used. This approach is useful in cases where the library is not
available when the test execution starts and only some other keywords
make it available.

.. table:: Using Import Library keyword
   :class: example

   ===========  =================  ==========  ==========  ==========
    Test Case       Action          Argument    Argument    Argument
   ===========  =================  ==========  ==========  ==========
   Example      Do Something       \           \           \
   \            Import Library     MyLibrary   arg1        arg2
   \            KW From Mylibrary  \           \           \
   ===========  =================  ==========  ==========  ==========

Library search path
'''''''''''''''''''

The most common way to specify a test library to import is using its
name, like it has been done in all the examples in this section. In
these cases Robot Framework tries to find the class or module
implementing the library from the *library search path*. Basically,
this means that the library code and all its possible dependencies
must be in :code:`PYTHONPATH` or, when running tests on Jython, in a
:code:`CLASSPATH`. `Setting the library search path`__ is explained in
a section of its own. Libraries can also set the search path
automatically or have special instructions on how to do it. All
`standard libraries`_, for example, are in the library search path
automatically.

The biggest benefit of this approach is that when the library search
path has been configured, often using a `custom start-up script`__,
normal users do not need to think where libraries actually are
installed. The drawback is that getting your own, possible
very simple, libraries into the search path may require some
additional configuration.

__ `Adjusting library search path`_
__ `Creating start-up scripts`_

Using physical path to library
''''''''''''''''''''''''''''''

Another mechanism for specifying the library to import is using a
path to it in the file system. This path is considered relative to the
directory where current test data file is situated similarly as paths
to `resource and variable files`_. The main benefit of this approach
is that there is no need to configure the library search path.

If the library is a file, the path to it must contain extension. For
Python libraries the extension is naturally :path:`.py` and for Java
libraries it can either be :path:`.class` or :path:`.java`, but the
class file must always be available. If Python library is implemented
as a directory, the path to it must have a trailing forward slash
(:path:`/`). Following examples demonstrate these different
usages.

.. table:: Importing test libraries using physical paths to them
   :class: example

   =========  ===========================  ========  =========
    Setting               Value             Value      Value
   =========  ===========================  ========  =========
   Library    PythonLib.py                 \         \
   Library    /absolute/path/JavaLib.java  \         \
   Library    relative/path/PythonDirLib/  possible  arguments
   Library    ${RESOURCES}/Example.class   \         \
   =========  ===========================  ========  =========

A limitation of this approach is that libraries implemented as Python classes `must
be in a module with the same name as the class`__. Additionally, importing
libraries distributed in JAR or ZIP packages is not possible with this mechanism.

__ `Test library names`_


Setting custom name to test library
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The library name is shown in test logs before keyword names, and if
multiple keywords have the same name, they must be used so that the
`keyword name is prefixed with the library name`__. The library name
is got normally from the module or class name implementing it, but
there are some situations where changing it is desirable:

__ `Handling keywords with same names`_

- There is a need to import the same library several times with
  different arguments. This is not possible otherwise.

- The library name is inconveniently long. This can happen, for
  example, if a Java library has a long package name.

- You want to use variables to import different libraries in
  different environments, but refer to them with the same name.

- The library name is misleading or otherwise poor. In this case,
  changing the actual name is, of course, a better solution.


The basic syntax for specifying the new name is having the text
:code:`WITH NAME` (case-insensitive) after the library name and then
having the new name in the next cell. The specified name is shown in
logs and must be used in the test data when using keywords' full name
(:name:`LibraryName.Keyword Name`).

.. table:: Importing libraries with custom names
   :class: example

   =========  ===================  =========  =========
    Setting          Value           Value      Value
   =========  ===================  =========  =========
   Library    com.company.TestLib  WITH NAME  TestLib
   Library    ${LIBRARY}           WITH NAME  MyName
   =========  ===================  =========  =========

Possible arguments to the library are placed into cells between the
original library name and the :code:`WITH NAME` text. The following example
illustrates how the same library can be imported several times with
different arguments:

.. table:: Importing the same library several times with a different name
   :class: example

   =========  ===========  =============  =======  =========  =========
    Setting      Value          Value      Value     Value      Value
   =========  ===========  =============  =======  =========  =========
   Library    SomeLibrary  localhost      1234     WITH NAME  LocalLib
   Library    SomeLibrary  server.domain  8080     WITH NAME  RemoteLib
   =========  ===========  =============  =======  =========  =========

.. table::
   :class: example

   ===========  ========================  ===========  ==========
    Test Case             Action           Argument     Argument
   ===========  ========================  ===========  ==========
   My Test      LocalLib.Some Keyword     some arg     second arg
   \            RemoteLib.Some Keyword    another arg  whatever
   \            LocalLib.Another Keyword  \            \
   ===========  ========================  ===========  ==========

Setting a custom name to a test library works both when importing a
library in the Setting table and when using the :name:`Import Library` keyword.

Standard libraries
~~~~~~~~~~~~~~~~~~~

Some test libraries are distributed with Robot Framework and these
libraries are called *standard libraries*. The BuiltIn_ library is special,
because it is taken into use automatically and thus its keywords are always
available. Other standard libraries need to be imported in the same way
as any other libraries, but there is no need to install them.

Normal standard libraries
'''''''''''''''''''''''''

The available normal standard libraries are listed below with links to their
documentations:

  - BuiltIn_
  - Collections_
  - Dialogs_
  - OperatingSystem_
  - Process_
  - Screenshot_
  - String_
  - Telnet_
  - XML_

.. _BuiltIn: ../libraries/BuiltIn.html
.. _Collections: ../libraries/Collections.html
.. _Dialogs: ../libraries/Dialogs.html
.. _OperatingSystem: ../libraries/OperatingSystem.html
.. _Process: ../libraries/Process.html
.. _String: ../libraries/String.html
.. _Screenshot: ../libraries/Screenshot.html
.. _Telnet: ../libraries/Telnet.html
.. _XML: ../libraries/XML.html

Remote library
''''''''''''''

In addition to the normal standard libraries listed above, there is
also :name:`Remote` library that is totally different than the other standard
libraries. It does not have any keywords of its own but it works as a
proxy between Robot Framework and actual test library implementations.
These libraries can be running on other machines than the core
framework and can even be implemented using languages not supported by
Robot Framework natively.

See separate `Remote library interface`_ section for more information
about this concept.

External libraries
~~~~~~~~~~~~~~~~~~~

Any test library that is not one of the standard libraries is, by
definition, *an external library*. Robot Framework developers provide
some generic libraries, such as Selenium2Library_ and SwingLibrary_,
which are not packaged with the framework itself, because they require
external dependencies. Generic libraries can also be provided by other
parties, and most teams have also some custom libraries only for
themselves.

Different external libraries can have a totally different mechanism
for installing and introducing them. Quite often they also require
some other dependencies to be installed separately. All libraries
should have clear instructions on this and preferably automate the
installation.

See `Creating test libraries`_ section for more information about how
to create new test libraries for your own or generic usage.
