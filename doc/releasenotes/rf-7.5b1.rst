==========================
Robot Framework 7.5 beta 1
==========================

.. default-role:: code

`Robot Framework`_ 7.5 is a new feature release with major enhancements
to the library documentation tool Libdoc, enhanced console logging
configuration and several other enhancements. There are also various
bigger and smaller bug fixes.

All issues targeted for Robot Framework 7.5 can be found from the
`issue tracker milestone`_.

Questions and comments related to the release can be sent to the `#devel`
channel on `Robot Framework Slack`_ and possible bugs submitted to
the `issue tracker`_.

If you have pip_ installed, just run

::

   pip install --pre --upgrade robotframework

to install the latest available release or use

::

   pip install robotframework==7.5b1

to install exactly this version. Alternatively you can download the package
from PyPI_ and install it manually. For more details and other installation
approaches, see the `installation instructions`_.

Robot Framework 7.5b1 was released on Friday July 17, 2026.

.. _Robot Framework: http://robotframework.org
.. _Robot Framework Foundation: http://robotframework.org/foundation
.. _pip: http://pip-installer.org
.. _PyPI: https://pypi.python.org/pypi/robotframework
.. _issue tracker milestone: https://github.com/robotframework/robotframework/issues?q=milestone%3Av7.5
.. _issue tracker: https://github.com/robotframework/robotframework/issues
.. _robotframework-users: http://groups.google.com/group/robotframework-users
.. _Slack: http://slack.robotframework.org
.. _Robot Framework Slack: Slack_
.. _installation instructions: ../../INSTALL.rst
.. _Markdown: https://en.wikipedia.org/wiki/Markdown
.. _Google Style: https://google.github.io/styleguide/pyguide.html#s3.8.3-functions-and-methods

.. contents::
   :depth: 2
   :local:

Most important enhancements
===========================

Libdoc enhancements
-------------------

The Libdoc tool got two major enhancements:

- Documentation can be written using Markdown_ (`#5304`_).
- Arguments, return values and exceptions can be documented using
  the `Google Style`_ documentation conventions (`#5604`_).

In practice this means that you can document keywords like the example below
demonstrates. Libdoc formats Markdown content as HTML and shows argument,
return value and exception documentation along with automatically collected
information such as argument names and types.

.. sourcecode:: python

    """Example library using **Markdown**."""

    ROBOT_LIBRARY_DOC_FORMAT = "Markdown"


    def example(first: int, second: bool = True) -> float:
        """Example keyword!

        This keywords uses:

        - [Markdown](https://en.wikipedia.org/wiki/Markdown) *formatting*
        - [Google Style] argument, return value and exception documentation

        Args:
            first: Doc for the first argument.
            second: Doc for the second argument.
                This time on multiple lines with *formatting*.

        Returns:
            Zero.

        Raises:
            ValueError: When `second` is False.

        Documentation can continue here after the [Google Style] documentation sections. Well,
        actually documentation is accepted *also* between the section.

        [Google Style]: https://google.github.io/styleguide/pyguide.html#383-functions-and-methods
        """
        if not second:
            raise ValueError
        return 0.0


    def internal_linking():
        """Internal linking is cool!

        This is link to library [introduction] and here we have the [Example] keyword.
        """
        pass

Libdoc still used Robot Frameworks custom documentation format by default, so
the documentation format needs to be specified using the `ROBOT_LIBRARY_DOC_FORMAT`
attribute, the `@library` decorator or the `--doc-format` command line option.

Because Markdown support is optional, the
`Python-Markdown <https://python-markdown.github.io/>`_ module needs to be
separately installed. It is typically done as follows::

    pip install markdown

Details about supported Markdown features can be found in the User Guide.
We only generate it for final releases, so as long as we only have preview
releases you need to look at the `documentation source`__ that luckily renders
pretty well on GitHub.

A nice extra feature that Libdoc adds is that internal linking to the introduction
section, to custom sections created in the introduction, to keywords and to types
used in arguments works using the standard Markdown reference link syntax like
`[introduction]`. This is documented more thoroughly under the Libdoc documentation.
Also in this case you need to look at the `documentation source`__ until the final
release.

We have not yet converted standard libraries to use Markdown or new argument
documentation features, but we plan to do that at least with some libraries
still in Robot Framework 7.5 (`#5709`__). This is something where external
help would be appreciated and the task is especially suitable for new
contributors!

.. note:: We may make Markdown the default documentation format in the future.
          If you plan to keep using the Robot Framework format, explicitly
          specifying that documentation format is `ROBOT` is a good idea.

__ https://github.com/robotframework/robotframework/blob/master/doc/userguide/src/Appendices/DocumentationFormatting.rst#markdown-format
__ https://github.com/robotframework/robotframework/blob/master/doc/userguide/src/SupportingTools/Libdoc.rst#markdown-documentation-syntax
__ https://github.com/robotframework/robotframework/issues/5709

Console logging enhancements
----------------------------

Robot Framework supports few different console loggers out-of-the-box (verbose,
dotted, quiet, none) and the one to use can be selected with the `--console`
option. Robot Framework 7.5 enhances this support so that it is also possible
to use custom console loggers (`#5618`_).

Custom console loggers have the same API as listeners__. Their main difference
is that console loggers are registered with the `--console` option that then
automatically disables normal console logging. The built-in console loggers
can be used as a base when implementing custom loggers. That makes it easy
to make simple changes to normal logging.

A related major change is that nowadays also the Rebot tool supports the `--console`
option (`#5674`_). It supports the same built-in loggers that can be used during
execution as well as custom loggers.

For details about the console logging API and everything else, see the documentation__.
Due to the User Guide not being generated with preview releases, the documentation
link points to documentation source.

__ https://robotframework.org/robotframework/latest/RobotFrameworkUserGuide.html#listener-interface
__ https://github.com/robotframework/robotframework/blob/master/doc/userguide/src/ExecutingTestCases/ConfiguringExecution.rst#custom-console-loggers

Embedding tests/tasks to Markdown files
---------------------------------------

It is nowadays possible to execute tests or tasks embedded into Markdown files
using code blocks (`#5603`_). For example, if the following Markdown file
would be executed, data in the `robotframework` code block would be parsed
and executed.

.. sourcecode:: markdown

    # Markdown example

    This text is outside code blocks and thus ignored.

    ```robotframework
    *** Test Cases ***
    Example
        Keyword

    *** Keywords ***
    Keyword
        Log    Hello, Markdown!
    ```

    More free text here. There could be additional code blocks with more
    Robot Framework data as well.

    ```python
    # This code block is ignored.
    def example():
        print('Hello, world!')
    ```

When executing a directory, Robot Framework does not parse normal Markdown files
with the `*.md` extension by default, but that can be changed with `--parseinclude`
and  `--extension` options. Files with the special `*.robot.md` extension are
automatically parsed and executed, though.

Backwards incompatible changes
==============================

There are some backwards incompatible changes in this release, but they are
unlikely to affect normal users:

- Robot Framework's internal `TimeoutExceeded` is nowadays based on `BaseException`
  instead of `Exception` (`#5610`_). The change was done to avoid these exceptions
  being accidentally caught by code using `except Exception:`. This means that code
  doing that on purpose does not work anymore. A fix is catching these exception
  explicitly like `except TimeoutExceeded:`.

- Libdoc has a feature that types used as type hints automatically create link
  targets that can be used with the internal linking syntax. With some types
  the link target was a less technical name like `integer` or `string` instead
  of the actual used type name like `int` or `str`. This has been changed
  so that nowadays the link target is always the used type name. This should not
  affect many users, because it is unlikely that there has been needs to link
  to types like `integer`. In addition to that, this particular feature was
  earlier not documented at all, so most users have probably been unaware of it.

- Libdoc's automatic table of contents generation was changed in various ways
  (`#5696`_, `#5697`_):

    - The TOC nowadays shows two levels of section headers instead of just one.
      That ought to be a good enhancement in general, but it can cause issues in
      some cases. If there are real problems, we can consider making the level
      configurable.

    - The `%TOC%` marker is replaced with the actual TOC during HTML generation,
      not in Libdoc's normal models and in spec files.

    - Links to `Importing` and `Keywords` sections are not added automatically.

Deprecated features
===================

Various features have been deprecated:

- The built-in Testdoc tool has been deprecated (`#5592`_) and the external
  `Testdoc <https://github.com/MarvKler/robotframework-testdoc>`__ should be
  used instead.

- Boolean operators used with tag patterns need to be separated from tags more clearly
  and usages like `XORY` are deprecated (`#5657`_). Operators can be surrounded
  with spaces like `X OR Y` or tags can be specified in lower case like `xORy`.

- Using `&` as a Boolean operator with tag patterns is deprecated and `AND`
  should be used instead (`#5661`_).

- French "Test Cases" translation "Unités de test" has been deprecated in favor
  of "Cas de test" (`#5510`_). Both terms work with Robot Framework 7.5 without
  warnings.

- When specifying tags as part of documentation, omitting an empty row before
  the `Tags:` header is deprecated (`#5707`_).

- `robot.utils.read_rest_data` (`#5639`_) and `robot.utils.split_tags_from_doc`
  (`#5707`_) utility functions became unnecessary for Robot Framework itself and
  are deprecated.

Acknowledgements
================

Robot Framework is developed with support from the Robot Framework Foundation
and its 80+ member organizations. Join the journey — support the project by
`joining the Foundation <Robot Framework Foundation_>`_.

Robot Framework 7.5 team funded by the foundation consisted of `Pekka Klärck`_ and
`Janne Härkönen <https://github.com/yanne>`_. Janne worked only part-time and was
mainly responsible for Libdoc related fixes. In addition to work done by them, the
community has provided some great contributions:

- `Tatu Aalto <https://github.com/aaltat>`__ worked with Pekka to implement
  support to document keyword arguments, return values and exceptions (`#5604`_),
  which is one of the biggest enhancements in this release. Huge thanks to Tatu
  and to his employer `OP <https://www.op.fi/>`__, a member of the
  `Robot Framework Foundation`_, for dedicating work time to make this happen!

- `Sudheer Reddy Patlolla <https://github.com/sudheerr937-ai>`__ fixed
  `Get Index From List` keyword that did not handle negative start indices
  correctly (`#5649`_) and enhanced handling invalid stringified type hints
  (`#5650`_).

- `Oliver Boehmer <https://github.com/oboehmer>`_ added custom console logger
  support (`#5618`_) and made console loggers configurable also with Rebot (`#5674`_).

- `Roberto Matarazzo <https://github.com/seto>`__ implemented support to embed
  tests/tasks to Markdown files (`#5603`_).

- `Guillaume Yvon <https://github.com/klaoude>`__ fixed a problem that type hints
  using non-existing values crashed the whole execution with Python 3.14 (`#5658`_).

- `J. Foederer <https://github.com/JFoederer>`__ enhanced `TimeoutExceeded` exception
  used for signaling test and keyword timeouts so that it is not caught by Python code
  using `except Exception:` (`#5610`_).

Big thanks to Robot Framework Foundation, to community members listed above, and
to everyone else who has tested preview releases, submitted bug reports, proposed
enhancements, debugged problems, or otherwise helped with Robot Framework 7.4
development.

| `Pekka Klärck <https://github.com/pekkaklarck>`_
| Robot Framework lead developer

Full list of fixes and enhancements
===================================

.. list-table::
    :header-rows: 1

    * - ID
      - Type
      - Priority
      - Summary
      - Added
    * - `#5304`_
      - feature
      - critical
      - Libdoc: Support documentation written with Markdown
      - beta 1
    * - `#5604`_
      - feature
      - critical
      - Libdoc: Argument and return value documentation syntax
      - beta 1
    * - `#5644`_
      - bug
      - high
      - Performance regression in resolving variables
      - beta 1
    * - `#5645`_
      - bug
      - high
      - Mutable IF condition can cause incorrect statements and branches to be run
      - beta 1
    * - `#5649`_
      - bug
      - high
      - Collections: `Get Index From List` does not handle negative start indices correctly
      - beta 1
    * - `#5658`_
      - bug
      - high
      - Type hints that use non-existing values or are invalid crash execution with Python 3.14
      - beta 1
    * - `#5592`_
      - feature
      - high
      - Deprecate built-in Testdoc tool
      - beta 1
    * - `#5603`_
      - feature
      - high
      - Support embedding tests/tasks to Markdown files
      - beta 1
    * - `#5618`_
      - feature
      - high
      - Support custom console loggers from command line and programmatically
      - beta 1
    * - `#5657`_
      - feature
      - high
      - Deprecate tag patterns in format `XORY`
      - beta 1
    * - `#5668`_
      - feature
      - high
      - Make it possible to deprecate translated section headers and settings
      - beta 1
    * - `#5674`_
      - feature
      - high
      - Support configuring console logger with Rebot
      - beta 1
    * - `#5650`_
      - bug
      - medium
      - Invalid `|` usage in stringified type hints can crash or hang execution
      - beta 1
    * - `#5655`_
      - bug
      - medium
      - Cannot use `KeywordName` (or any `str` sub type) in custom library type hints
      - beta 1
    * - `#5691`_
      - bug
      - medium
      - Libdoc: Problems with linking to type documentation
      - beta 1
    * - `#5695`_
      - bug
      - medium
      - Libdoc cannot projess JSON spec with `lineno` being `null`
      - beta 1
    * - `#5699`_
      - bug
      - medium
      - Automatic type conversion throws AttributeError on arguments that have no `__class__` attribute
      - beta 1
    * - `#5510`_
      - feature
      - medium
      - Change French "Test Cases" translation from "Unités de test" to "Cas de test"
      - beta 1
    * - `#5610`_
      - feature
      - medium
      - Avoid timeouts being caught by Python code using `except Exception:`
      - beta 1
    * - `#5634`_
      - feature
      - medium
      - Documentation: Promote dynamic library API and demote hybird library API
      - beta 1
    * - `#5661`_
      - feature
      - medium
      - Deprecate `&` operator with tag patterns and require using `AND`
      - beta 1
    * - `#5673`_
      - feature
      - medium
      - Add `result_file` fallback method to listener API v3
      - beta 1
    * - `#5675`_
      - feature
      - medium
      - Documentation: Use "execution artifacts", not "output files", when referring to all execution results
      - beta 1
    * - `#5696`_
      - feature
      - medium
      - Libdoc: Include two header levels in table of contents
      - beta 1
    * - `#5697`_
      - feature
      - medium
      - Libdoc: Do not add Keywords or Importing sections to table of contents
      - beta 1
    * - `#5703`_
      - feature
      - medium
      - Libdoc: Add explicit `None` return type information to spec files
      - beta 1
    * - `#5707`_
      - feature
      - medium
      - Enhance parsing tags from keyword documentation
      - beta 1
    * - `#5628`_
      - bug
      - low
      - Listener priority precision problems with huge integers
      - beta 1
    * - `#5636`_
      - bug
      - low
      - String: Bad error reporting when automatic bytes conversion fails
      - beta 1
    * - `#5648`_
      - bug
      - low
      - String: `Convert To Title Case` fails with bad error message if `exclude` contains invalid regexp
      - beta 1
    * - `#5639`_
      - feature
      - low
      - Deprecate `robot.utils.read_rest_data`
      - beta 1
    * - `#5653`_
      - feature
      - low
      - Docs: Clarify that tests are marked failed in the end if there are continuable failures
      - beta 1

Altogether 32 issues. View on the `issue tracker <https://github.com/robotframework/robotframework/issues?q=milestone%3Av7.5>`__.

.. _#5304: https://github.com/robotframework/robotframework/issues/5304
.. _#5604: https://github.com/robotframework/robotframework/issues/5604
.. _#5644: https://github.com/robotframework/robotframework/issues/5644
.. _#5645: https://github.com/robotframework/robotframework/issues/5645
.. _#5649: https://github.com/robotframework/robotframework/issues/5649
.. _#5658: https://github.com/robotframework/robotframework/issues/5658
.. _#5592: https://github.com/robotframework/robotframework/issues/5592
.. _#5603: https://github.com/robotframework/robotframework/issues/5603
.. _#5618: https://github.com/robotframework/robotframework/issues/5618
.. _#5657: https://github.com/robotframework/robotframework/issues/5657
.. _#5668: https://github.com/robotframework/robotframework/issues/5668
.. _#5674: https://github.com/robotframework/robotframework/issues/5674
.. _#5650: https://github.com/robotframework/robotframework/issues/5650
.. _#5655: https://github.com/robotframework/robotframework/issues/5655
.. _#5691: https://github.com/robotframework/robotframework/issues/5691
.. _#5695: https://github.com/robotframework/robotframework/issues/5695
.. _#5699: https://github.com/robotframework/robotframework/issues/5699
.. _#5510: https://github.com/robotframework/robotframework/issues/5510
.. _#5610: https://github.com/robotframework/robotframework/issues/5610
.. _#5634: https://github.com/robotframework/robotframework/issues/5634
.. _#5661: https://github.com/robotframework/robotframework/issues/5661
.. _#5673: https://github.com/robotframework/robotframework/issues/5673
.. _#5675: https://github.com/robotframework/robotframework/issues/5675
.. _#5696: https://github.com/robotframework/robotframework/issues/5696
.. _#5697: https://github.com/robotframework/robotframework/issues/5697
.. _#5703: https://github.com/robotframework/robotframework/issues/5703
.. _#5707: https://github.com/robotframework/robotframework/issues/5707
.. _#5628: https://github.com/robotframework/robotframework/issues/5628
.. _#5636: https://github.com/robotframework/robotframework/issues/5636
.. _#5648: https://github.com/robotframework/robotframework/issues/5648
.. _#5639: https://github.com/robotframework/robotframework/issues/5639
.. _#5653: https://github.com/robotframework/robotframework/issues/5653
