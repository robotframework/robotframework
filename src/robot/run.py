#!/usr/bin/env python

#  Copyright 2008-2015 Nokia Solutions and Networks
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
from robot.running import TestSuiteBuilder
from robot.utils import Application, unic


USAGE = """Robot Framework -- A generic test automation framework

Version:  <VERSION>

Usage:  robot [options] data_sources
   or:  python -m robot [options] data_sources
   or:  python path/to/robot [options] data_sources
   or:  java -jar robotframework.jar [options] data_sources

Robot Framework is a Python-based keyword-driven test automation framework for
acceptance level testing and acceptance test-driven development (ATDD). It has
an easy-to-use tabular syntax for creating test cases and its testing
capabilities can be extended by test libraries implemented either with Python
or Java. Users can also create new higher level keywords from existing ones
using the same simple syntax that is used for creating test cases.

The easiest way to execute tests is using the `robot` script created as part
of the normal installation. Alternatively it is possible to execute the `robot`
module directly using `python -m robot`, where `python` can be replaced with
any supported Python interpreter like `jython`, `ipy` or `python3`. Yet another
alternative is running the `robot` directory like `python path/to/robot`.
Finally, there is a standalone JAR distribution.

Data sources given to Robot Framework are either test case files or directories
containing them and/or other directories. Single test case file creates a test
suite containing all the test cases in it and a directory containing test case
files creates a higher level test suite with test case files or other
directories as sub test suites. If multiple data sources are given, a virtual
top level suite containing suites generated from given data sources is created.

By default Robot Framework creates an XML output file and a log and a report in
HTML format, but this can be configured using various options listed below.
Outputs in HTML format are for human consumption and XML output for integration
with other systems. XML outputs can also be combined and otherwise further
processed with `rebot` tool. Run `rebot --help` for more information.

Robot Framework is open source software released under Apache License 2.0. Its
copyrights are owned and development supported by Nokia Solutions and Networks.
For more information about the framework see http://robotframework.org/.

Options
=======

 -N --name name           Set the name of the top level test suite. Underscores
                          in the name are converted to spaces. Default name is
                          created from the name of the executed data source.
 -D --doc documentation   Set the documentation of the top level test suite.
                          Underscores in the documentation are converted to
                          spaces and it may also contain simple HTML formatting
                          (e.g. *bold* and http://url/).
 -M --metadata name:value *  Set metadata of the top level suite. Underscores
                          in the name and value are converted to spaces. Value
                          can contain same HTML formatting as --doc.
                          Example: --metadata version:1.2
 -G --settag tag *        Sets given tag(s) to all executed test cases.
 -t --test name *         Select test cases to run by name or long name. Name
                          is case and space insensitive and it can also be a
                          simple pattern where `*` matches anything and `?`
                          matches any char. If using `*` and `?` in the console
                          is problematic see --escape and --argumentfile.
 -s --suite name *        Select test suites to run by name. When this option
                          is used with --test, --include or --exclude, only
                          test cases in matching suites and also matching other
                          filtering criteria are selected. Name can be a simple
                          pattern similarly as with --test and it can contain
                          parent name separated with a dot. For example
                          `-s X.Y` selects suite `Y` only if its parent is `X`.
 -i --include tag *       Select test cases to run by tag. Similarly as name
                          with --test, tag is case and space insensitive and it
                          is possible to use patterns with `*` and `?` as
                          wildcards. Tags and patterns can also be combined
                          together with `AND`, `OR`, and `NOT` operators.
                          Examples: --include foo --include bar*
                                    --include fooANDbar*
 -e --exclude tag *       Select test cases not to run by tag. These tests are
                          not run even if included with --include. Tags are
                          matched using the rules explained with --include.
 -R --rerunfailed output  Select failed tests from an earlier output file to be
                          re-executed. Equivalent to selecting same tests
                          individually using --test option.
 -c --critical tag *      Tests having given tag are considered critical. If no
                          critical tags are set, all tags are critical. Tags
                          can be given as a pattern like with --include.
 -n --noncritical tag *   Tests with given tag are not critical even if they
                          have a tag set with --critical. Tag can be a pattern.
 -v --variable name:value *  Set variables in the test data. Only scalar
                          variables with string value are supported and name is
                          given without `${}`. See --escape for how to use
                          special characters and --variablefile for a more
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
                          disabled by giving a special value `NONE`. In this
                          case, also log and report are automatically disabled.
                          Default: output.xml
 -l --log file            HTML log file. Can be disabled by giving a special
                          value `NONE`. Default: log.html
                          Examples: `--log mylog.html`, `-l NONE`
 -r --report file         HTML report file. Can be disabled with `NONE`
                          similarly as --log. Default: report.html
 -x --xunit file          xUnit compatible result file. Not created unless this
                          option is specified.
    --xunitskipnoncritical  Mark non-critical tests on xUnit output as skipped.
 -b --debugfile file      Debug file written during execution. Not created
                          unless this option is specified.
 -T --timestampoutputs    When this option is used, timestamp in a format
                          `YYYYMMDD-hhmmss` is added to all generated output
                          files between their basename and extension. For
                          example `-T -o output.xml -r report.html -l none`
                          creates files like `output-20070503-154410.xml` and
                          `report-20070503-154410.html`.
    --splitlog            Split log file into smaller pieces that open in
                          browser transparently.
    --logtitle title      Title for the generated test log. The default title
                          is `<Name Of The Suite> Test Log`. Underscores in
                          the title are converted into spaces in all titles.
    --reporttitle title   Title for the generated test report. The default
                          title is `<Name Of The Suite> Test Report`.
    --reportbackground colors  Background colors to use in the report file.
                          Either `all_passed:critical_passed:failed` or
                          `passed:failed`. Both color names and codes work.
                          Examples: --reportbackground green:yellow:red
                                    --reportbackground #00E:#E00
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
                          and `Test Details` in log and report. By default all
                          tags set in test cases are shown. Given `tag` can
                          also be a simple pattern (see e.g. --test).
    --tagstatexclude tag *  Exclude matching tags from `Statistics by Tag` and
                          `Test Details`. This option can be used with
                          --tagstatinclude similarly as --exclude is used with
                          --include.
    --tagstatcombine tags:name *  Create combined statistics based on tags.
                          These statistics are added into `Statistics by Tag`
                          and matching tests into `Test Details`. If optional
                          `name` is not given, name of the combined tag is got
                          from the specified tags. Tags are combined using the
                          rules explained in --include.
                          Examples: --tagstatcombine requirement-*
                                    --tagstatcombine tag1ANDtag2:My_name
    --tagdoc pattern:doc *  Add documentation to tags matching given pattern.
                          Documentation is shown in `Test Details` and also as
                          a tooltip in `Statistics by Tag`. Pattern can contain
                          characters `*` (matches anything) and `?` (matches
                          any char). Documentation can contain formatting
                          similarly as with --doc option.
                          Examples: --tagdoc mytag:My_documentation
                                    --tagdoc regression:*See*_http://info.html
                                    --tagdoc owner-*:Original_author
    --tagstatlink pattern:link:title *  Add external links into `Statistics by
                          Tag`. Pattern can contain characters `*` (matches
                          anything) and `?` (matches any char). Characters
                          matching to wildcard expressions can be used in link
                          and title with syntax %N, where N is index of the
                          match (starting from 1). In title underscores are
                          automatically converted to spaces.
                          Examples: --tagstatlink mytag:http://my.domain:Link
                          --tagstatlink bug-*:http://tracker/id=%1:Bug_Tracker
    --removekeywords all|passed|for|wuks|name:<pattern>|tag:<pattern> *
                          Remove keyword data from the generated log file.
                          Keywords containing warnings are not removed except
                          in `all` mode.
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
                                   and may contain `*` and `?` as wildcards.
                                   Examples: --removekeywords name:Lib.HugeKw
                                             --removekeywords name:myresource.*
                          tag:<pattern>:  remove data from keywords that match
                                   the given pattern. Tags are case and space
                                   insensitive and it is possible to use
                                   patterns with `*` and `?` as wildcards.
                                   Tags and patterns can also be combined
                                   together with `AND`, `OR`, and `NOT`
                                   operators.
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
                          notifications e.g. when a test case starts and ends.
                          Arguments to the listener class can be given after
                          the name using colon or semicolon as a separator.
                          Examples: --listener MyListenerClass
                                    --listener path/to/Listener.py:arg1:arg2
    --warnonskippedfiles  If this option is used, skipped test data files will
                          cause a warning that is visible in the console output
                          and the log file. By default skipped files only cause
                          an info level syslog message.
    --nostatusrc          Sets the return code to zero regardless of failures
                          in test cases. Error codes are returned normally.
    --runemptysuite       Executes tests also if the top level test suite is
                          empty. Useful e.g. with --include/--exclude when it
                          is not an error that no test matches the condition.
    --dryrun              Verifies test data and runs tests so that library
                          keywords are not executed.
    --exitonfailure       Stops test execution if any critical test fails.
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
 -W --consolewidth chars  Width of the monitor output. Default is 78.
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
                          pattern matching multiple paths but then it normally
                          must be escaped or quoted.
                          Examples:
                          --pythonpath libs/
                          --pythonpath /opt/testlibs:mylibs.zip:yourlibs
                          -E star:STAR -P lib/STAR.jar -P mylib.jar
 -E --escape what:with *  Escape characters which are problematic in console.
                          `what` is the name of the character to escape and
                          `with` is the string to escape it with. Note that
                          all given arguments, incl. data sources, are escaped
                          so escape characters ought to be selected carefully.
                          <--------------------ESCAPES------------------------>
                          Examples:
                          --escape space:_ --metadata X:Value_with_spaces
                          -E space:SP -E quot:Q -v var:QhelloSPworldQ
 -A --argumentfile path *  Text file to read more arguments from. Use special
                          path `STDIN` to read contents from the standard input
                          stream. File can have both options and data sources
                          one per line. Contents do not need to be escaped but
                          spaces in the beginning and end of lines are removed.
                          Empty lines and lines starting with a hash character
                          (#) are ignored.
                          Example file:
                          |  --include regression
                          |  --name Regression Tests
                          |  # This is a comment line
                          |  my_tests.html
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
dry-run mode and would return normal status rc.

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

# Simple test run with `robot` without options.
$ robot tests.robot

# Using options.
$ robot --include smoke --name Smoke_Tests path/to/tests.robot

# Executing `robot` module using Python.
$ python -m robot test_directory

# Running `robot` directory with Jython.
$ jython /opt/robot tests.robot

# Executing multiple test case files and using case-insensitive long options.
$ robot --SuiteStatLevel 2 --Metadata Version:3 tests/*.robot more/tests.robot

# Setting default options and syslog file before running tests.
$ export ROBOT_OPTIONS="--critical regression --suitestatlevel 2"
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
        LOGGER.info('Settings:\n%s' % unic(settings))
        suite = TestSuiteBuilder(settings['SuiteNames'],
                                 settings['WarnOnSkipped']).build(*datasources)
        suite.configure(**settings.suite_config)
        if settings.pre_run_modifiers:
            suite.visit(ModelModifier(settings.pre_run_modifiers,
                                      settings.run_empty_suite, LOGGER))
        with pyloggingconf.robot_handler_enabled(settings.log_level):
            result = suite.run(settings)
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


def run_cli(arguments):
    """Command line execution entry point for running tests.

    :param arguments: Command line arguments as a list of strings.

    For programmatic usage the :func:`run` function is typically better. It has
    a better API for that usage and does not call :func:`sys.exit` like this
    function.

    Example::

        from robot import run_cli

        run_cli(['--include', 'tag', 'path/to/tests.html'])
    """
    RobotFramework().execute_cli(arguments)


def run(*datasources, **options):
    """Executes given Robot Framework data sources with given options.

    Data sources are paths to files and directories, similarly as when running
    `robot` command from the command line. Options are given as keyword
    arguments and their names are same as long command line options except
    without hyphens.

    Options that can be given on the command line multiple times can be
    passed as lists like `include=['tag1', 'tag2']`. If such option is used
    only once, it can be given also as a single string like `include='tag'`.

    Additionally listener, prerunmodifier and prerebotmodifier options support
    passing values as instances in addition to module names. For example,
    `run('tests.robot', listener=Listener(), prerunmodifier=Modifier())`.

    To capture stdout and/or stderr streams, pass open file objects in as
    special keyword arguments `stdout` and `stderr`, respectively.

    A return code is returned similarly as when running on the command line.

    Example::

        from robot import run

        run('path/to/tests.html', include=['tag1', 'tag2'])
        with open('stdout.txt', 'w') as stdout:
            run('t1.txt', 't2.txt', report='r.html', log='NONE', stdout=stdout)

    Equivalent command line usage::

        robot --include tag1 --include tag2 path/to/tests.html
        robot --report r.html --log NONE t1.txt t2.txt > stdout.txt
    """
    return RobotFramework().execute(*datasources, **options)


if __name__ == '__main__':
    run_cli(sys.argv[1:])
