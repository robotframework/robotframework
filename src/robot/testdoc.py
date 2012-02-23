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

USAGE = """Robot Framework Test Data Documentation Tool

Usage:  testdoc.py [options] data_sources

This tool generates a high level test documentation from a given test data.
Generated documentation includes the names, documentations and other metadata
of each test suite and test case, as well as the top-level keywords and their
arguments. Most of the options accepted by this tool have exactly same
semantics as same options have when executing test cases.

Options:
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
  $ testdoc.py mytestcases.html testdoc.html
  $ testdoc.py --name smoke_test_plan --include smoke path/to/my_tests/ doc.html
"""
import sys
import os
import codecs

if 'robot' not in sys.modules:
    import pythonpathsetter   # running testdoc.py as script

from robot import utils, version
from robot.running import TestSuite, Keyword
from robot.conf import RobotSettings
from robot.parsing import populators
from robot.reporting.htmlfilewriter import HtmlFileWriter, ModelWriter
from robot.reporting.jsonwriter import JsonWriter

populators.PROCESS_CURDIR = False

class TestDoc(utils.Application):

    def __init__(self):
        utils.Application.__init__(self, USAGE, arg_limits=(2,), auto_version=False)

    def main(self, args, title=None, **opts):
        datasources = args[0:-1]
        outfile = args[-1]
        suite = TestSuite(datasources, RobotSettings(opts))
        self._write_test_doc(suite, outfile, title)

    def _write_test_doc(self, suite, outfile, title):
        output = codecs.open(outfile, 'w', 'UTF-8')
        model_writer = TestdocModelWriter(output, suite, title)
        HtmlFileWriter(output, model_writer).write('testdoc.html')
        output.close()


class TestdocModelWriter(ModelWriter):

    def __init__(self, output, suite, title):
        self._output = output
        self._suite = suite
        self._title = title.replace('_', ' ') if title else ''

    def write(self, line):
        self._output.write('<script type="text/javascript">' + os.linesep)
        self._write_data()
        self._output.write('</script>' + os.linesep)

    def _write_data(self):
        json = JsonConverter().convert(self._suite)
        json['title'] = self._title
        JsonWriter(self._output).write_json('testdoc = ', json)


class JsonConverter(object):

    def convert(self, suite):
        return self._convert_suite(suite, 's-0')

    def _convert_suite(self, suite, suite_id, index=None):
        suite_id = self._get_id(suite_id, 's', index) if index is not None else suite_id
        return {
            'name': suite.name,
            'fullName': suite.longname,
            'source': suite.source,
            'doc': suite.doc,
            'id': suite_id,
            'metadata': dict(suite.metadata),
            'numberOfTests': suite.get_test_count(),
            'suites': self._convert_suites(suite, suite_id),
            'tests': self._convert_tests(suite, suite_id),
            'keywords': self._get_suite_keywords(suite, suite_id)
        }

    def _get_suite_keywords(self, suite, suite_id):
        kws = []
        if suite.setup.name:
            kws.append(self._convert_keyword(suite.setup, suite_id, 0, 'SETUP'))
        if suite.teardown.name:
            kws.append(self._convert_keyword(suite.teardown, suite_id, 1, 'TEARDOWN'))
        return kws

    def _convert_suites(self, suite, suite_id):
        return [self._convert_suite(suite, suite_id, index)
                for index, suite in enumerate(suite.suites)]

    def _convert_tests(self, suite, suite_id):
        return [self._convert_test(test, suite_id, index)
                for index, test in enumerate(suite.tests)]

    def _convert_test(self, test, suite_id, index):
        test_id = self._get_id(suite_id, 't', index)
        return {
            'name': test.name,
            'fullName': test.longname,
            'id': test_id,
            'doc': test.doc,
            'tags': test.tags,
            'timeout': self._get_timeout(test.timeout),
            'keywords': self._convert_keywords(test, test_id)
        }

    def _convert_keywords(self, test, test_id):
        types = {'kw': 'KEYWORD', 'for': 'FOR'}
        return [self._convert_keyword(k, test_id, index, types[k.type])
                for index, k in enumerate(test.keywords)]

    def _convert_keyword(self, kw, test_id, index, type):
        return {
            'name': kw._get_name(kw.name) if isinstance(kw, Keyword) else kw.name,
            'id': test_id + '-k-%d' % index,
            'arguments': ', '.join(kw.args),
            'type': type
        }

    def _get_timeout(self, timeout):
        try:
            tout = utils.secs_to_timestr(utils.timestr_to_secs(timeout.string))
        except ValueError:
            tout = timeout.string
        if timeout.message:
            tout += ' | ' + timeout.message
        return tout

    def _get_id(self, parent_id, type, index):
        return parent_id + '-%s-%d' % (type, index)


def testdoc_cli(args):
    TestDoc().execute_cli(args)

if __name__ == '__main__':
    testdoc_cli(sys.argv[1:])

