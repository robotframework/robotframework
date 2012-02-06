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

from robot.model import SuiteVisitor, SkipAllVisitor


def KeywordRemover(how):
    how = how and how.upper()
    return {
         'PASSED':PassedKeywordRemover,
         'FOR':ForLoopItemsRemover,
         'ALL':AllKeywordsRemover,
         'WUKS':WaitUntilKeywordSucceedsRemover,
    }.get(how, SkipAllVisitor)()


class _KeywordRemover(SuiteVisitor):

    def _clear_content(self, keyword):
        keyword.keywords = []
        keyword.messages = []

    def _contains_warning(self, item):
        contains_warning = ContainsWarning()
        item.visit(contains_warning)
        return contains_warning.result


class ContainsWarning(SuiteVisitor):

    def __init__(self):
        self.result = False

    def start_suite(self, suite):
        return not self.result

    def start_test(self, test):
        return not self.result

    def start_keyword(self, keyword):
        return not self.result

    def visit_message(self, msg):
        if msg.level == 'WARN':
            self.result = True


class AllKeywordsRemover(_KeywordRemover):

    def visit_keyword(self, keyword):
        self._clear_content(keyword)


class PassedKeywordRemover(_KeywordRemover):

    def start_suite(self, suite):
        if not suite.statistics.all.failed:
            for keyword in suite.keywords:
                if not self._contains_warning(keyword):
                    self._clear_content(keyword)

    def visit_test(self, test):
        if self._should_be_cleared(test):
            for keyword in test.keywords:
                self._clear_content(keyword)

    def _should_be_cleared(self, item):
        return item.is_passed and not self._contains_warning(item)

    def visit_keyword(self, keyword):
        pass


class ForLoopItemsRemover(_KeywordRemover):

    def start_keyword(self, kw):
        if kw.type == kw.FOR_LOOP_TYPE:
            kw.keywords = [item for item in kw.keywords
                           if not item.is_passed or self._contains_warning(item)]

class WaitUntilKeywordSucceedsRemover(_KeywordRemover):

    def start_keyword(self, kw):
        if kw.name == 'BuiltIn.Wait Until Keyword Succeeds' and kw.keywords:
            keywords = list(kw.keywords)
            last_included = 2 if kw.keywords[-1].is_passed else 1
            kw.keywords = self._kws_with_warnings(keywords[:-last_included]) + \
                          keywords[-last_included:]

    def _kws_with_warnings(self, keywords):
        return [k for k in keywords if self._contains_warning(k)]

