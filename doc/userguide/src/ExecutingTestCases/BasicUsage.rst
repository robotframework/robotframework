Basic usage
===========

Robot Framework test cases are executed from the command line, and the
end result is, by default, an `output file`_ in XML format and an HTML
report_ and log_. After the execution, output files can be combined and
otherwise `post-processed`__ with the ``rebot`` tool.

__ `Post-processing outputs`_

.. contents::
   :depth: 2
   :local:

Starting test execution
-----------------------

Synopsis
~~~~~~~~

::

    pybot|jybot|ipybot [options] data_sources
    python|jython|ipy -m robot.run [options] data_sources
    python|jython|ipy path/to/robot/run.py [options] data_sources
    java -jar robotframework.jar [options] data_sources

Test execution is normally started using ``pybot``, ``jybot``
or ``ipybot`` `runner script`_. These scripts are otherwise identical, but
the first one executes tests using Python_, the second using Jython_, and the
last one using IronPython_. Alternatively it is possible to use
``robot.run`` `entry point`_ either as a module or a script using
any interpreter, or use the `standalone JAR distribution`_.

Regardless of execution approach, the path (or paths) to the test data to be
executed is given as an argument after the command. Additionally, different
command line options can be used to alter the test execution or generated
outputs in some way.

Specifying test data to be executed
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Robot Framework test cases are created in files__ and directories__,
and they are executed by giving the path to the file or directory in
question to the selected runner script. The path can be absolute or,
more commonly, relative to the directory where tests are executed
from. The given file or directory creates the top-level test suite,
which gets its name, unless overridden with the :option:`--name` option__,
from the `file or directory name`__. Different execution possibilities
are illustrated in the examples below. Note that in these examples, as
well as in other examples in this section, only the ``pybot`` script
is used, but other execution approaches could be used similarly.

__ `Test case files`_
__ `Test suite directories`_
__ `Setting the name`_
__ `Test suite name and documentation`_

::

   pybot test_cases.html
   pybot path/to/my_tests/
   pybot c:\robot\tests.txt

It is also possible to give paths to several test case files or
directories at once, separated with spaces. In this case, Robot
Framework creates the top-level test suite automatically, and
the specified files and directories become its child test suites. The name
of the created test suite is got from child suite names by
catenating them together with an ampersand (&) and spaces. For example,
the name of the top-level suite in the first example below is
:name:`My Tests & Your Tests`. These automatically created names are
often quite long and complicated. In most cases, it is thus better to
use the :option:`--name` option for overriding it, as in the second
example below::

   pybot my_tests.html your_tests.html
   pybot --name Example path/to/tests/pattern_*.html

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

   pybot -L debug my_tests.txt
   pybot --include smoke --variable HOST:10.0.0.42 path/to/tests/

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

The long option format is case-insensitive, which facilitates writing option
names in an easy-to-read format. For example, :option:`--SuiteStatLevel`
is equivalent to, but easier to read than :option:`--suitestatlevel`.

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

.. note:: Support for adding or dropping `no` prefix is a new feature in
          Robot Framework 2.9. In earlier versions options accepting no
          values could be disabled by using the exact same option again.

Simple patterns
~~~~~~~~~~~~~~~

Many command line options take arguments as *simple patterns*. These
`glob-like patterns`__ are matched according to the following rules:

- `*` is a wildcard matching any string, even an empty string.
- `?` is a wildcard matching any single character.
- Unless noted otherwise, pattern matching is case, space, and underscore insensitive.

Examples::

   --test Example*     # Matches tests with name starting 'Example', case insensitively.
   --include f??       # Matches tests with a tag that starts with 'f' or 'F' and is three characters long.

__ http://en.wikipedia.org/wiki/Glob_(programming)

Tag patterns
~~~~~~~~~~~~

Most tag related options accept arguments as *tag patterns*. They have all the
same characteristics as `simple patterns`_, but they also support `AND`,
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

   Starting from Robot Framework 2.9 the pattern can also start with `NOT`
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

.. note:: `OR` operator is new in Robot Framework 2.8.4.

``ROBOT_OPTIONS`` and ``REBOT_OPTIONS`` environment variables
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Environment variables ``ROBOT_OPTIONS`` and ``REBOT_OPTIONS`` can be
used to specify default options for `test execution`_ and `result
post-processing`__, respectively. The options and their values must be
defined as a space separated list and they are placed in front of any
explicit options on the command line. The main use case for these
environment variables is setting global default values for certain options to
avoid the need to repeat them every time tests are run or ``rebot`` used.

.. sourcecode:: bash

   export ROBOT_OPTIONS="--critical regression --tagdoc mytag:Example_doc"
   pybot tests.txt
   export REBOT_OPTIONS="--reportbackground green:yellow:red"
   rebot --name example output.xml

.. note:: Support for ``ROBOT_OPTIONS`` and ``REBOT_OPTIONS`` environment
          variables was added in Robot Framework 2.8.2.

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
   2 critical tests, 1 passed, 1 failed
   2 tests total, 1 passed, 1 failed
   ==============================================================================
   Output:  /path/to/output.xml
   Report:  /path/to/report.html
   Log:     /path/to/log.html

Starting from Robot Framework 2.7, there is also a notification on the console
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
successfully and no `critical test`_ fail, the return code is zero.
All possible return codes are explained in the table below.

.. table:: Possible return codes
   :class: tabular

   ========  ==========================================
      RC                    Explanation
   ========  ==========================================
   0         All critical tests passed.
   1-249     Returned number of critical tests failed.
   250       250 or more critical failures.
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

The return code can be set to 0 even if there are critical failures using
the :option:`--NoStatusRC` command line option. This might be useful, for
example, in continuous integration servers where post-processing of results
is needed before the overall status of test execution can be determined.

.. note:: Same return codes are also used with rebot_.

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
       <td class="msg">Error in file '/home/robot/tests.html' in table 'Setting' in element on row 2: Resource file 'resource.html' does not exist</td>
     </tr>
     <tr>
       <td class="time">20090322&nbsp;19:58:43.931</td>
       <td class="warn level">WARN</td>
       <td class="msg">Keyword 'SomeLibrary.Example Keyword' is deprecated. Use keyword `Other Keyword` instead.</td>
     </tr>
   </table>

__ `Deprecating keywords`_

Escaping complicated characters
-------------------------------

Because spaces are used for separating options from each other, it is
problematic to use them in option values.  Some options, such as
:option:`--name`, automatically convert underscores to spaces, but
with others spaces must be escaped. Additionally, many special
characters are complicated to use on the command line.
Because escaping complicated characters with a backslash or quoting
the values does not always work too well, Robot Framework has its own
generic escaping mechanism. Another possibility is using `argument
files`_ where options can be specified in the plain text format. Both of
these mechanisms work when executing tests and when
post-processing outputs, and also some of the external supporting
tools have the same or similar capabilities.

In Robot Framework's command line escaping mechanism,
problematic characters are escaped with freely selected text. The
command line option to use is :option:`--escape (-E)`,
which takes an argument in the format `what:with`,
where `what` is the name of the character to escape and
`with` is the string to escape it with. Characters that can
be escaped are listed in the table below:

.. table:: Available escapes
   :class: tabular

   =========  =============  =========  =============
   Character   Name to use   Character   Name to use
   =========  =============  =========  =============
   &          amp            (          paren1
   '          apos           )          paren2
   @          at             %          percent
   \\         bslash         \|         pipe
   :          colon          ?          quest
   ,          comma          "          quot
   {          curly1         ;          semic
   }          curly2         /          slash
   $          dollar         \          space
   !          exclam         [          square1
   >          gt             ]          square2
   #          hash           \*         star
   <          lt             \          \
   =========  =============  =========  =============

The following examples make the syntax more clear. In the
first example, the metadata `X` gets the value `Value with
spaces`, and in the second example variable `${VAR}` is assigned to
`"Hello, world!"`::

    --escape space:_ --metadata X:Value_with_spaces
    -E space:SP -E quot:QU -E comma:CO -E exclam:EX -v VAR:QUHelloCOSPworldEXQU

Note that all the given command line arguments, including paths to test
data, are escaped. Escape character sequences thus need to be
selected carefully.

Argument files
--------------

Argument files allow placing all or some command line options and arguments
into an external file where they will be read. This avoids the problems with
characters that are problematic on the command line. If lot of options or
arguments are needed, argument files also prevent the command that is used on
the command line growing too long.

Argument files are taken into use with :option:`--argumentfile (-A)` option
along with possible other command line options.

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
space. In Robot Framework 2.7.6 and newer it is possible to use either an equal
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

   pybot --argumentfile all_arguments.txt
   pybot --name Example --argumentfile other_options_and_paths.txt
   pybot --argumentfile default_options.txt --name Example my_tests.html
   pybot -A first.txt -A second.txt -A third.txt tests.txt

Reading argument files from standard input
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Special argument file name `STDIN` can be used to read arguments from the
standard input stream instead of a file. This can be useful when generating
arguments with a script::

   generate_arguments.sh | pybot --argumentfile STDIN
   generate_arguments.sh | pybot --name Example --argumentfile STDIN tests.txt

Getting help and version information
------------------------------------

Both when executing test cases and when post-processing outputs, it is possible
to get command line help with the option :option:`--help (-h)`.
These help texts have a short general overview and
briefly explain the available command line options.

All runner scripts also support getting the version information with
the option :option:`--version`. This information also contains Python
or Jython version and the platform type::

   $ pybot --version
   Robot Framework 2.7 (Python 2.6.6 on linux2)

   $ jybot --version
   Robot Framework 2.7 (Jython 2.5.2 on java1.6.0_21)

   C:\>rebot --version
   Rebot 2.7 (Python 2.7.1 on win32)

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

In the first examples, the same web tests are executed with different
browsers and the results combined afterwards. This is easy with shell
scripts, as practically you just list the needed commands one after
another:

.. sourcecode:: bash

   #!/bin/bash
   pybot --variable BROWSER:Firefox --name Firefox --log none --report none --output out/fx.xml login
   pybot --variable BROWSER:IE --name IE --log none --report none --output out/ie.xml login
   rebot --name Login --outputdir out --output login.xml out/fx.xml out/ie.xml

Implementing the above example with Windows batch files is not very
complicated, either. The most important thing to remember is that
because ``pybot`` and ``rebot`` are implemented as batch
files, ``call`` must be used when running them from another batch
file. Otherwise execution would end when the first batch file is
finished.

.. sourcecode:: bat

   @echo off
   call pybot --variable BROWSER:Firefox --name Firefox --log none --report none --output out\fx.xml login
   call pybot --variable BROWSER:IE --name IE --log none --report none --output out\ie.xml login
   call rebot --name Login --outputdir out --output login.xml out\fx.xml out\ie.xml

In the next examples, jar files under the :file:`lib` directory are
put into ``CLASSPATH`` before starting the test execution. In these
examples, start-up scripts require that paths to the executed test
data are given as arguments. It is also possible to use command line
options freely, even though some options have already been set in the
script. All this is relatively straight-forward using bash:

.. sourcecode:: bash

   #!/bin/bash

   cp=.
   for jar in lib/*.jar; do
       cp=$cp:$jar
   done
   export CLASSPATH=$cp

   jybot --ouputdir /tmp/logs --suitestatlevel 2 $*

Implementing this using Windows batch files is slightly more complicated. The
difficult part is setting the variable containing the needed JARs inside a For
loop, because, for some reason, that is not possible without a helper
function.

.. sourcecode:: bat

   @echo off

   set CP=.
   for %%jar in (lib\*.jar) do (
       call :set_cp %%jar
   )
   set CLASSPATH=%CP%

   jybot --ouputdir c:\temp\logs --suitestatlevel 2 %*

   goto :eof

   :: Helper for setting variables inside a for loop
   :set_cp
       set CP=%CP%;%1
   goto :eof

Modifying Java startup parameters
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Sometimes when using Jython there is need to alter the Java startup parameters.
The most common use case is increasing the JVM maximum memory size as the
default value may not be enough for creating reports and logs when
outputs are very big. There are several ways to configure JVM options:

1. Modify Jython start-up script (``jython`` shell script or
   ``jython.bat`` batch file) directly. This is a permanent configuration.

2. Set ``JYTHON_OPTS`` environment variable. This can be done permanently
   in operating system level or per execution in a custom start-up script.

3. Pass the needed Java parameters wit :option:`-J` option to Jython start-up
   script that will pass them forward to Java. This is especially easy when
   using `direct entry points`_::

      jython -J-Xmx1024m -m robot.run some_tests.txt

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
the problem is in an individual keyword.

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
The typical way of invoking pdb by inserting

.. sourcecode:: python

   import pdb; pdb.set_trace()

at the location you want to break into debugger will not work correctly
with Robot Framework, though, as the standard output stream is
redirected during keyword execution. Instead, you can use the following:

.. sourcecode:: python

   import sys, pdb; pdb.Pdb(stdout=sys.__stdout__).set_trace()

__ http://docs.python.org/2/library/pdb.html
