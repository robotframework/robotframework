Test data syntax
----------------

This section covers Robot Framework's overall test data
syntax. The following sections will explain how to actually create test
cases, test suites and so on.

.. contents::
   :depth: 2
   :local:

Files and directories
~~~~~~~~~~~~~~~~~~~~~

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
~~~~~~~~~~~~~~~~~~~~~~

Robot Framework test data is defined in tabular format, using either
hypertext markup language (HTML), tab-separated values (TSV),
plain text, or reStructuredText (reST) formats. The details of these
formats, as well as the main benefits and problems with them, are explained
in the subsequent sections. Which format to use depends on the context,
but the plain text format is recommended if there are no special needs.

Robot Framework selects a parser for the test data based on the file extension.
The extension is case-insensitive, and the recognized extensions are
:path:`.html`, :path:`.htm` and :path:`.xhtml` for HTML, :path:`.tsv`
for TSV, :path:`.txt` and special :path:`.robot` for plain text, and
:path:`.rst` and :path:`.rest` for reStructuredText.

Different `test data templates`_ are available for HTML and TSV
formats to make it easier to get started writing tests.

.. note:: The special :path:`.robot` extension with plain text files is
          supported starting from Robot Framework 2.7.6.

HTML format
'''''''''''

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
`````````````````

Test data in HTML files can be edited with whichever editor you
prefer, but a graphic editor, where you can actually see the tables,
is recommended. RIDE_ can read and write HTML files, but unfortunately
it loses all HTML formatting and also possible data outside test case
tables.

Encoding and entity references
``````````````````````````````

HTML entity references (for example, :code:`&auml;`) are
supported. Additionally, any encoding can be used, assuming that it is
specified in the data file. Normal HTML files must use the META
element as in the example below::

  <meta http-equiv="Content-Type" content="text/html; charset=UTF-8">

XHTML files should use the XML preamble as in this example::

  <?xml version="1.0" encoding="Big5"?>

If no encoding is specified, Robot Framework uses ISO-8859-1 by default.

TSV format
''''''''''

TSV files can be edited in spreadsheet programs and, because the syntax is
so simple, they are easy to generate programmatically. They are also pretty
easy to edit using normal text editors and they work well in version control,
but the `plain text format`_ is even better suited for these purposes.

The TSV format can be used in Robot Framework's test data for all the
same purposes as HTML. In a TSV file, all the data is in one large
table. `Test data tables`_ are recognized from one or more asterisks
(:code:`*`), followed by a normal table name and an optional closing
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
`````````````````

You can create and edit TSV files in any spreadsheet program, such as
Microsoft Excel. Select the tab-separated format when you save the
file and remember to set the file extension to :path:`.tsv`. It is
also a good idea to turn all automatic corrections off and configure
the tool to treat all values in the file as plain text.

TSV files are relatively easy to edit with any text editor,
especially if the editor supports visually separating tabs from
spaces. The TSV format is also supported by RIDE_.

Robot Framework parses TSV data by first splitting all the content
into rows and then rows into cells on the basis of the tabular
characters. Spreadsheet programs sometimes surround cells with quotes
(for example, :code:`"my value"`) and Robot Framework removes
them. Possible quotes inside the data are doubled (for example,
:code:`"my ""quoted"" value"`) and also this is handled correctly.  If
you are using a spreadsheet program to create TSV data, you should not
need to pay attention to this, but if you create data
programmatically, you have to follow the same quoting conventions as
spreadsheets.

Encoding
````````

TSV files are always expected to use UTF-8 encoding. Because ASCII is
a subset of UTF-8, plain ASCII is naturally supported too.

Plain text format
'''''''''''''''''

The plain texts format is very easy to edit using any text editor and
they also work very well in version control. Because of these benefits
it has became the most used data format with Robot Framework.

The plain text format is technically otherwise similar to the `TSV
format`_ but the separator between the cells is different. The TSV
format uses tabs, but in the plain text format you can use either two
or more spaces or a pipe character surrounded with spaces :code:`( | )`.

The `test data tables`_ must have one or more asterisk before their
names similarly as in the TSV format. Otherwise asterisks and possible
spaces in the table header are ignored so, for example, :code:`***
Settings ***` and :code:`*Settings` work the same way. Also similarly
as in the TSV format, everything before the first table is ignored.

In plain text files tabs are automatically converted to two
spaces. This allows using a single tab as a separator similarly as in
the TSV format. Notice, however, that in the plain text format
multiple tabs are considered to be a single separator whereas in the
TSV format every tab would be a separator.

Space separated format
``````````````````````

The number of spaces used as separator can vary, as long as there are
at least two spaces, and it is thus possible to align the data nicely.
This is a clear benefit over editing the TSV format in a text editor
because with TSV the alignment cannot be controlled.

::

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
with :var:`${EMPTY}` variable or a single backslash. Otherwise
`handling whitespace`_ is not different than in other test data
because leading, trailing, and consecutive spaces must always be
escaped.

__ Escaping_

.. tip:: It is recommend to use four spaces between keywords and arguments.

Pipe and space separated format
```````````````````````````````

The biggest problem of the space delimited format is that visually
separating keywords form arguments can be tricky. This is a problem
especially if keywords take a lot of arguments and/or arguments
contain spaces. In such cases the pipe and space delimited variant can
work better because it makes the cell boundary more visible.

::

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
in the actual test data must be escaped with a backslash::

   | ${file count} = | Execute Command | ls -1 *.txt \| wc -l |
   | Should Be Equal | ${file count}   | 42                   |

__ Escaping_

Editing and encoding
````````````````````

One of the biggest benefit of the plain text format over HTML and TSV
is that editing it using normal text editors is very easy. Many editors
and IDEs (at least Eclipse, Emacs, Vim, and TextMate) also have plugins that
support syntax highlighting Robot Framework test data and may also provide
other features such as keyword completion. The plain text format is also
supported by RIDE_.

Similarly as with the TSV test data, plain text files are always expected
to use UTF-8 encoding. As a consequence also ASCII files are supported.

Recognized extensions
`````````````````````

Starting from Robot Framework 2.7.6, it is possible to save plain text
test data files using a special :path:`.robot` extension in addition to
the normal :path:`.txt` extension. The new extension makes it easier to
distinguish test data files from other plain text files.

reStructuredText format
'''''''''''''''''''''''

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
`````````````````

reStructuredText documents can contain code examples in so called code blocks.
When these documents are compiled into HTML or other formats, the code blocks
are syntax highlighted using Pygments_. In standard reST code blocks are
started using the :code:`code` directive, but Sphinx_ uses :code:`code-block`
or :code:`sourcecode` instead. The name of the programming language in
the code block is given as an argument to the directive. For example, following
code blocks contain Python and Robot Framework examples, respectively::

    .. code:: python

       def example_keyword():
           print 'Hello, world!'

    .. code:: robotframework

       *** Test Cases ***
       Example Test
           Example Keyword

When Robot Framework parses reStructuredText files, it first searches for
possible :code:`code`, :code:`code-block` or :code:`sourcecode` blocks
containing Robot Framework test data. If such code blocks are found, data
they contain is written into an in-memory file and executed. All data outside
the code blocks is ignored.

The test data in the code blocks must be defined using the `plain text format`_.
As the example below illustrates, both space and pipe separated variants are
supported::

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
````````````

If a reStructuredText document contains no code blocks with Robot Framework
data, it is expected to contain the data in tables similarly as in
the `HTML format`_. In this case Robot Framework compiles the document to
HTML in memory and parses it exactly like it would parse a normal HTML file.

Robot Framework identifies `test data tables`_ based on the text in the first
cell and all content outside of the recognized table types is ignored.
An example of each of the four test data tables is shown below
using both simple table and grid table syntax::

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
    === =========  ==================  ============  =============
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

.. note:: Empty cells in the first column of simple tables needs to be escaped.
          The above example uses :code:`\\` and :code:`..` could also be used.

.. note:: Because the backslash character is an escape character in reST,
          specifying a backslash so that Robot Framework will see it requires
          escaping it with an other backslash like :code:`\\\\`. For example,
          a new line character must be written like :code:`\\\\n`. Because
          the backslash is used for escaping_ also in Robot Framework data,
          specifying a literal backslash when using reST tables requires double
          escaping like :code:`c:\\\\\\\\temp`.

Generating HTML files based on reST files every time tests are run obviously
adds some overhead. If this is a problem, it can be a good idea to convert
reST files to HTML using external tools separately and let Robot Framework
use the generated files only.

Editing and encoding
````````````````````

Test data in reStructuredText files can be edited with any text editor, and
many editors also provide automatic syntax highlighting for it. reST format
is not supported by RIDE_, though.

Robot Framework requires reST files containing non-ASCII characters to be
saved using UTF-8 encoding.

Syntax errors in reST source files
``````````````````````````````````

If a reStructuredText document is not syntactically correct (a malformed table
for example), parsing it will fail and no test cases can be found from that
file. When executing a single reST file, Robot Framework will show the error
on the console. When executing a directory, such parsing errors will
generally be ignored.

Test data tables
~~~~~~~~~~~~~~~~

Test data is structured in four types of tables listed below. These
test data tables are identified by the first cell of the table, and
the last column in the table below lists different aliases that can be
used as a table name.

.. table:: Different test data tables
   :class: tabular

   +--------------+-------------------------------------------+-------------------+
   |  Table name  |                 Used for                  |      Aliases      |
   +==============+===========================================+===================+
   | Setting      | | 1) Importing `test libraries`_,         | Setting, Settings,|
   | table        |   `resource files`_ and `variable files`_ | Metadata          |
   |              | | 2) Defining metadata for `test suites`_ |                   |
   |              |   and `test cases`_                       |                   |
   +--------------+-------------------------------------------+-------------------+
   | Variable     | Defining variables_ that can be used      | Variable,         |
   | table        | elsewhere in the test data                | Variables         |
   +--------------+-------------------------------------------+-------------------+
   | Test case    | `Creating test cases`_ from available     | Test Case,        |
   | table        | keywords                                  | Test Cases        |
   +--------------+-------------------------------------------+-------------------+
   | Keyword      | `Creating user keywords`_ from existing   | Keyword, Keywords,|
   | table        | lower-level keywords                      | User Keyword,     |
   |              |                                           | User Keywords     |
   +--------------+-------------------------------------------+-------------------+

Rules for parsing the data
~~~~~~~~~~~~~~~~~~~~~~~~~~

Ignored data
''''''''''''

When Robot Framework parses the test data, it ignores:

- All tables that do not start with a recognized table name in the first cell.
- Everything else on the first row of a table apart from the first cell.
- Data before the first table and also between tables if the data format
  allows that.
- All empty rows, which means these kinds of rows can be used to make
  the tables more readable.
- All empty cells at the end of rows; you must add a backslash (\\) or `built-in
  variable`__ :var:`${EMPTY}` to prevent such cells from being ignored.
- All single backslashes (\\); they are used as an escape character.
- All characters following a hash mark (#), if it is the first
  character of a cell; this means that hash marks can be used to enter
  comments in the test data.
- All formatting in the HTML/reST test data.

When Robot Framework ignores some data, this data is not available in
any resulting reports and, additionally, most tools used with Robot
Framework also ignore them. To add information that is visible in
Robot Framework outputs, place it to the documentation or other metadata of
test cases or suites, or log it with the :name:`Log` or :name:`Comment` keywords
available from the BuiltIn_ library.

__ `Space and empty variables`_

Escaping
''''''''

The escape character in Robot Framework test data is the backslash (:code:`\\`).
It has has plenty of usages:

- Escape special characters so that their literal values are used:

  * :code:`\\${notvar}` means a literal string :code:`${notvar}`, not a variable_
  * :code:`\\#` means a literal hash character, even at the beginning of a cell, not a comment
  * :code:`name\\=value` means a literal value :code:`name=value`, not `named argument syntax`_
  * :code:`\\\\` means a literal backslash (for example, :code:`C:\\\\Temp`)

- Affect `the parsing of whitespaces`__.

- Prevent ignoring empty cells at the end of a row in general and
  everywhere when using the `plain text format`_. Another, and often
  clearer, possibility is using `built-in variable`__ :var:`${EMPTY}`.

- Escape the pipe character when using the `pipe and space separated format`_.

- Escape indented cells in `for loops`_ when using the `plain text format`_.

- Prevent catenating documentation split into multiple rows `with newlines`__.

__ `Handling whitespace`_
__ `Space and empty variables`_
__ `Automatic newlines in test data`_

.. note:: These escaping rules are applied only to arguments to
          keywords and values to settings. They are not used, for
          example, with keyword and test case names.

Handling whitespace
'''''''''''''''''''

Robot Framework handles whitespace, such as spaces, newlines and tabs,
the same way as they are handled in HTML. This means that Robot Framework:

- Removes leading and trailing whitespace in all cells.
- Changes multiple consecutive spaces into single spaces.
- Converts all newlines and tabs into spaces.

To prevent Robot Framework from parsing data according to these rules,
the backslash character can be used:

- Before leading spaces, for example :code:`\\ some text`.
- Between consecutive spaces, for example :code:`text \\ \\ more text`.
- After trailing spaces, for example :code:`some text \\ \\`.
- As :code:`\\n` to create a newline, for example :code:`first line\\n2nd line`.
- As :code:`\\t` to create a tab character, for example :code:`text\\tmore text`.
- As :code:`\\r` to create a carriage return, for example :code:`text\\rmore text`.

Another, and often clearer, possibility for representing leading,
trailing, or consecutive spaces is using `built-in variable`__
:var:`${SPACE}`. The `extended variable syntax`_ even allows syntax
like :var:`${SPACE * 8}` which makes handling consecutive spaces very simple.

.. note:: Possible un-escaped whitespace character after the :code:`\\n` is
          ignored to allow wrapping long lines containing newlines. This
          means that :code:`two lines\\nhere` and :code:`two lines\\n here`
          are equivalent. An exception to this rule is that the whitespace
          character is not ignored inside the `extended variable syntax`_.

.. note:: Starting from Robot Framework 2.7.5, non-breaking spaces are
          replaced with normal spaces regardless the test data format.
          This is done to avoid hard-to-debug errors when a non-breaking
          space is accidentally used instead of a normal space. If real
          non-breaking spaces are needed in test data, it is possible to
          create variables containing them, for example, in `variable files`_.

__ `Space and empty variables`_

Dividing test data to several rows
''''''''''''''''''''''''''''''''''

If there is more data than readily fits a row, it possible to use ellipsis
(:code:`...`) to continue the previous line. In test case and user keyword tables,
the ellipsis must be preceded by at least one empty cell.  In settings and
variable tables, it can be placed directly under the setting or variable name.

In all tables, all empty cells before the ellipsis are ignored.

Additionally, values of settings that take only one value (mainly
documentations) can be split to several columns. These values will be
then catenated together with spaces when the test data is
parsed. Starting from Robot Framework 2.7, documentation and test
suite metadata split into multiple rows will be `catenated together
with newlines`__.

All these syntaxes are illustrated in the following examples. In the
first three tables test data has not been split, and
the following three illustrate how fewer columns are needed after
splitting the data to several rows.

__ `Automatic newlines in test data`_

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

.. Note:: Empty cells before ellipsis are allowed generally only in Robot
          Framework 2.5.2 and newer. In earlier versions a single leading
          empty cell is allowed inside `for loops`_ but not otherwise.

Splitting test data in reST tables
```````````````````````````````````

In the plain text markup for reST tables, there are two types of table
syntax that can be used to create test data. When using the `Simple
Tables` syntax, a :code:`\\` or :code:`..` is required in the first cell
of a continued row in addition to the :code:`...` required by Robot Framework.

Here is an example using reST `Simple Table` format::

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
    \            ...               3               4           5
    \            ...               6
    ===========  ================  ==============  ==========  ==========

For `Grid Table` syntax, the first cell in a continued row may be blank,
and the second cell should contain :code:`...` as with HTML tables::

    +-----------+-------------------+---------------+------------+------------+
    | Test Case |      Action       |   Argument    |  Argument  |  Argument  |
    +===========+===================+===============+============+============+
    | Example   | [Documentation]   | Documentation | for this   | test case. |
    +-----------+-------------------+---------------+------------+------------+
    |           | ...               | This can get  | quite      | long...    |
    +-----------+-------------------+---------------+------------+------------+
    |           | [Tags]            | t-1           | t-2        | t-3        |
    +-----------+-------------------+---------------+------------+------------+
    |           | ...               | t-4           | t-5        |            |
    +-----------+-------------------+---------------+------------+------------+
    |           | Do X              | one           | two        | three      |
    +-----------+-------------------+---------------+------------+------------+
    |           | ...               | four          | five       | six        |
    +-----------+-------------------+---------------+------------+------------+
    |           | ${var} =          | Get X         | 1          | 2          |
    +-----------+-------------------+---------------+------------+------------+
    |           | ...               | 3             | 4          | 5          |
    +-----------+-------------------+---------------+------------+------------+
    |           | ...               | 6             |            |            |
    +-----------+-------------------+---------------+------------+------------+
