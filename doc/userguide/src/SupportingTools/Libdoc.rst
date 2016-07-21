.. _libdoc:

Library documentation tool (Libdoc)
===================================

.. contents::
   :depth: 1
   :local:

Libdoc is Robot Framework's built-in tool for generating keyword documentation
for test libraries and resource files in HTML and XML formats. The former
format is suitable for humans and the latter for RIDE_ and other
tools. Libdoc also has few special commands to show library or
resource information on the console.

Documentation can be created for:

- test libraries implemented with Python__ or Java__ using the normal
  static library API,
- test libraries using the `dynamic API`__, including remote libraries, and
- `resource files`_.

Additionally it is possible to use XML spec created by Libdoc
earlier as an input.

__ `Python libraries`_
__ `Java libraries`_
__ `Dynamic libraries`_

General usage
-------------

Synopsis
~~~~~~~~

::

    python -m robot.libdoc [options] library_or_resource output_file
    python -m robot.libdoc [options] library_or_resource list|show|version [names]

Options
~~~~~~~

  -f, --format <html|xml>  Specifies whether to generate HTML or XML output.
                           If this options is not used, the format is got
                           from the extension of the output file.
  -F, --docformat <robot|html|text|rest>
                           Specifies the source documentation format. Possible
                           values are Robot Framework's documentation format,
                           HTML, plain text, and reStructuredText. Default value
                           can be specified in test library source code and
                           the initial default value is `robot`.
                           New in Robot Framework 2.7.5.
  -N, --name <newname>     Sets the name of the documented library or resource.
  -V, --version <newversion>  Sets the version of the documented library or
                           resource. The default value for test libraries is
                           `got from the source code`__.
  -P, --pythonpath <path>  Additional locations where to search for libraries
                           and resources similarly as when `running tests`__.
  -E, --escape <what:with>  Escapes characters which are problematic in console.
                           `what` is the name of the character to escape
                           and `with` is the string to escape it with.
                           Available escapes are listed in the :option:`--help`
                           output.
  -h, --help               Prints this help.

__ `Specifying library version`_
__ `Using --pythonpath option`_

Alternative execution
~~~~~~~~~~~~~~~~~~~~~

Although Libdoc is used only with Python in the synopsis above, it works
also with Jython and IronPython. When documenting Java libraries, Jython is
actually required.

In the synopsis Libdoc is executed as an installed module
(`python -m robot.libdoc`). In addition to that, it can be run also as
a script::

    python path/robot/libdoc.py [options] arguments

Executing as a script can be useful if you have done `manual installation`_
or otherwise just have the :file:`robot` directory with the source code
somewhere in your system.

Specifying library or resource file
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Python libraries and dynamic libraries with name or path
''''''''''''''''''''''''''''''''''''''''''''''''''''''''

When documenting libraries implemented with Python or that use the
`dynamic library API`_, it is possible to specify the library either by
using just the library name or path to the library source code.
In the former case the library is searched using the `module search path`_
and its name must be in the same format as in Robot Framework test data.

If these libraries require arguments when they are imported, the arguments
must be catenated with the library name or path using two colons like
`MyLibrary::arg1::arg2`. If arguments change what keywords the library
provides or otherwise alter its documentation, it might be a good idea to use
:option:`--name` option to also change the library name accordingly.

Java libraries with path
''''''''''''''''''''''''

A Java test library implemented using the `static library API`_ can be
specified by giving the path to the source code file containing the
library implementation. Additionally, :file:`tools.jar`, which is part
of the Java JDK distribution, must be found from ``CLASSPATH`` when
Libdoc is executed. Notice that generating documentation for Java
libraries works only with Jython.

Resource files with path
''''''''''''''''''''''''

Resource files must always be specified using a path. If the path does
not exist, resource files are also searched from all directories in
the `module search path`_ similarly as when executing test cases.

Generating documentation
~~~~~~~~~~~~~~~~~~~~~~~~

When generating documentation in HTML or XML format, the output file must
be specified as the second argument after the library/resource name or path.
Output format is got automatically from the extension but can also be set
using the :option:`--format` option.

Examples::

   python -m robot.libdoc OperatingSystem OperatingSystem.html
   python -m robot.libdoc --name MyLibrary Remote::http://10.0.0.42:8270 MyLibrary.xml
   python -m robot.libdoc test/resource.html doc/resource_doc.html
   jython -m robot.libdoc --version 1.0 MyJavaLibrary.java MyJavaLibrary.html
   jython -m robot.libdoc my.organization.DynamicJavaLibrary my.organization.DynamicJavaLibrary.xml

Viewing information on console
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Libdoc has three special commands to show information on the console.
These commands are used instead of the name of the output file, and they can
also take additional arguments.

`list`
    List names of the keywords the library/resource contains. Can be
    limited to show only certain keywords by passing optional patterns
    as arguments. Keyword is listed if its name contains given pattern.
`show`
    Show library/resource documentation. Can be limited to show only
    certain keywords by passing names as arguments. Keyword is shown if
    its name matches any given name. Special argument `intro` will show
    only the library introduction and importing sections.
`version`
    Show library version

Optional patterns given to `list` and `show` are case and space
insensitive. Both also accept `*` and `?` as wildcards.

Examples::

  python -m robot.libdoc Dialogs list
  python -m robot.libdoc Selenium2Library list browser
  python -m robot.libdoc Remote::10.0.0.42:8270 show
  python -m robot.libdoc Dialogs show PauseExecution execute*
  python -m robot.libdoc Selenium2Library show intro
  python -m robot.libdoc Selenium2Library version

Writing documentation
---------------------

This section discusses writing documentation for Python__ and Java__ based test
libraries that use the static library API as well as for `dynamic libraries`_
and `resource files`__. `Creating test libraries`_ and `resource files`_ is
described in more details elsewhere in the User Guide.

__ `Python libraries`_
__ `Java libraries`_
__ `Resource file documentation`_

Python libraries
~~~~~~~~~~~~~~~~

The documentation for Python libraries that use the `static library API`_
is written simply as doc strings for the library class or module and for
methods implementing keywords. The first line of the method documentation is
considered as a short documentation for the keyword (used, for example, as
a tool tip in links in the generated HTML documentation), and it should
thus be as describing as possible, but not too long.

The simple example below illustrates how to write the documentation in
general, and there is a `bit longer example`__ at the end of this
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

            Examples:
            | Your Keyword | xxx |
            | Your Keyword | yyy |
            """
            pass

.. tip:: If you want to use non-ASCII charactes in the documentation of
         Python libraries, you must either use UTF-8 as your `source code
         encoding`__ or create docstrings as Unicode.

         For more information on Python documentation strings, see `PEP-257`__.

__ `Libdoc example`_
__ http://www.python.org/dev/peps/pep-0263
__ http://www.python.org/dev/peps/pep-0257

Java libraries
~~~~~~~~~~~~~~

Documentation for Java libraries that use the `static library API`_ is written
as normal `Javadoc comments`__ for the library class and methods. In this case
Libdoc actually uses the Javadoc tool internally, and thus
:file:`tools.jar` containing it must be in ``CLASSPATH``. This jar file is part
of the normal Java SDK distribution and ought to be found from :file:`bin`
directory under the Java SDK installation.

The following simple example has exactly same documentation (and functionality)
than the earlier Python example.

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
         * Examples:
         * | Your Keyword | xxx |
         * | Your Keyword | yyy |
         */
        public void yourKeyword(String arg) {
        }
    }

__ http://en.wikipedia.org/wiki/Javadoc

Dynamic libraries
~~~~~~~~~~~~~~~~~

To be able to generate meaningful documentation for dynamic libraries,
the libraries must return keyword argument names and documentation using
`get_keyword_arguments` and `get_keyword_documentation`
methods (or using their camelCase variants `getKeywordArguments`
and `getKeywordDocumentation`). Libraries can also support
general library documentation via special `__intro__` and
`__init__` values to the `get_keyword_documentation` method.

See the `Dynamic library API`_ section for more information about how to
create these methods.

Importing section
~~~~~~~~~~~~~~~~~

A separate section about how the library is imported is created based on its
initialization methods. For a Python library, if it has an  `__init__`
method that takes arguments in addition to `self`, its documentation and
arguments are shown. For a Java library, if it has a public constructor that
accepts arguments, all its public constructors are shown.

.. sourcecode:: python

   class TestLibrary:

       def __init__(self, mode='default')
           """Creates new TestLibrary. `mode` argument is used to determine mode."""
           self.mode = mode

       def some_keyword(self, arg):
           """Does something based on given `arg`.

           What is done depends on the `mode` specified when `importing` the library.
           """
           if self.mode == 'secret':
                # ...

Resource file documentation
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Keywords in resource files can have documentation using
:setting:`[Documentation]` setting, and this documentation is also used by
Libdoc. First line of the documentation (until the first
`implicit newline`__ or explicit `\n`) is considered to be the short
documentation similarly as with test libraries.

Also the resource file itself can have :setting:`Documentation` in the
Setting table for documenting the whole resource file.

Possible variables in resource files can not be documented.

.. sourcecode:: robotframework

   *** Settings ***
   Documentation    Resource file for demo purposes.
   ...              This resource is only used in an example and it doesn't do anything useful.

   *** Keywords ***
   My Keyword
       [Documentation]   Does nothing
       No Operation

   Your Keyword
       [Arguments]  ${arg}
       [Documentation]   Takes one argument and *does nothing* with it.
       ...
       ...    Examples:
       ...    | Your Keyword | xxx |
       ...    | Your Keyword | yyy |
       No Operation

__ `Newlines in test data`_

Documentation syntax
--------------------

Libdoc supports documentation in Robot Framework's own `documentation
syntax`_, HTML, plain text, and reStructuredText_. The format to use can be
specified in `test library source code`__ using `ROBOT_LIBRARY_DOC_FORMAT`
attribute or given from the command line using :option:`--docformat (-F)` option.
In both cases the possible case-insensitive values are `ROBOT` (default),
`HTML`, `TEXT` and `reST`.

Robot Framework's own documentation format is the default and generally
recommended format. Other formats are especially useful when using existing
code with existing documentation in test libraries. Support for other formats
was added in Robot Framework 2.7.5.

__ `Specifying documentation format`_

Robot Framework documentation syntax
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Most important features in Robot Framework's `documentation syntax`_ are
formatting using `*bold*` and `_italic_`, custom links and
automatic conversion of URLs to links, and the possibility to create tables and
pre-formatted text blocks (useful for examples) simply with pipe character.
If documentation gets longer, support for section titles (new in Robot
Framework 2.7.5) can also be handy.

Some of the most important formatting features are illustrated in the example
below. Notice that since this is the default format, there is no need to use
`ROBOT_LIBRARY_DOC_FORMAT` attribute nor give the format from the command
line.

.. sourcecode:: python

    """Example library in Robot Framework format.

    - Formatting with *bold* and _italic_.
    - URLs like http://example.com are turned to links.
    - Custom links like [http://robotframework.org|Robot Framework] are supported.
    - Linking to `My Keyword` works.
    """

    def my_keyword():
        """Nothing more to see here."""

HTML documentation syntax
~~~~~~~~~~~~~~~~~~~~~~~~~

When using HTML format, you can create documentation pretty much freely using
any syntax. The main drawback is that HTML markup is not that human friendly,
and that can make the documentation in the source code hard to maintain and read.
Documentation in HTML format is used by Libdoc directly without any
transformation or escaping. The special syntax for `linking to keywords`_ using
syntax like :codesc:`\`My Keyword\`` is supported, however.

Example below contains the same formatting examples as the previous example.
Now `ROBOT_LIBRARY_DOC_FORMAT` attribute must be used or format given
on the command line like `--docformat HTML`.

.. sourcecode:: python

    """Example library in HTML format.

    <ul>
      <li>Formatting with <b>bold</b> and <i>italic</i>.
      <li>URLs are not turned to links automatically.
      <li>Custom links like <a href="http://www.w3.org/html">HTML</a> are supported.
      <li>Linking to `My Keyword` works.
    </ul>
    """
    ROBOT_LIBRARY_DOC_FORMAT = 'HTML'

    def my_keyword():
        """Nothing more to see here."""

Plain text documentation syntax
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

When the plain text format is used, Libdoc uses the documentation as-is.
Newlines and other whitespace are preserved except for indentation, and
HTML special characters (`<>&`) escaped. The only formatting done is
turning URLs into clickable links and supporting `internal linking`_
like :codesc:`\`My Keyword\``.

.. sourcecode:: python

    """Example library in plain text format.

    - Formatting is not supported.
    - URLs like http://example.com are turned to links.
    - Custom links are not supported.
    - Linking to `My Keyword` works.
    """
    ROBOT_LIBRARY_DOC_FORMAT = 'text'

    def my_keyword():
        """Nothing more to see here"""

reStructuredText documentation syntax
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

reStructuredText_ is simple yet powerful markup syntax used widely in Python
projects (including this User Guide) and elsewhere. The main limitation
is that you need to have the docutils_ module installed to be able to generate
documentation using it. Because backtick characters have special meaning in
reStructuredText, `linking to keywords`_ requires them to be escaped like
:codesc:`\\\`My Keyword\\\``.

.. sourcecode:: python

    """Example library in reStructuredText format.

    - Formatting with **bold** and *italic*.
    - URLs like http://example.com are turned to links.
    - Custom links like reStructuredText__ are supported.
    - Linking to \`My Keyword\` works but requires backtics to be escaped.

    __ http://docutils.sourceforge.net
    """
    ROBOT_LIBRARY_DOC_FORMAT = 'reST'

    def my_keyword():
        """Nothing more to see here"""

.. _internal linking:

Internal linking
----------------

Libdoc supports internal linking to keywords and different
sections in the documentation. Linking is done by surrounding the
target name with backtick characters like :codesc:`\`target\``. Target
names are case-insensitive and possible targets are explained in the
subsequent sections.

There is no error or warning if a link target is not found, but instead Libdoc
just formats the text in italics. Earlier this formatting was recommended to
be used when referring to keyword arguments, but that was problematic because
it could accidentally create internal links. Nowadays it is recommended to
use `inline code style <inline styles_>`__ with double backticks like
:codesc:`\`\`argument\`\`` instead. The old formatting of single backticks
may even be removed in the future in favor of giving an error when a link
target is not found.

In addition to the examples in the following sections, internal linking
and argument formatting is shown also in the `longer example`__ at the
end of this chapter.

__ `Libdoc example`_

Linking to keywords
~~~~~~~~~~~~~~~~~~~

All keywords the library have automatically create link targets and they can
be linked using syntax :codesc:`\`Keyword Name\``. This is illustrated with
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

.. note:: When using `reStructuredText documentation syntax`_, backticks must
          be escaped like :codesc:`\\\`Keyword Name\\\``.

Linking to automatic sections
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The documentation generated by Libdoc always contains sections
for overall library introduction, shortcuts to keywords, and for
actual keywords.  If a library itself takes arguments, there is also
separate `importing section`_.

All these sections act as targets that can be linked, and the possible
target names are listed in the table below. Using these targets is
shown in the example of the next section.

.. table:: Automatic section link targets
   :class: tabular

   ================  ===========================================================
        Section                               Target
   ================  ===========================================================
   Introduction      :codesc:`\`introduction\`` and :codesc:`\`library introduction\``
   Importing         :codesc:`\`importing\`` and :codesc:`\`library importing\``
   Shortcuts         :codesc:`\`shortcuts\`` (New in Robot Framework 2.7.5.)
   Keywords          :codesc:`\`keywords\`` (New in Robot Framework 2.7.5.)
   ================  ===========================================================

Linking to custom sections
~~~~~~~~~~~~~~~~~~~~~~~~~~

Starting from version 2.7.5, Robot Framework's `documentation syntax`_
supports custom `section titles`_, and the titles used in the
library or resource file introduction automatically create link
targets. The example below illustrates linking both to automatic and
custom sections:

.. sourcecode:: python

   """Library for Libdoc demonstration purposes.

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

.. note:: Linking to custom sections works only when using `Robot Framework
          documentation syntax`_.

.. note:: Prior to Robot Framework 2.8, only the first level section
          titles were linkable.

Representing arguments
----------------------

Libdoc handles keywords' arguments automatically so that
arguments specified for methods in libraries or user keywords in
resource files are listed in a separate column. User keyword arguments
are shown without `${}` or `@{}` to make arguments look
the same regardless where keywords originated from.

Regardless how keywords are actually implemented, Libdoc shows arguments
similarly as when creating keywords in Python. This formatting is explained
more thoroughly in the table below.

.. table:: How Libdoc represents arguments
   :class: tabular

   +--------------------+----------------------------+------------------------+
   |      Arguments     |      Now represented       |        Examples        |
   +====================+============================+========================+
   | No arguments       | Empty column.              |                        |
   +--------------------+----------------------------+------------------------+
   | One or more        | List of strings containing | | `one_argument`       |
   | argument           | argument names.            | | `a1, a2, a3`         |
   +--------------------+----------------------------+------------------------+
   | Default values     | Default values separated   | | `arg=default value`  |
   | for arguments      | from names with `=`.       | | `a, b=1, c=2`        |
   +--------------------+----------------------------+------------------------+
   | Variable number    | Last (or second last with  | | `*varargs`           |
   | of arguments       | kwargs) argument has `*`   | | `a, b=42, *rest`     |
   | (varargs)          | before its name.           |                        |
   +--------------------+----------------------------+------------------------+
   | Free keyword       | Last arguments has         | | `**kwargs`           |
   | arguments (kwargs) | `**` before its name.      | | `a, b=42, **kws`     |
   |                    |                            | | `*varargs, **kwargs` |
   +--------------------+----------------------------+------------------------+

When referring to arguments in keyword documentation, it is recommended to
use `inline code style <inline styles_>`__ like :codesc:`\`\`argument\`\``.

Libdoc example
--------------

The following example illustrates how to use the most important
`documentation formatting`_ possibilities, `internal linking`_, and so
on. `Click here`__ to see how the generated documentation looks like.

.. sourcecode:: python

   src/SupportingTools/LoggingLibrary.py

All `standard libraries`_ have documentation generated by
Libdoc and their documentation (and source code) act as a more
realistic examples.

__ src/SupportingTools/LoggingLibrary.html
