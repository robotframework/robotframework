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

import os

from robot.result.visitor import ResultVisitor
from robot import utils


class XUnitWriter(ResultVisitor):
    """Provides an xUnit-compatible result file.

    Attempts to adhere to the de facto schema guessed by Peter Reilly, see:
    http://marc.info/?l=ant-dev&m=123551933508682
    """

    def __init__(self, output):
        self._writer = utils.XmlWriter(output)
        self._root_suite = None

    def start_suite(self, suite):
        if self._root_suite:
            return
        self._root_suite = suite
        attrs = {'name': suite.name,
                 'tests': suite.statistics.all.total,
                 'errors': 0,
                 'failures': suite.statistics.all.failed,
                 'skip': 0}
        self._writer.start('testsuite', attrs)

    def end_suite(self, suite):
        if suite is self._root_suite:
            self._writer.end('testsuite')

    def start_test(self, test):
        attrs = {'classname': test.parent.longname,
                 'name': test.name,
                 'time': self._time_as_seconds(test.elapsedtime)}
        self._writer.start('testcase', attrs)
        if test.status == 'FAIL':
            test.visit(TestFailureWriter(self._writer))

    def _time_as_seconds(self, millis):
        return int(round(millis, -3) / 1000)

    def end_test(self, test):
        self._writer.end('testcase')

    def visit_keyword(self, kw):
        pass

    def end_result(self, result):
        self._writer.close()


class TestFailureWriter(ResultVisitor):

    def __init__(self, writer):
        self._writer = writer

    def start_test(self, test):
        self._writer.start('failure', {'message': test.message,
                                       'type': 'AssertionError'})

    def end_test(self, test):
        self._writer.end('failure')

    def visit_message(self, msg):
        """Populates the <failure> section, normally only with a 'Stacktrace'.

        There is a weakness here because filtering is based on message level:
        - DEBUG level is used by RF for 'Tracebacks' (what is expected here)
        - INFO and TRACE are used for keywords and arguments (not errors)
        - first FAIL message is already reported as <failure> attribute
        """
        if msg.level == 'DEBUG':
            self._writer.content(msg.message + os.linesep)
