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
from robot.utils import html_escape


class Parallel(object):
    """
    Library for executing tests in parallel from inside of a robot test case.
    """

    def __init__(self, runner_script, *arguments):
        """
        `runner_script` is pybot or jybot or a custom script.

        `*arguments` is default arguments to give to every test execution.
        """
        self._script = runner_script
        self._arguments = list(arguments)
        self._processes = []
        self._data_source = None

    def add_arguments_for_parallel_tests(self, *args):
        """
        Add arguments to run script.

        `*args` is list of arguments to pass to parallel executions.
        """
        self._arguments += list(args)

    def set_data_source_for_parallel_tests(self, data_source):
        """
        Set the path to the data source that contains the tests to be
        executed in parallel.

        `data_source` is file path.
        """   
        self._data_source = data_source

    def start_parallel_test(self, test_name, *args):
        """
        `test_name` is name of the test to be executed.

        `*args` is list of arguments to pass to this execution.
        
        Returns a process object that represents this execution.
        
        NOTE: default arguments set during library import and by calling
        `Add Parallel Arguments` will also be given to this test execution.

        NOTE: Set suite by using 'Set Data Source For Parallel Tests' or library will use 
        ${SUITE_SOURCE}
        """
        if self._data_source is None:
            self._data_source = BuiltIn.BuiltIn().replace_variables('${SUITE_SOURCE}')
        process = _ParaRobo(test_name, self._data_source, self._arguments+list(args))
        process.run(self._script)
        self._processes.append(process)
        return process

    def run_parallel_tests(self, *tests):
        """
        `*tests` is list of tests to be executed in parallel.
        """
        processes = []
        for test in tests:
            processes += [self.start_parallel_test(test)]
        self.wait_parallel_tests(*processes)

    def wait_parallel_tests(self, *processes):
        """
        `*processes` is list of all the processes to wait.
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
        self.wait_parallel_tests(*self._processes)

    def stop_all_parallel_tests(self):
        """
        Forcefully stops all the executions.
        
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
        monitor_output = html_escape(monitor_output)
        if match:
            monitor_output = monitor_output.replace(match.group(1), '<a href="%s#test_%s.%s">%s</a>' % (self._log, self._suite_name, self.test, match.group(1)))
        monitor_output = self._add_colours(monitor_output)
        print "*HTML* %s" % monitor_output

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
