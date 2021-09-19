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

from robot.errors import DataError
from robot.model import SuiteVisitor
from robot.utils import html_escape, test_or_task


class Merger(SuiteVisitor):

    def __init__(self, result, rpa=False):
        self.result = result
        self.current = None
        self.rpa = rpa

    def merge(self, merged):
        self.result.set_execution_mode(merged)
        merged.suite.visit(self)
        self.result.errors.add(merged.errors)

    def start_suite(self, suite):
        if self.current is None:
            old = self._find_root(suite.name)
        else:
            old = self._find(self.current.suites, suite.name)
        if old is not None:
            old.starttime = old.endtime = None
            self.current = old
        else:
            suite.message = self._create_add_message(suite, suite=True)
            self.current.suites.append(suite)
        return bool(old)

    def _find_root(self, name):
        root = self.result.suite
        if root.name != name:
            raise DataError("Cannot merge outputs containing different root suites. "
                            "Original suite is '%s' and merged is '%s'."
                            % (root.name, name))
        return root

    def _find(self, items, name):
        for item in items:
            if item.name == name:
                return item
        return None

    def end_suite(self, suite):
        self.current = self.current.parent

    def visit_test(self, test):
        old = self._find(self.current.tests, test.name)
        if old is None:
            test.message = self._create_add_message(test)
            self.current.tests.append(test)
        elif test.skipped:
            old.message = self._create_skip_message(old, test)
        else:
            test.message = self._create_merge_message(test, old)
            index = self.current.tests.index(old)
            self.current.tests[index] = test

    def _create_add_message(self, item, suite=False):
        item_type = 'Suite' if suite else test_or_task('{Test}', self.rpa)
        prefix = '*HTML* %s added from merged output.' % item_type
        if not item.message:
            return prefix
        return ''.join([prefix, '<hr>', self._html(item.message)])

    def _html(self, message):
        if message.startswith('*HTML*'):
            return message[6:].lstrip()
        return html_escape(message)

    def _create_merge_message(self, new, old):
        header = test_or_task('*HTML* <span class="merge">'
                              '{Test} has been re-executed and results merged.'
                              '</span>', self.rpa)
        return ''.join([
            header,
            '<hr>',
            self._format_status_and_message('New', new),
            '<hr>',
            self._format_old_status_and_message(old, header)
        ])

    def _format_status_and_message(self, state, test):
        message = '%s %s<br>' % (self._status_header(state),
                                 self._status_text(test.status))
        if test.message:
            message += '%s %s<br>' % (self._message_header(state),
                                      self._html(test.message))
        return message

    def _status_header(self, state):
        return '<span class="%s-status">%s status:</span>' % (state.lower(), state)

    def _status_text(self, status):
        return '<span class="%s">%s</span>' % (status.lower(), status)

    def _message_header(self, state):
        return '<span class="%s-message">%s message:</span>' % (state.lower(), state)

    def _format_old_status_and_message(self, test, merge_header):
        if not test.message.startswith(merge_header):
            return self._format_status_and_message('Old', test)
        status_and_message = test.message.split('<hr>', 1)[1]
        return (
            status_and_message
            .replace(self._status_header('New'), self._status_header('Old'))
            .replace(self._message_header('New'), self._message_header('Old'))
        )

    def _create_skip_message(self, test, new):
        msg = test_or_task('*HTML* {Test} has been re-executed and results merged. '
                           'Latter result had %s status and was ignored. Message:\n%s'
                           % (self._status_text('SKIP'), self._html(new.message)))
        if not test.message:
            return msg
        return '%s<hr>Original message:\n%s' % (msg, self._html(test.message))
