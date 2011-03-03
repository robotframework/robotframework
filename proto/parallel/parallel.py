import subprocess
from time import time
from random import randint
import os
import sys
from robot.libraries import BuiltIn

class parallel(object):

    def run_parallel_test(self, test_name):
        process = _ParaRobo(test_name)
        process.run()
        return process

    def wait_for(self, *processes):
        fail = False
        for process in processes:
          rval = process.wait()
          process.report()
          if rval != 0:
            fail = True
        if fail:
            raise Exception('Subprocess failure')

class _ParaRobo(object):
    def __init__(self, test):
        self._built_in = BuiltIn.BuiltIn()
        id = "%s%s" % (time(), randint(0, 1000000))
        self._output = 'output_%s.xml' % id
        self._log = 'log_%s.html' % id
        self._monitor_out = 'monitor_%s.txt' % id
        self._test = test
        self._suite = os.path.split(self._built_in.replace_variables("${SUITE_SOURCE}"))[1]
        self._suite_name = self._built_in.replace_variables("${SUITE_NAME}")

    def run(self):
        monitor_file = open(self._monitor_out, 'w')
        self._process = subprocess.Popen(['pybot',
                                          '-l', self._log,
                                          '-o', self._output,
                                          '--monitorcolors', 'off',
                                          '--variable', 'PARALLEL:True',
                                          '--test', self._test,
                                          '--report', 'None',
                                          self._suite],
                                          shell=os.sep == '\\',
                                          stdout=monitor_file, 
                                          stderr=monitor_file)
        monitor_file.close()

    def wait(self):
        self._rcode = self._process.wait()
        return self._rcode

    def report(self):
        if self._rcode == 0:
            LEVEL = '*INFO*'
            STATUS = 'PASS'
        else:
            LEVEL = '*ERROR*'
            STATUS = 'FAIL'
        print '%s[%s] "%s.%s" output (%s)' % (LEVEL, STATUS, self._suite, self._test, self._output)
        print '*HTML* <a href="%s#test_%s.%s">Process log</a>' % (self._log, os.path.splitext(self._suite)[0].capitalize(), self._test)
