.. _libdoc:

Library documentation tool (:prog:`libdoc`)
-------------------------------------------

.. contents::
   :depth: 1
   :local:

:prog:`libdoc` is a tool for generating keyword documentation for test
libraries and resource files in HTML and XML formats. The former
format is suitable for humans and the latter for RIDE_ and other
tools. :prog:`libdoc` also has few special commands to show library or
resource information on the console.

Documentation can be created for:

- test libraries implemented with Python__ or Java__ using the normal
  static library API,
- test libraries using the `dynamic API`__, including remote libraries, and
- `resource files`_.

Additionally it is possible to use XML spec created by :prog:`libdoc`
earlier as an input.

:prog:`libdoc` is built-in into Robot Framework and automatically included
in the installation starting from version 2.7. With earlier versions you
need to download `libdoc.py script`__ separately. The command line usage
has changed slightly between these versions but the documentation syntax
is still the same.

__ `Python libraries`_
__ `Java libraries`_
__ `Dynamic libraries`_
__ http://code.google.com/p/robotframework/wiki/LibraryDocumentationTool

General usage
~~~~~~~~~~~~~

Synopsis
''''''''

::

    python -m robot.libdoc [options] library_or_resource output_file
    python -m robot.libdoc [options] library_or_resource list|show|version [names]

Options
'''''''

  -f, --format <html|xml>  Specifies whether to generate HTML or XML output.
                           If this options is not used, the format is got
                           from the extension of the output file.
  -N, --name <newname>     Sets the name of the documented library or resource.
  -V, --version <newversion>  Sets the version of the documented library or
                           resource. The default value for test libraries is
                           `got from the source code`__.
  -P, --pythonpath <path>  Additional locations where to search for libraries
                           and resources similarly as when `running tests`__.
  -E, --escape <what:with>  Escapes characters which are problematic in console.
                           :opt:`what` is the name of the character to escape
                           and :opt:`with` is the string to escape it with.
                           Available escapes are listed in the :opt:`--help`
                           output.
  -h, --help               Prints this help.


__ `Specifying library version`_
__ `Using --pythonpath option`_

Specifying library or resource file
'''''''''''''''''''''''''''''''''''

Python libraries and dynamic libraries with name or path
````````````````````````````````````````````````````````

When documenting libraries implemented with Python or that use the
dynamic library API, it is possible to specify the library either by
using just the library name or path to the library source code.
In the former case the library is searched using the `library search path`_
and its name must be in the same format as in Robot Framework test data.

If these libraries require arguments when they are imported, the arguments
must be catenated with the library name or path using two colons like
:cli:`MyLibrary::arg1::arg2`. If arguments change what keywords the library
provides or otherwise alter its documentation, it might be a good idea to use
:opt:`--name` option to also change the library name accordingly.

Java libraries with path
````````````````````````

A Java test library implemented with a normal library API can be
specified by giving the path to the source code file containing the
library implementation. Additionally, :path:`tools.jar`, which is part
of the Java JDK distribution, must be found from CLASSPATH when
:prog:`libdoc` is executed. Notice that generating documentation for Java
libraries works only with Jython.

Resource files with path
````````````````````````

Resource files must always be specified using a path. If the path does
not exist, resource files are also searched from all directories in
PYTHONPATH similarly as when executing test cases.

Creating documentation
''''''''''''''''''''''

When creating documentation in HTML or XML format, the output file must
be specified as the second argument after the library/resource name or path.
Output format is got automatically from the extension but can also be set
with :opt:`--format` option.

Examples::

   python -m robot.libdoc OperatingSystem OperatingSystem.html
   python -m robot.libdoc --name MyLibrary Remote::http://10.0.0.42:8270 MyLibrary.html
   python -m robot.libdoc test/resource.html doc/resource_doc.html
   jython -m robot.libdoc --version 1.0 MyJavaLibrary.java MyJavaLibrary.xml

Viewing information on console
''''''''''''''''''''''''''''''

:prog:`libdoc` has three special commands to show information on the console.
These commands are used instead of the name of the output file, and they can
also take additional arguments.

:opt:`list`
    List names of the keywords the library/resource contains. Can be
    limited to show only certain keywords by passing optional patterns
    as arguments. Keyword is listed if its name contains given pattern.
:opt:`show`
    Show library/resource documentation. Can be limited to show only
    certain keywords by passing names as arguments. Keyword is shown if
    its name matches any given name. Special argument :opt:`intro` will show
    only the library introduction and importing sections.
:opt:`version`
    Show library version

Optional patterns given to :opt:`list` and :opt:`show` are case and space
insensitive. Both also accept :opt:`*` and :opt:`?` as wildcards.

Examples::

  python -m robot.libdoc Dialogs list
  python -m robot.libdoc Selenium2Library list browser
  python -m robot.libdoc Remote::10.0.0.42:8270 show
  python -m robot.libdoc Dialogs show PauseExecution execute*
  python -m robot.libdoc Selenium2Library show intro
  python -m robot.libdoc Selenium2Library version

Alternative execution
'''''''''''''''''''''

Although :prog:`libdoc` is used only with Python in the synopsis above, it works
also with Jython and IronPython. When documenting Java libraries, Jython is
actually required. In the synopsis :prog:`libdoc` is executed as an installed
module (:cli:`python -m robot.libdoc`), but it can be run also as a script::

    python path/robot/libdoc.py [options] arguments

Executing as a script can be useful if you have done `manual installation`_
or otherwise just have the :path:`robot` directory with the source code
somewhere in your system.

Writing documentation
~~~~~~~~~~~~~~~~~~~~~

`Creating test libraries`_ and `resource files`_ is described in more
details elsewhere in this guide.

Python libraries
''''''''''''''''

The documentation for Python libraries is written simply as doc
strings for the library class or module and for methods implementing
keywords. The first line of the method documentation is considered as
a short documentation for the keyword (used, for example, as a tool tip in
links in the generated HTML documentation), and it should thus be as
describing as possible, but not too long.

The simple example below illustrates how to write the documentation in
general, and there is a little longer `example`_ at the end of this
chapter containing also an example of the generated documentation.

.. sourcecode:: python

    class ExampleLib:
        """Library for demo purposes.

        This library is only used in an example and it doesn't do anything useful.
        """

        def my_keyword(self):
            """Does nothing."""
            pass

        def your_keyword(self, arg):
            """Takes one argument and *does nothing* with it.

            Example:
            | Your Keyword | xxx |
            | Your Keyword | yyy |
            """
            pass

.. tip:: If you want to use non-ASCII charactes in the documentation of
         Python libraries, you must either use UTF-8 as your `source code
         encoding`__ or create docstrings as Unicode.

         For more information on Python documentation strings, see `PEP-257`__.

__ http://www.python.org/dev/peps/pep-0263
__ http://www.python.org/dev/peps/pep-0257

Java libraries
''''''''''''''

When writing documentation for a normal Java library, conventions for
writing Javadoc should be used. The documentation is generated based
on the Javadocs in the source files. For example, the following simple
example has exactly same documentation (and functionality) than the
earlier Python example.

.. sourcecode:: java

    /**
     * Library for demo purposes.
     *
     * This library is only used in an example and it doesn't do anything useful.
     */
    public class ExampleLib {

        /**
         * Does nothing.
         */
        public void myKeyword() {
        }

        /**
         * Takes one argument and *does nothing* with it.
         *
         * Example:
         * | Your Keyword | xxx |
         * | Your Keyword | yyy |
         */
        public void yourKeyword(String arg) {
        }
    }

Dynamic libraries
'''''''''''''''''

To be able to generate meaningful documentation for dynamic libraries,
the libraries must return keyword argument names and documentation using
:code:`get_keyword_arguments` and :code:`get_keyword_documentation`
methods (or using their camelCase variants :code:`getKeywordArguments`
and :code:`getKeywordDocumentation`). Libraries can also support
general library documentation via special :code:`__intro__` and
:code:`__init__` values to the :code:`get_keyword_documentation` method.

See the `Dynamic library API`_ section for more information about how to
create these methods.

Importing section
'''''''''''''''''

A separate section about how the library is imported is created based on its
initialization methods. For a Python library, if it has an  :code:`__init__`
method that takes arguments in addition to :code:`self`, its documentation and
arguments are shown. For a Java library, if it has a public constructor that
accepts arguments, all its public constructors are shown.

.. sourcecode:: python

   class TestLibrary:

       def __init__(self, mode='default')
           """Creates new TestLibrary. `mode` argument is used to determine mode."""
           self.mode = mode

       def some_keyword(self, arg):
           if self.mode == 'secret':
                # ...

Resource file documentation
'''''''''''''''''''''''''''

Keywords in resource files can have documentation using
:opt:`[Documentation]` setting, and this documentation is also used by
:prog:`libdoc`. First line of the documentation (until the first
`implicit newline`__ or explicit :code:`\\n`) is considered to be the short
documentation similarly as with test libraries.

Also the resource file itself can have :opt:`Documentation` in the
Setting table for documenting the whole resource file.

Possible variables in resource files are not documented.

.. table:: An example resource file
   :class: example

   +---------------+-----------------------------------------+-----------------------------------+
   |    Setting    |                  Value                  |               Value               |
   +===============+=========================================+===================================+
   | Documentation | Resource file for demo purposes.        |                                   |
   +---------------+-----------------------------------------+-----------------------------------+
   | ...           | This resource is only used in an example| and it doesn't do anything useful.|
   +---------------+-----------------------------------------+-----------------------------------+

.. table::
   :class: example

   +--------------+------------------+------------------------+-------------------------------+
   |    Keyword   |      Action      |         Argument       |            Argument           |
   +==============+==================+========================+===============================+
   | My Keyword   | [Documentation]  | Does nothing           |                               |
   +--------------+------------------+------------------------+-------------------------------+
   |              | No Operation     |                        |                               |
   +--------------+------------------+------------------------+-------------------------------+
   |              |                  |                        |                               |
   +--------------+------------------+------------------------+-------------------------------+
   | Your Keyword | [Arguments]      | ${arg}                 |                               |
   +--------------+------------------+------------------------+-------------------------------+
   |              | [Documentation]  | Takes one argument and | | Example:\\n                 |
   |              |                  | \*does nothing\* with  | | \| Your Keyword \| xxx \|\\n|
   |              |                  | it.\\n                 | | \| Your Keyword \| yyy \|\\n|
   +--------------+------------------+------------------------+-------------------------------+
   |              | No Operation     |                        |                               |
   +--------------+------------------+------------------------+-------------------------------+

__ `Automatic newlines in test data`_

Documentation syntax
~~~~~~~~~~~~~~~~~~~~

Generic formatting rules
''''''''''''''''''''''''

The documentation is generated according to Robot Framework's `documentation
formatting`_ rules. Most important features of are formatting using
:code:`*bold*` and :code:`_italic_`, custom links and automatic conversion of
URLs links, and the possibility to create tables and pre-formatted blocks
(useful for examples) simply with pipe character. If documentation gets longer,
support for section titles (new in Robot Framework 2.7.5) can also be handy.

.. _internal linking:

Internal linking and argument formatting
''''''''''''''''''''''''''''''''''''''''

:prog:`libdoc` supports internal linking to keywords and different
sections in the documentation. Linking is done by surrounding the
target name with backtick characters like :code:`\`target\``. Target
names are case-insensitive and possible targets are explained in the
subsequent sections. The same syntax can also be used for formatting
arguments or other data.

In addition to the examples in the following sections, internal linking
and argument formatting is shown also in the longer `example` at the
end of this chapter.

Linking to keywords
```````````````````

All keywords the library have automatically create link targets and they can
be linked using syntax :code:`\`Keyword Name\``. This is illustrated with
the example below where both keywords have links to each others.

.. sourcecode:: python

   def keyword(log_level="INFO"):
       """Does something and logs the output using the given level.

       Valid values for log level` are "INFO" (default) "DEBUG" and "TRACE".

       See also `Another Keyword`.
       """
       # ...

   def another_keyword(argument, log_level="INFO"):
       """Does something with the given argument else and logs the output.

       See `Keyword` for information about valid log levels.
       """
       # ...

Linking to automatic sections
`````````````````````````````

The documentation generated by :prog:`libdoc` always contains sections
for overall library introduction, shortcuts to keywords, and for
actual keywords.  If a library itself takes arguments, there is also
separate `importing section`_.

All these sections act as targets that can be linked, and the possible
target names are listed in the table below. Using these targets is
shown in the example of the next section.

.. table:: Automatic section link targets
   :class: tabular

   ================  =============================================================
        Section                                 Target
   ================  =============================================================
   Introduction      :code:`\`introduction\`` and :code:`\`library introduction\``
   Importing         :code:`\`importing\`` and :code:`\`library importing\``
   Shortcuts         :code:`\`shortcuts\`` (New in Robot Framework 2.7.5.)
   Keywords          :code:`\`keywords\`` (New in Robot Framework 2.7.5.)
   ================  =============================================================

Linking to custom sections
``````````````````````````

Starting from Robot Framework 2.7.5, `documentation formatting`_
supports custom `section titles`_. The first level titles used in the
library or resource file introduction automatically create link
targets. The example below illustrates linking both to automatic and
custom sections:

.. sourcecode:: python

   """Library for libdoc demonstration purposes.

   This library does not do anything useful.

   = My section  =

   We do have a custom section in the documentation, though.
   """

   def keyword():
       """Does nothing.

       See `introduction` for more information and `My section` to test how
       linking to custom sections works.
       """
       pass

Argument formatting
```````````````````

If the text between backticks does not match any target,
:prog:`libdoc` will not create a link but instead formats the text
specially. This formatting works very well with keyword arguments
referenced in keyword documentations, but can also be used with other
special data.

Keywords' arguments
'''''''''''''''''''

:prog:`libdoc` handles keywords' arguments automatically so that
arguments specified for methods in libraries or user keywords in
resource files are listed in a separate column. User keyword arguments
are shown without :var:`${}` or :var:`@{}` to make arguments look
the same regardless where keywords originated from.

Example
~~~~~~~

The following example illustrates how to use the most important
`documentation formatting`_ possibilities, `internal linking`_, and so
on. `Click here`__ to see how the generated documentation looks like.

.. sourcecode:: python

   src/SupportingTools/LoggingLibrary.py

All `standard libraries`_ have documentation generated by
:prog:`libdoc` and their documentation (and source code) act as a more
realistic examples.

__ src/SupportingTools/LoggingLibrary.html

