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
from robot.model import SuiteVisitor, TagPattern
from robot.utils import Matcher, plural_or_not


def TestCaseRemover(how):
    upper = how.upper()
    if upper.startswith('NAME:'):
        return ByNameTestCaseRemover(pattern=how[5:])
    if upper.startswith('TAG:'):
        return ByTagTestCaseRemover(pattern=how[4:])
    try:
        return {'ALL': AllTestCasesRemover,
                'PASSED': PassedTestCasesRemover}[upper]()
    except KeyError:
        raise DataError("Expected 'ALL', 'PASSED', 'TAG', 'NAME:<pattern>' but got '%s'." % how)


class _TestCaseRemover(SuiteVisitor):
    _message = 'Test case data removed using --RemoveTestCases option.'

    def __init__(self):
        self._removal_message = RemovalMessage(self._message)

    def _clear_content(self, tc):
        tc.keywords = []
        tc.message = []
        self._removal_message.set(tc)

    def _failed_or_warning_or_error(self, item):
        return not item.passed or self._warning_or_error(item)

    def _warning_or_error(self, item):
        finder = WarningAndErrorFinder()
        item.visit(finder)
        return finder.found

class AllTestCasesRemover(_TestCaseRemover):

    def start_suite(self, suite):
            for test in suite.tests:
                if not self._warning_or_error(test):
                    self._clear_content(test)


class ByTagTestCaseRemover(_TestCaseRemover):

    def __init__(self, pattern):
        _TestCaseRemover.__init__(self)
        self._pattern = TagPattern(pattern)

    def visit_test(self, tc):
        if self._pattern.match(tc.tags) and not self._warning_or_error(tc):
            self._clear_content(tc)


class PassedTestCasesRemover(_TestCaseRemover):

    def start_suite(self, suite):
        for test in suite.tests:
            if not self._failed_or_warning_or_error(test):
                self._clear_content(test)


class ByNameTestCaseRemover(_TestCaseRemover):

    def __init__(self, pattern):
        _TestCaseRemover.__init__(self)
        self._matcher = Matcher(pattern, ignore='_')

    def start_test(self, tc):
        if self._matcher.match(tc.name) and not self._warning_or_error(tc):
            self._clear_content(tc)


class WarningAndErrorFinder(SuiteVisitor):

    def __init__(self):
        self.found = False

    def start_suite(self, suite):
        return not self.found

    def start_test(self, test):
        return not self.found

    def start_test_case(self, keyword):
        return not self.found

    def visit_message(self, msg):
        if msg.level in ('WARN', 'ERROR'):
            self.found = True


class RemovalMessage(object):

    def __init__(self, message):
        self._message = message

    def set_if_removed(self, tc, len_before):
        removed = len_before - len(tc.keywords)
        if removed:
            self.set(tc, self._message % (removed, plural_or_not(removed)))

    def set(self, tc, message=None):
        tc.doc = ('%s\n\n_%s_' % (tc.doc, message or self._message)).strip()
