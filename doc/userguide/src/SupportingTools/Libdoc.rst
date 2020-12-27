.. _libdoc:

Library documentation tool (Libdoc)
===================================

.. contents::
   :depth: 1
   :local:

Libdoc is Robot Framework's built-in tool that can generate documentation for
Robot Framework libraries and resource files. It can generate HTML documentation
for humans as well as machine readable spec files in XML and JSON formats.
Libdoc also has few special commands to show library or resource information
on the console.

Documentation can be created for:

- libraries implemented with Python__ or Java__ using the normal
  static library API,
- libraries using the `dynamic API`__, including remote libraries, and
- `resource files`_.

Additionally it is possible to use XML and JSON spec files created by Libdoc
earlier as an input.

.. note:: The support for the JSON spec files is new in Robot Framework 4.0.

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

  -f, --format <html|xml|json|libspec>
                           Specifies whether to generate an HTML output for humans or
                           a machine readable spec file in XML or JSON format. The
                           `libspec` format means XML spec with documentations converted
                           to HTML. The default format is got from the output file
                           extension.
  -s, --specdocformat <raw|html>
                           Specifies the documentation format used with XML and JSON
                           spec files. `raw` means preserving the original documentation
                           format and `html` means converting documentation to HTML. The
                           default is `raw` with XML spec files and `html` with JSON
                           specs and when using the special `libspec` format.
                           New in Robot Framework 4.0.
  -F, --docformat <robot|html|text|rest>
                           Specifies the source documentation format. Possible
                           values are Robot Framework's documentation format,
                           HTML, plain text, and reStructuredText. Default value
                           can be specified in test library source code and
                           the initial default value is `robot`.
  -N, --name <newname>     Sets the name of the documented library or resource.
  -V, --version <newversion>  Sets the version of the documented library or
                           resource. The default value for test libraries is
                           `defined in the source code`__.
  -P, --pythonpath <path>  Additional locations where to search for libraries
                           and resources similarly as when `running tests`__.
  --quiet                  Do not print the path of the generated output file
                           to the console. New in Robot Framework 4.0.
  -h, --help               Prints this help.

__ `Library version`_
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
library implementation. When using Java 9 or newer, documentation can be
generated without external dependencies, but with older Java versions the
:file:`tools.jar`, which is part of the Java JDK distribution, must be found
from the ``CLASSPATH`` when Libdoc is executed. Notice that generating
documentation for Java libraries works only with Jython.

.. note:: Generating documentation without :file:`tools.jar` when using
          Java 9 or newer is a new feature in Robot Framework 3.1.

Resource files with path
''''''''''''''''''''''''

Resource files must always be specified using a path. If the path does
not exist, resource files are also searched from all directories in
the `module search path`_ similarly as when executing test cases.

Libdoc spec files
'''''''''''''''''

Earlier generated Libdoc XML or JSON spec files can also be used as inputs.
This works if spec files use either :file:`*.xml`, :file:`*.libspec` or
:file:`*.json` extension::

   python -m robot.libdoc Example.xml Example.html
   python -m robot.libdoc Example.libspec Example.html
   python -m robot.libdoc Example.json Example.html

.. note:: Support for the :file:`*.libspec` extension is new in
          Robot Framework 3.2.

.. note:: Support for the :file:`*.json` extension is new in
          Robot Framework 4.0.

Generating documentation
~~~~~~~~~~~~~~~~~~~~~~~~

Libdoc can generate documentation in HTML (for humans) and XML or JSON (for tools)
formats. The file where to write the documentation is specified as the second
argument after the library/resource name or path, and the output format is
got from the output file extension by default.

Libdoc HTML documentation
'''''''''''''''''''''''''

Most Robot Framework libraries use Libdoc to generate library documentation
in HTML format. This format is thus familiar for most people who have used
Robot Framework. A simple example can be seen below, and it has been generated
based on the example found a `bit later in this section`__.

.. figure:: src/SupportingTools/ExampleLibrary.png
   :target: src/SupportingTools/ExampleLibrary.html
   :width: 581

The HTML documentation starts with general library introduction, continues
with a section about configuring the library when it is imported (when
applicable), and finally has shortcuts to all keywords and the keywords
themselves. The magnifying glass icon on the lower right corner opens the
keyword search dialog that can also be opened by simply pressing the `s` key.

Libdoc automatically creates HTML documentation if the output file extension
is :file:`*.html`. If there is a need to use some other extension, the
format can be specified explicitly with the :option:`--format` option.

::

   python -m robot.libdoc OperatingSystem OperatingSystem.html
   python -m robot.libdoc --name MyLibrary Remote::http://10.0.0.42:8270 MyLibrary.html
   python -m robot.libdoc --format HTML test/resource.robot doc/resource.htm

__ `Python libraries`_

Libdoc XML spec files
'''''''''''''''''''''

Libdoc can also generate documentation in XML format that is suitable for
external tools such as editors. It contains all the same information as
the HTML format but in a machine readable format.

XML spec files also contain library and keyword source information so that
the library and each keyword can have source path (`source` attribute) and
line number (`lineno` attribute). The source path is relative to the directory
where the spec file is generated thus does not refer to a correct file if
the spec is moved. The source path is omitted with keywords if it is
the same as with the library, and both the source path and the line number
are omitted if getting them from the library fails for whatever reason.

Libdoc automatically uses the XML format if the output file extension is
:file:`*.xml` or :file:`*.libspec`. When using the special :file:`*.libspec`
extension, Libdoc automatically enables the options `-f XML -s HTML` which means
creating an XML output file where keyword documentation is converted to HTML.
If needed, the format can be explicitly set with the :option:`--format` option.

::

   python -m robot.libdoc OperatingSystem OperatingSystem.xml
   python -m robot.libdoc test/resource.robot doc/resource.libspec
   python -m robot.libdoc --format xml MyLibrary MyLibrary.spec
   python -m robot.libdoc --format xml -s html MyLibrary MyLibrary.xml

The exact Libdoc spec file format is documented with an `XML schema`__ (XSD)
at https://github.com/robotframework/robotframework/tree/master/doc/schema.
The spec file format may change between Robot Framework major releases.

To make it easier for external tools to know how to parse a certain
spec file, the spec file root element has a dedicated `specversion`
attribute. It was added in Robot Framework 3.2 with value `2` and earlier
spec files can be considered to have version `1`. The spec version will
be incremented in the future if and when changes are made.
Robot Framework 4.0 introduced new spec version `3` which is incompatible
with earlier versions.

.. note:: The `XML:HTML` format introduced in Robot Framework 3.2. has been
          replaced by the format `LIBSPEC` ot the option combination
          `--format XML --specdocformat HTML`.

.. note:: Including source information and spec version are new in Robot
          Framework 3.2.

__ https://en.wikipedia.org/wiki/XML_Schema_(W3C)

Libdoc JSON spec files
''''''''''''''''''''''

Since Robot Framework 4.0 Libdoc can also generate documentation in JSON
format that is suitable for external tools such as editors or web pages.
It contains all the same information as the HTML format but in a machine
readable format.

Similar to XML spec files the JSON spec files contain all information and
can also be used as input to Libdoc. From that format any other output format
can be created. By default the library documentation strings are converted
to HTML format within the JSON output file.

The exact JSON spec file format is documented with an `JSON schema`__
at https://github.com/robotframework/robotframework/tree/master/doc/schema.
The spec file format may change between Robot Framework major releases.

__ https://json-schema.org/

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
  python -m robot.libdoc SeleniumLibrary list browser
  python -m robot.libdoc Remote::10.0.0.42:8270 show
  python -m robot.libdoc Dialogs show PauseExecution execute*
  python -m robot.libdoc SeleniumLibrary show intro
  python -m robot.libdoc SeleniumLibrary version

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
general. How the HTML documentation generated based on this example looks
like can be seen above__, and there is also a `bit longer example`__ at
the end of this chapter.

.. sourcecode:: python

    src/SupportingTools/ExampleLibrary.py

If you want to use non-ASCII characters in the documentation, the documentation
must either be Unicode string (default in Python 3) or UTF-8 encoded bytes.

.. tip:: When using Python 2, you it is a good idea to set the
         `source code encoding`__ to ease using non-ASCII characters.

         For more information on Python documentation strings, see `PEP-257`__.

__ `Libdoc HTML documentation`_
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
    public class ExampleLibrary {

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
specified in `library source code`__ using `ROBOT_LIBRARY_DOC_FORMAT`
attribute or given from the command line using :option:`--docformat (-F)` option.
In both cases the possible case-insensitive values are `ROBOT` (default),
`HTML`, `TEXT` and `reST`.

Robot Framework's own documentation format is the default and generally
recommended format. Other formats are especially useful when using existing
code with existing documentation in test libraries.

__ `Documentation format`_

Robot Framework documentation syntax
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Most important features in Robot Framework's `documentation syntax`_ are
formatting using `*bold*` and `_italic_`, custom links and
automatic conversion of URLs to links, and the possibility to create tables and
pre-formatted text blocks (useful for examples) simply with pipe character.
If documentation gets longer, support for section titles can also be handy.

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

Creating table of contents automatically
''''''''''''''''''''''''''''''''''''''''

With bigger libraries it is often useful to add a table of contents to
the library introduction. When using the Robot Framework documentation format,
this can be done automatically by adding a special `%TOC%` marker into a line
on its own. The table of contents is created based on the top-level
`section titles`_ (e.g. `= Section =`) used in the introduction. In addition
to them, the TOC also gets links to the `automatically created sections`__
for shortcuts and keywords as well as for importing and tags sections when
applicable.

.. sourcecode:: python

    """Example library demonstrating TOC generation.

    The %TOC% marker only creates the actual table of contents and possible
    header or other explanation needs to be added separately like done below.

    == Table of contents ==

    %TOC%

    = Section title =

    The top-level section titles are automatically added to the TOC.

    = Second section =

    == Sub section ==

    Sub section titles are not added to the TOC.
    """

    def my_keyword():
        """Nothing more to see here."""

.. note:: Automatic TOC generation is a new feature in Robot Framework 3.2.

__ `Linking to automatic sections`_

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
        """Nothing more to see here."""

reStructuredText documentation syntax
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

reStructuredText_ is simple yet powerful markup syntax used widely in Python
projects (including this User Guide) and elsewhere. The main limitation
is that you need to have the docutils_ module installed to be able to generate
documentation using it. Because backtick characters have special meaning in
reStructuredText, `linking to keywords`_ requires them to be escaped like
:codesc:`\\\`My Keyword\\\``.

One of the nice features that reStructured supports is the ability to mark code
blocks that can be syntax highlighted. The code block syntax has always worked
with Robot Framework, but they are highlighted only in RF 3.0.1 and newer.
Syntax highlight requires additional Pygments_ module and supports all the
languages that Pygments supports.

.. sourcecode:: python

    """Example library in reStructuredText format.

    - Formatting with **bold** and *italic*.
    - URLs like http://example.com are turned to links.
    - Custom links like reStructuredText__ are supported.
    - Linking to \`My Keyword\` works but requires backtics to be escaped.

    __ http://docutils.sourceforge.net

    .. code:: robotframework

        *** Test Cases ***
        Example
            My keyword    # How cool is this!!?!!?!1!!
    """
    ROBOT_LIBRARY_DOC_FORMAT = 'reST'

    def my_keyword():
        """Nothing more to see here."""

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
for overall library introduction and for
keywords.  If a library itself takes arguments, there is also
separate `importing section`_. If any of the keywords has tags__,
a separate selector for them is also shown in the overview.

All the sections act as targets that can be linked, and the possible
target names are listed in the table below. Using these targets is
shown in the example of the next section.

.. table:: Automatic section link targets
   :class: tabular

   ================  ===========================================================
        Section                               Target
   ================  ===========================================================
   Introduction      :codesc:`\`introduction\`` and :codesc:`\`library introduction\``
   Importing         :codesc:`\`importing\`` and :codesc:`\`library importing\``
   Keywords          :codesc:`\`keywords\``
   ================  ===========================================================

.. note:: Before Robot Framework 4.0 there were also sections for tags and shortcuts.
          In Robot Framework 4.0 these have been removed in favor of the overview menu. This means
          that prior linking to shortcuts or tags sections does not work.

__ `Keyword tags`_

Linking to custom sections
~~~~~~~~~~~~~~~~~~~~~~~~~~

Robot Framework's `documentation syntax`_
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
