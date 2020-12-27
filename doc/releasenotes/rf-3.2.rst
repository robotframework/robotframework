===================
Robot Framework 3.2
===================

.. default-role:: code

`Robot Framework`_ 3.2 is a new major release with an enhanced test data
parser, handy `@library` and `@not_keyword` decorators, enhanced Libdoc
spec files for external tools, inline Python evaluation support, and many
other interesting new features and lot of bug fixes.

Questions and comments related to the release can be sent to the
`robotframework-users`_ mailing list or to `Robot Framework Slack`_,
and possible bugs submitted to the `issue tracker`_.

If you have pip_ installed, just run

::

   pip install --upgrade robotframework

to install the latest available stable release or use

::

   pip install robotframework==3.2

to install exactly this version.

Alternatively you can download the source distribution from PyPI_ and install
it manually. The standalone jar distribution is available at the
`Maven Central`_. For more details and other installation approaches,
see the `installation instructions`_.

Robot Framework 3.2 was released on Monday April 27, 2020.

**NOTE:** Robot Framework 3.2 had two severe regressions. All users are
recommended to upgrade to `Robot Framework 3.2.1 <rf-3.2.1.rst>`_
that was released on Monday May 4, 2020.

.. _Robot Framework: http://robotframework.org
.. _Robot Framework Foundation: http://robotframework.org/foundation
.. _pip: http://pip-installer.org
.. _PyPI: https://pypi.python.org/pypi/robotframework
.. _Maven Central: https://search.maven.org/artifact/org.robotframework/robotframework
.. _issue tracker milestone: https://github.com/robotframework/robotframework/issues?q=milestone%3Av3.2
.. _issue tracker: https://github.com/robotframework/robotframework/issues
.. _robotframework-users: http://groups.google.com/group/robotframework-users
.. _Robot Framework Slack: https://robotframework-slack-invite.herokuapp.com
.. _installation instructions: ../../INSTALL.rst


.. contents::
   :depth: 2
   :local:


Most important enhancements
===========================

New test data parser
--------------------

The absolutely biggest new feature in Robot Framework 3.2 is the new test
data parser (`#3076`_). The parser has been totally rewritten, but for most
parts it should work exactly like the earlier one.

The most important reason for the parser rewrite was making it possible to
add new syntax to Robot Framework in the future. No new syntax is introduced
yet in Robot Framework 3.2, but there are plans to add, for example,
`IF/ELSE` (`#3074`_), `TRY/EXCEPT` (`#3075`_), and nested control structures
(`#3079`_) in `Robot Framework 4.0`__ sometime in 2021.

The new parser also has much better APIs for external tools like editors,
linters and code formatters than the old one (`#3373`_). See the `API
documentation`__ for more information and examples. The drawback of the new
APIs is that tools using the old parsing APIs need to be updated.

New parsing APIs are already used by the `robotframework-lsp project`__
that exposes parsing (and other) APIs to editors and IDEs via the
`language server protocol (LSP)`__. This is a new project but definitely worth
checking out for anyone interested in developing editor plugins for Robot
Framework. The project also has ready-made integration to VSCode.

For the user the biggest direct enhancements provided by the new parser are
storing line numbers during parsing (`#549`_) and preserving ellipsis (`...`)
denoting line continuation (`#1272`_). The former means that many error
messages nowadays tell on which line the error occurred and the latter means
that tools like Tidy do not mess up the original formatting (`#2579`_).

The new parser supports only the plain text format (`#3081`_). This means
that the HTML format is not supported at all and the TSV format is supported
only when it is fully compatible with the plain text format. Because the
new parser only parses `*.robot` files by default (`#3084`_), users of the
`*.txt`, `*.tsv`, or `*.rst` files need to explicitly use the `--extension`
option.

__ https://github.com/robotframework/robotframework/issues?q=is%3Aopen+is%3Aissue+milestone%3Av4.0
__ https://robot-framework.readthedocs.io/en/master/autodoc/robot.parsing.html#module-robot.parsing
__ https://github.com/robocorp/robotframework-lsp
__ https://microsoft.github.io/language-server-protocol
.. _#3074: https://github.com/robotframework/robotframework/issues/3074
.. _#3075: https://github.com/robotframework/robotframework/issues/3075
.. _#3079: https://github.com/robotframework/robotframework/issues/3079

New `@library` decorator
------------------------

The new `@library` decorator can be used to decorate library classes
(`#3019`_) and it provides these useful features:

- It makes it convenient to set library scope, version, documentation
  format and listener. For example, these two libraries are equivalent:

  .. code-block:: python

      from robot.api.deco import library


      @library(scope='GLOBAL', version='3.2b1')
      class NewWay:

          # actual library code


      class OldWay:
          ROBOT_LIBRARY_SCOPE = 'GLOBAL'
          ROBOT_LIBRARY_VERSION = '3.2b1'

          # actual library code

- It forces using the `@keyword` decorator by default (`#3221`_).
  Only methods decorated with the `@keyword` decorator become keywords:

  .. code-block:: python

      from robot.api.deco import library, keyword


      @library
      class Example:

          @keyword
          def example_keyword(self):
              # ...

          def not_exposed_as_keyword(self):
              # ...

  If this behavior is needed with modules, it can be enabled by setting
  a module level attribute `ROBOT_AUTO_KEYWORDS = False`. If this behavior
  needs to be disabled when using the `@library` decorator, it is possible
  to use `@library(auto_keywords=True)`.

New `@not_keyword` decorator
----------------------------

The `@not_keyword` decorator is another way to tell Robot Framework that
a certain function or methods should not be considered a keyword (`#3455`_):

.. code-block:: python

    from robot.api.deco import not_keyword


    def example_keyword():
        # ...

    @not_keyword
    def not_exposed_as_keyword():
        # ...

This functionality is also used to mark the old `@keyword` decorator, the
new `@library` decorator, and the `@not_keyword` decorator itself as not
being keywords (`#3454`_).

Enhanced Libdoc spec files
--------------------------

The Libdoc tool is typically used for creating library documentation in HTML
for humans to read, but it can also create XML spec files where external tools
can easily read all the same information. These spec files have been enhanced
heavily in Robot Framework 3.2:

- Actual library and keyword documentation in spec files can be converted to
  HTML format by using the new `XML:HTML` format like `--format XML:HTML` (`#3301`_).

- Support for custom `*.libspec` extension has been added (`#3491`_).
  When an output file has that extension, Libdoc uses the aforementioned
  `XML:HTML` format by default.

- Spec files have an XSD schema (`#3520`_). It can be used for validation and
  it also thoroughly documents the spec format. The schema can be found here__.

- Somewhat related to the above, the `specversion` attribute tells the spec
  version that has been used (`#3523`_). The current version is 2 and it will
  incremented if and when changes are made.

- Library and keyword source information is included (`#3507`_). This includes
  a relative path to the file where library and each keyword is implemented
  along with the line number.

- Deprecated keywords get `deprecated="true"` attribute automatically (`#3498`_).

- `scope` and `namedargs` elements have been changed to attributes (`#3522`_).
  `scope` is nowadays consistently `GLOBAL`, `SUITE` or `TEST` (`#3532`_)
  and `namedargs` is a Boolean and not string `yes/no`. For backwards
  compatibility reasons the old `scope` and `namedargs` elements are still
  written to the spec files with old values.

- `type` attribute values have been changed to upper case `LIBRARY` and
  `RESOURCE` (`#3534`_). Tools using this information need to be updated.

- `generated` attribute has been changed from local time in custom format to
  UTC time represented as `xsd:dateTime`__ (`#3528`_). Tools using this
  value need to be updated.

__ https://github.com/robotframework/robotframework/tree/master/doc/schema
__ http://www.datypic.com/sc/xsd/t-xsd_dateTime.html

Inline Python evaluation
------------------------

Another nice feature is being able to evaluate Python expressions inline
using a variation of the variable syntax like `${{expression}}` (`#3179`_).
The actual `expression` syntax is basically the same that the `Evaluate`
keyword and some other keywords in the BuiltIn__ library support. The main
difference is that these keywords always evaluate expressions and thus the
`${{}}` decoration is not needed with them.

Main use cases for this pretty advanced functionality are:

- Evaluating Python expressions involving Robot Framework's variables
  (`${{len('${var}') > 3}}`, `${{$var[0] if $var is not None else None}}`).

- Creating values that are not Python base types
  (`${{decimal.Decimal('0.11')}}`, `${{datetime.date(2020, 4, 27)}}`).

- Creating values dynamically (`${{random.randint(0, 100)}}`,
  `${{datetime.date.today()}}`).

- Constructing collections, including nested collections (`${{[1, 2, 3, 4]}}`,
  `${{ {'id': 1, 'name': 'Example', children: [7, 9]} }}`).

- Accessing constants and other useful attributes in Python modules
  (`${{math.pi}}`, `${{platform.system()}}`).

This is somewhat similar functionality than the old `extended variable
syntax`__. As the examples above illustrate, this syntax is even more
powerful as it provides access to Python built-ins like `len()` and modules
like `math`. In addition to being able to use variables like `${var}` in
the expressions (they are replaced before evaluation), variables are also
available using the special `$var` syntax during evaluation.

Related to this change, also `Evaluate` and other BuiltIn keywords that
evaluate expressions import modules automatically (`#3349`_).

__ http://robotframework.org/robotframework/latest/libraries/BuiltIn.html#Evaluating%20expressions
__ http://robotframework.org/robotframework/latest/RobotFrameworkUserGuide.html#extended-variable-syntax

Native `&{dict}` iteration with FOR loops
-----------------------------------------

FOR loops support iterating dictionary items if values are `&{dict}`
variables (`#3485`_)::

    FOR    ${key}    ${value}    IN    &{dict}
        Log    Key is '${key}' and value is '${value}'.
    END

It is possible to use multiple dictionaries and add additional items
using the `key=value` syntax::

    FOR    ${key}    ${value}    IN    &{first}    &{second}    one=more
        Log    Key is '${key}' and value is '${value}'.
    END

If same keys is used multiple times, the last value is used but the original
order of keys is preserved.

In the future this syntax will be generalized so that it works also if all
values use the `key=value` syntax even if none of the values is a `&{dict}`
variable. In Robot Framework 3.1 such usage causes a deprecation warning.
Escaping like `key\=value` is possible to avoid dictionary iteration.

In addition to using separate loop variables for key and value, it is
possible to use one variable that then becomes a key-value tuple::

    FOR    ${item}    IN    &{dict}
        Length Should Be    ${item}    2
        Log    Key is '${item}[0]' and value is '${item}[1]'.
    END

The dictionary iteration works also with the FOR IN ENUMERATE loops::

    FOR    ${index}    ${key}    ${value}    IN ENUMERATE    &{dict}
        Log    Key is '${key}' and value is '${value}' at index ${index}.
    END
    FOR    ${item}    IN ENUMERATE    &{dict}
        Length Should Be    ${item}    3
        Log    Key is '${item}[1]' and value is '${item}[2]' at index ${item}[0].
    END

Listeners can add and remove tests
----------------------------------

Listeners__ are a powerful feature of Robot Framework and RF 3.2 makes
them a bit more powerful. Earlier listeners using the API v3 could not add
or remove new tests in their `start/end_test` methods (`#3251`_), but this
limitation has now been lifted. This makes it easier to implement advanced
tooling, for example, for model based testing using Robot Framework in its
core.

__ http://robotframework.org/robotframework/latest/RobotFrameworkUserGuide.html#listener-interface

Signatures of "wrapped" keywords are read correctly
---------------------------------------------------

When implementing keywords in libraries, it is sometimes useful to modify
them with `Python decorators`__. However, decorators often modify function
signatures and can thus confuse Robot Framework's introspection when
determining which arguments keywords accept. This includes also argument
default values and type hints.

Starting from Robot Framework 3.2 and when using Python 3, it is possible to
avoid this problem by decorating the decorator itself using `functools.wraps`__
(`#3027`_). In that case Robot Framework will automatically "unwrap" the
function or method to see the real signature.

__ https://realpython.com/primer-on-python-decorators/
__ https://docs.python.org/library/functools.html#functools.wraps

Standalone jar distribution updated to use Jython 2.7.2
-------------------------------------------------------

The standalone jar distribution was earlier based on Jython 2.7.0 but
nowadays it uses Jython 2.7.2 (`#3383`_). This brings all features and fixes
in the newer Jython version. The standalone jar is available at the
`Maven Central`_.

Continuous integrating
----------------------

Robot Framework project has not had working continuous integration (CI)
since the Nokia days but now we finally have it again (`#3420`_). Our CI
system is based on `GitHub actions`__ and it runs tests automatically every
time code is pushed to the repository or a pull request is opened. You
can see all actions at https://github.com/robotframework/robotframework/actions.

__ https://github.com/features/actions


Backwards incompatible changes
==============================

Although we try to avoid backwards incompatible changes, sometimes adding new
features mean that old features need to be changed or even removed. This is
never done lightly and we try to limit backwards incompatible changes to
major releases. In Robot Framework 3.2 these changes are mainly related to
parsing.

HTML and TSV formats are not supported anymore
----------------------------------------------

The new test data parser (`#3076`_) supports only the plain text format
and as a result neither HTML nor TSV formats are supported anymore (`#3081`_).
The TSV format still works if it is fully compatible with the plain text
format, but the support for the HTML format has been removed for good.

Only `*.robot` files are parsed by default
------------------------------------------

When executing a directory, Robot Framework nowadays only parsers `*.robot`
files by default (`#3084`_). Users of the `*.txt`, `*.tsv`, or `*.rst` file
need to explicitly use the `--extension` option like `--extension tsv` or
`--extension robot:tsv`. When executing a single file, the file is parsed
regardless the extension.

Parsing APIs have been rewritten
--------------------------------

One of the nice features of the `new test data parser`_ is the new stable
parsing API (`#3373`_). Unfortunately this API is stable only going forward,
and all tools using the old parsing API need to be updated when migrating
to Robot Framework 3.2. To see what has changed, see the old__ and new__
API documentation. Depending on the use case, it may be possible to instead use
the higher level `TestSuiteBuilder()`__ that has seen only minor configuration
changes.

__ https://robot-framework.readthedocs.io/en/v3.1.2/autodoc/robot.parsing.html
__ https://robot-framework.readthedocs.io/en/master/autodoc/robot.parsing.html
__ https://robot-framework.readthedocs.io/en/master/autodoc/robot.running.builder.html#robot.running.builder.builders.TestSuiteBuilder

Changes to recognizing and evaluating variables
-----------------------------------------------

When finding variables, all un-escaped curly braces in the variable body are
nowadays expected to be closed, when earlier the first closing curly brace
ended the variable (`#3288`_). This means that, for example, `${foo{bar}zap}`
is a single variable, but it used to be considered a variable `${foo{bar}`
followed by a literal string `zap}`. This also applies to variable item access
syntax `${var}[item]` so that possible unescaped opening square brackets in
the `item` part are expected to be closed.

This change was done to make it possible to implement inline Python evaluation
using `${{expression}}` syntax (`#3179`_). Another benefit of the change is
that `embedded arguments`__ containing custom patterns can be specified without
escaping like `${date:\d{4}-\d{2}-\d{2}}`. Unfortunately it also means that
the old `${date:\d{4\}-\d{2\}-\d{2\}}` syntax will not work anymore. A
workaround that works regardless Robot Framework version is avoiding curly
braces like `${date:\d\d\d\d-\d\d-\d\d}`.

In addition to the variable parsing logic changing, also variable evaluation
changes a little. These changes are limited to handling possible escape
characters in variable body (`#3295`_) and thus unlikely to cause bigger
problems.

__ http://robotframework.org/robotframework/latest/RobotFrameworkUserGuide.html#embedded-argument-syntax

Variables in test case names are resolved
-----------------------------------------

Earlier test case names were always used as-is, without replacing possible
variables in them, but this was changed by `#2962`_. If this causes problems,
variables need to be escaped like `Example \${name}`.

Changes to handling non-ASCII spaces
------------------------------------

The old parser handled `non-ASCII spaces`__ such as the no-break space
somewhat inconsistently (`#3121`_). The new parser fixes that and as a result
changes the syntax a little. Luckily it is pretty unlikely that these changes
affect anyone.

- Any space character is considered a separator. Earlier only the normal ASCII
  space and the no-break space were considered separators.
- Non-ASCII spaces in test data itself (i.e. not in separators) are not
  converted to normal spaces anymore. You can, for example, have an argument
  with a no-break space.
- When using the `pipe-separated format`_, consecutive spaces are not
  collapsed anymore. This affects also normal spaces, not only non-ASCII
  spaces.

__ http://jkorpela.fi/chars/spaces.html
.. _pipe-separated format: http://robotframework.org/robotframework/latest/RobotFrameworkUserGuide.html#pipe-separated-format

Old for loop style not supported with pipe-separated format
-----------------------------------------------------------

RF 3.2 deprecates the `old-style for loops`__ in general, but when using
the `pipe-separated format`_ there are even bigger changes. Earlier it was
possible to use syntax like

::

    | :FOR | ${x} | IN | 1 | 2
    |      | Log  | ${x}

but this is not supported anymore at all. The recommended way to resolve this
problem is switching to the new for loop style where `:FOR` is replaced with
`FOR` and an explicit `END` marker is added::

    | FOR | ${x} | IN | 1 | 2
    |     | Log  | ${x}
    | END |

For alternatives and more details in general see issue `#3108`_.

__ `Old for loop syntax`_
.. _#3108: https://github.com/robotframework/robotframework/issues/3108

Stricter section and setting name syntax
----------------------------------------

Section names like `Test Cases` and setting names like `Test Setup` are
nowadays space sensitive (`#3082`_). In practice this means that sections
like `TestCases` or settings like `TestSetup` are not recognized.

Stricter for loop separator syntax
----------------------------------

For loop separators `IN`, `IN RANGE`, `IN ZIP` and `IN ENUMERATE` are both
case and space sensitive (`#3083`_). In other works, separators like `in`
or `INZIP` are nor recognized. Notice also that the `old FOR loop syntax`_
has been deprecated in general.

Libdoc spec files have changed
------------------------------

As `discussed earlier`__, Libdoc spec files have been enhanced heavily.
Most of the changes are backwards compatible, but these changes may cause
problems for tools using the spec files:

- `type` attribute values have been changed to upper case `LIBRARY` and
  `RESOURCE` (`#3534`_).

- `generated` attribute has been changed from local time in custom format to
  UTC time represented as `xsd:dateTime`__ (`#3528`_).

__ `Enhanced Libdoc spec files`_
__ http://www.datypic.com/sc/xsd/t-xsd_dateTime.html

Pre-run modifiers are run before selecting tests cases to be executed
---------------------------------------------------------------------

Earlier possible `--test`, `--suite`, `--include`, and `--exclude` were
executed before running `pre-run modifiers`__, but that order has now
been reversed. The main reason was to allow using the aforementioned command
line options to match also tests generated by pre-run modifiers. Possible
use cases where the old order was important are obviously affected. If such
usages are common, we can consider reverting this change or somehow making
it possible to select which order to use.

__ http://robotframework.org/robotframework/latest/RobotFrameworkUserGuide.html#programmatic-modification-of-test-data

Other backwards incompatible changes
------------------------------------

- Using variable item access syntax like `${var}[0]` works with all sequences
  including strings and bytes (`#3182`_). With RF 3.1 that caused an error with
  sequences that were not considered list-like and with earlier versions
  this syntax was interpreted as variable `${var}` followed by a literal
  string `[0]`.

- BuiltIn keywords `Should Contain X Times` and `Get Count` argument names
  have been changed from `item1, item2` to `container, item` to be consistent
  with other similar keywords (`#3486`_). This affects tests only if keywords
  have been used with the named argument syntax like `item2=xxx`.

- String library methods `convert_to_uppercase` and `convert_to_lowercase`
  have been renamed to `convert_to_upper_case` to `convert_to_lower_case`,
  respectively (`#3484`_). This does not affect how keywords can be used in
  test data (both `Convert To Upper Case` and `Convert To Uppercase` variants
  work with all releases) but if someone uses these methods programmatically
  those usages need to be changes. There should be no need for such usage,
  though, as Python strings have built-in `upper` and `lower` methods.

- Support for custom timeout messages has been removed (`#2291`_). This
  functionality was deprecated already in Robot Framework 3.0.1 and it
  has now finally been removed.

- `--escape` option has been removed (`#3085`_). This option used to allow
  escaping problematic characters on the command line. Shell escaping or
  quoting mechanism needs to be used instead.

- `--warnonskippedfiles` option has been removed (`#3086`_). This option did
  not have any effect anymore and has now been removed altogether.

- Using `&{dict}` variable with FOR loops initiates dictionary iteration
  (`#3485`_). If this is not desired, the variable syntax should be changed
  to `${dict}`.


Deprecated features
===================

Whenever we notice a feature that needs to be changed in backwards incompatible
manner, we try to first deprecate the feature at least one major release before
the removal. There are not that many deprecations in Robot Framework 3.2, but
unfortunately especially changes to the for loop syntax are likely to affect
many users.

Old FOR loop syntax
-------------------

Robot Framework 3.1 `enhanced FOR loop syntax`__ so that nowadays loops can
be written like this::

   FOR    ${animal}    IN    cat    dog    cow
       Keyword    ${animal}
       Another keyword
   END

This is a big improvement compared to the old syntax that required starting
the loop with `:FOR` and escaping all keywords inside the loop with a
backslash::

   :FOR    ${animal}    IN    cat    dog    cow
   \    Keyword    ${animal}
   \    Another keyword

In Robot Framework 3.1 both the old and new formats worked without any
warnings, but using `:FOR` instead of `FOR` (`#3080`_) and not closing
the loop with an explicit `END` (`#3078`_) are both deprecated in Robot
Framework 3.2. The old syntax will be removed for good in Robot Framework 4.0.

This change is likely to cause lot of deprecation warnings and requires users
to update their test data. Here are some ideas how to find and updated the
data:

- Run tests and see how many deprecation warnings you get. The warning should
  tell where the old syntax is used. Even if you use some other way to find
  these usages, running tests tells you have you caught them all.
- Use the `Tidy tool`__ to update data. It also changes data otherwise, so
  it is a good idea to check changes and possibly commit only changes relevant
  to FOR loops. Tidy updates the old FOR loop syntax to new one starting from
  Robot Framework 3.1.2.
- Use operating system search functionality to find `:FOR` (case-insensitively)
  as well as possible `: FOR` variant from test data files. Then update loops
  by hand.
- Use an external command line tool like ack__ (Perl) or pss__ (Python) to
  find `:FOR` and `: FOR` and update data by hand. If using the `pss` tool,
  this command works well::

     pss -ai ": ?FOR" path/to/tests

__ https://github.com/robotframework/robotframework/blob/master/doc/releasenotes/rf-3.1.rst#for-loop-enhancements
__ http://robotframework.org/robotframework/latest/RobotFrameworkUserGuide.html#tidy
__ https://beyondgrep.com/
__ https://pypi.org/project/pss/

FOR loops when all values are in `key=value` syntax
---------------------------------------------------

The `&{dict}` iteration syntax with FOR loops (`#3485`_) supports giving
additional items using the `key=value` syntax like::

   FOR    ${key}    ${value}    IN    &{dict}    another=item    one=more
       Log    Key is '${key}' and value is '${value}'.
   END

In the future this will be generalized so that the same syntax works also
if none of the values is a `&{dict}` variable::

   FOR    ${key}    ${value}    IN    key=value    another=item    one=more
       Log    Key is '${key}' and value is '${value}'.
   END

With Robot Framework 3.2 the above syntax still works as it did earlier
but there is a deprecation warning. Notice that this problem occurs *only*
if all values are like `xxx=yyy`. An easy way to avoid is it escaping
at least one of the values like `xxx\=yyy`.

Accessing list and dictionary items using `@{var}[item]` and `&{var}[item]`
---------------------------------------------------------------------------

Robot Framework 3.1 enhanced the `syntax for accessing items in nested lists
and dictionaries`__ by making it possible to use `${var}[item]` and
`${var}[nested][item]` syntax regardless is `${var}` a list or dictionary.
The old variable type specific syntax `@{list}[item]` and `&{dict}[item]`
still worked, but this usage has now been deprecated (`#2974`_).

Also this deprecation is likely to cause quite a lot of warnings and require
users to update their data. Exactly like with for loops discussed above,
running tests is the easiest way to find out how much work there actually is.
The Tidy tool cannot handle this deprecation, but otherwise same approach
works to find these usages that was recommended with old for loops. If using
the `pss` tool, these commands help::

  pss -ai "@\{.+\}\[" path/to/tests
  pss -ai "&\{.+\}\[" path/to/tests

__ https://github.com/robotframework/robotframework/blob/master/doc/releasenotes/rf-3.1.rst#accessing-nested-list-and-dictionary-variable-items

Ignoring space after literal newline is deprecated
--------------------------------------------------

Earlier `two\n lines` has been considered equivalent to `two\nlines` in
Robot Framework data. This syntax helped constructing multiline strings when
using the HTML format, but now that the HTML format is not supported this
syntax has been deprecated (`#3333`_). It is unlikely that it would have
been used widely.


Acknowledgements
================

Robot Framework 3.2 development has been sponsored by the `Robot Framework
Foundation`_. Due to the foundation getting some more members and thus more
resources, there has now been two active (but part-time) developers.
`Pekka Klärck <https://github.com/pekkaklarck>`_ has continued working as
the lead developer and `Janne Härkönen <https://github.com/yanne>`_ has been
driving the new parser development. Big thanks to all the `30+ member
organizations <https://robotframework.org/foundation/#members>`_ for making
that possible and for your support in general! Hopefully the foundation growth
continues and we can speed up the development even more in the future.

In addition to the work sponsored by the foundation, we have got several
great contributions by the wider open source community:

- `Simandan Andrei-Cristian <https://github.com/cristii006>`__
  implemented the `@library` decorator (`#3019`_),
  added possibility to force using the `@keyword` decorator (`#3221`_),
  created the `Set Local Variable` keyword (`#3091`_) and
  added note to the Screenshot library documentation about the more powerful
  `ScreenCapLibrary <https://github.com/mihaiparvu/ScreenCapLibrary>`__
  (`#3330`_)

- `Bollen Nico <https://github.com/bollenn>`__ and
  `JasperCraeghs <https://github.com/JasperCraeghs>`__
  added support to use variable index access like `${var}[2]` with all
  sequences, including strings and bytes (`#3182`_)

- `Mihai Pârvu <https://github.com/mihaiparvu>`__
  added support to read "wrapped" signatures correctly (`#3027`_) and
  enhanced Libdoc, TestDoc and Tidy tools as well as Robot Framework's syslog
  files to automatically create output directories (`#2767`_)

- `René <https://github.com/Snooz82>`__
  made it possible to store documentation in Libdoc XML spec files using HTML
  regardless the original documentation format (`#3301`_) and helped
  creating XSD schema for these spec files (`#3520`_)

- `Dirk Richter <https://github.com/DirkRichter>`__
  added support to automatically expand certain keywords in the log file (`#2698`_)

- `Vladimir Vasyaev <https://github.com/VVasyaev>`__
  enhanced the built-in support for environment variables to allow default
  values like `%{EXAMPLE=default}` (`#3382`_)

- `Stavros Ntentos <https://github.com/stdedos>`__
  made it easier to disable process timeouts when using the Process library
  (`#3366`_) and fixed equality checking with `Tags` objects (`#3242`_)

- `Adrian Yorke <https://github.com/adrianyorke>`_
  implemented support to disable stdout and stderr altogether when using
  the Process library (`#3397`_)

- `Bharat Patel <https://github.com/bbpatel2001>`__
  enhanced `Lists Should Be Equal` keyword to allow ignoring order (`#2703`_)
  and provided initial implementation to `Convert To Title Case` keyword (`#2706`_)

- `Richard Turc <https://github.com/yamatoRT>`__
  added support to use variables in test case names (`#2962`_)

- `Theodoros Chatzigiannakis <https://github.com/TChatzigiannakis>`__
  fixed connection problems with the Remote library in some scenarios (`#3300`_)

- `Jarkko Peltonen <https://github.com/jpeltonen>`__
  fixed Dialogs library leaving dialogs minimized at least on Windows Server
  2016 (`#3492`_)

- `Hélio Guilherme <https://github.com/HelioGuilherme66>`__
  fixed Screenshot library with wxPython 4.0.7 on Linux (`#3403`_)

- `Jani Mikkonen <https://github.com/rasjani>`__
  enhanced Libdoc to allow viewing keywords with a certain tag by using query
  parameters in the URL (`#3440`_)

- `Mikhail Kulinich <https://github.com/tysonite>`__
  enhanced test message when results are merged with `rebot --merge` (`#3319`_)

- `Lukas Breitstadt <https://github.com/lubrst>`__
  fixed using the `ExecutionResult` API with bytes (`#3194`_)

- `Ossi R. <https://github.com/osrjv>`__
  added support for svg image links in documentation (`#3464`_)

- `Teddy Lee <https://github.com/Teddy12090>`__
  enhance documentation syntax to support images with data URIs (`#3536`_)

- `Marcin Koperski <https://github.com/IlfirinPL>`__
  enhanced the `plural_or_not` used also by other tools to consider `-1`
  singular (`#3460`_)

- `Mikhail Kulinich <https://github.com/tysonite>`__ and
  `Juho Saarinen <https://github.com/hi-fi>`__ set up CI system for
  the Robot Framework project (`#3420`_)

During the Robot Framework 3.2 development the total number of
contributors to the `Robot Framework project
<https://github.com/robotframework/robotframework>`__ has gone over 100.
That is a big number and a big milestone for the whole community!
Huge thanks to all contributors and to everyone else who has reported
problems, tested preview releases, participated discussion on various
forums, or otherwise helped to make Robot Framework as well as the ecosystem
and community around it better.

Thanks everyone and hopefully Robot Framework 3.2 works great for you!

| `Pekka Klärck <https://github.com/pekkaklarck>`__,
| Robot Framework Lead Developer


Full list of fixes and enhancements
===================================

.. list-table::
    :header-rows: 1

    * - ID
      - Type
      - Priority
      - Summary
    * - `#3076`_
      - enhancement
      - critical
      - New test data parser
    * - `#3081`_
      - enhancement
      - critical
      - Remove support for HTML and TSV formats
    * - `#3251`_
      - bug
      - high
      - Listeners cannot add/remove tests in their `start/end_test` methods
    * - `#1272`_
      - enhancement
      - high
      - Parsing modules should preserve ellipsis (...) denoting line continuation
    * - `#2579`_
      - enhancement
      - high
      - Tidy should not merge continued lines
    * - `#3019`_
      - enhancement
      - high
      - `@library` decorator that supports configuring and forces using `@keyword` to mark keywords
    * - `#3027`_
      - enhancement
      - high
      - Read signature (argument names, defaults, types) from "wrapped" keywords correctly
    * - `#3078`_
      - enhancement
      - high
      - Deprecate `FOR` loops without `END`
    * - `#3080`_
      - enhancement
      - high
      - Deprecate FOR loops starting with case-insensitive `:FOR`
    * - `#3084`_
      - enhancement
      - high
      - Remove support to parse other than `*.robot` files by default
    * - `#3179`_
      - enhancement
      - high
      - Inline Python evaluation support using `${{expression}}` syntax
    * - `#3221`_
      - enhancement
      - high
      - Possibility to consider only methods decorated with `@keyword` keywords
    * - `#3373`_
      - enhancement
      - high
      - Stable parsing APIs
    * - `#3383`_
      - enhancement
      - high
      - Update standalone jar distribution to use Jython 2.7.2
    * - `#3420`_
      - enhancement
      - high
      - Continuous integrating (CI)
    * - `#3455`_
      - enhancement
      - high
      - Add `@not_keyword` decorator to mark functions "not keywords"
    * - `#3485`_
      - enhancement
      - high
      - Native `&{dict}` iteration with FOR loops
    * - `#3507`_
      - enhancement
      - high
      - Include library and keyword source information in Libdoc spec files
    * - `#549`_
      - enhancement
      - high
      - Test parser should retain source line numbers
    * - `#3201`_
      - bug
      - medium
      - `Log List` and some other keywords in Collections and BuiltIn fail with tuples
    * - `#3213`_
      - bug
      - medium
      - Using abstract base classes directly from `collections` causes deprecation warning
    * - `#3226`_
      - bug
      - medium
      - XML library does not work with non-ASCII bytes on Python 2 or any bytes on Python 3
    * - `#3229`_
      - bug
      - medium
      - Variable in keyword teardown name causes failure in dry-run mode
    * - `#3259`_
      - bug
      - medium
      - Libdoc doesn't handle bytes containing non-ASCII characters in keyword arguments
    * - `#3263`_
      - bug
      - medium
      - Tidy does not preserve data before first section
    * - `#3264`_
      - bug
      - medium
      - Robot output can crash when piping output
    * - `#3265`_
      - bug
      - medium
      - `--test/--suite/--include/--exclude` don't affect tests added by pre-run modifiers
    * - `#3268`_
      - bug
      - medium
      - Execution crashes if directory is not readable
    * - `#3295`_
      - bug
      - medium
      - Inconsistent handling of escape character inside variable body
    * - `#3300`_
      - bug
      - medium
      - Remote library fails to connect in some scenarios
    * - `#3306`_
      - bug
      - medium
      - DateTime: `Get Current Date` with epoch format and timezone UTC return wrong value
    * - `#3338`_
      - bug
      - medium
      - Problems reporting errors when library import fails on Python 2 and import path contains non-ASCII characters
    * - `#3355`_
      - bug
      - medium
      - `Evaluate`: Using nested modules like `modules=rootmodule.submodule` does not work
    * - `#3364`_
      - bug
      - medium
      - Non-ASCII paths to test data not handled correctly with Jython 2.7.1+
    * - `#3403`_
      - bug
      - medium
      - Screenshot library doesn't work with wxPython 4.0.7 on Linux
    * - `#3424`_
      - bug
      - medium
      - Windows console encoding set with `chcp` not detected
    * - `#3454`_
      - bug
      - medium
      - `@keyword` decorator should not be exposed as keyword
    * - `#3483`_
      - bug
      - medium
      - Libdoc: Not possible to link to Tags section
    * - `#3500`_
      - bug
      - medium
      - Rerun functionality fails if test contains `[x]`
    * - `#3540`_
      - bug
      - medium
      - `Log Variables` fails is variable value is iterable but iteration fails
    * - `#2291`_
      - enhancement
      - medium
      - Remove possibility to specify custom timeout message
    * - `#2698`_
      - enhancement
      - medium
      - Possibility to automatically expand certain keywords in log file
    * - `#2703`_
      - enhancement
      - medium
      - `Lists Should Be Equal` keyword in Collections should have an option to ignore order
    * - `#2706`_
      - enhancement
      - medium
      - String: Add `Convert To Title Case` keyword
    * - `#2974`_
      - enhancement
      - medium
      - Deprecate accessing list/dict items using syntax `@{var}[item]` and `&{var}[item]`
    * - `#3085`_
      - enhancement
      - medium
      - Remove support using `--escape` to escape characters problematic on console
    * - `#3091`_
      - enhancement
      - medium
      - Add `Set Local Variable` keyword
    * - `#3121`_
      - enhancement
      - medium
      - Consistent handling of whitespace in test data
    * - `#3182`_
      - enhancement
      - medium
      - Support variable index access like `${var}[2]` with all sequences (incl. strings and bytes)
    * - `#3194`_
      - enhancement
      - medium
      - `ExecutionResult` should support input as bytes
    * - `#3202`_
      - enhancement
      - medium
      - Upgrade jQuery used by logs and reports
    * - `#3261`_
      - enhancement
      - medium
      - Add missing `list` methods to internally used `ItemList`
    * - `#3269`_
      - enhancement
      - medium
      - Support any file extension when explicitly running file and when using `--extension`
    * - `#3280`_
      - enhancement
      - medium
      - Libdoc: Support automatic generation of table of contents when using "robot format"
    * - `#3288`_
      - enhancement
      - medium
      - Require variables to have matching opening and closing curly braces and square brackets
    * - `#3301`_
      - enhancement
      - medium
      - Libdoc: Support converting docs to HTML with XML outputs
    * - `#3319`_
      - enhancement
      - medium
      - Enhance test message when results are merged with `rebot --merge`
    * - `#3333`_
      - enhancement
      - medium
      - Deprecate ignoring space after literal newline
    * - `#3349`_
      - enhancement
      - medium
      - Automatically import modules that are used with `Evaluate`, `Run Keyword If`, and others
    * - `#3366`_
      - enhancement
      - medium
      - `Run Process`: Ignore timeout if it is zero, negative or string `None`
    * - `#3382`_
      - enhancement
      - medium
      - Default values for environment variables
    * - `#3397`_
      - enhancement
      - medium
      - `Process`: Add option to disable stdout and stderr
    * - `#3440`_
      - enhancement
      - medium
      - Libdoc: Allow showing keywords based on tags using query string in URL
    * - `#3449`_
      - enhancement
      - medium
      - Support tokenizing strings with variables
    * - `#3451`_
      - enhancement
      - medium
      - Expose test line number via listener API v2
    * - `#3463`_
      - enhancement
      - medium
      - Setting suggestions when using invalid setting
    * - `#3464`_
      - enhancement
      - medium
      - Add support for svg image links in documentation
    * - `#3491`_
      - enhancement
      - medium
      - Libdoc: Support `*.libspec` extension when reading library information from spec files
    * - `#3494`_
      - enhancement
      - medium
      - FOR IN ZIP and FOR IN ENUMERATE enhancements
    * - `#3498`_
      - enhancement
      - medium
      - Libdoc could better handle keywords deprecation info
    * - `#3514`_
      - enhancement
      - medium
      - Dynamic API: Support returning real default values from `get_keyword_arguments`
    * - `#3516`_
      - enhancement
      - medium
      - Dynamic API: Add new `get_keyword_source` method
    * - `#3520`_
      - enhancement
      - medium
      - Libdoc: Create xsd schema for spec files
    * - `#3522`_
      - enhancement
      - medium
      - Libdoc spec files: Change `scope` and `namedargs` to attributes
    * - `#3523`_
      - enhancement
      - medium
      - Add spec version to Libdoc spec files
    * - `#3532`_
      - enhancement
      - medium
      - Libdoc spec files: Change scope to use values `GLOBAL`, `SUITE` and `TEST` consistently
    * - `#2767`_
      - bug
      - low
      - Syslog, Libdoc, Testdoc and Tidy don't create directory for outputs
    * - `#3231`_
      - bug
      - low
      - Log: Automatically formatting URLs does not handle `{` and `}` correctly
    * - `#3242`_
      - bug
      - low
      - `Tags` objects do not support equality checking correctly
    * - `#3260`_
      - bug
      - low
      - Document that Tidy with `--recursive` doesn't process resource files
    * - `#3339`_
      - bug
      - low
      - Libdoc, TestDoc and Tidy crash if output file is invalid
    * - `#3422`_
      - bug
      - low
      - `--help` text related to disabling output has outdated information
    * - `#3453`_
      - bug
      - low
      - Methods implemented in C are not exposed as keywords
    * - `#3456`_
      - bug
      - low
      - Libdoc: Shortcuts are messed up on Firefox
    * - `#3460`_
      - bug
      - low
      - `plural_or_not` utility should consider `-1` singular
    * - `#3489`_
      - bug
      - low
      - Variable containing `=` in its name should not initiate named argument syntax
    * - `#3524`_
      - bug
      - low
      - Rebot's merge message uses term "test" also with `--rpa`
    * - `#2962`_
      - enhancement
      - low
      - Support variables in test case names
    * - `#3082`_
      - enhancement
      - low
      - Remove support using section and setting names space-insensitively
    * - `#3083`_
      - enhancement
      - low
      - Remove support using for loops with other separators than exact `IN`, `IN RANGE`, `IN ZIP` and `IN ENUMERATE`
    * - `#3086`_
      - enhancement
      - low
      - Remove `--warnonskippedfiles` because it has no effect anymore
    * - `#3195`_
      - enhancement
      - low
      - Support `.yml` extension in addition to `.yaml` extension with YAML variable files
    * - `#3273`_
      - enhancement
      - low
      - UG: Handling documentation split to multiple columns will not change
    * - `#3291`_
      - enhancement
      - low
      - Document making `.robot` files executable
    * - `#3330`_
      - enhancement
      - low
      - Add a note about more powerful ScreenCapLibrary to Screenshot library documentation
    * - `#3365`_
      - enhancement
      - low
      - Document that zero and negative test/keyword timeout is ignored
    * - `#3376`_
      - enhancement
      - low
      - UG: Enhance creating start-up scripts section
    * - `#3415`_
      - enhancement
      - low
      - Document (and test) that glob pattern wildcards like `*` can be escaped like `[*]`
    * - `#3465`_
      - enhancement
      - low
      - Better reporting if using valid setting is used in wrong context
    * - `#3484`_
      - enhancement
      - low
      - String: Rename `convert_to_uppercase` to `convert_to_upper_case` (and same with `lower`)
    * - `#3486`_
      - enhancement
      - low
      - BuiltIn: Consistent argument names to `Should Contain X Times` and `Get Count`
    * - `#3492`_
      - enhancement
      - low
      - Dialogs library bring to front doesn't work in Windows Server 2016
    * - `#3528`_
      - enhancement
      - low
      - Libdoc specs: Change generation time to be valid `xsd:dateTime`
    * - `#3531`_
      - enhancement
      - low
      - Allow using `"SUITE"` and `"TEST"` as library scope values
    * - `#3534`_
      - enhancement
      - low
      - Libdoc spec files: Change type to upper case  `LIBRARY` and `RESOURCE`
    * - `#3536`_
      - enhancement
      - low
      - Enhance documentation syntax to support images with data URIs
    * - `#645`_
      - enhancement
      - low
      - Empty rows should not be discarded during parsing

Altogether 107 issues. View on the `issue tracker <https://github.com/robotframework/robotframework/issues?q=milestone%3Av3.2>`__.

.. _#3076: https://github.com/robotframework/robotframework/issues/3076
.. _#3081: https://github.com/robotframework/robotframework/issues/3081
.. _#3251: https://github.com/robotframework/robotframework/issues/3251
.. _#1272: https://github.com/robotframework/robotframework/issues/1272
.. _#2579: https://github.com/robotframework/robotframework/issues/2579
.. _#3019: https://github.com/robotframework/robotframework/issues/3019
.. _#3027: https://github.com/robotframework/robotframework/issues/3027
.. _#3078: https://github.com/robotframework/robotframework/issues/3078
.. _#3080: https://github.com/robotframework/robotframework/issues/3080
.. _#3084: https://github.com/robotframework/robotframework/issues/3084
.. _#3179: https://github.com/robotframework/robotframework/issues/3179
.. _#3221: https://github.com/robotframework/robotframework/issues/3221
.. _#3373: https://github.com/robotframework/robotframework/issues/3373
.. _#3383: https://github.com/robotframework/robotframework/issues/3383
.. _#3420: https://github.com/robotframework/robotframework/issues/3420
.. _#3455: https://github.com/robotframework/robotframework/issues/3455
.. _#3485: https://github.com/robotframework/robotframework/issues/3485
.. _#3507: https://github.com/robotframework/robotframework/issues/3507
.. _#549: https://github.com/robotframework/robotframework/issues/549
.. _#3201: https://github.com/robotframework/robotframework/issues/3201
.. _#3213: https://github.com/robotframework/robotframework/issues/3213
.. _#3226: https://github.com/robotframework/robotframework/issues/3226
.. _#3229: https://github.com/robotframework/robotframework/issues/3229
.. _#3259: https://github.com/robotframework/robotframework/issues/3259
.. _#3263: https://github.com/robotframework/robotframework/issues/3263
.. _#3264: https://github.com/robotframework/robotframework/issues/3264
.. _#3265: https://github.com/robotframework/robotframework/issues/3265
.. _#3268: https://github.com/robotframework/robotframework/issues/3268
.. _#3295: https://github.com/robotframework/robotframework/issues/3295
.. _#3300: https://github.com/robotframework/robotframework/issues/3300
.. _#3306: https://github.com/robotframework/robotframework/issues/3306
.. _#3338: https://github.com/robotframework/robotframework/issues/3338
.. _#3355: https://github.com/robotframework/robotframework/issues/3355
.. _#3364: https://github.com/robotframework/robotframework/issues/3364
.. _#3403: https://github.com/robotframework/robotframework/issues/3403
.. _#3424: https://github.com/robotframework/robotframework/issues/3424
.. _#3454: https://github.com/robotframework/robotframework/issues/3454
.. _#3483: https://github.com/robotframework/robotframework/issues/3483
.. _#3500: https://github.com/robotframework/robotframework/issues/3500
.. _#3540: https://github.com/robotframework/robotframework/issues/3540
.. _#2291: https://github.com/robotframework/robotframework/issues/2291
.. _#2698: https://github.com/robotframework/robotframework/issues/2698
.. _#2703: https://github.com/robotframework/robotframework/issues/2703
.. _#2706: https://github.com/robotframework/robotframework/issues/2706
.. _#2974: https://github.com/robotframework/robotframework/issues/2974
.. _#3085: https://github.com/robotframework/robotframework/issues/3085
.. _#3091: https://github.com/robotframework/robotframework/issues/3091
.. _#3121: https://github.com/robotframework/robotframework/issues/3121
.. _#3182: https://github.com/robotframework/robotframework/issues/3182
.. _#3194: https://github.com/robotframework/robotframework/issues/3194
.. _#3202: https://github.com/robotframework/robotframework/issues/3202
.. _#3261: https://github.com/robotframework/robotframework/issues/3261
.. _#3269: https://github.com/robotframework/robotframework/issues/3269
.. _#3280: https://github.com/robotframework/robotframework/issues/3280
.. _#3288: https://github.com/robotframework/robotframework/issues/3288
.. _#3301: https://github.com/robotframework/robotframework/issues/3301
.. _#3319: https://github.com/robotframework/robotframework/issues/3319
.. _#3333: https://github.com/robotframework/robotframework/issues/3333
.. _#3349: https://github.com/robotframework/robotframework/issues/3349
.. _#3366: https://github.com/robotframework/robotframework/issues/3366
.. _#3382: https://github.com/robotframework/robotframework/issues/3382
.. _#3397: https://github.com/robotframework/robotframework/issues/3397
.. _#3440: https://github.com/robotframework/robotframework/issues/3440
.. _#3449: https://github.com/robotframework/robotframework/issues/3449
.. _#3451: https://github.com/robotframework/robotframework/issues/3451
.. _#3463: https://github.com/robotframework/robotframework/issues/3463
.. _#3464: https://github.com/robotframework/robotframework/issues/3464
.. _#3491: https://github.com/robotframework/robotframework/issues/3491
.. _#3494: https://github.com/robotframework/robotframework/issues/3494
.. _#3498: https://github.com/robotframework/robotframework/issues/3498
.. _#3514: https://github.com/robotframework/robotframework/issues/3514
.. _#3516: https://github.com/robotframework/robotframework/issues/3516
.. _#3520: https://github.com/robotframework/robotframework/issues/3520
.. _#3522: https://github.com/robotframework/robotframework/issues/3522
.. _#3523: https://github.com/robotframework/robotframework/issues/3523
.. _#3532: https://github.com/robotframework/robotframework/issues/3532
.. _#2767: https://github.com/robotframework/robotframework/issues/2767
.. _#3231: https://github.com/robotframework/robotframework/issues/3231
.. _#3242: https://github.com/robotframework/robotframework/issues/3242
.. _#3260: https://github.com/robotframework/robotframework/issues/3260
.. _#3339: https://github.com/robotframework/robotframework/issues/3339
.. _#3422: https://github.com/robotframework/robotframework/issues/3422
.. _#3453: https://github.com/robotframework/robotframework/issues/3453
.. _#3456: https://github.com/robotframework/robotframework/issues/3456
.. _#3460: https://github.com/robotframework/robotframework/issues/3460
.. _#3489: https://github.com/robotframework/robotframework/issues/3489
.. _#3524: https://github.com/robotframework/robotframework/issues/3524
.. _#2962: https://github.com/robotframework/robotframework/issues/2962
.. _#3082: https://github.com/robotframework/robotframework/issues/3082
.. _#3083: https://github.com/robotframework/robotframework/issues/3083
.. _#3086: https://github.com/robotframework/robotframework/issues/3086
.. _#3195: https://github.com/robotframework/robotframework/issues/3195
.. _#3273: https://github.com/robotframework/robotframework/issues/3273
.. _#3291: https://github.com/robotframework/robotframework/issues/3291
.. _#3330: https://github.com/robotframework/robotframework/issues/3330
.. _#3365: https://github.com/robotframework/robotframework/issues/3365
.. _#3376: https://github.com/robotframework/robotframework/issues/3376
.. _#3415: https://github.com/robotframework/robotframework/issues/3415
.. _#3465: https://github.com/robotframework/robotframework/issues/3465
.. _#3484: https://github.com/robotframework/robotframework/issues/3484
.. _#3486: https://github.com/robotframework/robotframework/issues/3486
.. _#3492: https://github.com/robotframework/robotframework/issues/3492
.. _#3528: https://github.com/robotframework/robotframework/issues/3528
.. _#3531: https://github.com/robotframework/robotframework/issues/3531
.. _#3534: https://github.com/robotframework/robotframework/issues/3534
.. _#3536: https://github.com/robotframework/robotframework/issues/3536
.. _#645: https://github.com/robotframework/robotframework/issues/645
