#  Copyright 2008-2014 Nokia Solutions and Networks
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

from robot.model import SuiteVisitor


class ReRunMerger(SuiteVisitor):

    def __init__(self, result):
        self.root = result.suite
        self.current = None

    def merge(self, merged):
        merged.suite.visit(self)

    def start_suite(self, suite):
        try:
            if not self.current:
                self.current = self._find_root(suite)
            else:
                self.current = self._find(self.current.suites, suite.name)
        except ValueError:
            self._report_ignored(suite)
            return False

    def _find_root(self, suite):
        if self.root.name != suite.name:
            raise ValueError
        return self.root

    def _find(self, items, name):
        for item in items:
            if item.name == name:
                return item
        raise ValueError

    def _report_ignored(self, item, test=False):
        from robot.output import LOGGER
        type = 'suite' if not test else 'test'
        LOGGER.error("Merged %s '%s' is ignored because it is not found from "
                     "original result." % (type, item.longname))

    def end_suite(self, suite):
        self.current = self.current.parent

    def visit_test(self, test):
        try:
            old = self._find(self.current.tests, test.name)
        except ValueError:
            self._report_ignored(test, test=True)
        else:
            test.message = self._create_merge_message(test, old)
            index = self.current.tests.index(old)
            self.current.tests[index] = test

    def _create_merge_message(self, new, old):
        return '\n'.join(['Test has been re-run and results replaced.',
                          '-  -  -',
                          'New status:  %s' % new.status,
                          'New message:  %s' % new.message,
                          '-  -  -',
                          'Old status:  %s' % old.status,
                          'Old message:  %s' % old.message])
