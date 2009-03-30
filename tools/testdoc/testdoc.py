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


"""Robot Framework Test Data Documentation Tool

Usage:  testdoc.py [options] data_sources

This tool generates a high level test documentation from a given test data.
Generated documentation includes the names, documentations and other metadata
of each test suite and test case, as well as the top-level keywords and their
arguments. Most of the options accepted by this tool have exactly same
semantics as same options have when executing test cases.

Options:
  -o --output path       Where to write the generated documentation. If the 
                         path is a directory, the documentation is
                         generated there using name '<suitename>-doc.html'.
  -T --title title       Set the title of the generated documentation. 
                         Underscores in the title are converted to spaces.
  -N --name name         Set the name of the top level test suite.
  -D --doc document      Set the document of the top level test suite.
  -M --metadata name:value *  Set metadata of the top level test suite. 
  -G --settag tag *      Set given tag(s) to all test cases. 
  -t --test name *       Include test cases by name. 
  -s --suite name *      Include test suites by name. 
  -i --include tag *     Include test cases by tags.
  -e --exclude tag *     Exclude test cases by tags.
  -h --help              Print this help.

Examples:
  $ testdoc.py mytestcases.html
  $ testdoc.py --name smoke_test_plan --include smoke path/to/my_tests/
  
Note that this tool requires Robot Framework 2.0.3 or newer to be installed.
"""

import sys
import os
import time

from robot.common import BaseKeyword, BaseTestSuite
from robot.running import TestSuite, Keyword
from robot.conf import RobotSettings
from robot.output import LOGGER
from robot.serializing.serializer import LogSuiteSerializer
from robot.serializing import templates
from robot.serializing.templating import Namespace, Template
from robot import utils
from robot.errors import DataError, Information

LOGGER.register_console_logger()


def generate_test_doc(args):
    opts, datasources = process_arguments(args)
    suite = TestSuite(datasources, RobotSettings(opts))
    outpath = get_outpath(opts['output'], suite.name)
    serialize_test_doc(suite, outpath, opts['title'])
    exit(msg=outpath)
    
def serialize_test_doc(suite, outpath, title):
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

def process_arguments(args_list):
    argparser = utils.ArgumentParser(__doc__)
    try:
        opts, args = argparser.parse_args(args_list, help='help', check_args=True)
    except Information, msg:
        exit(msg=str(msg))
    except DataError, err:
        exit(error=str(err))
    return opts, args
    
def exit(msg=None, error=None):
    if msg:
        sys.stdout.write(msg + '\n')
        sys.exit(0)
    sys.stderr.write(error + '\n\nTry --help for usage information.\n')
    sys.exit(1)

def get_outpath(path, suite_name):
    if not path:
        path = '.'
    if os.path.isdir(path):
        path = os.path.join(path, '%s-doc.html' % suite_name.replace(' ', '_'))
    return os.path.abspath(path)


class MySerializer(LogSuiteSerializer):

    def __init__(self, output, suite):
        self._writer = utils.HtmlWriter(output)
        self._idgen = utils.IdGenerator()
        self._suite_level = 0

    def start_suite(self, suite):
        suite._init_suite(NonResolvingVariableScopes())
        LogSuiteSerializer.start_suite(self, suite)

    def start_test(self, test):
        test._init_test(NonResolvingVariableScopes())
        LogSuiteSerializer.start_test(self, test)

    def start_keyword(self, kw):
        if isinstance(kw, Keyword):  # Doesn't match For or Parallel
            kw.name = kw._get_name(kw.name, NonResolvingVariableScopes())
        LogSuiteSerializer.start_keyword(self, kw)

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
        if test.timeout.secs < 0:
            tout = ''
        else:
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


class NonResolvingVariableScopes:

    def replace_from_meta(self, name, item, errors):
        return item

    def replace_string(self, item):
        return item


if __name__ == '__main__':
    generate_test_doc(sys.argv[1:])
