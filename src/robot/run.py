#!/usr/bin/env python

#  Copyright 2008-2015 Nokia Networks
#  Copyright 2016-     Robot Framework Foundation
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

"""Module implementing the command line entry point for executing tests.

This module can be executed from the command line using the following
approaches::

    python -m robot.run
    python path/to/robot/run.py

Instead of ``python`` it is possible to use also other Python interpreters.
This module is also used by the installed ``robot`` start-up script.

This module also provides :func:`run` and :func:`run_cli` functions
that can be used programmatically. Other code is for internal usage.
"""

import sys

# Allows running as a script. __name__ check needed with multiprocessing:
# https://github.com/robotframework/robotframework/issues/1137
if 'robot' not in sys.modules and __name__ == '__main__':
    import pythonpathsetter

from robot.conf import RobotSettings
from robot.model import ModelModifier
from robot.output import LOGGER, pyloggingconf
from robot.reporting import ResultWriter
from robot.running.builder import TestSuiteBuilder
from robot.utils import Application, unic, text


USAGE = """Robot Framework -- A generic automation framework

Version:  <VERSION>

Usage:  robot [options] paths
   or:  python -m robot [options] paths
   or:  python path/to/robot [options] paths
   or:  java -jar robotframework.jar [options] paths

Robot Framework is a generic open source automation framework for acceptance
testing, acceptance test-driven development (ATDD) and robotic process
automation (RPA). It has simple, easy-to-use syntax that utilizes the
keyword-driven automation approach. Keywords adding new capabilities are
implemented in libraries using either Python or Java. New higher level
keywords can also be created using Robot Framework's own syntax.

The easiest way to execute Robot Framework is using the `robot` command created
as part of the normal installation. Alternatively it is possible to execute
the `robot` module directly like `python -m robot`, where `python` can be
replaced with any supported Python interpreter such as `jython`, `ipy` or
`python3`. Yet another alternative is running the `robot` directory like
`python path/to/robot`. Finally, there is a standalone JAR distribution
available.

Tests (or tasks in RPA terminology) are created in files typically having the
`*.robot` extension. Files automatically create test (or task) suites and
directories with these files create higher level suites. When Robot Framework
is executed, paths to these files or directories are given to it as arguments.

By default Robot Framework creates an XML output file and a log and a report in
HTML format, but this can be configured using various options listed below.
Outputs in HTML format are for human consumption and XML output for integration
with other systems. XML outputs can also be combined and otherwise further
post-processed with the Rebot tool that is an integral part of Robot Framework.
Run `rebot --help` for more information.

Robot Framework is open source software released under Apache License 2.0.
For more information about the framework and the rich ecosystem around it
see http://robotframework.org/.

Options
=======

    --rpa                 Turn on the generic automation mode. Mainly affects
                          terminology so that "test" is replaced with "task"
                          in logs and reports. By default the mode is got
                          from test/task header in data files. New in RF 3.1.
 -F --extension value     Parse only files with this extension when executing
                          a directory. Has no effect when running individual
                          files or when using resource files. If more than one
                          extension is needed, separate them with a colon.
                          Examples: `--extension txt`, `--extension robot:txt`
                          Starting from RF 3.2 only `*.robot` files are parsed
                          by default.
 -N --name name           Set the name of the top level suite. By default the
                          name is created based on the executed file or
                          directory.
 -D --doc documentation   Set the documentation of the top level suite.
                          Simple formatting is supported (e.g. *bold*). If the
                          documentation contains spaces, it must be quoted.
                          Example: --doc "Very *good* example"
 -M --metadata name:value *  Set metadata of the top level suite. Value can
                          contain formatting similarly as --doc.
                          Example: --metadata Version:1.2
 -G --settag tag *        Sets given tag(s) to all executed tests.
 -t --test name *         Select tests by name or by long name containing also
                          parent suite name like `Parent.Test`. Name is case
                          and space insensitive and it can also be a simple
                          pattern where `*` matches anything, `?` matches any
                          single character, and `[chars]` matches one character
                          in brackets.
    --task name *         Alias to --test. Especially applicable with --rpa.
 -s --suite name *        Select suites by name. When this option is used with
                          --test, --include or --exclude, only tests in
                          matching suites and also matching other filtering
                          criteria are selected. Name can be a simple pattern
                          similarly as with --test and it can contain parent
                          name separated with a dot. For example, `-s X.Y`
                          selects suite `Y` only if its parent is `X`.
 -i --include tag *       Select tests by tag. Similarly as name with --test,
                          tag is case and space insensitive and it is possible
                          to use patterns with `*`, `?` and `[]` as wildcards.
                          Tags and patterns can also be combined together with
                          `AND`, `OR`, and `NOT` operators.
                          Examples: --include foo --include bar*
                                    --include fooANDbar*
 -e --exclude tag *       Select test cases not to run by tag. These tests are
                          not run even if included with --include. Tags are
                          matched using same rules as with --include.
 -R --rerunfailed output  Select failed tests from an earlier output file to be
                          re-executed. Equivalent to selecting same tests
                          individually using --test.
 -S --rerunfailedsuites output  Select failed suites from an earlier output
                          file to be re-executed.
    --runemptysuite       Executes suite even if it contains no tests. Useful
                          e.g. with --include/--exclude when it is not an error
                          that no test matches the condition.
    --skip tag *          Tests having given tag will be skipped. Tag can be
                          a pattern. New in RF 4.0.
    --skiponfailure tag *  Tests having given tag will be skipped if they fail.
                          Tag can be a pattern. New in RF 4.0.
 -n --noncritical tag *   Alias for --skiponfailure. Deprecated since RF 4.0.
 -c --critical tag *      Opposite of --noncritical. Deprecated since RF 4.0.
 -v --variable name:value *  Set variables in the test data. Only scalar
                          variables with string value are supported and name is
                          given without `${}`. See --variablefile for a more
                          powerful variable setting mechanism.
                          Examples:
                          --variable str:Hello       =>  ${str} = `Hello`
                          -v hi:Hi_World -E space:_  =>  ${hi} = `Hi World`
                          -v x: -v y:42              =>  ${x} = ``, ${y} = `42`
 -V --variablefile path *  Python or YAML file file to read variables from.
                          Possible arguments to the variable file can be given
                          after the path using colon or semicolon as separator.
                          Examples: --variablefile path/vars.yaml
                                    --variablefile environment.py:testing
 -d --outputdir dir       Where to create output files. The default is the
                          directory where tests are run from and the given path
                          is considered relative to that unless it is absolute.
 -o --output file         XML output file. Given path, similarly as paths given
                          to --log, --report, --xunit, and --debugfile, is
                          relative to --outputdir unless given as an absolute
                          path. Other output files are created based on XML
                          output files after the test execution and XML outputs
                          can also be further processed with Rebot tool. Can be
                          disabled by giving a special value `NONE`.
                          Default: output.xml
 -l --log file            HTML log file. Can be disabled by giving a special
                          value `NONE`. Default: log.html
                          Examples: `--log mylog.html`, `-l NONE`
 -r --report file         HTML report file. Can be disabled with `NONE`
                          similarly as --log. Default: report.html
 -x --xunit file          xUnit compatible result file. Not created unless this
                          option is specified.
    --xunitskipnoncritical  Deprecated since RF 4.0 and has no effect anymore.
 -b --debugfile file      Debug file written during execution. Not created
                          unless this option is specified.
 -T --timestampoutputs    When this option is used, timestamp in a format
                          `YYYYMMDD-hhmmss` is added to all generated output
                          files between their basename and extension. For
                          example `-T -o output.xml -r report.html -l none`
                          creates files like `output-20070503-154410.xml` and
                          `report-20070503-154410.html`.
    --splitlog            Split the log file into smaller pieces that open in
                          browsers transparently.
    --logtitle title      Title for the generated log file. The default title
                          is `<SuiteName> Test Log`.
    --reporttitle title   Title for the generated report file. The default
                          title is `<SuiteName> Test Report`.
    --reportbackground colors  Background colors to use in the report file.
                          Order is `passed:failed:skipped`. Both color names
                          and codes work. `skipped` can be omitted.
                          Examples: --reportbackground green:red:yellow
                                    --reportbackground #00E:#E00
    --maxerrorlines lines  Maximum number of error message lines to show in
                          report when tests fail. Default is 40, minimum is 10
                          and `NONE` can be used to show the full message.
 -L --loglevel level      Threshold level for logging. Available levels: TRACE,
                          DEBUG, INFO (default), WARN, NONE (no logging). Use
                          syntax `LOGLEVEL:DEFAULT` to define the default
                          visible log level in log files.
                          Examples: --loglevel DEBUG
                                    --loglevel DEBUG:INFO
    --suitestatlevel level  How many levels to show in `Statistics by Suite`
                          in log and report. By default all suite levels are
                          shown. Example:  --suitestatlevel 3
    --tagstatinclude tag *  Include only matching tags in `Statistics by Tag`
                          in log and report. By default all tags are shown.
                          Given tag can be a pattern like with --include.
    --tagstatexclude tag *  Exclude matching tags from `Statistics by Tag`.
                          This option can be used with --tagstatinclude
                          similarly as --exclude is used with --include.
    --tagstatcombine tags:name *  Create combined statistics based on tags.
                          These statistics are added into `Statistics by Tag`.
                          If the optional `name` is not given, name of the
                          combined tag is got from the specified tags. Tags are
                          matched using the same rules as with --include.
                          Examples: --tagstatcombine requirement-*
                                    --tagstatcombine tag1ANDtag2:My_name
    --tagdoc pattern:doc *  Add documentation to tags matching the given
                          pattern. Documentation is shown in `Test Details` and
                          also as a tooltip in `Statistics by Tag`. Pattern can
                          use `*`, `?` and `[]` as wildcards like --test.
                          Documentation can contain formatting like --doc.
                          Examples: --tagdoc mytag:Example
                                    --tagdoc "owner-*:Original author"
    --tagstatlink pattern:link:title *  Add external links into `Statistics by
                          Tag`. Pattern can use `*`, `?` and `[]` as wildcards
                          like --test. Characters matching to `*` and `?`
                          wildcards can be used in link and title with syntax
                          %N, where N is index of the match (starting from 1).
                          Examples: --tagstatlink mytag:http://my.domain:Title
                          --tagstatlink "bug-*:http://url/id=%1:Issue Tracker"
    --expandkeywords name:<pattern>|tag:<pattern> *
                          Matching keywords will be automatically expanded in
                          the log file. Matching against keyword name or tags
                          work using same rules as with --removekeywords.
                          Examples: --expandkeywords name:BuiltIn.Log
                                    --expandkeywords tag:expand
                          New in RF 3.2.
    --removekeywords all|passed|for|wuks|name:<pattern>|tag:<pattern> *
                          Remove keyword data from the generated log file.
                          Keywords containing warnings are not removed except
                          in the `all` mode.
                          all:     remove data from all keywords
                          passed:  remove data only from keywords in passed
                                   test cases and suites
                          for:     remove passed iterations from for loops
                          wuks:    remove all but the last failing keyword
                                   inside `BuiltIn.Wait Until Keyword Succeeds`
                          name:<pattern>:  remove data from keywords that match
                                   the given pattern. The pattern is matched
                                   against the full name of the keyword (e.g.
                                   'MyLib.Keyword', 'resource.Second Keyword'),
                                   is case, space, and underscore insensitive,
                                   and may contain `*`, `?` and `[]` wildcards.
                                   Examples: --removekeywords name:Lib.HugeKw
                                             --removekeywords name:myresource.*
                          tag:<pattern>:  remove data from keywords that match
                                   the given pattern. Tags are case and space
                                   insensitive and patterns can contain `*`,
                                   `?` and `[]` wildcards. Tags and patterns
                                   can also be combined together with `AND`,
                                   `OR`, and `NOT` operators.
                                   Examples: --removekeywords foo
                                             --removekeywords fooANDbar*
    --flattenkeywords for|foritem|name:<pattern>|tag:<pattern> *
                          Flattens matching keywords in the generated log file.
                          Matching keywords get all log messages from their
                          child keywords and children are discarded otherwise.
                          for:     flatten for loops fully
                          foritem: flatten individual for loop iterations
                          name:<pattern>:  flatten matched keywords using same
                                   matching rules as with
                                   `--removekeywords name:<pattern>`
                          tag:<pattern>:  flatten matched keywords using same
                                   matching rules as with
                                   `--removekeywords tag:<pattern>`
    --listener class *    A class for monitoring test execution. Gets
                          notifications e.g. when tests start and end.
                          Arguments to the listener class can be given after
                          the name using a colon or a semicolon as a separator.
                          Examples: --listener MyListenerClass
                                    --listener path/to/Listener.py:arg1:arg2
    --nostatusrc          Sets the return code to zero regardless of failures
                          in test cases. Error codes are returned normally.
    --dryrun              Verifies test data and runs tests so that library
                          keywords are not executed.
 -X --exitonfailure       Stops test execution if any critical test fails.
    --exitonerror         Stops test execution if any error occurs when parsing
                          test data, importing libraries, and so on.
    --skipteardownonexit  Causes teardowns to be skipped if test execution is
                          stopped prematurely.
    --randomize all|suites|tests|none  Randomizes the test execution order.
                          all:    randomizes both suites and tests
                          suites: randomizes suites
                          tests:  randomizes tests
                          none:   no randomization (default)
                          Use syntax `VALUE:SEED` to give a custom random seed.
                          The seed must be an integer.
                          Examples: --randomize all
                                    --randomize tests:1234
    --prerunmodifier class *  Class to programmatically modify the test suite
                          structure before execution.
    --prerebotmodifier class *  Class to programmatically modify the result
                          model before creating reports and logs.
    --console type        How to report execution on the console.
                          verbose:  report every suite and test (default)
                          dotted:   only show `.` for passed test, `f` for
                                    failed non-critical tests, and `F` for
                                    failed critical tests
                          quiet:    no output except for errors and warnings
                          none:     no output whatsoever
 -. --dotted              Shortcut for `--console dotted`.
    --quiet               Shortcut for `--console quiet`.
 -W --consolewidth chars  Width of the console output. Default is 78.
 -C --consolecolors auto|on|ansi|off  Use colors on console output or not.
                          auto: use colors when output not redirected (default)
                          on:   always use colors
                          ansi: like `on` but use ANSI colors also on Windows
                          off:  disable colors altogether
                          Note that colors do not work with Jython on Windows.
 -K --consolemarkers auto|on|off  Show markers on the console when top level
                          keywords in a test case end. Values have same
                          semantics as with --consolecolors.
 -P --pythonpath path *   Additional locations (directories, ZIPs, JARs) where
                          to search test libraries and other extensions when
                          they are imported. Multiple paths can be given by
                          separating them with a colon (`:`) or by using this
                          option several times. Given path can also be a glob
                          pattern matching multiple paths.
                          Examples:
                          --pythonpath libs/ --pythonpath resources/*.jar
                          --pythonpath /opt/testlibs:mylibs.zip:yourlibs
 -A --argumentfile path *  Text file to read more arguments from. Use special
                          path `STDIN` to read contents from the standard input
                          stream. File can have both options and input files
                          or directories, one per line. Contents do not need to
                          be escaped but spaces in the beginning and end of
                          lines are removed. Empty lines and lines starting
                          with a hash character (#) are ignored.
                          Example file:
                          |  --include regression
                          |  --name Regression Tests
                          |  # This is a comment line
                          |  my_tests.robot
                          |  path/to/test/directory/
                          Examples:
                          --argumentfile argfile.txt --argumentfile STDIN
 -h -? --help             Print usage instructions.
 --version                Print version information.

Options that are marked with an asterisk (*) can be specified multiple times.
For example, `--test first --test third` selects test cases with name `first`
and `third`. If an option accepts a value but is not marked with an asterisk,
the last given value has precedence. For example, `--log A.html --log B.html`
creates log file `B.html`. Options accepting no values can be disabled by
using the same option again with `no` prefix added or dropped. The last option
has precedence regardless of how many times options are used. For example,
`--dryrun --dryrun --nodryrun --nostatusrc --statusrc` would not activate the
dry-run mode and would return a normal return code.

Long option format is case-insensitive. For example, --SuiteStatLevel is
equivalent to but easier to read than --suitestatlevel. Long options can
also be shortened as long as they are unique. For example, `--logti Title`
works while `--lo log.html` does not because the former matches only --logtitle
but the latter matches --log, --loglevel and --logtitle.

Environment Variables
=====================

ROBOT_OPTIONS             Space separated list of default options to be placed
                          in front of any explicit options on the command line.
ROBOT_SYSLOG_FILE         Path to a file where Robot Framework writes internal
                          information about parsing test case files and running
                          tests. Can be useful when debugging problems. If not
                          set, or set to a special value `NONE`, writing to the
                          syslog file is disabled.
ROBOT_SYSLOG_LEVEL        Log level to use when writing to the syslog file.
                          Available levels are the same as with --loglevel
                          command line option and the default is INFO.
ROBOT_INTERNAL_TRACES     When set to any non-empty value, Robot Framework's
                          internal methods are included in error tracebacks.

Examples
========

# Simple test run using `robot` command without options.
$ robot tests.robot

# Using options.
$ robot --include smoke --name "Smoke Tests" path/to/tests.robot

# Executing `robot` module using Python.
$ python -m robot path/to/tests

# Running `robot` directory with Jython.
$ jython /opt/robot tests.robot

# Executing multiple test case files and using case-insensitive long options.
$ robot --SuiteStatLevel 2 --Metadata Version:3 tests/*.robot more/tests.robot

# Setting default options and syslog file before running tests.
$ export ROBOT_OPTIONS="--outputdir results --suitestatlevel 2"
$ export ROBOT_SYSLOG_FILE=/tmp/syslog.txt
$ robot tests.robot
"""


class RobotFramework(Application):

    def __init__(self):
        Application.__init__(self, USAGE, arg_limits=(1,),
                             env_options='ROBOT_OPTIONS', logger=LOGGER)

    def main(self, datasources, **options):
        settings = RobotSettings(options)
        LOGGER.register_console_logger(**settings.console_output_config)
        if settings['Critical'] or settings['NonCritical']:
            LOGGER.warn("Command line options --critical and --noncritical have been "
                        "deprecated. Use --skiponfailure instead.")
        if settings['XUnitSkipNonCritical']:
            LOGGER.warn("Command line option --xunitskipnoncritical has been "
                        "deprecated and has no effect.")
        LOGGER.info('Settings:\n%s' % unic(settings))
        builder = TestSuiteBuilder(settings['SuiteNames'],
                                   included_extensions=settings.extension,
                                   rpa=settings.rpa,
                                   allow_empty_suite=settings.run_empty_suite)
        suite = builder.build(*datasources)
        settings.rpa = suite.rpa
        if settings.pre_run_modifiers:
            suite.visit(ModelModifier(settings.pre_run_modifiers,
                                      settings.run_empty_suite, LOGGER))
        suite.configure(**settings.suite_config)
        with pyloggingconf.robot_handler_enabled(settings.log_level):
            old_max_error_lines = text.MAX_ERROR_LINES
            text.MAX_ERROR_LINES = settings.max_error_lines
            try:
                result = suite.run(settings)
            finally:
                text.MAX_ERROR_LINES = old_max_error_lines
            LOGGER.info("Tests execution ended. Statistics:\n%s"
                        % result.suite.stat_message)
            if settings.log or settings.report or settings.xunit:
                writer = ResultWriter(settings.output if settings.log
                                      else result)
                writer.write_results(settings.get_rebot_settings())
        return result.return_code

    def validate(self, options, arguments):
        return self._filter_options_without_value(options), arguments

    def _filter_options_without_value(self, options):
        return dict((name, value) for name, value in options.items()
                    if value not in (None, []))


def run_cli(arguments=None, exit=True):
    """Command line execution entry point for running tests.

    :param arguments: Command line options and arguments as a list of strings.
        Starting from RF 3.1, defaults to ``sys.argv[1:]`` if not given.
    :param exit: If ``True``, call ``sys.exit`` with the return code denoting
        execution status, otherwise just return the rc.

    Entry point used when running tests from the command line, but can also
    be used by custom scripts that execute tests. Especially useful if the
    script itself needs to accept same arguments as accepted by Robot Framework,
    because the script can just pass them forward directly along with the
    possible default values it sets itself.

    Example::

        from robot import run_cli

        # Run tests and return the return code.
        rc = run_cli(['--name', 'Example', 'tests.robot'], exit=False)

        # Run tests and exit to the system automatically.
        run_cli(['--name', 'Example', 'tests.robot'])

    See also the :func:`run` function that allows setting options as keyword
    arguments like ``name="Example"`` and generally has a richer API for
    programmatic test execution.
    """
    if arguments is None:
        arguments = sys.argv[1:]
    return RobotFramework().execute_cli(arguments, exit=exit)


def run(*tests, **options):
    """Programmatic entry point for running tests.

    :param tests: Paths to test case files/directories to be executed similarly
        as when running the ``robot`` command on the command line.
    :param options: Options to configure and control execution. Accepted
        options are mostly same as normal command line options to the ``robot``
        command. Option names match command line option long names without
        hyphens so that, for example, ``--name`` becomes ``name``.

    Most options that can be given from the command line work. An exception
    is that options ``--pythonpath``, ``--argumentfile``, ``--help`` and
    ``--version`` are not supported.

    Options that can be given on the command line multiple times can be
    passed as lists. For example, ``include=['tag1', 'tag2']`` is equivalent
    to ``--include tag1 --include tag2``. If such options are used only once,
    they can be given also as a single string like ``include='tag'``.

    Options that accept no value can be given as Booleans. For example,
    ``dryrun=True`` is same as using the ``--dryrun`` option.

    Options that accept string ``NONE`` as a special value can also be used
    with Python ``None``. For example, using ``log=None`` is equivalent to
    ``--log NONE``.

    ``listener``, ``prerunmodifier`` and ``prerebotmodifier`` options allow
    passing values as Python objects in addition to module names these command
    line options support. For example, ``run('tests', listener=MyListener())``.

    To capture the standard output and error streams, pass an open file or
    file-like object as special keyword arguments ``stdout`` and ``stderr``,
    respectively.

    A return code is returned similarly as when running on the command line.
    Zero means that tests were executed and no critical test failed, values up
    to 250 denote the number of failed critical tests, and values between
    251-255 are for other statuses documented in the Robot Framework User Guide.

    Example::

        from robot import run

        run('path/to/tests.robot')
        run('tests.robot', include=['tag1', 'tag2'], splitlog=True)
        with open('stdout.txt', 'w') as stdout:
            run('t1.robot', 't2.robot', name='Example', log=None, stdout=stdout)

    Equivalent command line usage::

        robot path/to/tests.robot
        robot --include tag1 --include tag2 --splitlog tests.robot
        robot --name Example --log NONE t1.robot t2.robot > stdout.txt
    """
    return RobotFramework().execute(*tests, **options)


if __name__ == '__main__':
    run_cli(sys.argv[1:])
