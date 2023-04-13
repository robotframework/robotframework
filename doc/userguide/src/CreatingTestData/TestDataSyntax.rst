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

- Test cases are created in `suite files`_.
- A test case file automatically creates a `test suite`_ containing
  the test cases in that file.
- A directory containing test case files forms a higher-level test
  suite. Such a `suite directory`_ has suites created from test
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
vary as long as there is at least one asterisk in the beginning. For example,
also `*settings` would be recognized as a section header.

Robot Framework also supports the singular form with headers like
`*** Setting ***,` but that support is deprecated. There are no visible
deprecation warnings yet, but warnings will emitted in the future and
singular headers will eventually not be supported at all.

The header row can contain also other data than the actual section header.
The extra data must be separated from the section header using the data
format dependent separator, typically two or more spaces. These extra headers
are ignored at parsing time, but they can be used for documenting
purposes. This is especially useful when creating test cases using the
`data-driven style`_.

Possible data before the first section is ignored.

.. note:: Section headers can be localized_. See the Translations_ appendix for
          supported translations.

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

       | *** Keywords ***  |                        |         |
       | My Keyword        | [Arguments]            | ${path} |
       |                   | Directory Should Exist | ${path} |

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
   | Using backslash    | Do Something | first arg | \          |
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

__ `Suite documentation`_
__ `Test case documentation`_
__ `User keyword documentation`_
__ `Free suite metadata`_
__ `Newlines`_

.. sourcecode:: robotframework

   *** Settings ***
   Documentation      Here we have documentation for this suite.\nDocumentation is often quite long.\n\nIt can also contain multiple paragraphs.
   Default Tags       default tag 1    default tag 2    default tag 3    default tag 4    default tag 5

   *** Variables ***
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

   *** Variables ***
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

Localization
------------

Robot Framework localization efforts were started in Robot Framework 6.0
that allowed translation of `section headers`_, settings_,
`Given/When/Then prefixes`__ used in Behavior Driven Development (BDD), and
`true and false strings`__ used in automatic Boolean argument conversion.
The plan is to extend localization support in the future, for example,
to log and report and possibly also to control structures.

This section explains how to `activate languages`__, what `built-in languages`_
are supported, how to create `custom language files`_ and how new translations
can be contributed__.

__ `Enabling languages`_
__ `Behavior-driven style`_
__ `Supported conversions`_
__ `Contributing translations`_

Enabling languages
~~~~~~~~~~~~~~~~~~

Using command line option
'''''''''''''''''''''''''

The main mechanism to activate languages is specifying them from the command line
using the :option:`--language` option. When enabling `built-in languages`_,
it is possible to use either the language name like `Finnish` or the language
code like `fi`. Both names and codes are case and space insensitive and also
the hyphen (`-`) is ignored. To enable multiple languages, the
:option:`--language` option needs to be used multiple times::

    robot --language Finnish testit.robot
    robot --language pt --language ptbr testes.robot

The same :option:`--language` option is also used when activating
`custom language files`_. With them the value can be either a path to the file or,
if the file is in the `module search path`_, the module name::

    robot --language Custom.py tests.robot
    robot --language MyLang tests.robot

For backwards compatibility reasons, and to support partial translations,
English is always activated automatically. Future versions may allow disabling
it.

Pre-file configuration
''''''''''''''''''''''

It is also possible to enable languages directly in data files by having
a line `Language: <value>` (case-insensitive) before any of the section
headers. The value after the colon is interpreted the same way as with
the :option:`--language` option::

    Language: Finnish

    *** Asetukset ***
    Dokumentaatio        Example using Finnish.

If there is a need to enable multiple languages, the `Language:` line
can be repeated. These configuration lines cannot be in comments so something like
`# Language: Finnish` has no effect.

Due to technical limitations, the per-file language configuration affects also
parsing subsequent files as well as the whole execution. This
behavior is likely to change in the future and *should not* be relied upon.
If you use per-file configuration, use it with all files or enable languages
globally with the :option:`--language` option.

Built-in languages
~~~~~~~~~~~~~~~~~~

The following languages are supported out-of-the-box. Click the language name
to see the actual translations:

.. START GENERATED CONTENT
.. Generated by translations.py used by ug2html.py.

- `Bulgarian (bg)`_
- `Bosnian (bs)`_
- `Czech (cs)`_
- `German (de)`_
- `Spanish (es)`_
- `Finnish (fi)`_
- `French (fr)`_
- `Hindi (hi)`_
- `Italian (it)`_
- `Dutch (nl)`_
- `Polish (pl)`_
- `Portuguese (pt)`_
- `Brazilian Portuguese (pt-BR)`_
- `Romanian (ro)`_
- `Russian (ru)`_
- `Swedish (sv)`_
- `Thai (th)`_
- `Turkish (tr)`_
- `Ukrainian (uk)`_
- `Chinese Simplified (zh-CN)`_
- `Chinese Traditional (zh-TW)`_

.. END GENERATED CONTENT

All these translations have been provided by the awesome Robot Framework
community. If a language you are interested in is not included, you can
consider contributing__ it!

__ `Contributing translations`_

Custom language files
~~~~~~~~~~~~~~~~~~~~~

If a language you would need is not available as a built-in language, or you
want to create a totally custom language for some specific need, you can easily
create a custom language file. Language files are Python files that contain
one or more language definitions that are all loaded when the language file
is taken into use. Language definitions are created by extending the
`robot.api.Language` base class and overriding class attributes as needed:

.. sourcecode:: python

    from robot.api import Language


    class Example(Language):
        test_cases_header = 'Validations'
        tags_setting = 'Labels'
        given_prefixes = ['Assuming']
        true_strings = ['OK', '\N{THUMBS UP SIGN}']

Assuming the above code would be in file :file:`example.py`, a path to that
file or just the module name `example` could be used when the language file
is activated__.

The above example adds only some of the possible translations. That is fine
because English is automatically enabled anyway. Most values must be specified
as strings, but BDD prefixes and true/false strings allow more than one value
and must be given as lists. For more examples, see Robot Framework's internal
languages__ module that contains the `Language` class as well as all built-in
language definitions.

__ `Enabling languages`_
__ https://github.com/robotframework/robotframework/blob/master/src/robot/conf/languages.py

Contributing translations
~~~~~~~~~~~~~~~~~~~~~~~~~

If you want to add translation for a new language or enhance existing, head
to Crowdin__ that we use for collaboration. For more details, see the
separate Localization__ project, and for questions and free discussion join
the `#localization` channel on our Slack_.

__ https://robotframework.crowdin.com
__ https://github.com/MarketSquare/localization
