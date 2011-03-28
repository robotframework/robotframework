#  Copyright 2008-2011 Nokia Siemens Networks Oyj
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


from __future__ import with_statement
import subprocess
import time
from random import randint
import os
import re
import sys
from robot.libraries import BuiltIn
from robot.utils import html_escape, ArgumentParser
from robot.version import get_version


class Parallel(object):
    """
    Library for executing tests in parallel from inside of a robot test case.
    Tests are executed in subprocesses. 
    
    You can add arguments to all parallel test runs from `library importing`,
    for a set of parallel tests with `Add Arguments For Parallel Tests` and
    for an individual parallel test by passing the arguments in `Start Parallel Test`.
     
    The following command line arguments (also from argument files) are automatically 
    passed to parallel tests:
    --loglevel, --runmode, --pythonpath, --variable, --variablefile
    
    Example:
    | *Settings* |
    | Library | Parallel | pybot |
    
    
    | *Test Cases* |
    | Runner |
    |        | Run Parallel Tests | Hello | World |  
    | Hello |
    |       | [Tags] | parallel |
    |       | Log    | Hello ${WORLD} |
    | World |
    |       | [Tags] | parallel |
    |       | Log    | ${HELLO} World |
    
    `pybot --exclude parallel --variable HELLO:Hello --variable WORLD:World .`
    """

    def __init__(self, runner_script, *arguments):
        """
        `runner_script` is pybot or jybot or a custom script.

        `arguments` are default arguments given to every test execution.

        Example:
        | Library | Parallel | pybot | --variable | variable:value | --loglevel | DEBUG |
        """
        self._script = runner_script
        self._arguments = self._get_arguments(arguments)
        self._processes = []
        self._data_source = None

    def _get_arguments(self, additional_arguments):
        options,_ = ArgumentParser(COMMAND_LINE_ARGUMENTS).parse_args(sys.argv[1:], argfile='argumentfile', unescape='escape')
        args = []
        for arg in ['loglevel', 'runmode', 'pythonpath', 'variable', 'variablefile']:
           args += self._get_type_arguments(options, arg)
        args += list(additional_arguments)
        return args

    def _get_type_arguments(self, options, key):
        value = options[key]
        args = []
        if value is not None:
            if not isinstance(value, list):
                value = [value]
            for var in value:
                args += ['--%s' % key, var]
        return args  

    def add_arguments_for_parallel_tests(self, *arguments):
        """Adds `arguments` to be used when parallel test is started.

        `arguments` is a list of arguments to pass to parallel executions.

        In the following example variable my_var is used in both of the tests 
        started with the keyword `Run Parallel Tests`:
        | Add Arguments For Parallel Tests | --variable | my_var:value |
        | Run Parallel Tests | Test | Another Test |
        """
        self._arguments += list(arguments)

    def set_data_source_for_parallel_tests(self, data_source):
        """Sets data source which is used when parallel tests are started.

        `data_source` is path to file which contains the test/tests which are
        started/executed with keywords `Start Parallel Test` or `Run Parallel
        Tests`.

        If tests to be executed are in the same suite and Robot Framework 2.5
        or later is used, there is no need to use this keyword as `data_source`
        can be automatically resolved.

        Examples:
        | Set Data Source For Parallel Tests | ${CURDIR}${/}my_parallel_suite.txt |
        | Start Parallel Test | My Parallel Test |
        | Wait All Parallel Tests |
        """   
        self._data_source = data_source

    def start_parallel_test(self, test_name, *arguments):
        """Starts executing test with given `test_name` and `arguments`.

        `arguments` is a list of Robot Framework command line arguments passed to 
        the started test execution. It should not include data source. Use
        `Set Data Source For Parallel Tests` keyword for setting the data
        source. Additional arguments can also be set in library import and with
        `Add Arguments For Parallel Tests` keyword.

        Returns a process object that represents this execution.
        
        Example:
        | Set Data Source For Parallel Tests | MySuite.txt |
        | Start Parallel Test | Test From My Suite |
        | Set Data Source For Parallel Tests | MyFriendsSuite.txt |
        | Start Parallel Test | Test From My Friends Suite |
        | Wait All Parallel Tests |
        """
        if self._data_source is None:
            self._data_source = BuiltIn.BuiltIn().replace_variables('${SUITE_SOURCE}')
        process = _ParaRobo(test_name, self._data_source, 
                            self._arguments+list(arguments))
        process.run(self._script)
        self._processes.append(process)
        return process

    def run_parallel_tests(self, *test_names):
        """Executes all given tests parallel and wait those to be ready.

        Arguments can be set with keyword `Add Arguments For Parallel Tests`
        and data source with keyword `Set Data Source For Parallel Tests`. 
        
        Example:
        | Add Arguments For Parallel Tests | --variable | SOME_VARIABLE:someValue |
        | Set Data Source For Parallel Tests | MySuite.txt |
        | Run Parallel Tests | My Parallel Test | My Another Parallel Test |
        
        When the parallel tests are from different data sources see the example in `Start Parallel Test`.
        """
        processes = []
        for name in test_names:
            processes += [self.start_parallel_test(name)]
        self.wait_parallel_tests(*processes)

    def wait_parallel_tests(self, *processes):
        """Waits given `processes` to be ready and fails if any of the tests failed.

        `Processes` are list of test execution processes returned from keyword 
        `Start Parallel Test`.
        
        Example
        | ${test 1}= | Start Parallel Test | First Test |
        | ${test 2}= | Start Parallel Test | Test That Runs All The Time |
        | Wait Parallel Tests | ${test 1} |
        | ${test 3}= | Start Parallel Test | Third Test |
        | Wait Parallel Tests | ${test 2} | ${test 3} |
        """
        failed = []
        for process in processes:
            if process.wait() != 0:
                failed += [process.test]
            process.report()
            self._processes.remove(process)
        if failed:
            raise AssertionError("Following tests failed:\n%s" % "\n".join(failed))

    def wait_all_parallel_tests(self):
        """Wait all started test executions to be ready and fails if any of those failed."""
        self.wait_parallel_tests(*self._processes)

    def stop_all_parallel_tests(self):
        """Forcefully stops all the test executions.
        
        NOTE: Requires Python 2.6 or later.
        """
        for process in self._processes:
            process.stop_test_execution()
        self._processes = []


class _ParaRobo(object):

    def __init__(self, test, data_source, arguments):
        self.test = test
        self._data_source = data_source
        self._args = arguments
        self._built_in = BuiltIn.BuiltIn()
        id = self._create_id()
        self._output = 'output_%s.xml' % id
        self._log = 'log_%s.html' % id
        self._output_dir = self._built_in.replace_variables("${OUTPUT DIR}")
        self._monitor_out = os.path.join(self._output_dir, 'monitor_%s.txt' % id)

    @property
    def _suite_name(self):
        name = os.path.splitext(os.path.basename(self._data_source))[0]
        name = name.split('__', 1)[-1]  # Strip possible prefix
        name = name.replace('_', ' ').strip()
        if name.islower():
            name = name.title()
        return name

    def _create_id(self):
        return "%s_%s" % (randint(0, 10000), time.strftime('%Y%m%d_%H%m%S.')+\
                                    ('%03d' % (int(time.time()*1000) % 1000)))

    def run(self, script):
        self._monitor_file = open(self._monitor_out, 'w')
        cmd = [script,
              '--outputdir', self._output_dir,
               '--output', self._output,
              '--report', 'None',
               '--log', self._log,
              '--monitorcolors', 'off',
              '--test', self.test]+\
              self._args + [self._data_source]
        print "Starting test execution: %s" % " ".join(cmd)
        self._process = subprocess.Popen(cmd,
                                          shell=os.sep == '\\',
                                          stdout=self._monitor_file, 
                                          stderr=self._monitor_file,
                                          env=self._get_environment_variables())

    def _get_environment_variables(self):
        environment_variables = os.environ.copy()
        if environment_variables.has_key("ROBOT_SYSLOG_FILE"):
            del(environment_variables["ROBOT_SYSLOG_FILE"])
        return environment_variables

    def wait(self):
        rc = self._process.wait()
        self._monitor_file.close()
        return rc

    def report(self):
        with open(self._monitor_out, 'r') as monitor_file:
            monitor_output = monitor_file.read()
        try:
            os.remove(self._monitor_out)
        except:
            pass
        match = re.search('^Log:     (.*)$', monitor_output, re.MULTILINE)
        monitor_output = self._replace_stdout_log_message_levels(monitor_output)
        monitor_output = html_escape(monitor_output)
        if match:
            monitor_output = monitor_output.replace(match.group(1), '<a href="%s#test_%s.%s">%s</a>' % (self._log, self._suite_name, self.test, match.group(1)))
        monitor_output = self._add_colours(monitor_output)
        print "*HTML* %s" % monitor_output

    def _replace_stdout_log_message_levels(self, output):
        for level in ['TRACE', 'WARN', 'DEBUG', 'INFO', 'HTML']:
            output = output.replace('\n*%s*' % level, '\n *%s*' % level)
        return output

    def _add_colours(self, output):
        for name, colour in [("PASS", "pass"), ("FAIL", "fail"), ("ERROR", "fail")]:
            output = output.replace(' %s ' % name, ' <span class="%s">%s</span> ' % (colour, name))
        return output

    def stop_test_execution(self):
        try:
            self._process.terminate()
        except AttributeError:
            pass
        self.report()


if get_version() < "2.5":
    COMMAND_LINE_ARGUMENTS = """
 -N --name name           Set the name of the top level test suite. Name is
                          automatically capitalized and underscores converted
                          to spaces. Default name is created from the name of
                          the executed data source.
 -D --doc document        Set the document of the top level test suite.
                          Underscores in the document are turned into spaces
                          and it may also contain simple HTML formatting (e.g.
                          *bold* and http://url/).
 -M --metadata name:value *  Set metadata of the top level test suite. Name is
                          automatically capitalized and underscores converted
                          to spaces. Value can contain same HTML formatting as
                          --doc. Example: '--metadata version:1.2'
 -G --settag tag *        Sets given tag(s) to all executed test cases. 
 -t --test name *         Select test cases to run by name. Name is case and
                          space insensitive and it can also be a simple pattern
                          where '*' matches anything and '?' matches any char.
                          If using '*' and '?' in the console is problematic
                          see --escape and --argumentfile.
 -s --suite name *        Select test suites to run by name. When this option
                          is used with --test, --include or --exclude, only
                          test cases in matching suites and also matching other
                          filtering criteria are selected. Name can be a simple
                          pattern similarly as with --test and it can contain
                          parent name separated with a dot. For example 
                          '-s X.Y' selects suite 'Y' only if its parent is 'X'.
 -i --include tag *       Select test cases to run by tag. Similarly as name in
                          --test, tag is case and space insensitive. There are
                          three ways to include test based on tags:
                          1) One tag as a simple pattern. Tests having        print options
 a tag
                          matching the pattern are included. Example: 'it-*'
                          2) Two or more tags (or patterns) separated by '&' or
                          'AND'. Only tests having all these tags are included.
                          Examples: 'tag1&tag2', 'smokeANDowner-*ANDit-10'
                          3) Two or more tags (or patterns) separated by 'NOT'.
                          Tests having the first tag but not any of the latter
                          ones are included. Example: 'it-10NOTsmoke'
 -e --exclude tag *       Select test cases not to run by tag. These tests are
                          not run even if they are included with --include.
                          Tags are excluded using the rules explained in
                          --include.
 -c --critical tag *      Tests having given tag are considered critical. If no
                          critical tags are set, all tags are critical. Tags
                          can be given as a pattern like e.g. with --test.
 -n --noncritical tag *   Tests with given tag are not critical even if they
                          have a tag set with --critical. Tag can be a pattern.
    --runmode mode        Possible values are 'random:test', 'random:suite',  
                          'random:all' and 'exitonfailure'. Any other value is 
                          ignored. First three change the execution order of 
                          suites or tests (or both). 'exitonfailure' causes the
                          execution of tests to be stopped if a critical test
                          fails.  
 -v --variable name:value *  Set variables in the test data. Only scalar
                          variables are supported and name is given without 
                          '${}'. See --escape for how to use special characters
                          and --variablefile for a more powerful variable
                          setting mechanism that allows also list variables.
                          Examples:
                          --variable str:Hello  =>  ${str} = 'Hello'
                          -v str:Hi_World -E space:_  =>  ${str} = 'Hi World'
                          -v x: -v y:42  =>  ${x} = '', ${y} = '42'
 -V --variablefile path *  File to read variables from (e.g. 'path/vars.py').
                          Example file:
                          |  import random
                          |  __all__ = ['scalar','LIST__var','integer']
                          |  scalar = 'Hello world!'
                          |  LIST__var = ['Hello','list','world']
                          |  integer = random.randint(1,10)
                          =>
                          ${scalar} = 'Hello world!'
                          @{var} = ['Hello','list','world']
                          ${integer} = <random integer from 1 to 10>
 -d --outputdir dir       Where to create output files. The default is the
                          directory where tests are run from and the given path
                          is considered relative to that unless it is absolute.
 -o --output file         XML output file. Given path, similarly as paths given
                          to --log, --report, --summary and --debugfile, is 
                          relative to --outputdir unless given as an absolute 
                          path. Other output files are created from XML output 
                          file after the test execution and XML output can also
                          be further processed with Rebot tool (e.g. combined 
                          with other XML output files). Default: output.xml
 -l --log file            HTML log file. Can be disabled by giving a special
                          name 'NONE'. Default: log.html
                          Examples: '--log mylog.html', '-l NONE'
 -r --report file         HTML report file. Can be disabled with 'NONE'
                          similarly as --log. Default: report.html
 -S --summary file        HTML summary report. Not created unless this option
                          is specified. Example: '--summary summary.html'
 -b --debugfile file      Debug file written during execution. Not created 
                          unless this option is specified.
    --transform ignored   This option is ignored. Please use '--log' and
                          '--report' to control what outputs to generate.
 -T --timestampoutputs    When this option is used, timestamp in a format
                          'YYYYMMDD-hhmmss' is added to all generated output 
                          files between their basename and extension. For
                          example '-T -o output.xml -r report.html -l none'
                          creates files like 'output-20070503-154410.xml' and 
                          'report-20070503-154410.html'.
    --splitoutputs level  Split output and log files from specified suite
                          level. This makes generated files smaller and lower
                          level files available immediately when a respective
                          test suite is executed. Top level files have links to
                          lower level files for easy navigation. 
    --logtitle title      Title for the generated test log. The default title
                          is '<Name Of The Suite> Test Log'. Underscores in
                          the title are converted into spaces in all titles.
    --reporttitle title   Title for the generated test report. The default
                          title is '<Name Of The Suite> Test Report'.
    --summarytitle title  Title for the generated summary report. The default
                          title is '<Name Of The Suite> Summary Report'.
 -L --loglevel level      Threshold level for logging. Available levels: 
                          TRACE, DEBUG, INFO (default), WARN, NONE (no logging)
    --suitestatlevel level  How many levels to show in 'Statistics by Suite'
                          table in outputs. By default all suite levels are
                          shown. If zero (0) is given the whole table is 
                          removed. Example: '--SuiteStatLevel 3'
    --tagstatinclude tag *  Include only these tags in 'Statistics by Tag' and
                          and 'Test Details by Tag' tables in outputs. By
                          default all tags set in test cases are shown. Given
                          'tag' can also be a simple pattern (see e.g. --test).
    --tagstatexclude tag *  Exclude these tags from 'Statistics by Tag' and
                          'Test Details by Tag' tables in outputs. This option
                          can be used with --tagstatinclude similarly as
                          --exclude is used with --include.
    --tagstatcombine tags:name *  Create combined statistics based on tags.
                          These statistics are added into 'Statistics by Tag'
                          table and matching tests into 'Test Details by Tag'
                          table. Unless the optional 'name' is used, name of
                          the added combined tag is got from specified tags.
                          Tags are combined using the rules explained in
                          --include.
    --tagdoc pattern:doc *  Add documentation to tags matching given pattern.
                          Documentation is shown in 'Test Details by Tag' 
                          table and also as a tooltip in 'Statistics by Tag' 
                          table. Pattern can contain characters '*' (matches 
                          anything) and '?' (matches any char). In case of 
                          multiple matches, documentations are catenated with
                          spaces. Documentation can contain formatting as with
                          --doc option.
                          Examples:
                          --tagdoc mytag:My_documentation
                          --tagdoc regression:*See*_http://info.html
                          --tagdoc owner-*:Original_author
    --tagstatlink pattern:link:title *  Add external links into 'Statistics by 
                          Tag' table in outputs. Pattern can contain characters
                          '*' (matches anything) and '?' (matches any char).
                          Character(s) matching to wildcard expression(s) can 
                          be used in the resulting link with syntax %N, where N
                          is the index of the match (starting from 1). In title
                          underscores are automatically converted to spaces.
                          Examples:
                          --tagstatlink mytag:http://my.domain:Link
                          --tagstatlink bug-*:http://tracker/id=%1:Bug_Tracker
    --listener class *    A class for monitoring test execution. Gets 
                          notifications e.g. when a test case starts and ends.
                          Arguments to listener class can be given after class 
                          name, using colon as separator. For example:
                          --listener MyListenerClass:arg1:arg2
 -W --monitorwidth chars  Width of the monitor output. Default is 78.
 -C --monitorcolors on|off|force  Using ANSI colors in console. Normally colors
                          work in unixes but not in Windows. Default is 'on'.
                          'on'    - use colors in unixes but not in Windows
                          'off'   - never use colors
                          'force' - always use colors (also in Windows)
    --colormonitor param  Deprecated. Use --monitorcolors instead.
 -P --pythonpath path *   Additional locations (directories, ZIPs, JARs) where
                          to search test libraries from when they are imported.
                          Multiple paths can be given by separating them with a
                          colon (':') or using this option several times. Given
                          path can also be a glob pattern matching multiple
                          paths but then it normally must be escaped or quoted.
                          Examples:
                          --pythonpath libs/
                          --pythonpath /opt/testlibs:mylibs.zip:yourlibs
                          -E star:STAR -P lib/STAR.jar -P mylib.jar
 -E --escape what:with *  Escape characters which are problematic in console.
                          'what' is the name of the character to escape and
                          'with' is the string to escape it with. Note that
                          all given arguments, incl. data sources, are escaped
                          so escape characters ought to be selected carefully.
                          <--------------------ESCAPES------------------------>
                          Examples:
                          --escape space:_ --metadata X:Value_with_spaces
                          -E space:SP -E quot:Q -v var:QhelloSPworldQ
 -A --argumentfile path *  Text file to read more arguments from. File can have
                          both options and data sources one per line. Contents
                          do not need to be escaped but spaces in the beginning
                          and end of lines are removed. Empty lines and lines
                          starting with a hash character (#) are ignored.
                          Example file:
                          |  --include regression
                          |  --name Regression Tests
                          |  # This is a comment line
                          |  my_tests.html
                          |  path/to/test/directory/
 -h -? --help             Print usage instructions.
 --version                Print version information.
"""
else:
    from robot import runner as _runner
    COMMAND_LINE_ARGUMENTS = _runner.__doc__
