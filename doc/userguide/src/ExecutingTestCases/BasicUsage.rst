Basic usage
===========

Robot Framework test cases are executed from the command line, and the
end result is, by default, an `output file`_ in XML format and an HTML
report_ and log_. After the execution, output files can be combined and
otherwise `post-processed`__ with the Rebot tool.

__ `Post-processing outputs`_

.. contents::
   :depth: 2
   :local:

.. _executing test cases:

Starting test execution
-----------------------

Synopsis
~~~~~~~~

::

    robot [options] data
    python -m robot [options] data
    python path/to/robot/ [options] data

Execution is normally started using the ``robot`` command created as part of
installation__. Alternatively it is possible to execute the installed ``robot``
module using the selected Python interpreter. This is especially convenient
if Robot Framework has been installed under multiple Python versions.
Finally, if you know where the installed ``robot`` directory exists, it can
be executed using Python as well.

Regardless of execution approach, the path (or paths) to the test data to be
executed is given as an argument after the command. Additionally, different
command line options can be used to alter the test execution or generated
outputs in many ways.

__ `Installation instructions`_

Specifying test data to be executed
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Robot Framework test cases are created in files__ and directories__,
and they are executed by giving the path to the file or directory in
question to the selected runner script. The path can be absolute or,
more commonly, relative to the directory where tests are executed
from. The given file or directory creates the top-level test suite,
which, by default, gets its name from the `file or directory name`__.
Different execution possibilities
are illustrated in the examples below. Note that in these examples, as
well as in other examples in this section, only the ``robot`` script
is used, but other execution approaches could be used similarly.

::

   robot tests.robot
   robot path/to/my_tests/
   robot c:\robot\tests.robot

.. note:: When executing a directory__, all files and directories starting with
          a dot (:file:`.`) or an underscore (:file:`_`) are ignored and,
          by default, only files with the :file:`.robot` extension executed.
          See the `Selecting files to parse`_ section for more details.

It is also possible to give paths to several test case files or
directories at once, separated with spaces. In this case, Robot
Framework creates the top-level test suite automatically, and
the specified files and directories become its child test suites. The name
of the created test suite is got from child suite names by
concatenating them together with an ampersand (&) and spaces. For example,
the name of the top-level suite in the first example below is
:name:`My Tests & Your Tests`. These automatically created names are
often quite long and complicated. In most cases, it is thus better to
use the :option:`--name` option for overriding it, as in the second
example below::

   robot my_tests.robot your_tests.robot
   robot --name Example path/to/tests/pattern_*.robot

Starting from Robot Framework 6.1, it is also possible to define a
`test suite initialisation file`__ for the automatically created top-level
suite. The path to the init file is given similarly to the
test case files::

    robot __init__.robot my_tests.robot other_tests.robot

__ `Suite files`_
__ `Suite directories`_
__ `Suite name`_
__ `Suite directories`_
__ `Suite initialization files`_

Using command line options
--------------------------

Robot Framework provides a number of command line options that can be
used to control how test cases are executed and what outputs are
generated. This section explains the option syntax, and what
options actually exist. How they can be used is discussed elsewhere
in this chapter.

Using options
~~~~~~~~~~~~~

When options are used, they must always be given between the runner
script and the data sources. For example::

   robot -L debug my_tests.robot
   robot --include smoke --variable HOST:10.0.0.42 path/to/tests/

Short and long options
~~~~~~~~~~~~~~~~~~~~~~

Options always have a long name, such as :option:`--name`, and the
most frequently needed options also have a short name, such as
:option:`-N`. In addition to that, long options can be shortened as
long as they are unique. For example, `--logle DEBUG` works,
while `--lo log.html` does not, because the former matches only
:option:`--loglevel`, but the latter matches several options. Short
and shortened options are practical when executing test cases
manually, but long options are recommended in `start-up scripts`_,
because they are easier to understand.

The long option names are case-insensitive and hyphen-insensitive,
which facilitates writing option names in an easy-to-read format.
For example, :option:`--SuiteStatLevel` and :option:`--suite-stat-level`
are equivalent to, but easier to read than, :option:`--suitestatlevel`.

.. note:: Long options being hyphen-insensitive is new in Robot Framework 6.1.

Setting option values
~~~~~~~~~~~~~~~~~~~~~

Most of the options require a value, which is given after the option
name. Both short and long options accept the value separated
from the option name with a space, as in `--include tag`
or `-i tag`. With long options, the separator can also be the
equals sign, for example `--include=tag`, and with short options the
separator can be omitted, as in `-itag`.

Some options can be specified several times. For example,
`--variable VAR1:value --variable VAR2:another` sets two
variables. If the options that take only one value are used several
times, the value given last is effective.

Disabling options accepting no values
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Options accepting no values can be disabled by using the same option again
with `no` prefix added or dropped. The last option has precedence regardless
of how many times options are used. For example, `--dryrun --dryrun --nodryrun
--nostatusrc --statusrc` would not activate the dry-run mode and would return
normal status rc.

.. _wildcards:

Simple patterns
~~~~~~~~~~~~~~~

Many command line options take arguments as *simple patterns*. These
`glob-like patterns`__ are matched according to the following rules:

- `*` matches any string, even an empty string.
- `?` matches any single character.
- `[abc]` matches one character in the bracket.
- `[!abc]` matches one character not in the bracket.
- `[a-z]` matches one character from the range in the bracket.
- `[!a-z]` matches one character not from the range in the bracket.
- Unlike with glob patterns normally, path separator characters `/` and
  :codesc:`\\` and the newline character `\n` are matches by the above
  wildcards.
- Unless noted otherwise, pattern matching is case, space, and underscore insensitive.

Examples::

   --test Example*        # Matches tests with name starting 'Example'.
   --test Example[1-2]    # Matches tests 'Example1' and 'Example2'.
   --include f??          # Matches tests with a tag that starts with 'f' is three characters long.

All matching in above examples is case, space and underscore insensitive.
For example, the second example would also match test named `example 1`.

If the matched text happens to contain some of the wildcard characters and
they need to be matched literally, it is possible to do that by using
the `[...]` syntax. The pattern `[*]` matches the literal `*` character,
`[?]` matches `?`, and `[[]` matches `[`. Lone `[` and `]` do not need to
be escaped.

.. note:: Support for brackets like `[abc]` and `[!a-z]` is new in
          Robot Framework 3.1.

__ http://en.wikipedia.org/wiki/Glob_(programming)

Tag patterns
~~~~~~~~~~~~

Most tag related options accept arguments as *tag patterns*. They support same
wildcards as `simple patterns`_ (e.g. `examp??`, `ex*le`), but they also support `AND`,
`OR` and `NOT` operators explained below. These operators can be
used for combining two or more individual tags or patterns together.

`AND` or `&`
   The whole pattern matches if all individual patterns match. `AND` and
   `&` are equivalent::

      --include fooANDbar     # Matches tests containing tags 'foo' and 'bar'.
      --exclude xx&yy&zz      # Matches tests containing tags 'xx', 'yy', and 'zz'.

`OR`
   The whole pattern matches if any individual pattern matches::

      --include fooORbar      # Matches tests containing either tag 'foo' or tag 'bar'.
      --exclude xxORyyORzz    # Matches tests containing any of tags 'xx', 'yy', or 'zz'.

`NOT`
   The whole pattern matches if the pattern on the left side matches but
   the one on the right side does not. If used multiple times, none of
   the patterns after the first `NOT` must not match::

      --include fooNOTbar     # Matches tests containing tag 'foo' but not tag 'bar'.
      --exclude xxNOTyyNOTzz  # Matches tests containing tag 'xx' but not tag 'yy' or tag 'zz'.

   The pattern can also start with `NOT`
   in which case the pattern matches if the pattern after `NOT` does not match::

      --include NOTfoo        # Matches tests not containing tag 'foo'
      --include NOTfooANDbar  # Matches tests not containing tags 'foo' and 'bar'

The above operators can also be used together. The operator precedence,
from highest to lowest, is `AND`, `OR` and `NOT`::

    --include xANDyORz      # Matches tests containing either tags 'x' and 'y', or tag 'z'.
    --include xORyNOTz      # Matches tests containing either tag 'x' or 'y', but not tag 'z'.
    --include xNOTyANDz     # Matches tests containing tag 'x', but not tags 'y' and 'z'.

Although tag matching itself is case-insensitive, all operators are
case-sensitive and must be written with upper case letters. If tags themselves
happen to contain upper case `AND`, `OR` or `NOT`, they need to specified
using lower case letters to avoid accidental operator usage::

    --include port          # Matches tests containing tag 'port', case-insensitively
    --include PORT          # Matches tests containing tag 'P' or 'T', case-insensitively
    --exclude handoverORportNOTnotification

``ROBOT_OPTIONS`` and ``REBOT_OPTIONS`` environment variables
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Environment variables ``ROBOT_OPTIONS`` and ``REBOT_OPTIONS`` can be
used to specify default options for `test execution`_ and `result
post-processing`__, respectively. The options and their values must be
defined as a space separated list and they are placed in front of any
explicit options on the command line. The main use case for these
environment variables is setting global default values for certain options to
avoid the need to repeat them every time tests are run or Rebot used.

.. sourcecode:: bash

   export ROBOT_OPTIONS="--outputdir results --tagdoc 'mytag:Example doc with spaces'"
   robot tests.robot
   export REBOT_OPTIONS="--reportbackground blue:red:yellow"
   rebot --name example output.xml

__ `Post-processing outputs`_

Test results
------------

Command line output
~~~~~~~~~~~~~~~~~~~

The most visible output from test execution is the output displayed in
the command line. All executed test suites and test cases, as well as
their statuses, are shown there in real time. The example below shows the
output from executing a simple test suite with only two test cases::

   ==============================================================================
   Example test suite
   ==============================================================================
   First test :: Possible test documentation                             | PASS |
   ------------------------------------------------------------------------------
   Second test                                                           | FAIL |
   Error message is displayed here
   ==============================================================================
   Example test suite                                                    | FAIL |
   2 tests, 1 passed, 1 failed
   ==============================================================================
   Output:  /path/to/output.xml
   Report:  /path/to/report.html
   Log:     /path/to/log.html

There is also a notification on the console
whenever a top-level keyword in a test case ends. A green dot is used if
a keyword passes and a red F if it fails. These markers are written to the end
of line and they are overwritten by the test status when the test itself ends.
Writing the markers is disabled if console output is redirected to a file.

Generated output files
~~~~~~~~~~~~~~~~~~~~~~

The command line output is very limited, and separate output files are
normally needed for investigating the test results. As the example
above shows, three output files are generated by default. The first
one is in XML format and contains all the information about test
execution. The second is a higher-level report and the third is a more
detailed log file. These files and other possible output files are
discussed in more detail in the section `Different output files`_.

Return codes
~~~~~~~~~~~~

Runner scripts communicate the overall test execution status to the
system running them using return codes. When the execution starts
successfully and no tests fail, the return code is zero.
All possible return codes are explained in the table below.

.. table:: Possible return codes
   :class: tabular

   ========  ==========================================
      RC                    Explanation
   ========  ==========================================
   0         All tests passed.
   1-249     Returned number of tests failed.
   250       250 or more failures.
   251       Help or version information printed.
   252       Invalid test data or command line options.
   253       Test execution stopped by user.
   255       Unexpected internal error.
   ========  ==========================================

Return codes should always be easily available after the execution,
which makes it easy to automatically determine the overall execution
status. For example, in bash shell the return code is in special
variable `$?`, and in Windows it is in `%ERRORLEVEL%`
variable. If you use some external tool for running tests, consult its
documentation for how to get the return code.

The return code can be set to 0 even if there are failures using
the :option:`--NoStatusRC` command line option. This might be useful, for
example, in continuous integration servers where post-processing of results
is needed before the overall status of test execution can be determined.

.. note:: Same return codes are also used with Rebot_.

Errors and warnings during execution
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

During the test execution there can be unexpected problems like
failing to import a library or a resource file or a keyword being
deprecated__. Depending on the severity such problems are categorized
as errors or warnings and they are written into the console (using the
standard error stream), shown on a separate *Test Execution Errors*
section in log files, and also written into Robot Framework's own
`system log`_. Normally these errors and warnings are generated by Robot
Framework itself, but libraries can also log `errors and warnings`_.
Example below illustrates how errors and warnings look like in the log file.

.. raw:: html

   <table class="messages">
     <tr>
       <td class="time">20090322&nbsp;19:58:42.528</td>
       <td class="error level">ERROR</td>
       <td class="msg">Error in file '/home/robot/tests.robot' in table 'Setting' in element on row 2: Resource file 'resource.robot' does not exist</td>
     </tr>
     <tr>
       <td class="time">20090322&nbsp;19:58:43.931</td>
       <td class="warn level">WARN</td>
       <td class="msg">Keyword 'SomeLibrary.Example Keyword' is deprecated. Use keyword `Other Keyword` instead.</td>
     </tr>
   </table>

__ `Deprecating keywords`_

Argument files
--------------

Argument files allow placing all or some command line options and arguments
into an external file where they will be read. This avoids the problems with
characters that are problematic on the command line. If lot of options or
arguments are needed, argument files also prevent the command that is used on
the command line growing too long.

Argument files are taken into use with :option:`--argumentfile (-A)` option
along with possible other command line options.

.. note:: Unlike other `long command line options`__, :option:`--argumentfile`
          cannot be given in shortened format like :option:`--argumentf`.

__ `Short and long options`_

Argument file syntax
~~~~~~~~~~~~~~~~~~~~

Argument files can contain both command line options and paths to the test data,
one option or data source per line. Both short and long options are supported,
but the latter are recommended because they are easier to understand.
Argument files can contain any characters without escaping, but spaces in
the beginning and end of lines are ignored. Additionally, empty lines and
lines starting with a hash mark (#) are ignored::

   --doc This is an example (where "special characters" are ok!)
   --metadata X:Value with spaces
   --variable VAR:Hello, world!
   # This is a comment
   path/to/my/tests

In the above example the separator between options and their values is a single
space. It is possible to use either an equal
sign (=) or any number of spaces. As an example, the following three lines are
identical::

    --name An Example
    --name=An Example
    --name       An Example

If argument files contain non-ASCII characters, they must be saved using
UTF-8 encoding.

Using argument files
~~~~~~~~~~~~~~~~~~~~

Argument files can be used either alone so that they contain all the options
and paths to the test data, or along with other options and paths. When
an argument file is used with other arguments, its contents are placed into
the original list of arguments to the same place where the argument file
option was. This means that options in argument files can override options
before it, and its options can be overridden by options after it. It is possible
to use :option:`--argumentfile` option multiple times or even recursively::

   robot --argumentfile all_arguments.robot
   robot --name Example --argumentfile other_options_and_paths.robot
   robot --argumentfile default_options.txt --name Example my_tests.robot
   robot -A first.txt -A second.txt -A third.txt tests.robot

Reading argument files from standard input
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Special argument file name `STDIN` can be used to read arguments from the
standard input stream instead of a file. This can be useful when generating
arguments with a script::

   generate_arguments.sh | robot --argumentfile STDIN
   generate_arguments.sh | robot --name Example --argumentfile STDIN tests.robot

Getting help and version information
------------------------------------

Both when executing test cases and when post-processing outputs, it is possible
to get command line help with the option :option:`--help (-h)`.
These help texts have a short general overview and
briefly explain the available command line options.

All runner scripts also support getting the version information with
the option :option:`--version`. This information also contains Python
version and the platform type::

   $ robot --version
   Robot Framework 7.0 (Python 3.12.1 on darwin)

   C:\>rebot --version
   Rebot 6.1.1 (Python 3.11.0 on win32)

.. _start-up script:
.. _start-up scripts:

Creating start-up scripts
-------------------------

Test cases are often executed automatically by a continuous
integration system or some other mechanism. In such cases, there is a
need to have a script for starting the test execution, and possibly
also for post-processing outputs somehow. Similar scripts are also
useful when running tests manually, especially if a large number of
command line options are needed or setting up the test environment is
complicated.

In UNIX-like environments, shell scripts provide a simple but powerful
mechanism for creating custom start-up scripts. Windows batch files
can also be used, but they are more limited and often also more
complicated. A platform-independent alternative is using Python or
some other high-level programming language. Regardless of the
language, it is recommended that long option names are used, because
they are easier to understand than the short names.

Shell script example
~~~~~~~~~~~~~~~~~~~~

In this example, the same web tests in the ``login`` directory are executed
with different browsers and the results combined afterwards using Rebot_.
The script also accepts command line options itself and simply forwards them
to the ``robot`` command using the handy ``$*`` variable:

.. sourcecode:: bash

   #!/bin/bash
   robot --name Firefox --variable BROWSER:Firefox --output out/fx.xml --log none --report none $* login
   robot --name IE --variable BROWSER:IE --output out/ie.xml --log none --report none  $* login
   rebot --name Login --outputdir out --output login.xml out/fx.xml out/ie.xml

Batch file example
~~~~~~~~~~~~~~~~~~

Implementing the above shell script example using batch files is not very
complicated either. Notice that arguments to batch files can be forwarded
to executed commands using ``%*``:

.. sourcecode:: bat

   @echo off
   robot --name Firefox --variable BROWSER:Firefox --output out\fx.xml --log none --report none %* login
   robot --name IE --variable BROWSER:IE --log none --output out\ie.xml --report none %* login
   rebot --name Login --outputdir out --output login.xml out\fx.xml out\ie.xml

.. note:: Prior to Robot Framework 3.1 ``robot`` and ``rebot`` commands were
          implemented as batch files on Windows and using them in another
          batch file required prefixing the whole command with ``call``.

Python example
~~~~~~~~~~~~~~

When start-up scripts gets more complicated, implementing them using shell
scripts or batch files is not that convenient. This is especially true if
both variants are needed and same logic needs to be implemented twice. In
such situations it is often better to switch to Python. It is possible to
execute Robot Framework from Python using the `subprocess module`__, but
often using Robot Framework's own `programmatic API`__ is more convenient.
The easiest APIs to use are ``robot.run_cli`` and ``robot.rebot_cli`` that
accept same command line arguments than the ``robot`` and ``rebot`` commands.

The following example implements the same logic as the earlier shell script
and batch file examples. In Python arguments to the script itself are
available in ``sys.argv``:

.. sourcecode:: python

   #!/usr/bin/env python
   import sys
   from robot import run_cli, rebot_cli

   common = ['--log', 'none', '--report', 'none'] + sys.argv[1:] + ['login']
   run_cli(['--name', 'Firefox', '--variable', 'BROWSER:Firefox', '--output', 'out/fx.xml'] + common, exit=False)
   run_cli(['--name', 'IE', '--variable', 'BROWSER:IE', '--output', 'out/ie.xml'] + common, exit=False)
   rebot_cli(['--name', 'Login', '--outputdir', 'out', 'out/fx.xml', 'out/ie.xml'])


.. note:: ``exit=False`` is needed because by default ``run_cli`` exits to
          system with the correct `return code`_. ``rebot_cli`` does that too,
          but in the above example that is fine.

__ https://docs.python.org/library/subprocess.html
__ https://robot-framework.readthedocs.io

Making :file:`*.robot` files executable
---------------------------------------

On UNIX-like operating systems it is possible to make :file:`*.robot`
files executable by giving them execution permission and adding a shebang__
like in this example:

.. sourcecode:: robotframework

    #!/usr/bin/env robot

    *** Test Cases ***
    Example
        Log to console    Executing!

If the above content would be in a file :file:`example.robot` and that file
would be executable, it could be executed from the command line like below.
Starting from Robot Framework 3.2, individually executed files can have any
extension, or no extension at all, so the same would work also if the file
would be named just :file:`example`.

.. sourcecode:: bash

    ./example.robot

This trick does not work when executing a directory but can be handy when
executing a single file. It is probably more often useful when
`automating tasks`__ than when automating tests.

__ https://en.wikipedia.org/wiki/Shebang_(Unix)
__ `Creating tasks`_

Debugging problems
------------------

A test case can fail because the system under test does not work
correctly, in which case the test has found a bug, or because the test
itself is buggy. The error message explaining the failure is shown on
the `command line output`_ and in the `report file`_, and sometimes
the error message alone is enough to pinpoint the problem. More often
that not, however, `log files`_ are needed because they have also
other log messages and they show which keyword actually failed.

When a failure is caused by the tested application, the error message
and log messages ought to be enough to understand what caused it. If
that is not the case, the test library does not provide `enough
information`__ and needs to be enhanced. In this situation running the
same test manually, if possible, may also reveal more information
about the issue.

Failures caused by test cases themselves or by keywords they use can
sometimes be hard to debug. If the error message, for example, tells
that a keyword is used with wrong number of arguments fixing the
problem is obviously easy, but if a keyword is missing or fails in
unexpected way finding the root cause can be harder. The first place
to look for more information is the `execution errors`_ section in
the log file. For example, an error about a failed test library import
may well explain why a test has failed due to a missing keyword.

If the log file does not provide enough information by default, it is
possible to execute tests with a lower `log level`_. For example
tracebacks showing where in the code the failure occurred are logged
using the `DEBUG` level, and this information is invaluable when
the problem is in an individual library keyword.

Logged tracebacks do not contain information about methods inside Robot
Framework itself. If you suspect an error is caused by a bug in the framework,
you can enable showing internal traces by setting environment variable
``ROBOT_INTERNAL_TRACES`` to any non-empty value.

If the log file still does not have enough information, it is a good
idea to enable the syslog_ and see what information it provides. It is
also possible to add some keywords to the test cases to see what is
going on. Especially BuiltIn_ keywords :name:`Log` and :name:`Log
Variables` are useful. If nothing else works, it is always possible to
search help from `mailing lists`_ or elsewhere.

__ `Communicating with Robot Framework`_

Using the Python debugger (pdb)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

It is also possible to use the pdb__ module from the Python standard
library to set a break point and interactively debug a running test.
The typical way of invoking pdb by inserting:

.. sourcecode:: python

   import pdb; pdb.set_trace()

at the location you want to break into debugger will not work correctly
with Robot Framework, as the standard output stream is
redirected during keyword execution. Instead, you can use the following:

.. sourcecode:: python

   import sys, pdb; pdb.Pdb(stdout=sys.__stdout__).set_trace()

from within a python library or alternatively:

.. sourcecode:: robotframework

  Evaluate    pdb.Pdb(stdout=sys.__stdout__).set_trace()    modules=sys, pdb

can be used directly in a test case.

__ http://docs.python.org/library/pdb.html
