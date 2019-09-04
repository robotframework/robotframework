Test data syntax
================

This section covers Robot Framework's overall test data syntax. The following
sections will explain how to actually create test cases, test suites and so on.
Although this section mostly uses term *test*, the same rules apply also
when `creating tasks`_.

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
  case files as its child test suites.
- A test suite directory can also contain other test suite directories,
  and this hierarchical structure can be as deeply nested as needed.
- Test suite directories can have a special `initialization file`_
  configuring the created test suite.

In addition to this, there are:

- `Test libraries`_ containing the lowest-level keywords.
- `Resource files`_ with variables_ and higher-level `user keywords`_.
- `Variable files`_ to provide more flexible ways to create variables
  than resource files.

Test case files, test suite initialization files and resource files are
all created using Robot Framework test data syntax. Test libraries and
variable files are created using "real" programming languages, most
often Python.

.. _test data tables:

Test data sections
------------------

Robot Framework data is defined in different sections, often also
called tables, listed below:

.. table:: Different sections in data
   :class: tabular

   +------------+--------------------------------------------+
   |   Section  |                 Used for                   |
   +============+============================================+
   | Settings   | | 1) Importing `test libraries`_,          |
   |            |   `resource files`_ and `variable files`_. |
   |            | | 2) Defining metadata for `test suites`_  |
   |            |   and `test cases`_.                       |
   +------------+--------------------------------------------+
   | Variables  | Defining variables_ that can be used       |
   |            | elsewhere in the test data.                |
   +------------+--------------------------------------------+
   | Test Cases | `Creating test cases`_ from available      |
   |            | keywords.                                  |
   +------------+--------------------------------------------+
   | Tasks      | `Creating tasks`_ using available          |
   |            | keywords. Single file can only contain     |
   |            | either test cases or tasks.                |
   +------------+--------------------------------------------+
   | Keywords   | `Creating user keywords`_ from existing    |
   |            | lower-level keywords                       |
   +------------+--------------------------------------------+
   | Comments   | Additional comments or data. Ignored by    |
   |            | Robot Framework.                           |
   +------------+--------------------------------------------+

Different sections are recognized by their header row. The recommended
header format is `*** Settings ***`, but the header is case-insensitive,
surrounding spaces are optional, and the number of asterisk characters can
vary as long as there is one asterisk in the beginning. In addition to using
the plural format, also singular variants like `Setting` and `Test Case` are
accepted. In other words, also `*setting` would be recognized as a section
header.

The header row can contain also other data than the actual section header.
The extra data must be separated from the section header using the data
format dependent separator, typically two or more spaces. These extra headers
are ignored at parsing time, but they can be used for documenting
purposes. This is especially useful when creating test cases using the
`data-driven style`_.

Possible data before the first section is ignored.

.. note:: Section names used to be space-insensitive, but that was deprecated
          in Robot Framework 3.1 and trying to use something like `TestCases`
          or `S e t t i n g s` causes an error in Robot Framework 3.2.

.. note:: Prior to Robot Framework 3.1, all unrecognized sections were silently
          ignored but nowadays they cause an error. `Comments` sections can
          be used if sections not containing actual test data are needed.

Supported file formats
----------------------

Robot Framework test data can be defined in few different formats:

1. The most common approach is using the `plain text format`_ and store files
   using the :file:`.robot` extension. Alternatively it is possible to use
   the :file:`.txt` extension.

2. The `TSV format`_ can be used as long as files are compatible
   with the plain text format.

3. Plain text test data can be embedded into `reStructuredText files`__.

4. Earlier Robot Framework versions supported test data in `HTML format`_.

Prior to Robot Framework 3.1, all aforementioned file formats were parsed
automatically unless the :option:`--extension` option was used to `limit
parsing`__. In Robot Framework 3.1 automatically parsing other than
`*.robot` files was deprecated, and in the future other files are parsed
only if that is `explicitly configured`__ using the :option:`--extension` option.
The support for the HTML format has bee deprecated in general it will be
removed altogether in the future.

__ `reStructuredText format`_
__ `Selecting files to parse`_
__ `Selecting files to parse`_

Plain text format
~~~~~~~~~~~~~~~~~

The plain text format is the base for all supported Robot Framework data
formats. Test data is parsed line by line, but long logical lines
`can be split`__ if needed. In a single line different data items
like keywords and their arguments are separated from each others using
a separator. The most commonly used separator is two or more spaces, but
it is also possible to use a pipe character surrounded with spaces
(:codesc:`\ |\ `). Depending on the separator we can talk about the `space
separated format`_ and the `pipe separated format`_, but same file can
actually contain lines with both separators.

Possible literal tab characters are converted to two spaces before parsing
lines otherwise. This allows using a single tab as a separator instead of
multiple spaces. Notice, however, that multiple consecutive tabs are still
considered to be a single separator. If an actual tab character is needed
in the data, it must be escaped__ like `\t`.

Plain text files containing non-ASCII characters must be saved using the
UTF-8 encoding.

__ `Dividing test data to several rows`_
__ Escaping_

.. _space separated plain text format:

Space separated format
''''''''''''''''''''''

In the space separated format two or more spaces (or one or more tab
characters) act as a separator between different data items.
The number of spaces used as separator can vary, as long as there are
at least two, making it possible to align the data nicely in settings
and elsewhere if it makes sense.

.. sourcecode:: robotframework

   *** Settings ***
   Documentation    Example using the space separated plain text format.
   Library          OperatingSystem

   *** Variables ***
   ${MESSAGE}       Hello, world!

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

Because space is used as separator, all empty items and items containing
only spaces must be escaped__ with backslashes or with built-in  `${EMPTY}`
and `${SPACE}` variables, respectively.

__ Escaping_

.. tip:: Although using two spaces as a separator is enough, it is recommend
         to use four spaces to make the separator easier to notice.

Pipe separated format
'''''''''''''''''''''

The biggest problem of the space delimited format is that visually
separating keywords from arguments can be tricky. This is a problem
especially if keywords take a lot of arguments and/or arguments
contain spaces. In such cases the pipe delimited variant can
work better because it makes the separator more visible.

One file can contain both space separated and pipe separated lines.
Pipe separated lines are recognized by the mandatory leading pipe character,
but the pipe at the end of the line is optional. There must always be at
least one space on both sides of the pipe except at the beginning and at
the end of the line. There is no need to align the pipes, but that often
makes the data easier to read.

.. sourcecode:: robotframework

   | *** Settings ***   |
   | Documentation      | Example using the pipe separated plain text format.
   | Library            | OperatingSystem

   | *** Variables ***  |
   | ${MESSAGE}         | Hello, world!

   | *** Test Cases *** |                 |              |
   | My Test            | [Documentation] | Example test |
   |                    | Log             | ${MESSAGE}   |
   |                    | My Keyword      | /tmp         |
   | Another Test       | Should Be Equal | ${MESSAGE}   | Hello, world!

   | *** Keywords ***   |                        |         |
   | My Keyword         | [Arguments]            | ${path} |
   |                    | Directory Should Exist | ${path} |

There is no need to escape empty cells (other than the `trailing empty
cells`__) when using the pipe separated format. Possible pipes surrounded by
spaces in the actual test data must be escaped with a backslash, though:

.. sourcecode:: robotframework

   | *** Test Cases *** |                 |                 |                      |
   | Escaping Pipe      | ${file count} = | Execute Command | ls -1 *.txt \| wc -l |
   |                    | Should Be Equal | ${file count}   | 42                   |

__ Escaping_

Editing
'''''''

Plain text files can be easily edited using normal text editors and IDEs.
`Many of these tools`__ also have plugins that support syntax highlighting
Robot Framework test data and may also provide other features such as keyword
completion. Robot Framework specific editors like RIDE_ naturally support
the plain text format as well.

As already mentioned, plain text files containing non-ASCII characters must
be saved using the UTF-8 encoding.

__ http://robotframework.org/#tools

Recognized extensions
'''''''''''''''''''''

The recommended extension for `test case files`_ in the plain text format is
:file:`.robot`. Files using this extension are parsed automatically.
Also the :file:`.txt` extension can be used, but starting from Robot
Framework 3.1 the :option:`--extension` option must be used to
explicitly tell that `these files should be parsed`__.

When creating `resource files`_, it is possible to use the special
:file:`.resource` extension in addition to the aforementioned
:file:`.robot` and :file:`.txt` extensions. This way resource files and
test cases files are easily separated from each others.

.. note:: The :file:`.resource` extension is new in Robot Framework 3.1.

__ `Selecting files to parse`_

TSV format
~~~~~~~~~~

Files in the tab-separated values (TSV) format are typically edited in
spreadsheet programs and, because the syntax is so simple, they are easy
to generate programmatically. They are also pretty easy to edit using
normal text editors and they work well in version control, but the
`plain text format`_ is even better suited for these purposes.

.. table:: Using the TSV format
   :class: tsv-example

   =============  =============================  =============  =============
   \*Setting*     \*Value*                       \*Value*       \*Value*
   Documentation  Example using the TSV format.
   Library        OperatingSystem
   \
   \
   \*Variable*    \*Value*                       \*Value*       \*Value*
   ${MESSAGE}     Hello, world!
   \
   \
   \*Test Case*   \*Action*                      \*Argument*    \*Argument*
   My Test        [Documentation]                Example test
   \              Log                            ${MESSAGE}
   \              My Keyword                     /tmp
   \
   Another Test   Should Be Equal                ${MESSAGE}     Hello, world!
   \
   \
   \*Keyword*     \*Action*                      \*Argument*    \*Argument*
   My Keyword     [Arguments]                    ${path}
   \              Directory Should Exist         ${path}
   =============  =============================  =============  =============

The TSV format and the space separated variant of the `plain text format`_
are nearly identical, but earlier Robot Framework versions had slightly
different parser for these formats. The differences were:

- The TSV parser did not require escaping empty intermediate cells.
- The TSV parser removed possible quotes around cells that may be added
  by spreadsheet programs.

The TSV parser was deprecated in Robot Framework 3.1 and it will be removed
in the future. It is still possible to use the TSV format, but files
must be fully compatible with the plain text format. This basically requires
escaping all empty cells and configuring spreadsheet program or other tool
saving TSV files not to add surrounding quotes to cells.

Editing test data
'''''''''''''''''

You can create and edit TSV files in any spreadsheet program, such as
Microsoft Excel. Select the tab-separated format when you save the file.
It is also a good idea to turn all automatic corrections off and configure
the tool to treat all values in the file as plain text. As explained above,
TSV files should also be saved so that no quotes are added around the cells.

TSV files are relatively easy to edit with any text editor,
especially if the editor supports visually separating tabs from
spaces. The TSV format is also supported by RIDE_.

Like plain text files, TSV files containing non-ASCII characters must be
saved using the UTF-8 encoding.

Recognized extensions
'''''''''''''''''''''

Files in the TSV format are customarily saved using the :file:`.tsv`
extension, but starting from Robot Framework 3.1 the :option:`--extension`
option must be used to explicitly tell that `these files should be parsed`__.
Another possibility is saving also these files using the the :file:`.robot`
extension, but this requires the file to be fully compatible with the
plain text syntax.

__ `Selecting files to parse`_

reStructuredText format
~~~~~~~~~~~~~~~~~~~~~~~

reStructuredText_ (reST) is an easy-to-read plain text markup syntax that
is commonly used for documentation of Python projects (including
Python itself, as well as this User Guide). reST documents are most
often compiled to HTML, but also other output formats are supported.

Using reST with Robot Framework allows you to mix richly formatted documents
and test data in a concise text format that is easy to work with
using simple text editors, diff tools, and source control systems.

When using reST files with Robot Framework, test data is defined `using code
blocks`_. Earlier Robot Framework versions also supported `using tables`_ and
converting reST files to HTML, but this was deprecated in Robot Framework 3.1.

.. note:: Using reST files with Robot Framework requires the Python docutils_
          module to be installed.

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
           print('Hello, world!')

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
       Documentation    Example using the reStructuredText format.
       Library          OperatingSystem

       *** Variables ***
       ${MESSAGE}       Hello, world!

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

Using tables
''''''''''''

Earlier Robot Framework versions supported using reStructuredText also
so that test data was defined in tables. These files were then internally
converted to `HTML format`_ before parsing them. This functionality was
deprecated in Robot Framework 3.1 and will be removed in the future
along with the general support for the HTML format.

Editing
'''''''

Test data in reStructuredText files can be edited with any text editor, and
many editors also provide automatic syntax highlighting for it.

Robot Framework requires reST files containing non-ASCII characters to be
saved using the UTF-8 encoding.

Recognized extensions
'''''''''''''''''''''

Robot Framework supports reStructuredText files using both :file:`.rst` and
:file:`.rest` extension. Starting from Robot Framework 3.1 the
:option:`--extension` option must be used to explicitly tell that
`these files should be parsed`__.

__ `Selecting files to parse`_

Syntax errors in reST source files
''''''''''''''''''''''''''''''''''

When Robot Framework parses reStructuredText files, errors below level
`SEVERE` are ignored to avoid noise about possible non-standard directives
and other such markup. This may hide also real errors, but they can be seen
when processing files using reStructuredText tooling normally.

HTML format
~~~~~~~~~~~

Earlier Robot Framework versions supported test data in HTML format but
this support has been deprecated in Robot Framework 3.1. All test data in
HTML format should be converted to the `plain text format`_ or other supported
formats. This is typically easiest by using the built-in Tidy_ tool.

Rules for parsing the data
--------------------------

.. _comment:

Ignored data
~~~~~~~~~~~~

When Robot Framework parses the test data files, it ignores:

- All data before the first `test data section`__. If the data format allows
  data between sections, also that is ignored.
- Data in the `Comments`__ section.
- All empty rows.
- All empty cells at the end of rows, unless they are escaped__.
- All single backslashes (:codesc:`\\`) when not used for escaping_.
- All characters following the hash character (`#`), when it is the first
  character of a cell. This means that hash marks can be used to enter
  comments in the test data.

When Robot Framework ignores some data, this data is not available in
any resulting reports and, additionally, most tools used with Robot
Framework also ignore them. To add information that is visible in
Robot Framework outputs, place it to the documentation or other metadata of
test cases or suites, or log it with the BuiltIn_ keywords :name:`Log` or
:name:`Comment`.

__ `Test data sections`_
__ `Test data sections`_
__ `Handling empty cells`_

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
   `\&`         Ampersand, never starts a `dictionary variable`_.                 `\&{notvar}`
   `\%`         Percent sign, never starts an `environment variable`_.            `\%{notvar}`
   `\#`         Hash sign, never starts a comment_.                               `\# not comment`
   `\=`         Equal sign, never part of `named argument syntax`_.               `not\=named`
   `\|`         Pipe character, not a separator in the `pipe separated format`_.  `ls -1 *.txt \| wc -l`
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
          something like `value.encode('UTF-8')` in Python code.

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

Handling empty cells
''''''''''''''''''''

If empty values are needed as arguments for keywords or otherwise, they often
need to be escaped to prevent them from being ignored__. Empty trailing cells
must be escaped regardless of the test data format, and when using the
`space separated format`_ all empty values must be escaped.

Empty cells can be escaped either with the backslash character or with
`built-in variable`_ `${EMPTY}`. The latter is typically recommended
as it is easier to understand. All these cases are illustrated by the following
examples:

.. sourcecode:: robotframework

   *** Test Cases ***
   Using backslash
       Do Something    first arg    \
   Using ${EMPTY}
       Do Something    first arg    ${EMPTY}
   Non-trailing empty
       Do Something    ${EMPTY}     second arg    # Escaping needed in space separated format

__ `Ignored data`_

Handling spaces
'''''''''''''''

Spaces, especially consecutive spaces, as part of arguments for keywords or
needed otherwise are problematic for two reasons:

- Two or more consecutive spaces is considered a separator when using the
  `space separated format`_.
- Leading and trailing spaces are ignored when using the
  `pipe separated format`_.

In these cases spaces need to be escaped. Similarly as when escaping empty
cells, it is possible to do that either by using the backslash character or
by using the `built-in variable`_ `${SPACE}`.

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

Dividing test data to several rows
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If there is more data than readily fits a row, it possible to use ellipsis
(`...`) to continue the previous line. In test case and keyword tables,
the ellipsis must be preceded by at least one empty cell. In settings and
variable tables, it can be placed directly under the setting or variable name.
In all tables, all empty cells before the ellipsis are ignored.

Also suite, test or keyword documentation and value of test suite metadata
can be too long to fit into one row nicely. These values can be split into
multiple rows as well, and they will be `joined together with newlines`__.

All the syntax discussed above is illustrated in the following examples.
In the first three tables test data has not been split, and
the following three illustrate how fewer columns are needed after
splitting the data to several rows.

__ `Newlines in test data`_

.. sourcecode:: robotframework

   *** Settings ***
   Documentation      This is documentation for this test suite.\nThis kind of documentation can often be get quite long...
   Default Tags       default tag 1    default tag 2    default tag 3    default tag 4    default tag 5

   *** Variable ***
   @{LIST}            this     list     is      quite    long     and    items in it could also be long

   *** Test Cases ***
   Example
       [Tags]    you    probably    do    not    have    this    many    tags    in    real   life
       Do X    first argument    second argument    third argument    fourth argument    fifth argument    sixth argument
       ${var} =    Get X    first argument passed to this keyword is pretty long   second argument passed to this keyword is long too


.. sourcecode:: robotframework

   *** Settings ***
   Documentation      This is documentation for this test suite.
   ...                This kind of documentation can often be get quite long...
   Default Tags       default tag 1    default tag 2    default tag 3
   ...                default tag 4    default tag 5

   *** Variable ***
   @{LIST}            this     list     is      quite    long     and
   ...                items in it could also be long

   *** Test Cases ***
   Example
       [Tags]    you    probably    do    not    have    this    many
       ...       tags    in    real   life
       Do X    first argument    second argument    third argument
       ...    fourth argument    fifth argument    sixth argument
       ${var} =    Get X
       ...    first argument passed to this keyword is pretty long
       ...    second argument passed to this keyword is long too
