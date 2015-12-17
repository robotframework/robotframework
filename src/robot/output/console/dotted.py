#  Copyright 2008-2015 Nokia Solutions and Networks
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

import sys

from robot.model import SuiteVisitor
from robot.utils import plural_or_not, secs_to_timestr

from .highlighting import HighlightingStream


class DottedOutput(object):

    def __init__(self, width=78, colors='AUTO', stdout=None, stderr=None):
        self._width = width
        self._stdout = HighlightingStream(stdout or sys.__stdout__, colors)
        self._stderr = HighlightingStream(stderr or sys.__stderr__, colors)
        self._markers_on_row = 0

    def start_suite(self, suite):
        if not suite.parent:
            self._stdout.write("Running suite '%s' with %d tests.\n"
                               % (suite.name, suite.test_count))
            self._stdout.write('=' * self._width + '\n')

    def end_test(self, test):
        if self._markers_on_row == self._width:
            self._stdout.write('\n')
            self._markers_on_row = 0
        self._markers_on_row += 1
        if test.passed:
            self._stdout.write('.')
        elif 'robot-exit' in test.tags:
            self._stdout.write('x')
        elif not test.critical:
            self._stdout.write('f')
        else:
            self._stdout.highlight('F', 'FAIL')

    def end_suite(self, suite):
        if not suite.parent:
            self._stdout.write('\n')
            StatusReporter(self._stdout, self._width).report(suite)
            self._stdout.write('\n')

    def message(self, msg):
        if msg.level in ('WARN', 'ERROR'):
            self._stderr.error(msg.message, msg.level)

    def output_file(self, name, path):
        self._stdout.write('%-8s %s\n' % (name+':', path))


class StatusReporter(SuiteVisitor):

    def __init__(self, stream, width):
        self._stream = stream
        self._width = width

    def report(self, suite):
        suite.visit(self)
        stats = suite.statistics
        self._stream.write("%s\nRun suite '%s' with %d test%s in %s.\n\n"
                           % ('=' * self._width, suite.name,
                              stats.all.total, plural_or_not(stats.all.total),
                              secs_to_timestr(suite.elapsedtime/1000.0)))
        self._stream.highlight(suite.status + 'ED', suite.status)
        self._stream.write('\n%s\n' % stats.message)

    def visit_test(self, test):
        if not test.passed and test.critical and 'robot-exit' not in test.tags:
            self._stream.write('-' * self._width + '\n')
            self._stream.highlight('FAIL')
            self._stream.write(': %s\n%s\n' % (test.longname,
                                               test.message.strip()))
