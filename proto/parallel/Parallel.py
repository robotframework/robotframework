import subprocess
from time import time
from random import randint
import os
import re
import sys
from robot.libraries import BuiltIn
from robot.utils import html_escape

class Parallel(object):

    def __init__(self, runner_script, *arguments):
        self._script = runner_script
        self._arguments = list(arguments)
        self._processes = []
        self._suite = None

    def add_parallel_arguments(self, *args):
        self._argumens += list(args)

    def set_suite_for_parallel_tests(self, suite):
        self._suite = suite

    def run_parallel_robot(self, test_name, *args):
        if self._suite is None:
            self._suite = BuiltIn.BuiltIn().replace_variables('${SUITE_SOURCE}')
        arguments = self._arguments+list(args)+[self._suite]
        process = _ParaRobo(test_name, *arguments)
        process.run(self._script)
        self._processes.append(process)
        return process

    def run_parallel_tests(self, *tests):
        for test in tests:
            self.run_parallel_robot(test)
        self.wait_for_all_parallel_tests_to_be_ready()

    def wait_for_parallel_tests_to_be_ready(self, *processes):
        failed = []
        for process in processes:
          rval = process.wait()
          process.report()
          if rval != 0:
            failed.append(process.test)
        if failed:
            raise AssertionError("Following tests failed:\n%s" % "\n".join(failed))

    def wait_for_all_parallel_tests_to_be_ready(self):
        self.wait_for_parallel_tests_to_be_ready(*self._processes)
        self._processes = []


class _ParaRobo(object):
    def __init__(self, test, *args):
        self._built_in = BuiltIn.BuiltIn()
        id = "%s%s" % (time(), randint(0, 1000000))
        self._output = 'output_%s.xml' % id
        self._log = 'log_%s.html' % id
        self.test = test
        self._args = list(args)
        self._output_dir = self._built_in.replace_variables("${OUTPUT DIR}")
        self._monitor_out = os.path.join(self._output_dir, 'monitor_%s.txt' % id)
        self._suite_name = self._built_in.replace_variables("${SUITE_NAME}")

    def run(self, script):
        with open(self._monitor_out, 'w') as monitor_file:
            cmd = [script, 
                  '--outputdir', self._output_dir,
                   '--output', self._output,
                  '--report', 'None',
                   '--log', self._log, 
                  '--monitorcolors', 'off',
                  '--test', self.test.replace(' ', '').replace('/', '?')]+\
                  self._args
            print "Starting test execution: %s" % " ".join(cmd)
            self._process = subprocess.Popen(cmd,
                                              shell=os.sep == '\\',
                                              stdout=monitor_file, 
                                              stderr=monitor_file)

    def wait(self):
        return self._process.wait()

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
