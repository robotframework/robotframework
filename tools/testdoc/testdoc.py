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
 -o --output path       Where to write the generated documentation. If the 
                        path is a directory, the documentation is
                        generated there using name '<suitename>_doc.html'.
 -T --title title       Set the title of the generated documentation. 
                        Underscores in the title are converted to spaces.
 -N --name name         Set the name of the top level test suite. Name is
                        automatically capitalized and underscores converted
                        to spaces. Default name is created from the name of
                        the executed data source.
 -D --doc document      Set the document of the top level test suite.
                        Underscores in the document are turned into spaces
                        and it may also contain simple HTML formatting (e.g.
                        *bold* and http://url/).
 -M --metadata name:value *  Set metadata of the top level test suite. Name is
                        automatically capitalized and underscores converted
                        to spaces. Value can contain same HTML formatting as
                        --doc. Example: '--metadata version:1.2'
 -G --settag tag *      Sets given tag(s) to all executed test cases. 
 -t --test name *       Select test cases to run by name. Name is case and
                        space insensitive and it can also be a simple pattern
                        where '*' matches anything and '?' matches any char.
                        If using '*' and '?' in the console is problematic
                        see --escape and --argumentfile.
 -s --suite name *      Select test suites to run by name. When this option
                        is used with --test, --include or --exclude, only
                        test cases in matching suites and also matching other
                        filtering criteria are selected. Name can be a simple
                        pattern similarly as with --test and it can contain
                        parent name separated with a dot. For example 
                        '-s X.Y' selects suite 'Y' only if its parent is 'X'.
 -i --include tag *     Select test cases to run by tag. Similarly as name in
                        -\\-test, tag is case and space insensitive and it 
                        can also be a simple pattern. To include only tests
                        which have more than one tag use '&' or 'AND' between
                        tag names. For example '--include tag1&tag2' includes
                        only those tests that have both 'tag1' and 'tag2'.
 -e --exclude tag *     Select test cases not to run by tag. These tests are
                        not run even if they are included with --include. Tag
                        names are handled similarly as in --include and
                        excluding only tests containing multiple tags works
                        the same way using '&' or 'AND'.
 -h --help              Print this help. 
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
        self._write_metadata_row('Number of Tests', suite.get_test_count())
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
        

def generate_test_doc(args):
    opts, datasources = _process_arguments(args)
    suite = TestSuite(datasources, RobotSettings(opts), SystemLogger())
    outpath = _get_outpath(opts['output'], suite.name)
    _serialize_test_doc(suite, outpath, opts['title'])
    print outpath
    
def _serialize_test_doc(suite, outpath, title):
    outfile = open(outpath, 'w')
    serializer = MySerializer(outfile, suite)
    ttuple = time.localtime()
    str_time = '%s %s' % (utils.format_time(ttuple, daytimesep='&nbsp;'),
                          utils.get_diff_to_gmt())
    int_time = long(time.mktime(ttuple))
    if title:
        title = title.replace('_', ' ')
    else:
        title = 'Documentation for %s' % suite.name
    namespace = Namespace(gentime_str=str_time, gentime_int=int_time, 
                          version=utils.get_full_version('testdoc.py'), 
                          suite=suite, title=title)
    Template(template=templates.LOG).generate(namespace, outfile)
    suite.serialize(serializer)
    outfile.write('</body>\n</html>\n')
    outfile.close()

def _process_arguments(args_list):
    argparser = utils.ArgumentParser(__doc__)
    try:
        opts, args = argparser.parse_args(args_list)
    except DataError, err:
        exit(error=str(err))
    if opts['help'] or not args:
        exit(msg=__doc__)
    return opts, args
    
def exit(msg=None, error=None):
    if msg:
        sys.stdout.write(msg + '\n')
    if error:
        sys.stderr.write(error + '\n\nTry --help for usage information.\n')
        sys.exit(1)
    sys.exit(0)

def _get_outpath(path, suite_name):
    if not path:
        path = '.'
    if os.path.isdir(path):
        path = os.path.join(path, '%s_doc.html' % suite_name.replace(' ', '_'))
    return os.path.abspath(path)


if __name__ == '__main__':
    generate_test_doc(sys.argv[1:])
