#!/usr/bin/env python

#  Copyright 2008 Nokia Siemens Networks Oyj
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


"""Robot Framework Test Plan Generation Tool

Usage:  testdoc.py [options] data_sources

This script generates a high level documentation of given suite. This 
documentation includes the names and documentation for each suite and test case
and also the top level keywords and their documentation for each test.

Options:
 -o --output path        Where to write the generated documentation. If the 
                         path is a directory, the documentation is
                         generated there using name '<suitename>_doc.html'.
 -h --help               Print this help. 
"""

import sys
import os
import time

from robot.common import BaseKeyword, BaseTestSuite
from robot.running import TestSuite
from robot.conf import RobotSettings
from robot.output import SystemLogger
from robot.serializing.serializer import LogSuiteSerializer
from robot.serializing import templates
from robot.serializing.templating import Namespace, Template
from robot import utils
from robot.errors import DataError


class _FakeVariableScopes:
    
    def replace_from_meta(self, name, item, errors):
        return item


class MySerializer(LogSuiteSerializer):
    
    def __init__(self, output, suite):
        self._writer = utils.HtmlWriter(output)
        self._idgen = utils.IdGenerator()
        self._suite_level = 0
    
    def start_suite(self, suite):
        suite._init_suite(_FakeVariableScopes())
        LogSuiteSerializer.start_suite(self, suite)
    
    def start_test(self, test):
        test._init_test(_FakeVariableScopes())
        LogSuiteSerializer.start_test(self, test)
    
    def _is_element_open(self, item):
        return isinstance(item, BaseTestSuite)
    
    def _write_times(self, item):
        pass
        
    def _write_suite_metadata(self, suite):
        self._start_suite_or_test_metadata(suite)
        for name, value in suite.get_metadata(html=True):
            self._write_metadata_row(name, value, escape=False, write_empty=True)
        self._writer.end_element('table')
    
    def _write_test_metadata(self, test):
        self._start_suite_or_test_metadata(test)
        tout = ''
        if test.timeout.secs > 0:
            tout = utils.secs_to_timestr(test.timeout.secs)
            if test.timeout.message:
                tout += ' | ' + test.timeout.message
        self._write_metadata_row('Timeout', tout)
        self._write_metadata_row('Tags', ', '.join(test.tags))
        self._writer.end_element('table')
    
    def _write_folding_button(self, item):
        if not isinstance(item, BaseKeyword):
            LogSuiteSerializer._write_folding_button(self, item)

    def _write_expand_all(self, item):
        if isinstance(item, BaseTestSuite):
            LogSuiteSerializer._write_expand_all(self, item)
        

def generate_test_plan(args):
    outpath, datasources = _process_arguments(args)
    suite = TestSuite(datasources, RobotSettings(), SystemLogger())
    _serialize_test_plan(suite, outpath)
    
def _serialize_test_plan(suite, outpath):
    outfile = open(_get_outpath(outpath, suite.name), 'w')
    serializer = MySerializer(outfile, suite)
    ttuple = time.localtime()
    str_time = '%s %s' % (utils.format_time(ttuple, daytimesep='&nbsp;'),
                          utils.get_diff_to_gmt())
    int_time = long(time.mktime(ttuple))
    namespace = Namespace(gentime_str=str_time, gentime_int=int_time, 
                          version=utils.get_full_version('RoboPlan'), 
                          suite=suite, title='Test plan for %s' % suite.name)
    tmpl = Template(template=templates.LOG)
    tmpl.generate(namespace, outfile)
    suite.serialize(serializer)
    outfile.write('</body>\n</html>\n')
    outfile.close()

def _process_arguments(args_list):
    argparser = utils.ArgumentParser(__doc__)
    try:
        opts, args = argparser.parse_args(args_list, check_args=True)
    except DataError:
        exit(error=__doc__)
    if opts['help']:
        exit(msg=__doc__)
    output = opts['output'] is not None and opts['output'] or '.'
    return os.path.abspath(output), args

def exit(msg=None, error=None):
    if msg:
        sys.stdout.write(msg + '\n')
    if error:
        sys.stderr.write(error + '\n')
        sys.exit(1)
    sys.exit(0)

def _get_outpath(path, suite_name):
    if os.path.isdir(path):
        path = os.path.join(path, '%s_doc.html' % suite_name)
    return path


if __name__ == '__main__':
    generate_test_plan(sys.argv[1:])
