Test data syntax
================

This section covers Robot Framework's overall test data
syntax. The following sections will explain how to actually create test
cases, test suites and so on.

.. contents::
   :depth: 2
   :local:

Files and directories
---------------------

The hierarchical structure for arranging test cases is built as follows:

- Test cases are created in `test case files`_.
- A test case file automatically creates a `test suite`_ containing
  the test cases in that file.
- A directory containing test case files forms a higher-level test
  suite. Such a `test suite directory`_ has suites created from test
  case files as its sub test suites.
- A test suite directory can also contain other test suite directories,
  and this hierarchical structure can be as deeply nested as needed.
- Test suite directories can have a special `initialization file`_.

In addition to this, there are:

- `Test libraries`_ containing the lowest-level keywords.
- `Resource files`_ with variables_ and higher-level `user keywords`_.
- `Variable files`_ to provide more flexible ways to create variables
  than resource files.

Supported file formats
----------------------

Robot Framework test data is defined in tabular format, using either
hypertext markup language (HTML), tab-separated values (TSV),
plain text, or reStructuredText (reST) formats. The details of these
formats, as well as the main benefits and problems with them, are explained
in the subsequent sections. Which format to use depends on the context,
but the plain text format is recommended if there are no special needs.

Robot Framework selects a parser for the test data based on the file extension.
The extension is case-insensitive, and the recognized extensions are
:file:`.html`, :file:`.htm` and :file:`.xhtml` for HTML, :file:`.tsv`
for TSV, :file:`.txt` and special :file:`.robot` for plain text, and
:file:`.rst` and :file:`.rest` for reStructuredText.

Different `test data templates`_ are available for HTML and TSV
formats to make it easier to get started writing tests.

.. note:: The special :file:`.robot` extension with plain text files is
          supported starting from Robot Framework 2.7.6.

HTML format
~~~~~~~~~~~

HTML files support formatting and free text around tables. This makes it
possible to add additional information into test case files and allows creating
test case files that look like formal test specifications. The main problem
with HTML format is that editing these files using normal text editors is not
that easy. Another problem is that HTML does not work as well with version
control systems because the diffs resulting from changes contain HTML syntax
in addition to changes to the actual test data.

In HTML files, the test data is defined in separate tables (see the
example below). Robot Framework recognizes these `test data tables`_
based on the text in their first cell. Everything outside recognized
tables is ignored.

.. table:: Using the HTML format
   :class: example

   ============  ================  =======  =======
      Setting          Value        Value    Value
   ============  ================  =======  =======
   Library       OperatingSystem
   \
   ============  ================  =======  =======

.. table::
   :class: example

   ============  ================  =======  =======
     Variable        Value          Value    Value
   ============  ================  =======  =======
   ${MESSAGE}    Hello, world!
   \
   ============  ================  =======  =======

.. table::
   :class: example

   ============  ===================  ============  =============
    Test Case           Action          Argument      Argument
   ============  ===================  ============  =============
   My Test       [Documentation]      Example test
   \             Log                  ${MESSAGE}
   \             My Keyword           /tmp
   \
   Another Test  Should Be Equal      ${MESSAGE}    Hello, world!
   ============  ===================  ============  =============

.. table::
   :class: example

   ============  ======================  ============  ==========
     Keyword            Action             Argument     Argument
   ============  ======================  ============  ==========
   My Keyword    [Arguments]             ${path}
   \             Directory Should Exist  ${path}
   ============  ======================  ============  ==========

Editing test data
'''''''''''''''''

Test data in HTML files can be edited with whichever editor you
prefer, but a graphic editor, where you can actually see the tables,
is recommended. RIDE_ can read and write HTML files, but unfortunately
it loses all HTML formatting and also possible data outside test case
tables.

Encoding and entity references
''''''''''''''''''''''''''''''

HTML entity references (for example, `&auml;`) are
supported. Additionally, any encoding can be used, assuming that it is
specified in the data file. Normal HTML files must use the META
element as in the example below::

  <meta http-equiv="Content-Type" content="text/html; charset=UTF-8">

XHTML files should use the XML preamble as in this example::

  <?xml version="1.0" encoding="Big5"?>

If no encoding is specified, Robot Framework uses ISO-8859-1 by default.

TSV format
~~~~~~~~~~

TSV files can be edited in spreadsheet programs and, because the syntax is
so simple, they are easy to generate programmatically. They are also pretty
easy to edit using normal text editors and they work well in version control,
but the `plain text format`_ is even better suited for these purposes.

The TSV format can be used in Robot Framework's test data for all the
same purposes as HTML. In a TSV file, all the data is in one large
table. `Test data tables`_ are recognized from one or more asterisks
(`*`), followed by a normal table name and an optional closing
asterisks.  Everything before the first recognized table is ignored
similarly as data outside tables in HTML data.

.. table:: Using the TSV format
   :class: tsv-example

   ============  =======================  =============  =============
   \*Setting*    \*Value*                 \*Value*       \*Value*
   Library       OperatingSystem
   \
   \
   \*Variable*   \*Value*                 \*Value*       \*Value*
   ${MESSAGE}    Hello, world!
   \
   \
   \*Test Case*  \*Action*                \*Argument*    \*Argument*
   My Test       [Documentation]          Example test
   \             Log                      ${MESSAGE}
   \             My Keyword               /tmp
   \
   Another Test  Should Be Equal          ${MESSAGE}     Hello, world!
   \
   \
   \*Keyword*    \*Action*                \*Argument*    \*Argument*
   My Keyword    [Arguments]              ${path}
   \             Directory Should Exist   ${path}
   ============  =======================  =============  =============

Editing test data
'''''''''''''''''

You can create and edit TSV files in any spreadsheet program, such as
Microsoft Excel. Select the tab-separated format when you save the
file and remember to set the file extension to :file:`.tsv`. It is
also a good idea to turn all automatic corrections off and configure
the tool to treat all values in the file as plain text.

TSV files are relatively easy to edit with any text editor,
especially if the editor supports visually separating tabs from
spaces. The TSV format is also supported by RIDE_.

Robot Framework parses TSV data by first splitting all the content
into rows and then rows into cells on the basis of the tabular
characters. Spreadsheet programs sometimes surround cells with quotes
(for example, `"my value"`) and Robot Framework removes
them. Possible quotes inside the data are doubled (for example,
`"my ""quoted"" value"`) and also this is handled correctly.  If
you are using a spreadsheet program to create TSV data, you should not
need to pay attention to this, but if you create data
programmatically, you have to follow the same quoting conventions as
spreadsheets.

Encoding
''''''''

TSV files are always expected to use UTF-8 encoding. Because ASCII is
a subset of UTF-8, plain ASCII is naturally supported too.

Plain text format
~~~~~~~~~~~~~~~~~

The plain texts format is very easy to edit using any text editor and
they also work very well in version control. Because of these benefits
it has became the most used data format with Robot Framework.

The plain text format is technically otherwise similar to the `TSV
format`_ but the separator between the cells is different. The TSV
format uses tabs, but in the plain text format you can use either two
or more spaces or a pipe character surrounded with spaces (:codesc:`\ |\ `).

The `test data tables`_ must have one or more asterisk before their
names similarly as in the TSV format. Otherwise asterisks and possible
spaces in the table header are ignored so, for example, `***
Settings ***` and `*Settings` work the same way. Also similarly
as in the TSV format, everything before the first table is ignored.

In plain text files tabs are automatically converted to two
spaces. This allows using a single tab as a separator similarly as in
the TSV format. Notice, however, that in the plain text format
multiple tabs are considered to be a single separator whereas in the
TSV format every tab would be a separator.

Space separated format
''''''''''''''''''''''

The number of spaces used as separator can vary, as long as there are
at least two spaces, and it is thus possible to align the data nicely.
This is a clear benefit over editing the TSV format in a text editor
because with TSV the alignment cannot be controlled.

.. sourcecode:: robotframework

   *** Settings ***
   Library       OperatingSystem

   *** Variables ***
   ${MESSAGE}    Hello, world!

   *** Test Cases ***
   My Test
       [Documentation]    Example test
       Log    ${MESSAGE}
       My Keyword    /tmp

   Another Test
       Should Be Equal    ${MESSAGE}    Hello, world!

   *** Keywords ***
   My Keyword
       [Arguments]    ${path}
       Directory Should Exist    ${path}

Because space is used as separator, all empty cells must be escaped__
with `${EMPTY}` variable or a single backslash. Otherwise
`handling whitespace`_ is not different than in other test data
because leading, trailing, and consecutive spaces must always be
escaped.

__ Escaping_

.. tip:: It is recommend to use four spaces between keywords and arguments.

.. _pipe separated format:

Pipe and space separated format
'''''''''''''''''''''''''''''''

The biggest problem of the space delimited format is that visually
separating keywords form arguments can be tricky. This is a problem
especially if keywords take a lot of arguments and/or arguments
contain spaces. In such cases the pipe and space delimited variant can
work better because it makes the cell boundary more visible.

.. sourcecode:: robotframework

   | *Setting*  |     *Value*     |
   | Library    | OperatingSystem |

   | *Variable* |     *Value*     |
   | ${MESSAGE} | Hello, world!   |

   | *Test Case*  | *Action*        | *Argument*   |
   | My Test      | [Documentation] | Example test |
   |              | Log             | ${MESSAGE}   |
   |              | My Keyword      | /tmp         |
   | Another Test | Should Be Equal | ${MESSAGE}   | Hello, world!

   | *Keyword*  |
   | My Keyword | [Arguments] | ${path}
   |            | Directory Should Exist | ${path}

A plain text file can contain test data in both space-only and
space-and-pipe separated formats, but a single line must always use
the same separator. Pipe and space separated lines are recognized by
the mandatory leading pipe, but the pipe at the end of the line is
optional. There must always be at least one space on both sides of the
pipe (except at the beginning and end) but there is no need to align
the pipes other than if it makes the data more clear.

There is no need to escape empty cells (other than the `trailing empty
cells`__) when using the pipe and space separated format. The only
thing to take into account is that possible pipes surrounded by spaces
in the actual test data must be escaped with a backslash:

.. sourcecode:: robotframework

   | *** Test Cases *** |                 |                 |                      |
   | Escaping Pipe      | ${file count} = | Execute Command | ls -1 *.txt \| wc -l |
   |                    | Should Be Equal | ${file count}   | 42                   |

__ Escaping_

Editing and encoding
''''''''''''''''''''

One of the biggest benefit of the plain text format over HTML and TSV
is that editing it using normal text editors is very easy. Many editors
and IDEs (at least Eclipse, Emacs, Vim, and TextMate) also have plugins that
support syntax highlighting Robot Framework test data and may also provide
other features such as keyword completion. The plain text format is also
supported by RIDE_.

Similarly as with the TSV test data, plain text files are always expected
to use UTF-8 encoding. As a consequence also ASCII files are supported.

Recognized extensions
'''''''''''''''''''''

Starting from Robot Framework 2.7.6, it is possible to save plain text
test data files using a special :file:`.robot` extension in addition to
the normal :file:`.txt` extension. The new extension makes it easier to
distinguish test data files from other plain text files.

reStructuredText format
~~~~~~~~~~~~~~~~~~~~~~~

reStructuredText_ (reST) is an easy-to-read plain text markup syntax that
is commonly used for documentation of Python projects (including
Python itself, as well as this User Guide). reST documents are most
often compiled to HTML, but also other output formats are supported.

Using reST with Robot Framework allows you to mix richly formatted documents
and test data in a concise text format that is easy to work with
using simple text editors, diff tools, and source control systems.
In practice it combines many of the benefits of plain text and HTML formats.

When using reST files with Robot Framework, there are two ways to define the
test data. Either you can use `code blocks`__ and define test cases in them
using the `plain text format`_ or alternatively you can use tables__ exactly
like you would with the `HTML format`_.

.. note:: Using reST files with Robot Framework requires the Python docutils_
          module to be installed.

__ `Using code blocks`_
__ `Using tables`_

Using code blocks
'''''''''''''''''

reStructuredText documents can contain code examples in so called code blocks.
When these documents are compiled into HTML or other formats, the code blocks
are syntax highlighted using Pygments_. In standard reST code blocks are
started using the `code` directive, but Sphinx_ uses `code-block`
or `sourcecode` instead. The name of the programming language in
the code block is given as an argument to the directive. For example, following
code blocks contain Python and Robot Framework examples, respectively:

.. sourcecode:: rest

    .. code:: python

       def example_keyword():
           print 'Hello, world!'

    .. code:: robotframework

       *** Test Cases ***
       Example Test
           Example Keyword

When Robot Framework parses reStructuredText files, it first searches for
possible `code`, `code-block` or `sourcecode` blocks
containing Robot Framework test data. If such code blocks are found, data
they contain is written into an in-memory file and executed. All data outside
the code blocks is ignored.

The test data in the code blocks must be defined using the `plain text format`_.
As the example below illustrates, both space and pipe separated variants are
supported:

.. sourcecode:: rest

    Example
    -------

    This text is outside code blocks and thus ignored.

    .. code:: robotframework

       *** Settings ***
       Library       OperatingSystem

       *** Variables ***
       ${MESSAGE}    Hello, world!

       *** Test Cases ***
       My Test
           [Documentation]    Example test
           Log    ${MESSAGE}
           My Keyword    /tmp

       Another Test
           Should Be Equal    ${MESSAGE}    Hello, world!

    Also this text is outside code blocks and ignored. Above block used
    the space separated plain text format and the block below uses the pipe
    separated variant.

    .. code:: robotframework

       | *** Keyword ***  |                        |         |
       | My Keyword       | [Arguments]            | ${path} |
       |                  | Directory Should Exist | ${path} |

.. note:: Escaping_ using the backslash character works normally in this format.
          No double escaping is needed like when using reST tables.

.. note:: Support for test data in code blocks is a new feature in
          Robot Framework 2.8.2.

Using tables
''''''''''''

If a reStructuredText document contains no code blocks with Robot Framework
data, it is expected to contain the data in tables similarly as in
the `HTML format`_. In this case Robot Framework compiles the document to
HTML in memory and parses it exactly like it would parse a normal HTML file.

Robot Framework identifies `test data tables`_ based on the text in the first
cell and all content outside of the recognized table types is ignored.
An example of each of the four test data tables is shown below
using both simple table and grid table syntax:

.. sourcecode:: rest

    Example
    -------

    This text is outside tables and thus ignored.

    ============  ================  =======  =======
      Setting          Value         Value    Value
    ============  ================  =======  =======
    Library       OperatingSystem
    ============  ================  =======  =======


    ============  ================  =======  =======
      Variable         Value         Value    Value
    ============  ================  =======  =======
    ${MESSAGE}    Hello, world!
    ============  ================  =======  =======


    =============  ==================  ============  =============
      Test Case          Action          Argument      Argument
    =============  ==================  ============  =============
    My Test        [Documentation]     Example test
    \              Log                 ${MESSAGE}
    \              My Keyword          /tmp
    \
    Another Test   Should Be Equal     ${MESSAGE}    Hello, world!
    =============  ==================  ============  =============

    Also this text is outside tables and ignored. Above tables are created
    using the simple table syntax and the table below uses the grid table
    approach.

    +-------------+------------------------+------------+------------+
    |   Keyword   |         Action         |  Argument  |  Argument  |
    +-------------+------------------------+------------+------------+
    | My Keyword  | [Arguments]            | ${path}    |            |
    +-------------+------------------------+------------+------------+
    |             | Directory Should Exist | ${path}    |            |
    +-------------+------------------------+------------+------------+

.. note:: Empty cells in the first column of simple tables need to be escaped.
          The above example uses :codesc:`\\` but `..` could also be used.

.. note:: Because the backslash character is an escape character in reST,
          specifying a backslash so that Robot Framework will see it requires
          escaping it with an other backslash like `\\`. For example,
          a new line character must be written like `\\n`. Because
          the backslash is used for escaping_ also in Robot Framework data,
          specifying a literal backslash when using reST tables requires double
          escaping like `c:\\\\temp`.

Generating HTML files based on reST files every time tests are run obviously
adds some overhead. If this is a problem, it can be a good idea to convert
reST files to HTML using external tools separately, and let Robot Framework
use the generated files only.

Editing and encoding
''''''''''''''''''''

Test data in reStructuredText files can be edited with any text editor, and
many editors also provide automatic syntax highlighting for it. reST format
is not supported by RIDE_, though.

Robot Framework requires reST files containing non-ASCII characters to be
saved using UTF-8 encoding.

Syntax errors in reST source files
''''''''''''''''''''''''''''''''''

If a reStructuredText document is not syntactically correct (a malformed table
for example), parsing it will fail and no test cases can be found from that
file. When executing a single reST file, Robot Framework will show the error
on the console. When executing a directory, such parsing errors will
generally be ignored.

Starting from Robot Framework 2.9.2, errors below level `SEVERE` are ignored
when running tests to avoid noise about non-standard directives and other such
markup. This may hide also real errors, but they can be seen when processing
files normally.

Test data tables
----------------

Test data is structured in four types of tables listed below. These
test data tables are identified by the first cell of the table. Recognized
table names are `Settings`, `Variables`, `Test Cases`, and `Keywords`. Matching
is case-insensitive and also singular variants like `Setting` and `Test Case`
are accepted.

.. table:: Different test data tables
   :class: tabular

   +--------------+--------------------------------------------+
   |    Table     |                 Used for                   |
   +==============+============================================+
   | Settings     | | 1) Importing `test libraries`_,          |
   |              |   `resource files`_ and `variable files`_. |
   |              | | 2) Defining metadata for `test suites`_  |
   |              |   and `test cases`_.                       |
   +--------------+--------------------------------------------+
   | Variables    | Defining variables_ that can be used       |
   |              | elsewhere in the test data.                |
   +--------------+--------------------------------------------+
   | Test Cases   | `Creating test cases`_ from available      |
   |              | keywords.                                  |
   +--------------+--------------------------------------------+
   | Keywords     | `Creating user keywords`_ from existing    |
   |              | lower-level keywords                       |
   +--------------+--------------------------------------------+

Rules for parsing the data
--------------------------

.. _comment:

Ignored data
~~~~~~~~~~~~

When Robot Framework parses the test data, it ignores:

- All tables that do not start with a `recognized table name`__ in the first cell.
- Everything else on the first row of a table apart from the first cell.
- All data before the first table. If the data format allows data between
  tables, also that is ignored.
- All empty rows, which means these kinds of rows can be used to make
  the tables more readable.
- All empty cells at the end of rows, unless they are escaped__.
- All single backslashes (:codesc:`\\`) when not used for escaping_.
- All characters following the hash character (`#`), when it is the first
  character of a cell. This means that hash marks can be used to enter
  comments in the test data.
- All formatting in the HTML/reST test data.

When Robot Framework ignores some data, this data is not available in
any resulting reports and, additionally, most tools used with Robot
Framework also ignore them. To add information that is visible in
Robot Framework outputs, place it to the documentation or other metadata of
test cases or suites, or log it with the BuiltIn_ keywords :name:`Log` or
:name:`Comment`.

__ `Test data tables`_
__ `Prevent ignoring empty cells`_

Handling whitespace
~~~~~~~~~~~~~~~~~~~

Robot Framework handles whitespace the same way as they are handled in HTML
source code:

- Newlines, carriage returns, and tabs are converted to spaces.
- Leading and trailing whitespace in all cells is ignored.
- Multiple consecutive spaces are collapsed into a single space.

In addition to that, non-breaking spaces are replaced with normal spaces.
This is done to avoid hard-to-debug errors
when a non-breaking space is accidentally used instead of a normal space.

If leading, trailing, or consecutive spaces are needed, they `must be
escaped`__. Newlines, carriage returns, tabs, and non-breaking spaces can be
created using `escape sequences`_ `\n`, `\r`, `\t`, and `\xA0` respectively.

__ `Prevent ignoring spaces`_

Escaping
~~~~~~~~

The escape character in Robot Framework test data is the backslash
(:codesc:`\\`) and additionally `built-in variables`_ `${EMPTY}` and `${SPACE}`
can often be used for escaping. Different escaping mechanisms are
discussed in the sections below.

Escaping special characters
'''''''''''''''''''''''''''

The backslash character can be used to escape special characters
so that their literal values are used.

.. table:: Escaping special characters
   :class: tabular

   ===========  ================================================================  ==============================
    Character                              Meaning                                           Examples
   ===========  ================================================================  ==============================
   `\$`         Dollar sign, never starts a `scalar variable`_.                   `\${notvar}`
   `\@`         At sign, never starts a `list variable`_.                         `\@{notvar}`
   `\%`         Percent sign, never starts an `environment variable`_.            `\%{notvar}`
   `\#`         Hash sign, never starts a comment_.                               `\# not comment`
   `\=`         Equal sign, never part of `named argument syntax`_.               `not\=named`
   `\|`         Pipe character, not a separator in the `pipe separated format`_.  `| Run | ps \| grep xxx |`
   `\\`         Backslash character, never escapes anything.                      `c:\\temp, \\${var}`
   ===========  ================================================================  ==============================

.. _escape sequence:
.. _escape sequences:

Forming escape sequences
''''''''''''''''''''''''

The backslash character also allows creating special escape sequences that are
recognized as characters that would otherwise be hard or impossible to create
in the test data.

.. table:: Escape sequences
   :class: tabular

   =============  ====================================  ============================
      Sequence                  Meaning                           Examples
   =============  ====================================  ============================
   `\n`           Newline character.                    `first line\n2nd line`
   `\r`           Carriage return character             `text\rmore text`
   `\t`           Tab character.                        `text\tmore text`
   `\xhh`         Character with hex value `hh`.        `null byte: \x00, ä: \xE4`
   `\uhhhh`       Character with hex value `hhhh`.      `snowman: \u2603`
   `\Uhhhhhhhh`   Character with hex value `hhhhhhhh`.  `love hotel: \U0001f3e9`
   =============  ====================================  ============================

.. note:: All strings created in the test data, including characters like
          `\x02`, are Unicode and must be explicitly converted to
          byte strings if needed. This can be done, for example, using
          :name:`Convert To Bytes` or :name:`Encode String To Bytes` keywords
          in BuiltIn_ and String_ libraries, respectively, or with
          something like `str(value)` or `value.encode('UTF-8')`
          in Python code.

.. note:: If invalid hexadecimal values are used with `\x`, `\u`
          or `\U` escapes, the end result is the original value without
          the backslash character. For example, `\xAX` (not hex) and
          `\U00110000` (too large value) result with `xAX`
          and `U00110000`, respectively. This behavior may change in
          the future, though.

.. note:: `Built-in variable`_ `${\n}` can be used if operating system
          dependent line terminator is needed (`\r\n` on Windows and
          `\n` elsewhere).

.. note:: Possible un-escaped whitespace character after the `\n` is
          ignored. This means that `two lines\nhere` and
          `two lines\n here` are equivalent. The motivation for this
          is to allow wrapping long lines containing newlines when using
          the HTML format, but the same logic is used also with other formats.
          An exception to this rule is that the whitespace character is not
          ignored inside the `extended variable syntax`_.

.. note:: `\x`, `\u` and `\U` escape sequences are new in Robot Framework 2.8.2.

Prevent ignoring empty cells
''''''''''''''''''''''''''''

If empty values are needed as arguments for keywords or otherwise, they often
need to be escaped to prevent them from being ignored__. Empty trailing cells
must be escaped regardless of the test data format, and when using the
`space separated format`_ all empty values must be escaped.

Empty cells can be escaped either with the backslash character or with
`built-in variable`_ `${EMPTY}`. The latter is typically recommended
as it is easier to understand. An exception to this recommendation is escaping
the indented cells in `for loops`_ with a backslash when using the
`space separated format`_. All these cases are illustrated in the following
examples first in HTML and then in the space separated plain text format:

.. table::
   :class: example

   ==================  ============  ==========  ==========  ================================
        Test Case         Action      Argument    Argument                Argument
   ==================  ============  ==========  ==========  ================================
   Using backslash     Do Something  first arg   \\
   Using ${EMPTY}      Do Something  first arg   ${EMPTY}
   Non-trailing empty  Do Something              second arg  # No escaping needed in HTML
   For loop            :FOR          ${var}      IN          @{VALUES}
   \                                 Log         ${var}      # No escaping needed here either
   ==================  ============  ==========  ==========  ================================

.. sourcecode:: robotframework

   *** Test Cases ***
   Using backslash
       Do Something    first arg    \
   Using ${EMPTY}
       Do Something    first arg    ${EMPTY}
   Non-trailing empty
       Do Something    ${EMPTY}     second arg    # Escaping needed in space separated format
   For loop
       :FOR    ${var}    IN    @{VALUES}
       \    Log    ${var}                         # Escaping needed here too

__ `Ignored data`_

Prevent ignoring spaces
'''''''''''''''''''''''

Because leading, trailing, and consecutive spaces in cells are ignored__, they
need to be escaped if they are needed as arguments to keywords or otherwise.
Similarly as when preventing ignoring empty cells, it is possible to do that
either using the backslash character or using `built-in variable`_
`${SPACE}`.

.. table:: Escaping spaces examples
   :class: tabular

   ==================================  ==================================  ==================================
        Escaping with backslash             Escaping with `${SPACE}`                      Notes
   ==================================  ==================================  ==================================
   :codesc:`\\ leading space`          `${SPACE}leading space`
   :codesc:`trailing space \\`         `trailing space${SPACE}`            Backslash must be after the space.
   :codesc:`\\ \\`                     `${SPACE}`                          Backslash needed on both sides.
   :codesc:`consecutive \\ \\ spaces`  `consecutive${SPACE * 3}spaces`     Using `extended variable syntax`_.
   ==================================  ==================================  ==================================

As the above examples show, using the `${SPACE}` variable often makes the
test data easier to understand. It is especially handy in combination with
the `extended variable syntax`_ when more than one space is needed.

__ `Handling whitespace`_

Dividing test data to several rows
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If there is more data than readily fits a row, it possible to use ellipsis
(`...`) to continue the previous line. In test case and keyword tables,
the ellipsis must be preceded by at least one empty cell.  In settings and
variable tables, it can be placed directly under the setting or variable name.
In all tables, all empty cells before the ellipsis are ignored.

Additionally, values of settings that take only one value (mainly
documentations) can be split to several columns. These values will be
then catenated together with spaces when the test data is
parsed. Starting from Robot Framework 2.7, documentation and test
suite metadata split into multiple rows will be `catenated together
with newlines`__.

All the syntax discussed above is illustrated in the following examples.
In the first three tables test data has not been split, and
the following three illustrate how fewer columns are needed after
splitting the data to several rows.

__ `Newlines in test data`_

.. table:: Test data that has not been split
   :class: example

   ============  =======  =======  =======  =======  =======  =======
     Setting      Value    Value    Value    Value    Value    Value
   ============  =======  =======  =======  =======  =======  =======
   Default Tags  tag-1    tag-2    tag-3    tag-4    tag-5    tag-6
   ============  =======  =======  =======  =======  =======  =======

.. table::
   :class: example

   ==========  =======  =======  =======  =======  =======  =======
    Variable    Value    Value    Value    Value    Value    Value
   ==========  =======  =======  =======  =======  =======  =======
   @{LIST}     this     list     has      quite    many     items
   ==========  =======  =======  =======  =======  =======  =======

.. table::
   :class: example

   +-----------+-----------------+---------------+------+-------+------+------+-----+-----+
   | Test Case |     Action      |   Argument    | Arg  |  Arg  | Arg  | Arg  | Arg | Arg |
   +===========+=================+===============+======+=======+======+======+=====+=====+
   | Example   | [Documentation] | Documentation |      |       |      |      |     |     |
   |           |                 | for this test |      |       |      |      |     |     |
   |           |                 | case.\\n This |      |       |      |      |     |     |
   |           |                 | can get quite |      |       |      |      |     |     |
   |           |                 | long...       |      |       |      |      |     |     |
   +-----------+-----------------+---------------+------+-------+------+------+-----+-----+
   |           | [Tags]          | t-1           | t-2  | t-3   | t-4  | t-5  |     |     |
   +-----------+-----------------+---------------+------+-------+------+------+-----+-----+
   |           | Do X            | one           | two  | three | four | five | six |     |
   +-----------+-----------------+---------------+------+-------+------+------+-----+-----+
   |           | ${var} =        | Get X         | 1    | 2     | 3    | 4    | 5   | 6   |
   +-----------+-----------------+---------------+------+-------+------+------+-----+-----+

.. table:: Test data split to several rows
   :class: example

   ============  =======  =======  =======
     Setting      Value    Value    Value
   ============  =======  =======  =======
   Default Tags  tag-1    tag-2    tag-3
   ...           tag-4    tag-5    tag-6
   ============  =======  =======  =======

.. table::
   :class: example

   ==========  =======  =======  =======
    Variable    Value    Value    Value
   ==========  =======  =======  =======
   @{LIST}     this     list     has
   ...         quite    many     items
   ==========  =======  =======  =======

.. table::
   :class: example

   ===========  ================  ==============  ==========  ==========
    Test Case       Action           Argument      Argument    Argument
   ===========  ================  ==============  ==========  ==========
   Example      [Documentation]   Documentation   for this    test case.
   \            ...               This can get    quite       long...
   \            [Tags]            t-1             t-2         t-3
   \            ...               t-4             t-5
   \            Do X              one             two         three
   \            ...               four            five        six
   \            ${var} =          Get X           1           2
   \                              ...             3           4
   \                              ...             5           6
   ===========  ================  ==============  ==========  ==========
