#  Copyright 2008-2015 Nokia Networks
#  Copyright 2016-     Robot Framework Foundation
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

from __future__ import division

from robot.result import ResultVisitor
from robot.utils import XmlWriter


class XUnitWriter(object):

    def __init__(self, execution_result):
        self._execution_result = execution_result

    def write(self, output):
        xml_writer = XmlWriter(output, usage='xunit')
        writer = XUnitFileWriter(xml_writer)
        self._execution_result.visit(writer)


class XUnitFileWriter(ResultVisitor):
    """Provides an xUnit-compatible result file.

    Attempts to adhere to the de facto schema guessed by Peter Reilly, see:
    http://marc.info/?l=ant-dev&m=123551933508682
    """

    def __init__(self, xml_writer):
        self._writer = xml_writer
        self._root_suite = None

    def start_suite(self, suite):
        if self._root_suite:
            return
        self._root_suite = suite
        tests, failures, skipped = self._get_stats(suite.statistics)
        attrs = {'name': suite.name,
                 'tests': tests,
                 'errors': '0',
                 'failures': failures,
                 'skipped': skipped,
                 'time': self._time_as_seconds(suite.elapsedtime)}
        self._writer.start('testsuite', attrs)

    def _get_stats(self, statistics):
        return (
            str(statistics.total),
            str(statistics.failed),
            str(statistics.skipped)
        )

    def end_suite(self, suite):
        if suite is self._root_suite:
            self._writer.end('testsuite')

    def visit_test(self, test):
        self._writer.start('testcase',
                           {'classname': test.parent.longname,
                            'name': test.name,
                            'time': self._time_as_seconds(test.elapsedtime)})
        if test.failed:
            self._writer.element('failure', attrs={'message': test.message,
                                                   'type': 'AssertionError'})
        if test.skipped:
            self._writer.element('skipped', attrs={'message': test.message,
                                                   'type': 'SkipExecution'})
        self._writer.end('testcase')

    def _time_as_seconds(self, millis):
        return '{:.3f}'.format(millis / 1000)

    def visit_keyword(self, kw):
        pass

    def visit_statistics(self, stats):
        pass

    def visit_errors(self, errors):
        pass

    def end_result(self, result):
        self._writer.close()
