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
from robot.utils import html_escape


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
        try:
            self.current = self._find_suite(self.current, suite.name)
        except IndexError:
            suite.message = self._create_add_message(suite, suite=True)
            self.current.suites.append(suite)
            return False

    def _find_suite(self, parent, name):
        if not parent:
            suite = self._find_root(name)
        else:
            suite = self._find(parent.suites, name)
        suite.starttime = suite.endtime = None
        return suite

    def _find_root(self, name):
        root = self.result.suite
        if root.name != name:
            raise DataError("Cannot merge outputs containing different root "
                            "suites. Original suite is '%s' and merged is "
                            "'%s'." % (root.name, name))
        return root

    def _find(self, items, name):
        for item in items:
            if item.name == name:
                return item
        raise IndexError

    def end_suite(self, suite):
        self.current = self.current.parent

    def visit_test(self, test):
        try:
            old = self._find(self.current.tests, test.name)
        except IndexError:
            test.message = self._create_add_message(test)
            self.current.tests.append(test)
        else:
            test.message = self._create_merge_message(test, old)
            index = self.current.tests.index(old)
            self.current.tests[index] = test

    def _create_add_message(self, item, suite=False):
        if suite:
            item_type = 'Suite'
        elif self.rpa:
            item_type = 'Task'
        else:
            item_type = 'Test'
        prefix = '*HTML* %s added from merged output.' % item_type
        if not item.message:
            return prefix
        return ''.join([prefix, '<hr>', self._html_escape(item.message)])

    def _html_escape(self, message):
        if message.startswith('*HTML*'):
            return message[6:].lstrip()
        else:
            return html_escape(message)

    def _create_merge_message(self, new, old):
        header = ('*HTML* <span class="merge">'
                  '%s has been re-executed and results merged.'
                  '</span>' % ('Test' if not self.rpa else 'Task'))
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
                                      self._html_escape(test.message))
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
