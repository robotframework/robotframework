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
   |            | either tests or tasks.                     |
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

The most common approach to create Robot Framework data is using the
`space separated format`_ where pieces of the data, such as keywords
and their arguments, are separated from each others with two or more spaces.
An alternative is using the `pipe separated format`_ where the separator is
the pipe character surrounded with spaces (:codesc:`\ |\ `).

Executed files typically use the :file:`.robot` extension, but that `can be
configured`__ with the :option:`--extension` option. `Resource files`_
can use the :file:`.robot` extension as well, but using the dedicated
:file:`.resource` extension is recommended. Files containing non-ASCII
characters must be saved using the UTF-8 encoding.

Robot Framework also supports reStructuredText_ files so that normal
Robot Framework data is `embedded into code blocks`__. It is possible to
use either :file:`.rst` or :file:`.rest` extension with reStructuredText
files, but the aforementioned :option:`--extension` option `must be used`__
to enable parsing them when executing a directory.

Earlier Robot Framework versions supported data also in HTML and TSV formats.
The TSV format still works if the data is compatible with the `space separated
format`_, but the support for the HTML format has been removed altogether.
If you encounter such data files, you need to convert them to the plain text
format to be able to use them with Robot Framework 3.2 or newer. The easiest
way to do that is using the Tidy_ tool, but you must use the version included
with Robot Framework 3.1 because newer versions do not understand the HTML
format at all.

__ `Selecting files to parse`_
__ `reStructuredText format`_
__ `Selecting files to parse`_

.. _space separated plain text format:

Space separated format
~~~~~~~~~~~~~~~~~~~~~~

When Robot Framework parses data, it first splits the data to lines and then
lines to tokens such as keywords and arguments. When using the space
separated format, the separator between tokens is two or more spaces or
alternatively one or more tab characters. In addition to the normal ASCII
space, any Unicode character considered to be a space (e.g. no-break space)
works as a separator. The number of spaces used as separator can vary, as
long as there are at least two, making it possible to align the data nicely
in settings and elsewhere when it makes the data easier to understand.

.. sourcecode:: robotframework

   *** Settings ***
   Documentation     Example using the space separated format.
   Library           OperatingSystem

   *** Variables ***
   ${MESSAGE}        Hello, world!

   *** Test Cases ***
   My Test
       [Documentation]    Example test.
       Log    ${MESSAGE}
       My Keyword    ${CURDIR}

   Another Test
       Should Be Equal    ${MESSAGE}    Hello, world!

   *** Keywords ***
   My Keyword
       [Arguments]    ${path}
       Directory Should Exist    ${path}

Because tabs and consecutive spaces are considered separators, they must
be escaped if they are needed in keyword arguments or elsewhere
in the actual data. It is possible to use special escape syntax like
`\t` for tab and `\xA0` for no-break space as well as `built-in variables`_
`${SPACE}` and `${EMPTY}`. See the Escaping_ section for details.

.. tip:: Although using two spaces as a separator is enough, it is recommended
         to use four spaces to make the separator easier to recognize.

.. note:: Prior to Robot Framework 3.2, non-ASCII spaces used in the data
          were converted to ASCII spaces during parsing. Nowadays all data
          is preserved as-is.

Pipe separated format
~~~~~~~~~~~~~~~~~~~~~

The biggest problem of the space delimited format is that visually
separating keywords from arguments can be tricky. This is a problem
especially if keywords take a lot of arguments and/or arguments
contain spaces. In such cases the pipe delimited variant can
work better because it makes the separator more visible.

One file can contain both space separated and pipe separated lines.
Pipe separated lines are recognized by the mandatory leading pipe character,
but the pipe at the end of the line is optional. There must always be at
least one space or tab on both sides of the pipe except at the beginning and
at the end of the line. There is no need to align the pipes, but that often
makes the data easier to read.

.. sourcecode:: robotframework

   | *** Settings ***   |
   | Documentation      | Example using the pipe separated format.
   | Library            | OperatingSystem

   | *** Variables ***  |
   | ${MESSAGE}         | Hello, world!

   | *** Test Cases *** |                 |               |
   | My Test            | [Documentation] | Example test. |
   |                    | Log             | ${MESSAGE}    |
   |                    | My Keyword      | ${CURDIR}     |
   | Another Test       | Should Be Equal | ${MESSAGE}    | Hello, world!

   | *** Keywords ***   |                        |         |
   | My Keyword         | [Arguments]            | ${path} |
   |                    | Directory Should Exist | ${path} |

When using the pipe separated format, consecutive spaces or tabs inside
arguments do not need to be escaped. Similarly empty columns do not need
to be escaped except `if they are at the end`__. Possible pipes surrounded by
spaces in the actual test data must be escaped with a backslash, though:

.. sourcecode:: robotframework

   | *** Test Cases *** |                 |                 |                      |
   | Escaping Pipe      | ${file count} = | Execute Command | ls -1 *.txt \| wc -l |
   |                    | Should Be Equal | ${file count}   | 42                   |

__ Escaping_

.. note:: Preserving consecutive spaces and tabs in arguments is new
          in Robot Framework 3.2. Prior to it non-ASCII spaces used in
          the data were also converted to ASCII spaces.

reStructuredText format
~~~~~~~~~~~~~~~~~~~~~~~

reStructuredText_ (reST) is an easy-to-read plain text markup syntax that
is commonly used for documentation of Python projects, including Python itself
as well as this User Guide. reST documents are most often compiled to HTML,
but also other output formats are supported. Using reST with Robot Framework
allows you to mix richly formatted documents and test data in a concise text
format that is easy to work with using simple text editors, diff tools, and
source control systems.

.. note:: Using reStructuredText_ files with Robot Framework requires the
          Python docutils_ module to be installed.

When using Robot Framework with reStructuredText files, normal Robot Framework
data is embedded to so called code blocks. In standard reST code blocks are
marked using the `code` directive, but Robot Framework supports also
`code-block` or `sourcecode` directives used by the Sphinx_ tool.

.. sourcecode:: rest

    reStructuredText example
    ------------------------

    This text is outside code blocks and thus ignored.

    .. code:: robotframework

       *** Settings ***
       Documentation    Example using the reStructuredText format.
       Library          OperatingSystem

       *** Variables ***
       ${MESSAGE}       Hello, world!

       *** Test Cases ***
       My Test
           [Documentation]    Example test.
           Log    ${MESSAGE}
           My Keyword    ${CURDIR}

       Another Test
           Should Be Equal    ${MESSAGE}    Hello, world!

    Also this text is outside code blocks and ignored. Code blocks not
    containing Robot Framework data are ignored as well.

    .. code:: robotframework

       # Both space and pipe separated formats are supported.

       | *** Keyword ***  |                        |         |
       | My Keyword       | [Arguments]            | ${path} |
       |                  | Directory Should Exist | ${path} |

    .. code:: python

       # This code block is ignored.
       def example():
           print('Hello, world!')

Robot Framework supports reStructuredText files using both :file:`.rst` and
:file:`.rest` extension. When executing a directory containing reStucturedText
files, the :option:`--extension` option must be used to explicitly tell that
`these files should be parsed`__.

__ `Selecting files to parse`_

When Robot Framework parses reStructuredText files, errors below level
`SEVERE` are ignored to avoid noise about possible non-standard directives
and other such markup. This may hide also real errors, but they can be seen
when processing files using reStructuredText tooling normally.

Rules for parsing the data
--------------------------

.. _comment:

Ignored data
~~~~~~~~~~~~

When Robot Framework parses the test data files, it ignores:

- All data before the first `test data section`__.
- Data in the `Comments`__ section.
- All empty rows.
- All empty cells at the end of rows when using the `pipe separated format`_.
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

Handling empty values
'''''''''''''''''''''

When using the `space separated format`_, the number of spaces used as
a separator can vary and thus empty values cannot be recognized unless they
are escaped. Empty cells can be escaped either with the backslash character
or with `built-in variable`_ `${EMPTY}`. The latter is typically recommended
as it is easier to understand.

.. sourcecode:: robotframework

   *** Test Cases ***
   Using backslash
       Do Something    first arg    \
       Do Something    \            second arg

   Using ${EMPTY}
       Do Something    first arg    ${EMPTY}
       Do Something    ${EMPTY}     second arg

When using the `pipe separated format`_, empty values need to be escaped
only when they are at the end of the row:

.. sourcecode:: robotframework

   | *** Test Cases *** |              |           |            |
   | Using backslash    | Do Something | first arg | \          |
   |                    | Do Something |           | second arg |
   |                    |              |           |            |
   | Using ${EMPTY}     | Do Something | first arg | ${EMPTY}   |
   |                    | Do Something |           | second arg |

Handling spaces
'''''''''''''''

Spaces, especially consecutive spaces, as part of arguments for keywords or
needed otherwise are problematic for two reasons:

- Two or more consecutive spaces is considered a separator when using the
  `space separated format`_.
- Leading and trailing spaces are ignored when using the
  `pipe separated format`_.

In these cases spaces need to be escaped. Similarly as when escaping empty
values, it is possible to do that either by using the backslash character or
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

Dividing data to several rows
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If there is more data than readily fits a row, it is possible to split it
and start continuing rows with ellipsis (`...`). Ellipses can be indented
to match the indentation of the starting row and they must always be followed
by the normal test data separator.

In most places split lines have exact same semantics as lines that are not
split. Exceptions to this rule are suite__, test__ and keyword__ documentation
as well `suite metadata`__. With them split values are automatically
`joined together with the newline character`__ to ease creating multiline
values.

The `...` syntax allows also splitting variables in the `Variable section`_.
When long scalar variables (e.g. `${STRING}`) are split to multiple rows,
the final value is got by concatenating the rows together. The separator is
a space by default, but that can be changed by starting the value with
`SEPARATOR=<sep>`.

Splitting lines is illustrated in the following two examples containing
exactly same data without and with splitting.

__ `Test suite documentation`_
__ `Test case documentation`_
__ `User keyword documentation`_
__ `Free test suite metadata`_
__ `Newlines in test data`_

.. sourcecode:: robotframework

   *** Settings ***
   Documentation      Here we have documentation for this suite.\nDocumentation is often quite long.\n\nIt can also contain multiple paragraphs.
   Default Tags       default tag 1    default tag 2    default tag 3    default tag 4    default tag 5

   *** Variable ***
   ${STRING}          This is a long string. It has multiple sentences. It does not have newlines.
   ${MULTILINE}       This is a long multiline string.\nThis is the second line.\nThis is the third and the last line.
   @{LIST}            this     list     is    quite    long     and    items in it can also be long
   &{DICT}            first=This value is pretty long.    second=This value is even longer. It has two sentences.

   *** Test Cases ***
   Example
       [Tags]    you    probably    do    not    have    this    many    tags    in    real    life
       Do X    first argument    second argument    third argument    fourth argument    fifth argument    sixth argument
       ${var} =    Get X    first argument passed to this keyword is pretty long    second argument passed to this keyword is long too

.. sourcecode:: robotframework

   *** Settings ***
   Documentation      Here we have documentation for this suite.
   ...                Documentation is often quite long.
   ...
   ...                It can also contain multiple paragraphs.
   Default Tags       default tag 1    default tag 2    default tag 3
   ...                default tag 4    default tag 5

   *** Variable ***
   ${STRING}          This is a long string.
   ...                It has multiple sentences.
   ...                It does not have newlines.
   ${MULTILINE}       SEPARATOR=\n
   ...                This is a long multiline string.
   ...                This is the second line.
   ...                This is the third and the last line.
   @{LIST}            this     list     is      quite    long     and
   ...                items in it can also be long
   &{DICT}            first=This value is pretty long.
   ...                second=This value is even longer. It has two sentences.

   *** Test Cases ***
   Example
       [Tags]    you    probably    do    not    have    this    many
       ...       tags    in    real    life
       Do X    first argument    second argument    third argument
       ...    fourth argument    fifth argument    sixth argument
       ${var} =    Get X
       ...    first argument passed to this keyword is pretty long
       ...    second argument passed to this keyword is long too
