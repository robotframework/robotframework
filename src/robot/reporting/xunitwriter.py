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

from robot.result import ResultVisitor
from robot.utils import roundup, XmlWriter


class XUnitWriter(object):

    def __init__(self, execution_result, skip_noncritical):
        self._execution_result = execution_result
        self._skip_noncritical = skip_noncritical

    def write(self, output):
        writer = XUnitFileWriter(XmlWriter(output), self._skip_noncritical)
        self._execution_result.visit(writer)


class XUnitFileWriter(ResultVisitor):
    """Provides an xUnit-compatible result file.

    Attempts to adhere to the de facto schema guessed by Peter Reilly, see:
    http://marc.info/?l=ant-dev&m=123551933508682
    """

    def __init__(self, xml_writer, skip_noncritical=False):
        self._writer = xml_writer
        self._root_suite = None
        self._skip_noncritical = skip_noncritical

    def start_suite(self, suite):
        if self._root_suite:
            return
        self._root_suite = suite
        tests, failures, skip = self._get_stats(suite.statistics)
        attrs = {'name': suite.name,
                 'tests': tests,
                 'errors': '0',
                 'failures': failures,
                 'skip': skip}
        self._writer.start('testsuite', attrs)

    def _get_stats(self, statistics):
        if self._skip_noncritical:
            failures = statistics.critical.failed
            skip = statistics.all.total - statistics.critical.total
        else:
            failures = statistics.all.failed
            skip = 0
        return str(statistics.all.total), str(failures), str(skip)

    def end_suite(self, suite):
        if suite is self._root_suite:
            self._writer.end('testsuite')

    def visit_test(self, test):
        self._writer.start('testcase',
                           {'classname': test.parent.longname,
                            'name': test.name,
                            'time': self._time_as_seconds(test.elapsedtime)})
        if self._skip_noncritical and not test.critical:
            self._skip_test(test)
        elif not test.passed:
            self._fail_test(test)
        self._writer.end('testcase')

    def _skip_test(self, test):
        self._writer.element('skipped', '%s: %s' % (test.status, test.message)
                                        if test.message else test.status)

    def _fail_test(self, test):
        self._writer.element('failure', attrs={'message': test.message,
                                               'type': 'AssertionError'})

    def _time_as_seconds(self, millis):
        return str(roundup(millis, -3) // 1000)

    def visit_keyword(self, kw):
        pass

    def visit_statistics(self, stats):
        pass

    def visit_errors(self, errors):
        pass

    def end_result(self, result):
        self._writer.close()
