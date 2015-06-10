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

from .highlighting import StatusHighlighter


class DottedOutput(object):

    def __init__(self, width=78, colors='AUTO', stdout=None, stderr=None):
        self._width = width
        self._stdout = stdout or sys.__stdout__
        self._stderr = stderr or sys.__stderr__
        self._highlighter = StatusHighlighter(colors, self._stdout, self._stderr)

    def end_test(self, test):
        if test.passed:
            self._stdout.write('.')
        elif not test.critical:
            self._stdout.write('f')
        else:
            self._highlighter.highlight('FAIL', self._stdout, 'F')
        self._stdout.flush()

    def end_suite(self, suite):
        if not suite.parent:
            self._stdout.write('\n')
            StatusReporter(self._stdout, self._highlighter, self._width).report(suite)
            self._stdout.write('\n')

    def message(self, msg):
        if msg.level in ('WARN', 'ERROR'):
            self._highlighter.error(msg.message, msg.level, self._stderr)

    def output_file(self, name, path):
        self._stdout.write('%-8s %s\n' % (name+':', path))


class StatusReporter(SuiteVisitor):

    def __init__(self, stream, highlighter, width):
        self._stream = stream
        self._highlighter = highlighter
        self._width = width

    def report(self, suite):
        suite.visit(self)
        stats = suite.statistics
        self._stream.write('%s\nRun %d test%s in %s\n\n'
                           % ('-' * self._width, stats.all.total,
                              plural_or_not(stats.all.total),
                              secs_to_timestr(suite.elapsedtime/1000.0)))
        self._highlighter.highlight(suite.status, self._stream, suite.status + 'ED')
        self._stream.write('\n%s\n' % stats.message)

    def visit_test(self, test):
        if not test.passed and test.critical:
            self._stream.write('%s\n' % ('=' * self._width))
            self._highlighter.highlight('FAIL', self._stream)
            self._stream.write(': %s\n%s\n%s\n\n'
                               % (test.longname, '-' * self._width, test.message))
