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
 -h -? --help            Print this help. 
"""

import sys
import os
import time

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
        self._suite = suite
    
    def start_suite(self, suite):
        suite._init_suite(_FakeVariableScopes())
        LogSuiteSerializer.start_suite(self, suite)
    
    def start_test(self, test):
        test._init_test(_FakeVariableScopes())
        LogSuiteSerializer.start_test(self, test)
        for kw in test.keywords:
            LogSuiteSerializer.start_keyword(self, kw)
            LogSuiteSerializer.end_keyword(self, kw)
    
    def _is_element_open(self, item):
        return False
    
    def _write_times(self, item):
        pass
    
    def _write_suite_or_test_name(self, item, type_):
        self._writer.start_elements(['tr', 'td'])
        self._writer.whole_element('a', 'Expand All', {'class': 'expand', 
                                   'href': "javascript:expand_all_children('%s')" % item.id})
        self._write_folding_button(item)
        label = type_ == 'suite' and 'TEST&nbsp;SUITE: ' or 'TEST&nbsp;CASE: '
        self._writer.whole_element('span', label, escape=False)
        self._writer.whole_element('a', item.name, 
                                   {'name': '%s_%s' % (type_, item.mediumname),
                                    'class': 'name', 'title': item.longname})
        self._writer.end_elements(['td', 'tr'])
        
    def _write_suite_metadata(self, suite):
        self._start_suite_or_test_metadata(suite)
        for name, value in suite.get_metadata(html=True):
            self._write_metadata_row(name, value, escape=False, write_empty=True)
        for title, values in [ ('Critical Tags', suite.critical.tags),
                               ('Non-Critical Tags', suite.critical.nons),
                               ('Included Suites', suite.filtered.suites), 
                               ('Included Tests', suite.filtered.tests),
                               ('Included Tags', suite.filtered.incls), 
                               ('Excluded Tags', suite.filtered.excls) ]:
            self._write_metadata_row(title, ', '.join(values), escape=False)
        self._writer.end_element('table')
    
    def _write_test_metadata(self, test):
        self._start_suite_or_test_metadata(test)
        self._write_metadata_row('Tags', ', '.join(test.tags))
        crit = test.critical == 'yes' and 'critical' or 'non-critical'
        self._writer.end_element('table')
        
    def _write_keyword_name(self, kw):
        self._writer.start_element('tr', {'id': kw.id})
        self._writer.start_element('td')
        self._write_folding_button(kw)
        kw_type = kw.type in ['setup','teardown'] and kw.type.upper() or 'KEYWORD'
        self._writer.whole_element('span' ) # TODO: some style here
        self._writer.whole_element('span', kw.name+' ', {'class': 'name'})
        self._writer.whole_element('span', u', '.join(kw.args), {'class': 'arg'})
        self._writer.end_elements(['td', 'tr'])
        
        
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

def _get_outpath(path, suite_name):
    if os.path.isdir(path):
        path = os.path.join(path, '%s_doc.html' % suite_name)
    return path


if __name__ == '__main__':
    generate_test_plan(sys.argv[1:])
