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

from robot.errors import DataError
from robot.model import SuiteVisitor


class Merger(SuiteVisitor):

    def __init__(self, result):
        self.result = result
        self.current = None

    def merge(self, merged):
        merged.suite.visit(self)
        self.result.errors.add(merged.errors)

    def start_suite(self, suite):
        try:
            self.current = self._find_suite(self.current, suite.name)
        except IndexError:
            suite.message = self._create_add_message(suite, test=False)
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
                            "suites. Original suite is '%s' and merged is '%s'."
                            % (root.name, name))
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

    def _create_add_message(self, item, test=True):
        prefix = '%s added from merged output.' % ('Test' if test else 'Suite')
        if not item.message:
            return prefix
        return '\n'.join([prefix, '-  -  -', item.message])

    def _create_merge_message(self, new, old):
        return '\n'.join(['Re-executed test has been merged.',
                          '-  -  -',
                          'New status:  %s' % new.status,
                          'New message:  %s' % new.message,
                          '-  -  -',
                          'Old status:  %s' % old.status,
                          'Old message:  %s' % old.message])
