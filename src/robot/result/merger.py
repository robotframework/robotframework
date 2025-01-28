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
            old.start_time = old.end_time = old.elapsed_time = None
            old.doc = suite.doc
            old.metadata.update(suite.metadata)
            old.setup = suite.setup
            old.teardown = suite.teardown
            self.current = old
        else:
            suite.message = self._create_add_message(suite, suite=True)
            self.current.suites.append(suite)
        return old is not None

    def _find_root(self, name):
        root = self.result.suite
        if root.name != name:
            raise DataError(f"Cannot merge outputs containing different root suites. "
                            f"Original suite is '{root.name}' and merged is '{name}'.")
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
        item_type = 'Suite' if suite else test_or_task('Test', self.rpa)
        prefix = f'*HTML* {item_type} added from merged output.'
        if not item.message:
            return prefix
        return ''.join([prefix, '<hr>', self._html(item.message)])

    def _html(self, message):
        if message.startswith('*HTML*'):
            return message[6:].lstrip()
        return html_escape(message)

    def _create_merge_message(self, new, old):
        header = (f'*HTML* <span class="merge">{test_or_task("Test", self.rpa)} '
                  f'has been re-executed and results merged.</span>')
        return ''.join([
            header,
            '<hr>',
            self._format_status_and_message('New', new),
            '<hr>',
            self._format_old_status_and_message(old, header)
        ])

    def _format_status_and_message(self, state, test):
        msg = f'{self._status_header(state)} {self._status_text(test.status)}<br>'
        if test.message:
            msg += f'{self._message_header(state)} {self._html(test.message)}<br>'
        return msg

    def _status_header(self, state):
        return f'<span class="{state.lower()}-status">{state} status:</span>'

    def _status_text(self, status):
        return f'<span class="{status.lower()}">{status}</span>'

    def _message_header(self, state):
        return f'<span class="{state.lower()}-message">{state} message:</span>'

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
        msg = (f'*HTML* {test_or_task("Test", self.rpa)} has been re-executed and '
               f'results merged. Latter result had {self._status_text("SKIP")} status '
               f'and was ignored. Message:\n{self._html(new.message)}')
        if test.message:
            msg += f'<hr>Original message:\n{self._html(test.message)}'
        return msg
