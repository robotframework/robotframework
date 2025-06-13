Contribution guidelines
=======================

These guidelines instruct how to submit issues and contribute code or
documentation to the `Robot Framework project
<https://github.com/robotframework/robotframework>`_.
There are also many other projects in the larger `Robot Framework ecosystem
<http://robotframework.org>`_ that you can contribute to. If you notice
a library or tool missing, there is hardly any better way to contribute
than creating your own project. Other great ways to contribute include
answering questions and participating discussion on our
`Slack <https://slack.robotframework.org>`_,
`Forum <https://forum.robotframework.org>`_,
`LinkedIn group <https://www.linkedin.com/groups/3710899/>`_,
or other such discussion forum, speaking at conferences or local events,
and spreading the word about the framework otherwise.

These guidelines expect readers to have a basic knowledge about open source
as well as why and how to contribute to an open source project. If you are
new to these topics, it may be a good idea to look at the generic
`Open Source Guides <https://opensource.guide/>`_ first.

.. contents::
   :depth: 2
   :local:

Submitting issues
-----------------

Bugs and enhancements are tracked in the `issue tracker
<https://github.com/robotframework/robotframework/issues>`_. If you are unsure
if something is a bug or is a feature worth implementing, you can
first ask on the ``#devel`` channel on our Slack_. Slack and other such forums,
not the issue tracker, are also places where to ask general questions about
the framework.

Before submitting a new issue, it is always a good idea to check is the
same bug or enhancement already reported. If it is, please add your comments
to the existing issue instead of creating a new one.

Reporting bugs
~~~~~~~~~~~~~~

Explain the bug you have encountered so that others can understand it and
preferably also reproduce it. Key things to include in good bug report:

1. Version information

   - Robot Framework version
   - Python interpreter version
   - Operating system and its version

   Typically including the output of ``robot --version`` is enough.

2. Steps to reproduce the problem. With more complex problems it is often
   a good idea to create a `short, self contained, correct example (SSCCE)
   <http://sscce.org>`_.

3. Possible error message and traceback.

Notice that all information in the issue tracker is public. Do not include
any confidential information there.

Enhancement requests
~~~~~~~~~~~~~~~~~~~~

Describe the new feature and use cases for it in as much detail as possible.
Especially with larger enhancements, be prepared to contribute the code
in the form of a pull request as explained below. If you would like to sponsor
a development of a certain feature, you can contact the `Robot Framework
Foundation <https://robotframework.org/foundation>`_.
Consider also would it be better to implement new functionality as a separate
library or tool outside the core framework.

Code contributions
------------------

If you have fixed a bug or implemented an enhancement, you can contribute
your changes via GitHub's pull requests. This is not restricted to code,
on the contrary, fixes and enhancements to documentation_ and tests_ alone
are also very valuable.

Choosing something to work on
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Often you already have a bug or an enhancement you want to work on in your
mind, but you can also look at the `issue tracker`_ to find bugs and
enhancements submitted by others. The issues vary significantly in complexity
and difficulty, so you can try to find something that matches your skill level
and knowledge. There are two specific labels to look for when looking for
something to contribute:

`good first issue`__
   These issues typically do not require any knowledge of Robot Framework
   internals and are generally easy to implement or fix. Thus these issues
   are especially good for new contributors.

`help wanted`__
   These issues require external help to get implemented or fixed.

__ https://github.com/robotframework/robotframework/issues?q=is%3Aopen+is%3Aissue+label%3A%22good+first+issue%22
__ https://github.com/robotframework/robotframework/issues?q=is%3Aopen+is%3Aissue+label%3A%22help+wanted%22

Pull requests
~~~~~~~~~~~~~

On GitHub pull requests are the main mechanism to contribute code. They
are easy to use both for the contributor and for the person accepting
the contribution, and with more complex contributions it is easy also
for others to join the discussion. Preconditions for creating pull
requests are having a `GitHub account <https://github.com/>`_,
installing `Git <https://git-scm.com>`_ and forking the
`Robot Framework project`_.

GitHub has good articles explaining how to
`set up Git <https://help.github.com/articles/set-up-git/>`_,
`fork a repository <https://help.github.com/articles/fork-a-repo/>`_ and
`use pull requests <https://help.github.com/articles/using-pull-requests>`_
and we do not go through them in more detail. We do, however, recommend to
create dedicated topic branches for pull requests instead of creating
them based on the master branch. This is especially important if you plan to
work on multiple pull requests at the same time.

Development dependencies
~~~~~~~~~~~~~~~~~~~~~~~~

Code formatting and other tasks require external tools to be installed. All
of them are listed in the `<requirements-dev.txt>`_ file and you can install
them by running::

    pip install -r requirements-dev.txt

Coding conventions
~~~~~~~~~~~~~~~~~~

Robot Framework follows the general Python code conventions defined in `PEP-8
<https://peps.python.org/pep-0008/>`_. Code is `automatically formatted`__, but
`manual adjustments`__ may sometimes be needed.

__ `Automatic formatting`_
__ `Manual formatting adjustments`_

Automatic formatting
''''''''''''''''''''

The code is automatically linted and formatted using a combination of tools
that are driven by an `Invoke <https://pyinvoke.org/>`_ task::

    invoke format

Make sure to run this command before creating a pull request!

By default the task formats Python code under ``src``, ``atest`` and ``utest``
directories, but it can be configured to format only certain directories
or files::

    invoke format -t src

Formatting is done in multiple phases:

    1. Code is listed using `Ruff <https://docs.astral.sh/ruff/>`_ . If linting
       fails, the formatting process is stopped.
    2. Code is formatted code using `Black <https://black.readthedocs.io/>`_.
       We plan to switch to Ruff as soon as they stop removing the
       `empty row after the class declaration`__.
    3. Multiline imports are reformatted using `isort <https://pycqa.github.io/isort/>`_.
       We use the "`hanging grid grouped`__" style to use less vertical space compared
       to having each imported item on its own row. Public APIs using `redundant import
       aliases`__ are not reformatted, though.

Tool configurations are in the `<pyproject.toml>`_ file.

__ https://github.com/astral-sh/ruff/issues/9745
__ https://pycqa.github.io/isort/docs/configuration/multi_line_output_modes.html#5-hanging-grid-grouped
__ https://typing.python.org/en/latest/spec/distributing.html#import-conventions

Manual formatting adjustments
'''''''''''''''''''''''''''''

Automatic formatting works pretty well, but there are some cases where the results
are suboptimal and manual adjustments are needed.

.. note:: As a contributor, you do not need to care about this if you do not want to.
          Maintainers can fix these issues themselves after merging your pull request.
          Just running the aforementioned ``invoke format`` is enough.

Force lists to have one item per row
````````````````````````````````````

Automatic formatting has three modes how to handle lists:

- Short lists are formatted on a single row. This includes list items and opening
  and closing braces and other markers.
- If all list items fit into a single row, but the whole list with opening and
  closing markers does not, items are placed into a single row and opening and
  closing markers are on their own rows.
- Long lists are formatted so that all list items are own their own rows and
  opening and closing markers are on their own rows as well.

In addition to lists and other containers, the above applies also to function
calls and function signatures:

.. sourcecode:: python

    def short(first_arg: Iterable[int], second_arg: int = 0) -> int:
        ...

    def medium(
        first_arg: Iterable[float], second_arg: float = 0.0, third_arg: bool = True
    ) -> int:
        ...

    def long(
        first_arg: Iterable[float],
        second_arg: float = 0.0,
        third_arg: bool = True,
        fourth_arg: bool = False,
    ) -> int:
        ...

This formatting is typically fine, but similar code being formatted differently
in a single file can look inconsistent. Having multiple items in a single row, as in
the ``medium`` example above, can also make the code hard to read. A simple fix
is forcing list items to own rows by adding a `magic trailing comma`__ and running
auto-formatter again:

.. sourcecode:: python

    def short(first_arg: Iterable[int], second_arg: int = 0) -> int:
        ...

    def medium(
        first_arg: Iterable[float],
        second_arg: float = 0.0,
        third_arg: bool = True,
    ) -> int:
        ...

    def long(
        first_arg: Iterable[float],
        second_arg: float = 0.0,
        third_arg: bool = True,
        fourth_arg: bool = False,
    ) -> int:
        ...

Lists and signatures fitting into a single line, such as the ``short`` example above,
should typically not be forced to multiple lines.

__ https://black.readthedocs.io/en/stable/the_black_code_style/current_style.html#the-magic-trailing-comma

Force multi-line lists to have multiple items per row
`````````````````````````````````````````````````````

Automatically formatting all list items into own rows uses a lot of vertical space.
This is typically not a problem, but with long lists having simple items it can
be somewhat annoying:

.. sourcecode:: python

    class Branches(
        BaseBranches[
            'Keyword',
            'For',
            'While',
            'Group',
            'If',
            'Try',
            'Var',
            'Return',
            'Continue',
            'Break',
            'Message',
            'Error',
            IT,
        ]
    ):
        __slots__ = ()


    added_in_rf60 = {
        "bg",
        "bs",
        "cs",
        "de",
        "en",
        "es",
        "fi",
        "fr",
        "hi",
        "it",
        "nl",
        "pl",
        "pt",
        "pt-BR",
        "ro",
        "ru",
        "sv",
        "th",
        "tr",
        "uk",
        "zh-CN",
        "zh-TW",
    }

The best way to fix this is disabling formatting altogether with the ``# fmt: skip``
pragma. The code should be formatted so that opening and closing list markers
are on their own rows, list items are wrapped, and the ``# fmt: skip`` pragma
is placed after the closing list marker:

.. sourcecode:: python

    class Branches(BaseBranches[
        "Keyword", "For", "While", "Group", "If", "Try", "Var", "Return", "Continue",
        "Break", "Message", "Error", IT,
    ]):  # fmt: skip
        __slots__ = ()


    added_in_rf60 = {
        "bg", "bs", "cs", "de", "en", "es", "fi", "fr", "hi", "it", "nl", "pl",
        "pt", "pt-BR", "ro", "ru", "sv", "th", "tr", "uk", "zh-CN", "zh-TW",
    }  # fmt: skip

Handle Boolean expressions
``````````````````````````

Autoformatting handles Boolean expressions having two items that do not fit into
a single line *really* strangely:

.. sourcecode::

    ext = getattr(self.parser, 'EXTENSION', None) or getattr(
        self.parser, 'extension', None
    )

    runner = self._get_runner_from_resource_files(
        name
    ) or self._get_runner_from_libraries(name)

Expressions having three or more items would be grouped with parentheses and
`there is an issue`__ about doing that also if there are two items. A workaround
is using parentheses and disabling formatting:

.. sourcecode::

    ext = (
        getattr(self.parser, 'EXTENSION', None)
        or getattr(self.parser, 'extension', None)
    )  # fmt: skip

    runner = (
        self._get_runner_from_resource_files(name)
        or self._get_runner_from_libraries(name)
    )  # fmt: skip

__ https://github.com/psf/black/issues/2156

Docstrings
''''''''''

Docstrings should be added to public APIs, but they are not generally needed in
internal code. When docstrings are added, they should follow `PEP-257
<https://www.python.org/dev/peps/pep-0257/>`_. See `API documentation`_
section below for more details about documentation syntax, generating
API docs, etc.

Type hints
''''''''''

All public APIs must have type hints and adding type hints also to new internal
code is recommended. Full type coverage is not a goal at the moment, though.

Type hints should follow the Python `Typing Best Practices
<https://typing.python.org/en/latest/reference/best_practices.html>`_ with the
following exceptions:

- Annotation features are restricted to the minimum Python version supported by
  Robot Framework.
- Annotations should use the stringified format for annotations not supported
  by the minimum supported Python version. For example, ``"int | float"``
  instead of ``Union[int, float]`` and ``"list[int]"`` instead of ``List[int]``.
- Keywords accepting either an integer or a float should typically be annotated as
  ``int | float`` instead of just ``float``. This way argument conversion tries to
  first convert arguments to an integer and only converts to a float if that fails.
- No ``-> None`` annotation on functions that do not explicitly return anything.

Documentation
~~~~~~~~~~~~~

With new features adequate documentation is as important as the actual
functionality. Different documentation is needed depending on the issue.

User Guide
''''''''''

Robot Framework's features are explained in the `User Guide
<http://robotframework.org/robotframework/#user-guide>`_. It is generated
using a custom script based on the source in `reStructuredText
<http://docutils.sourceforge.net/rst.html>`_ format. For more details about
editing and generating it see `<doc/userguide/README.rst>`_.

Libraries
'''''''''

If `standard libraries
<http://robotframework.org/robotframework/#standard-libraries>`_ distributed
with Robot Framework are enhanced, also their documentation needs to
be updated. Keyword documentation is created from docstrings using the `Libdoc
<http://robotframework.org/robotframework/latest/RobotFrameworkUserGuide.html#libdoc>`_
tool. Documentation must use Robot Framework's own `documentation formatting
<http://robotframework.org/robotframework/latest/RobotFrameworkUserGuide.html#documentation-formatting>`_
and follow these guidelines:

- All new enhancements or changes should have a note telling when the change
  was introduced. Often adding something like ``New in Robot Framework 7.3.``
  is enough.

- Other keywords and sections in the library introduction can be referenced
  with internal links created with backticks like ```Example Keyword```.

- When referring to arguments, argument names must use inline code style
  created with double backticks like ````argument````.

- Examples are recommended whenever the new keyword or enhanced functionality is
  not trivial.

Library documentation can be generated using Invoke_ by running command

::

    invoke library-docs <name>

where ``<name>`` is the name of the library or its unique prefix. Run

::

    invoke --help library-docs

for more information.

API documentation
'''''''''''''''''

Modules and classes defined to be public should have API documentation.
We do not generally use API docs with internal code because it is so hard
to keep the docs in sync with the code. Instead we try to keep the code
as clean and easy to understand as possible.

API docs are created using docstrings following guidelines defined in
`PEP-257`_. They are converted to HTML using `Sphinx <http://sphinx-doc.org/>`_
and its `autodoc <http://sphinx-doc.org/ext/autodoc.html>`_ extension.
Documentation can be created locally using `<doc/api/generate.py>`_ script
that unfortunately creates a lot of errors on the console. Releases API docs
are visible at https://robot-framework.readthedocs.org/.

Tests
~~~~~

When submitting a pull request with a new feature or a fix, you should
always include tests for your changes. These tests prove that your changes
work, help prevent bugs in the future, and help document what your changes
do. Depending on the change, you may need acceptance tests, unit tests
or both.

Make sure to run all of the tests before submitting a pull request to be sure
that your changes do not break anything. If you can, test in multiple
environments and interpreters (Windows, Linux, OS X, different Python
versions etc). Pull requests are also automatically tested by GitHub Actions.

Executing changed code
''''''''''''''''''''''

If you want to manually verify the changes, an easy approach is directly
running the `<src/robot/run.py>`_ script that is part of Robot Framework
itself. Alternatively, you can use the `<rundevel.py>`_ script that sets
some command line options and environment variables to ease executing tests
under the `<atest/testdata>`_ directory. It also automatically creates a
``tmp`` directory in the project root and writes all outputs there.

Acceptance tests
''''''''''''''''

Most of Robot Framework's testing is done using acceptance tests that
naturally use Robot Framework itself for testing. Every new functionality
or fix should generally get one or more acceptance tests. See
`<atest/README.rst>`_ for more details about creating and executing them.

Unit tests
''''''''''

Unit tests are great for testing internal logic and should be added when
appropriate. For more details see `<utest/README.rst>`_.
