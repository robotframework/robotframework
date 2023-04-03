Using test libraries
====================

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

Importing libraries
-------------------

Test libraries are typically imported using the :setting:`Library` setting,
but it is also possible to use the :name:`Import Library` keyword.

Using `Library` setting
~~~~~~~~~~~~~~~~~~~~~~~

Test libraries are normally imported using the :setting:`Library`
setting in the Setting section and having the library name in the
subsequent column. Unlike most of the other data, the library name
is both case- and space-sensitive. If a library is in a package,
the full name including the package name must be used.

In those cases where the library needs arguments, they are listed in
the columns after the library name. It is possible to use default
values, variable number of arguments, and named arguments in test
library imports similarly as with `arguments to keywords`__.  Both the
library name and arguments can be set using variables.

__ `Using arguments`_

.. sourcecode:: robotframework

   *** Settings ***
   Library    OperatingSystem
   Library    my.package.TestLibrary
   Library    MyLibrary    arg1    arg2
   Library    ${LIBRARY}

It is possible to import test libraries in `suite files`_,
`resource files`_ and `suite initialization files`_. In all these
cases, all the keywords in the imported library are available in that
file. With resource files, those keywords are also available in other
files using them.

Using `Import Library` keyword
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Another possibility to take a test library into use is using the
keyword :name:`Import Library` from the BuiltIn_ library. This keyword
takes the library name and possible arguments similarly as the
:setting:`Library` setting. Keywords from the imported library are
available in the test suite where the :name:`Import Library` keyword was
used. This approach is useful in cases where the library is not
available when the test execution starts and only some other keywords
make it available.

.. sourcecode:: robotframework

   *** Test Cases ***
   Example
       Do Something
       Import Library    MyLibrary    arg1    arg2
       KW From MyLibrary

Specifying library to import
----------------------------

Libraries to import can be specified either by using the library name
or the path to the library. These approaches work the same way regardless
if the library is imported using the :setting:`Library` setting or the
:name:`Import Library` keyword.

Using library name
~~~~~~~~~~~~~~~~~~

The most common way to specify a test library to import is using its
name, like it has been done in all the examples in this section. In
these cases Robot Framework tries to find the class or module
implementing the library from the `module search path`_. Libraries that
are installed somehow ought to be in the module search path automatically,
but with other libraries the search path may need to be configured separately.

The biggest benefit of this approach is that when the module search
path has been configured, often using a custom `start-up script`_,
normal users do not need to think where libraries actually are
installed. The drawback is that getting your own, possible
very simple, libraries into the search path may require some
additional configuration.

Using physical path to library
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Another mechanism for specifying the library to import is using a
path to it in the file system. This path is considered relative to the
directory where current test data file is situated similarly as paths
to `resource and variable files`_. The main benefit of this approach
is that there is no need to configure the module search path.

If the library is a file, the path to it must contain extension,
i.e. :file:`.py`. If a library is implemented
as a directory, the path to it must have a trailing forward slash (`/`)
if the path is relative. With absolute paths the trailing slash is optional.
Following examples demonstrate these different usages.

.. sourcecode:: robotframework

   *** Settings ***
   Library    PythonLibrary.py
   Library    relative/path/PythonDirLib/    possible    arguments
   Library    ${RESOURCES}/Example.class


A limitation of this approach is that libraries implemented as Python classes `must
be in a module with the same name as the class`__.

__ `Library name`_

Setting custom name to library
------------------------------

The library name is shown in test logs before keyword names, and if
multiple keywords have the same name, they must be used so that the
`keyword name is prefixed with the library name`__. The library name
is got normally from the module or class name implementing it, but
there are some situations where changing it is desirable:

__ `Handling keywords with same names`_

- There is a need to import the same library several times with
  different arguments. This is not possible otherwise.

- The library name is inconveniently long.

- You want to use variables to import different libraries in
  different environments, but refer to them with the same name.

- The library name is misleading or otherwise poor. In this case,
  changing the actual name is, of course, a better solution.

The basic syntax for specifying the new name is having the text
`AS` (case-sensitive) after the library name and then
having the new name after that. The specified name is shown in
logs and must be used in the test data when using keywords' full name
(:name:`LibraryName.Keyword Name`).

.. sourcecode:: robotframework

   *** Settings ***
   Library    packagename.TestLib    AS    TestLib
   Library    ${LIBRARY}    AS    MyName

Possible arguments to the library are placed between the
original library name and the `AS` marker. The following example
illustrates how the same library can be imported several times with
different arguments:

.. sourcecode:: robotframework

   *** Settings ***
   Library    SomeLibrary    localhost        1234    AS    LocalLib
   Library    SomeLibrary    server.domain    8080    AS    RemoteLib

   *** Test Cases ***
   Example
       LocalLib.Some Keyword     some arg       second arg
       RemoteLib.Some Keyword    another arg    whatever
       LocalLib.Another Keyword

Setting a custom name to a test library works both when importing a
library in the Setting section and when using the :name:`Import Library` keyword.

.. note:: Prior to Robot Framework 6.0 the marker to use when giving a custom name
          to a library was `WITH NAME` instead of `AS`. The old syntax continues
          to work, but it is considered deprecated and will eventually be removed.

Standard libraries
------------------

Some test libraries are distributed with Robot Framework and these
libraries are called *standard libraries*. The BuiltIn_ library is special,
because it is taken into use automatically and thus its keywords are always
available. Other standard libraries need to be imported in the same way
as any other libraries, but there is no need to install them.

Normal standard libraries
~~~~~~~~~~~~~~~~~~~~~~~~~

The available normal standard libraries are listed below with links to their
documentations:

  - BuiltIn_
  - Collections_
  - DateTime_
  - Dialogs_
  - OperatingSystem_
  - Process_
  - Screenshot_
  - String_
  - Telnet_
  - XML_

.. _BuiltIn: ../libraries/BuiltIn.html
.. _Collections: ../libraries/Collections.html
.. _DateTime: ../libraries/DateTime.html
.. _Dialogs: ../libraries/Dialogs.html
.. _OperatingSystem: ../libraries/OperatingSystem.html
.. _Process: ../libraries/Process.html
.. _String: ../libraries/String.html
.. _Screenshot: ../libraries/Screenshot.html
.. _Telnet: ../libraries/Telnet.html
.. _XML: ../libraries/XML.html

Remote library
~~~~~~~~~~~~~~

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
------------------

Any test library that is not one of the standard libraries is, by
definition, *an external library*. The Robot Framework open source community
has implemented several generic libraries, such as SeleniumLibrary_ and
SwingLibrary_, which are not packaged with the core framework. A list of
publicly available libraries can be found from http://robotframework.org.

Generic and custom libraries can obviously also be implemented by teams using
Robot Framework. See `Creating test libraries`_ section for more information
about that topic.

Different external libraries can have a totally different mechanism
for installing them and taking them into use. Sometimes they may also require
some other dependencies to be installed separately. All libraries
should have clear installation and usage documentation and they should
preferably automate the installation process.
