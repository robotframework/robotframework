#!/usr/bin/env python

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

USAGE = """robot.testdoc -- Robot Framework test data documentation tool

Version:  <VERSION>

Usage:  python -m robot.testdoc [options] data_sources output_file

This tool generates a high level test documentation from a given test data.
Generated documentation includes the names, documentations and other metadata
of each test suite and test case, as well as the top-level keywords and their
arguments. Most of the options accepted by this tool have exactly same
semantics as same options have when executing test cases.

Options
=======

  -T --title title       Set the title of the generated documentation.
                         Underscores in the title are converted to spaces.
  -N --name name         Set the name of the top level test suite.
  -D --doc document      Set the documentation of the top level test suite.
  -M --metadata name:value *  Set metadata of the top level test suite.
  -G --settag tag *      Set given tag(s) to all test cases.
  -t --test name *       Include test cases by name.
  -s --suite name *      Include test suites by name.
  -i --include tag *     Include test cases by tags.
  -e --exclude tag *     Exclude test cases by tags.
  -h -? --help           Print this help.

Examples
========

  python .m robot.testdoc mytestcases.html testdoc.html
  python .m robot.testdoc --name smoke_test_plan -i smoke path/to/my_tests/ doc.html
"""

import sys
import os
import codecs

if 'robot' not in sys.modules:
    import pythonpathsetter   # running testdoc.py as script

from robot import utils
from robot.running import TestSuite, Keyword
from robot.conf import RobotSettings
from robot.parsing import populators
from robot.reporting.htmlfilewriter import HtmlFileWriter, ModelWriter
from robot.reporting.jsonwriter import JsonWriter


class TestDoc(utils.Application):

    def __init__(self):
        utils.Application.__init__(self, USAGE, arg_limits=(2,))

    def main(self, args, title=None, **options):
        datasources = args[0:-1]
        outfile = os.path.abspath(args[-1])
        suite = TestSuiteFactory(datasources, **options)
        self._write_test_doc(suite, outfile, title)
        self.console(outfile)

    def _write_test_doc(self, suite, outfile, title):
        output = codecs.open(outfile, 'w', 'UTF-8')
        model_writer = TestdocModelWriter(output, suite, title)
        HtmlFileWriter(output, model_writer).write('testdoc.html')
        output.close()


def TestSuiteFactory(datasources, **options):
    if isinstance(datasources, basestring):
        datasources = [datasources]
    populators.PROCESS_CURDIR = False
    try:
        return TestSuite(datasources, RobotSettings(options))
    finally:
        populators.PROCESS_CURDIR = True


class TestdocModelWriter(ModelWriter):

    def __init__(self, output, suite, title=None):
        self._output = output
        self._suite = suite
        self._title = title.replace('_', ' ') if title else ''

    def write(self, line):
        self._output.write('<script type="text/javascript">' + os.linesep)
        self.write_data()
        self._output.write('</script>' + os.linesep)

    def write_data(self):
        json = JsonConverter().convert(self._suite)
        json['title'] = self._title
        JsonWriter(self._output).write_json('testdoc = ', json)


class JsonConverter(object):

    def convert(self, suite):
        return self._convert_suite(suite)

    def _convert_suite(self, suite):
        return {
            'source': suite.source,
            'id': suite.id,
            'name': suite.name,
            'fullName': suite.longname,
            'doc': suite.doc,
            'metadata': dict(suite.metadata),
            'numberOfTests': suite.get_test_count(),
            'suites': self._convert_suites(suite),
            'tests': self._convert_tests(suite),
            'keywords': list(self._convert_keywords(suite))
        }

    def _convert_suites(self, suite):
        return [self._convert_suite(s) for s in suite.suites]

    def _convert_tests(self, suite):
        return [self._convert_test(t) for t in suite.tests]

    def _convert_test(self, test):
        return {
            'name': test.name,
            'fullName': test.longname,
            'id': test.id,
            'doc': test.doc,
            'tags': utils.normalize_tags(test.tags),
            'timeout': self._get_timeout(test.timeout),
            'keywords': list(self._convert_keywords(test))
        }

    def _convert_keywords(self, item):
        if item.setup.name:
            yield self._convert_keyword(item.setup, type='SETUP')
        for kw in getattr(item, 'keywords', []):
            yield self._convert_keyword(kw)
        if item.teardown.name:
            yield self._convert_keyword(item.teardown, type='TEARDOWN')

    def _convert_keyword(self, kw, type=None):
        return {
            'name': kw._get_name(kw.name) if isinstance(kw, Keyword) else kw.name,
            'arguments': ', '.join(kw.args),
            'type': type or {'kw': 'KEYWORD', 'for': 'FOR'}[kw.type]
        }

    def _get_timeout(self, timeout):
        try:
            tout = utils.secs_to_timestr(utils.timestr_to_secs(timeout.string))
        except ValueError:
            tout = timeout.string
        if timeout.message:
            tout += ' :: ' + timeout.message
        return tout


def testdoc_cli(args):
    """Executes testdoc similarly as from the command line.

    :param args: command line arguments as a list of strings.

    Example:
       testdoc_cli(['--title', 'Test Plan', 'mytests', 'plan.html'])
    """
    TestDoc().execute_cli(args)


if __name__ == '__main__':
    testdoc_cli(sys.argv[1:])
