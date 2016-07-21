Contribution guidelines
=======================

These guidelines instruct how to submit issues and contribute code to the
`Robot Framework project <https://github.com/robotframework/robotframework>`_.
There are also many other projects in the larger `Robot Framework ecosystem
<http://robotframework.org>`_ that you can contribute to. If you notice
a library or tool missing, there is hardly any better way to contribute
than creating your own project. Other great ways to contribute include
answering questions and participating discussion on `robotframework-users
<https://groups.google.com/forum/#!forum/robotframework-users>`_ mailing list
and other forums, as well as spreading the word about the framework one way or
the other.

.. contents::
   :depth: 2
   :local:

Submitting issues
-----------------

Bugs and enhancements are tracked in the `issue tracker
<https://github.com/robotframework/robotframework/issues>`_. If you are
unsure if something is a bug or is a feature worth implementing, you can
first ask on `robotframework-users`_ mailing list, on `IRC
<http://webchat.freenode.net/?channels=robotframework&prompt=1>`_
(#robotframework on irc.freenode.net), or on `Slack
<https://robotframework-slack.herokuapp.com>`_. These and other similar
forums, not the issue tracker, are also places where to ask general questions.

Before submitting a new issue, it is always a good idea to check is the
same bug or enhancement already reported. If it is, please add your comments
to the existing issue instead of creating a new one.

Reporting bugs
~~~~~~~~~~~~~~

Explain the bug you have encountered so that others can understand it
and preferably also reproduce it. Key things to have in good bug report:

1. Version information

   - Robot Framework version
   - Python interpreter type (Python, Jython or IronPython) and version
   - Operating system name and version

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
in form of a pull request as explained below or to pay someone for the work.
Consider also would it be better to implement this functionality as a separate
tool outside the core framework.

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
and knowledge.

Pull requests
~~~~~~~~~~~~~

On GitHub pull requests are the main mechanism to contribute code. They
are easy to use both for the contributor and for person accepting
the contribution, and with more complex contributions it is easy also
for others to join the discussion. Preconditions for creating a pull
requests are having a `GitHub account <https://github.com/>`_,
installing `Git <https://git-scm.com>`_ and forking the
`Robot Framework project`_.

GitHub has good articles explaining how to
`set up Git <https://help.github.com/articles/set-up-git/>`_,
`fork a repository <https://help.github.com/articles/fork-a-repo/>`_ and
`use pull requests <https://help.github.com/articles/using-pull-requests>`_
and we do not go through them in more detail. We do, however,
recommend to create dedicated branches for pull requests instead of creating
them based on the master branch. This is especially important if you plan to
work on multiple pull requests at the same time.

Coding conventions
~~~~~~~~~~~~~~~~~~

General guidelines
''''''''''''''''''

Robot Framework uses the general Python code conventions defined in `PEP-8
<https://www.python.org/dev/peps/pep-0008/>`_. In addition to that, we try
to write `idiomatic Python
<http://python.net/~goodger/projects/pycon/2007/idiomatic/handout.html>`_
and follow the `SOLID principles
<https://en.wikipedia.org/wiki/SOLID_(object-oriented_design)>`_ with all
new code. An important guideline is that the code should be clear enough that
comments are generally not needed.

All code, including test code, must be compatible with all supported Python
interpreters and versions. Most importantly this means that the code must
support both Python 2 and Python 3.

Whitespace
''''''''''

We are pretty picky about using whitespace. We follow `PEP-8`_ in how to use
blank lines and whitespace in general, but we also have some stricter rules:

- No blank lines inside functions.
- Indentation using spaces, not tabs.
- No trailing spaces.
- No extra empty lines at the end of the file.
- Files must end with a newline.

Most of these rules are such that any decent text editor or IDE can be
configured to automatically format files according to them.

Docstrings
''''''''''

Docstrings should be added to public APIs, but they are not generally needed in
internal code. When docstrings are added, they should follow `PEP-257
<https://www.python.org/dev/peps/pep-0257/>`_. See `API documentation`_
section below for more details about documentation syntax, generating
API docs, etc.

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

- Other keywords and sections in the library introduction can be referenced
  with internal links created with backticks like ```Example Keyword```.

- When referring to arguments, argument names must use inline code style
  created with double backticks like ````argument````.

- Examples are recommended whenever the new keyword or enhanced functionality is
  not trivial.

- All new enhancements or changes should have a note telling when the change
  was introduced. Often adding something like ``New in Robot Framework 2.9.``
  is enough.

Library documentation can be easily created using `<doc/libraries/lib2html.py>`_
script. Resulting docs should be verified before the code is committed.

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

Robot Framework's public API docs are lacking in many ways. All public
classes are not yet documented, existing documentation is somewhat scarce,
and there could be more examples. Documentation improvements are highly
appreciated!

Tests
~~~~~

When submitting a pull request with a new feature or a fix, you should
always include tests for your changes. These tests prove that your changes
work, help prevent bugs in the future, and help document what your changes
do. Depending an the change, you may need acceptance tests, unit tests
or both.

Make sure to run all of the tests before submitting a pull request to be sure
that your changes do not break anything. If you can, test in multiple
environments and interpreters (Windows, Linux, OS X, Python, Jython,
IronPython, Python 3, etc). Pull requests are also automatically tested on
continuous integration.

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

Continuous integration
''''''''''''''''''''''

Robot Framework's continuous integration (CI) servers are visible through
http://robot.radiaatto.ri.fi/. They automatically test all new commits
to the repository both on Linux and on Windows, and pull requests can be
tested there too.

When a new pull request comes in, the CI will ask if one of the admins
can verify the pull request. The admins are currently @jussimalinen and
@pekkaklarck. The commands are:

-  ``robotci: once`` (run once)
-  ``robotci: enable`` (run whenever this pull request changes)
-  ``robotci: whitelist user`` (enable CI for all pull requests coming
   from this user)

The commands can be anywhere on the comment. Adding the skip statement
(``[skip ci]``, with the square brackets) to the pull request body will
cause the job not to be executed.

Finalizing pull requests
~~~~~~~~~~~~~~~~~~~~~~~~

Once you have code, documentation and tests ready, it is time to finalize
the pull request.

AUTHORS.txt
'''''''''''

If you have done any non-trivial change and would like to be credited,
add yourself to `<AUTHORS.txt>`_ file.

Resolving conflicts
'''''''''''''''''''

Conflicts can occur if there are new changes to the master that touch the
same code as your changes. In that case you should `sync your fork
<https://help.github.com/articles/syncing-a-fork>`_ and `resolve conflicts
<https://help.github.com/articles/resolving-a-merge-conflict-from-the-command-line>`_
to allow for an easy merge.

The most common conflicting file is the aforementioned `AUTHORS.txt`_, but
luckily fixing those conflicts is typically easy.

Squashing commits
'''''''''''''''''

If the pull request contains multiple commits, it is recommended that you
squash them into a single commit before the pull request is merged.
See `Squashing Github pull requests into a single commit
<http://eli.thegreenplace.net/2014/02/19/squashing-github-pull-requests-into-a-single-commit>`_
article for more details about why and how.

Squashing is especially important if the pull request contains lots of
temporary commits and changes that have been later reverted or redone.
Squashing is not needed if the commit history is clean and individual
commits are meaningful alone.
