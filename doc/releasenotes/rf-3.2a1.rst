===========================
Robot Framework 3.2 alpha 1
===========================

.. default-role:: code

`Robot Framework`_ 3.2 is a new major release with new, enhanced test data
parser, inline Python evaluation support, and many other interesting new
features and bug fixes. RF 3.2 alpha 1 is its first preview release and it already contains
majority of the planned new features and fixes, including the new parser. All
issues targeted for RF 3.2 can be found from the `issue tracker milestone`_.

Questions and comments related to the release can be sent to the
`robotframework-users`_ mailing list or to `Robot Framework Slack`_,
and possible bugs submitted to the `issue tracker`_.

If you have pip_ installed, just run

::

   pip install --pre --upgrade robotframework

to install the latest available release or use

::

   pip install robotframework==3.2a1

to install exactly this version. Alternatively you can download the source
distribution from PyPI_ and install it manually. For more details and other
installation approaches, see the `installation instructions`_.

Robot Framework 3.2 alpha 1 was released on Tuesday November 12, 2019.

.. _Robot Framework: http://robotframework.org
.. _Robot Framework Foundation: http://robotframework.org/foundation
.. _pip: http://pip-installer.org
.. _PyPI: https://pypi.python.org/pypi/robotframework
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
add new syntax like `IF/ELSE` (`#3074`_), `TRY/EXCEPT` (`#3075`_), and
nested control structures (`#3079`_) in the future. Adding such features
to the old parser would have been extremely complicated and the resulting
code would have been hard to maintain going forward.

The new parser also has much better APIs for external tools like editors, IDEs,
and linters than the old one, and they could possibly be exposed even more
widely using the `language server protocol (LSP)`__. These APIs are still
under development (`#3373`_), though, but they will be finalized before
the final RF 3.2 version. Possible LSP implementation would also be a
separate project, not part of Robot Framework itself.

For the user the biggest concrete enhancement provided by the new parser is
that ellipsis (`...`) denoting line continuation are preserved during parsing
(`#1272`_), which means that the Tidy tool does not loose them either
(`#2579`_). Some other enhancement, such as preserving line number (`#549`_)
and thus enhancing error reporting, will be exposed to users still before
the final RF 3.2 release.

The new parser supports only the plain text format (`#3081`_). This means
that the HTML format is not supported at all, and the TSV format is supported
only when it is fully compatible with the plain text format. Because the
new parser only parses `*.robot` files by default (`#3084`_), users of the
`*.txt`, `*.tsv`, or `*.rst` files need to explicitly use the `--extension`
option.

__ https://microsoft.github.io/language-server-protocol
.. _#3373:  https://github.com/robotframework/robotframework/issues/3373
.. _#549: https://github.com/robotframework/robotframework/issues/549
.. _#3074: https://github.com/robotframework/robotframework/issues/3074
.. _#3075: https://github.com/robotframework/robotframework/issues/3075
.. _#3079: https://github.com/robotframework/robotframework/issues/3079

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
  (`${{decimal.Decimal('0.11')}}`, `${{datetime.date(2019, 11, 12)}}`).

- Creating values dynamically (`${{random.randint(0, 100)}}`,
  `${{datetime.date.today()}}`).

- Constructing collections, especially nested collections (`${{[1, 2, 3, 4]}}`,
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

Listeners can add and remove tests
----------------------------------

Listeners__ are a powerful feature of Robot Framework and RF 3.2 makes
them a bit more powerful. Earlier listeners using the API v3 could not add
or remove new tests in their `start/end_test` methods (`#3251`_), but this
limitation has now been lifted. This makes it easier to implement advanced
tooling, for example, for model based testing using Robot Framework in its
core.

__ http://robotframework.org/robotframework/latest/RobotFrameworkUserGuide.html#listener-interface

Backwards incompatible changes
==============================

Although we try to avoid backwards incompatible changes, sometimes adding new
features mean that old features need to be changed or even removed. This is
never done lightly and we try to limit backwards incompatible changes to
major releases. In Robot Framework 3.2 these changes are mainly related to
parsing one way or the other.

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
- When using the `pipe-separated format`__, consecutive spaces are not
  collapsed anymore. This affects also normal spaces, not only non-ASCII
  spaces.

__ http://jkorpela.fi/chars/spaces.html
__ http://robotframework.org/robotframework/latest/RobotFrameworkUserGuide.html#pipe-separated-format

Stricter section and setting name syntax
----------------------------------------

Section names like `Test Cases` and setting names like `Test Setup` are
nowadays space sensitive (`#3082`_). In practice this means that sections
like `TestCases` or settings like `TestSetup` are not recognized.

Stricter for loop separator syntax
----------------------------------

For loop separators `IN`, `IN RANGE`, `IN ZIP` and `IN ENUMERATE` are both
case and space sensitive (`#3083`_). In other works, separators like `in`
or `INZIP` are nor recognized. Notice also that the `old for loop syntax
has been deprecated`_ in general.

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

Support for custom timeout messages has been removed
----------------------------------------------------

This functionality was deprecated already in Robot Framework 3.0.1 and
it has now been removed (`#2291`_).

`--escape` option has been removed
----------------------------------

This option used to allow escaping problematic characters on the command line.
Shell escaping or quoting mechanism needs to be used instead (`#3085`_).

`--warnonskippedfiles` option has been removed
----------------------------------------------

This option did not have any effect anymore and has now been removed
altogether (`#3086`_).

Deprecated features
===================

Whenever we notice a feature that needs to be changed in backwards incompatible
manner, we try to first deprecate the feature at least one major release before
the removal. There are not that many deprecations in Robot Framework 3.2, but
unfortunately especially changes to the for loop syntax are likely to affect
many users.

Old for loop syntax has been deprecated
---------------------------------------

Robot Framework 3.1 `enhanced for loop syntax`__ so that nowadays loops can
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

The old format still worked in Robot Framework 3.1, but now both using `:FOR`
instead of `FOR` (`#3080`_) and not closing the loop with an explicit `END`
(`#3078`_) are both deprecated. The syntax old will be removed for good
already in Robot Framework 3.3.

This change is likely to cause lot of deprecation warnings and requires users
to update their test data. Here are some ideas how to find and updated the
data:

- Run tests and see how many deprecation warnings you get. The warning should
  tell where the old syntax is used. Even if you use some other way to find
  these usages, running tests tells you have you caught them all.
- Use the `Tidy tool`__ to update data. It also changes data otherwise, so
  it is a good idea to check changes and possibly commit only changes relevant
  to for loops. Tidy updates the old for loop syntax to new one starting from
  Robot Framework 3.1.2.
- Use operating system search functionality to find `:FOR` (case-insensitively)
  as well as possible `: FOR` variant from test data files. Then update loops
  by hand.
- Use an external command line tool like ack__ (Perl) or pss__ (Python) to
  find `:FOR` and `: FOR` and update data by hand. If using the `pss` tool,
  this command works well::

     pss -ai ': ?FOR' path/to/tests

__ https://github.com/robotframework/robotframework/blob/master/doc/releasenotes/rf-3.1.rst#for-loop-enhancements
__ http://robotframework.org/robotframework/latest/RobotFrameworkUserGuide.html#tidy
__ https://beyondgrep.com/
__ https://pypi.org/project/pss/

Accessing list and dictionary items using `@{var}[item]` and `&{var}[item]` is deprecated
-----------------------------------------------------------------------------------------

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

  pss -ai '@\{.+\}\[' path/to/tests
  pss -ai '&\{.+\}\[' path/to/tests

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
  implemented `Set Local Variable` keyword (`#3091`_) and added note to
  the Screenshot library documentation about the more powerful
  `ScreenCapLibrary <https://github.com/mihaiparvu/ScreenCapLibrary>`__
  (`#3330`_)

- `Lukas Breitstadt <https://github.com/lubrst>`__ fixed using
  `ExecutionResult` API with bytes (`#3194`_)

- `René <https://github.com/Snooz82>`__ made it possible to store documentation
  in XML outputs using HTML regardless the original documentation format
  (`#3301`_)

- `Mihai Pârvu <https://github.com/mihaiparvu>`__ enhanced Libdoc, TestDoc and
  Tidy tools as well as Robot Framework's syslog files to automatically create
  output directories (`#2767`_)

- `Stavros Ntentos <https://github.com/stdedos>`__ fixed equality checking
  with `Tags` objects (`#3242`_)

Huge thanks to all contributors and to everyone else who has reported
problems, tested preview releases, participated discussion on various
forums, or otherwise helped to make Robot Framework as well as the ecosystem
and community around it better.

Thanks everyone and hopefully Robot Framework 3.2 works great for you!

Full list of fixes and enhancements
===================================

.. list-table::
    :header-rows: 1

    * - ID
      - Type
      - Priority
      - Summary
      - Added
    * - `#3076`_
      - enhancement
      - critical
      - New test data parser
      - alpha 1
    * - `#3081`_
      - enhancement
      - critical
      - Remove support for HTML and TSV formats
      - alpha 1
    * - `#3251`_
      - bug
      - high
      - Listeners cannot add/remove tests in their `start/end_test` methods
      - alpha 1
    * - `#1272`_
      - enhancement
      - high
      - Parsing modules should preserve ellipsis (...) denoting line continuation
      - alpha 1
    * - `#2579`_
      - enhancement
      - high
      - Tidy should not merge continued lines
      - alpha 1
    * - `#3078`_
      - enhancement
      - high
      - Deprecate `FOR` loops without `END`
      - alpha 1
    * - `#3080`_
      - enhancement
      - high
      - Deprecate FOR loops starting with case-insensitive `:FOR`
      - alpha 1
    * - `#3084`_
      - enhancement
      - high
      - Remove support to parse other than `*.robot` files by default
      - alpha 1
    * - `#3179`_
      - enhancement
      - high
      - Inline Python evaluation support using `${{expression}}` syntax
      - alpha 1
    * - `#3201`_
      - bug
      - medium
      - `Log List` and some other keywords in Collections and BuiltIn fail with tuples
      - alpha 1
    * - `#3213`_
      - bug
      - medium
      - Using abstract base classes directly from `collections` causes deprecation warning
      - alpha 1
    * - `#3226`_
      - bug
      - medium
      - XML library does not work with non-ASCII bytes on Python 2 or any bytes on Python 3
      - alpha 1
    * - `#3229`_
      - bug
      - medium
      - Variable in keyword teardown name causes failure in dry-run mode
      - alpha 1
    * - `#3259`_
      - bug
      - medium
      - Libdoc doesn't handle bytes containing non-ASCII characters in keyword arguments
      - alpha 1
    * - `#3263`_
      - bug
      - medium
      - Tidy does not preserve data before first section
      - alpha 1
    * - `#3264`_
      - bug
      - medium
      - Robot output can crash when piping output
      - alpha 1
    * - `#3265`_
      - bug
      - medium
      - `--test/--suite/--include/--exclude` don't affect tests added by pre-run modifiers
      - alpha 1
    * - `#3268`_
      - bug
      - medium
      - Execution crashes if directory is not readable
      - alpha 1
    * - `#3295`_
      - bug
      - medium
      - Inconsistent handling of escape character inside variable body
      - alpha 1
    * - `#3306`_
      - bug
      - medium
      - DateTime: `Get Current Date` with epoch format and timezone UTC return wrong value
      - alpha 1
    * - `#3338`_
      - bug
      - medium
      - Problems reporting errors when library import fails on Python 2 and import path contains non-ASCII characters
      - alpha 1
    * - `#3355`_
      - bug
      - medium
      - `Evaluate`: Using nested modules like `modules=rootmodule.submodule` does not work
      - alpha 1
    * - `#3364`_
      - bug
      - medium
      - Non-ASCII paths to test data not handled correctly with Jython 2.7.1+
      - alpha 1
    * - `#2291`_
      - enhancement
      - medium
      - Remove possibility to specify custom timeout message
      - alpha 1
    * - `#2974`_
      - enhancement
      - medium
      - Deprecate accessing list/dict items using syntax `@{var}[item]` and `&{var}[item]`
      - alpha 1
    * - `#3085`_
      - enhancement
      - medium
      - Remove support using `--escape` to escape characters problematic on console
      - alpha 1
    * - `#3091`_
      - enhancement
      - medium
      - Add `Set Local Variable` keyword
      - alpha 1
    * - `#3121`_
      - enhancement
      - medium
      - Consistent handling of whitespace in test data
      - alpha 1
    * - `#3194`_
      - enhancement
      - medium
      - `ExecutionResult` should support input as bytes
      - alpha 1
    * - `#3202`_
      - enhancement
      - medium
      - Upgrade jQuery used by logs and reports
      - alpha 1
    * - `#3261`_
      - enhancement
      - medium
      - Add missing `list` methods to internally used `ItemList`
      - alpha 1
    * - `#3269`_
      - enhancement
      - medium
      - Support any file extension when explicitly running file and when using `--extension`
      - alpha 1
    * - `#3288`_
      - enhancement
      - medium
      - Require variables to have matching opening and closing curly braces and square brackets
      - alpha 1
    * - `#3301`_
      - enhancement
      - medium
      - Libdoc: Support converting docs to HTML with XML outputs
      - alpha 1
    * - `#3333`_
      - enhancement
      - medium
      - Deprecate ignoring space after literal newline
      - alpha 1
    * - `#3349`_
      - enhancement
      - medium
      - Automatically import modules that are used with `Evaluate`, `Run Keyword If`, and others
      - alpha 1
    * - `#2767`_
      - bug
      - low
      - Syslog, Libdoc, Testdoc and Tidy don't create directory for outputs
      - alpha 1
    * - `#3242`_
      - bug
      - low
      - Tags(tag_list) != Tags(tag_list)
      - alpha 1
    * - `#3260`_
      - bug
      - low
      - Document that Tidy with `--recursive` doesn't process resource files
      - alpha 1
    * - `#3339`_
      - bug
      - low
      - Libdoc, TestDoc and Tidy crash if output file is invalid
      - alpha 1
    * - `#3082`_
      - enhancement
      - low
      - Remove support using section and setting names space-insensitively
      - alpha 1
    * - `#3083`_
      - enhancement
      - low
      - Remove support using for loops with other separators than exact `IN`, `IN RANGE`, `IN ZIP` and `IN ENUMERATE`
      - alpha 1
    * - `#3086`_
      - enhancement
      - low
      - Remove `--warnonskippedfiles` because it has no effect anymore
      - alpha 1
    * - `#3195`_
      - enhancement
      - low
      - Feature request: add older YAML file extension (.yml - Variable file as YAML)
      - alpha 1
    * - `#3273`_
      - enhancement
      - low
      - UG: Handling documentation split to multiple columns will not change
      - alpha 1
    * - `#3330`_
      - enhancement
      - low
      - Add a note about more powerful ScreenCapLibrary to Screenshot library documentation
      - alpha 1
    * - `#3365`_
      - enhancement
      - low
      - Document that zero and negative test/keyword timeout is ignored
      - alpha 1
    * - `#645`_
      - enhancement
      - low
      - Empty rows should not be discarded during parsing
      - alpha 1

Altogether 48 issues. View on the `issue tracker <https://github.com/robotframework/robotframework/issues?q=milestone%3Av3.2>`__.

.. _#3076: https://github.com/robotframework/robotframework/issues/3076
.. _#3081: https://github.com/robotframework/robotframework/issues/3081
.. _#3251: https://github.com/robotframework/robotframework/issues/3251
.. _#1272: https://github.com/robotframework/robotframework/issues/1272
.. _#2579: https://github.com/robotframework/robotframework/issues/2579
.. _#3078: https://github.com/robotframework/robotframework/issues/3078
.. _#3080: https://github.com/robotframework/robotframework/issues/3080
.. _#3084: https://github.com/robotframework/robotframework/issues/3084
.. _#3121: https://github.com/robotframework/robotframework/issues/3121
.. _#3179: https://github.com/robotframework/robotframework/issues/3179
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
.. _#3306: https://github.com/robotframework/robotframework/issues/3306
.. _#3338: https://github.com/robotframework/robotframework/issues/3338
.. _#3355: https://github.com/robotframework/robotframework/issues/3355
.. _#3364: https://github.com/robotframework/robotframework/issues/3364
.. _#2291: https://github.com/robotframework/robotframework/issues/2291
.. _#2974: https://github.com/robotframework/robotframework/issues/2974
.. _#3085: https://github.com/robotframework/robotframework/issues/3085
.. _#3091: https://github.com/robotframework/robotframework/issues/3091
.. _#3194: https://github.com/robotframework/robotframework/issues/3194
.. _#3202: https://github.com/robotframework/robotframework/issues/3202
.. _#3261: https://github.com/robotframework/robotframework/issues/3261
.. _#3269: https://github.com/robotframework/robotframework/issues/3269
.. _#3288: https://github.com/robotframework/robotframework/issues/3288
.. _#3301: https://github.com/robotframework/robotframework/issues/3301
.. _#3333: https://github.com/robotframework/robotframework/issues/3333
.. _#3349: https://github.com/robotframework/robotframework/issues/3349
.. _#2767: https://github.com/robotframework/robotframework/issues/2767
.. _#3242: https://github.com/robotframework/robotframework/issues/3242
.. _#3260: https://github.com/robotframework/robotframework/issues/3260
.. _#3339: https://github.com/robotframework/robotframework/issues/3339
.. _#3082: https://github.com/robotframework/robotframework/issues/3082
.. _#3083: https://github.com/robotframework/robotframework/issues/3083
.. _#3086: https://github.com/robotframework/robotframework/issues/3086
.. _#3195: https://github.com/robotframework/robotframework/issues/3195
.. _#3273: https://github.com/robotframework/robotframework/issues/3273
.. _#3330: https://github.com/robotframework/robotframework/issues/3330
.. _#3365: https://github.com/robotframework/robotframework/issues/3365
.. _#645: https://github.com/robotframework/robotframework/issues/645
