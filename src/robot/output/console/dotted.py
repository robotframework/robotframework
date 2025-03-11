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

import sys
from typing import TYPE_CHECKING

from robot.model import SuiteVisitor
from robot.utils import plural_or_not as s, secs_to_timestr

from .highlighting import HighlightingStream
from ..loggerapi import LoggerApi

if TYPE_CHECKING:
    from robot.result import TestCase, TestSuite


class DottedOutput(LoggerApi):

    def __init__(self, width=78, colors='AUTO', links='AUTO', stdout=None, stderr=None):
        self.width = width
        self.stdout = HighlightingStream(stdout or sys.__stdout__, colors, links)
        self.stderr = HighlightingStream(stderr or sys.__stderr__, colors, links)
        self.markers_on_row = 0

    def start_suite(self, data, result):
        if not data.parent:
            count = data.test_count
            ts = ('test' if not data.rpa else 'task') + s(count)
            self.stdout.write(f"Running suite '{result.name}' with {count} {ts}.\n")
            self.stdout.write('=' * self.width + '\n')

    def end_test(self, data, result):
        if self.markers_on_row == self.width:
            self.stdout.write('\n')
            self.markers_on_row = 0
        self.markers_on_row += 1
        if result.passed:
            self.stdout.write('.')
        elif result.skipped:
            self.stdout.highlight('s', 'SKIP')
        elif result.tags.robot('exit'):
            self.stdout.write('x')
        else:
            self.stdout.highlight('F', 'FAIL')

    def end_suite(self, data, result):
        if not data.parent:
            self.stdout.write('\n')
            StatusReporter(self.stdout, self.width).report(result)
            self.stdout.write('\n')

    def message(self, msg):
        if msg.level in ('WARN', 'ERROR'):
            self.stderr.error(msg.message, msg.level)

    def result_file(self, kind, path):
        self.stdout.result_file(kind, path)


class StatusReporter(SuiteVisitor):

    def __init__(self, stream, width):
        self.stream = stream
        self.width = width

    def report(self, suite: 'TestSuite'):
        suite.visit(self)
        stats = suite.statistics
        ts = ('test' if not suite.rpa else 'task') + s(stats.total)
        elapsed = secs_to_timestr(suite.elapsed_time)
        self.stream.write(f"{'=' * self.width}\nRun suite '{suite.name}' with "
                          f"{stats.total} {ts} in {elapsed}.\n\n")
        ed = 'ED' if suite.status != 'SKIP' else 'PED'
        self.stream.highlight(suite.status + ed, suite.status)
        self.stream.write(f'\n{stats.message}\n')

    def visit_test(self, test: 'TestCase'):
        if test.failed and not test.tags.robot('exit'):
            self.stream.write('-' * self.width + '\n')
            self.stream.highlight('FAIL')
            self.stream.write(f': {test.full_name}\n{test.message.strip()}\n')
