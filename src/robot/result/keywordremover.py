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

from robot.result.visitor import SuiteVisitor, SkipAllVisitor


def KeywordRemover(how):
    how = how and how.upper()
    if how == 'PASSED':
        return PassedKeywordRemover()
    if how == 'FOR':
        return ForLoopItemsRemover()
    if how == 'ALL':
        return AllKeywordsRemover()
    return SkipAllVisitor()


class _KeywordRemover(SuiteVisitor):

    def _clear_content(self, keyword):
        keyword.messages = []
        keyword.keywords = []

    def _contains_warning(self, item):
        contains_warning_visitor = ContainsWarningVisitor()
        item.visit(contains_warning_visitor)
        return contains_warning_visitor.result


class AllKeywordsRemover(_KeywordRemover):

    def visit_keyword(self, keyword):
        self._clear_content(keyword)


class PassedKeywordRemover(_KeywordRemover):

    def start_suite(self, suite):
        if not suite.all_stats.failed:
            for keyword in suite.keywords:
                if not self._contains_warning(keyword):
                    self._clear_content(keyword)

    def visit_test(self, test):
        if self._should_be_cleared(test):
            for keyword in test.keywords:
                self._clear_content(keyword)

    def visit_keyword(self, keyword):
        pass

    def _should_be_cleared(self, item):
        return item.is_passed and not self._contains_warning(item)


class ForLoopItemsRemover(_KeywordRemover):

    def start_keyword(self, keyword):
        if not keyword.is_passed:
            return False
        if keyword.is_forloop:
            self._clear_content(keyword)
            return False

    def start_test(self, test):
        return test.is_passed and not self._contains_warning(test)


def _stop_if_result(method):
    def wrapped(s, i):
        if s.result:
            return
        method(s, i)
    return wrapped


class ContainsWarningVisitor(SuiteVisitor):

    def __init__(self):
        self.result = False

    def visit_message(self, msg):
        self.result |= msg.level == 'WARN'

    visit_keyword = _stop_if_result(SuiteVisitor.visit_keyword)
    visit_suite = _stop_if_result(SuiteVisitor.visit_suite)
    visit_test = _stop_if_result(SuiteVisitor.visit_test)

