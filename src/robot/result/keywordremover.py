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


def KeywordRemover(how):
    upper = how.upper()
    if upper.startswith('NAME:'):
        return ByNameKeywordRemover(pattern=how[5:])
    if upper.startswith('TAG:'):
        return ByTagKeywordRemover(pattern=how[4:])
    try:
        return {'ALL': AllKeywordsRemover,
                'PASSED': PassedKeywordRemover,
                'FOR': ForLoopItemsRemover,
                'WHILE': WhileLoopItemsRemover,
                'WUKS': WaitUntilKeywordSucceedsRemover}[upper]()
    except KeyError:
        raise DataError(f"Expected 'ALL', 'PASSED', 'NAME:<pattern>', 'TAG:<pattern>', "
                        f"'FOR' or 'WUKS', got '{how}'.")


class _KeywordRemover(SuiteVisitor):
    _message = 'Keyword data removed using --RemoveKeywords option.'

    def __init__(self):
        self._removal_message = RemovalMessage(self._message)

    def _clear_content(self, item):
        item.body.clear()
        self._removal_message.set(item)

    def _failed_or_warning_or_error(self, item):
        return not item.passed or self._warning_or_error(item)

    def _warning_or_error(self, item):
        finder = WarningAndErrorFinder()
        item.visit(finder)
        return finder.found


class AllKeywordsRemover(_KeywordRemover):

    def visit_keyword(self, keyword):
        self._clear_content(keyword)

    def visit_for(self, for_):
        self._clear_content(for_)

    def visit_if_branch(self, branch):
        self._clear_content(branch)


class PassedKeywordRemover(_KeywordRemover):

    def start_suite(self, suite):
        if not suite.statistics.failed:
            for keyword in suite.setup, suite.teardown:
                if not self._warning_or_error(keyword):
                    self._clear_content(keyword)

    def visit_test(self, test):
        if not self._failed_or_warning_or_error(test):
            for keyword in test.body:
                self._clear_content(keyword)

    def visit_keyword(self, keyword):
        pass


class ByNameKeywordRemover(_KeywordRemover):

    def __init__(self, pattern):
        _KeywordRemover.__init__(self)
        self._matcher = Matcher(pattern, ignore='_')

    def start_keyword(self, kw):
        if self._matcher.match(kw.name) and not self._warning_or_error(kw):
            self._clear_content(kw)


class ByTagKeywordRemover(_KeywordRemover):

    def __init__(self, pattern):
        _KeywordRemover.__init__(self)
        self._pattern = TagPattern.from_string(pattern)

    def start_keyword(self, kw):
        if self._pattern.match(kw.tags) and not self._warning_or_error(kw):
            self._clear_content(kw)


class _LoopItemsRemover(_KeywordRemover):
    _message = '%d passing step%s removed using --RemoveKeywords option.'

    def _remove_from_loop(self, loop):
        before = len(loop.body)
        self._remove_keywords(loop.body)
        self._removal_message.set_if_removed(loop, before)

    def _remove_keywords(self, body):
        iterations = body.filter(messages=False)
        for it in iterations[:-1]:
            if not self._failed_or_warning_or_error(it):
                body.remove(it)


class ForLoopItemsRemover(_LoopItemsRemover):

    def start_for(self, for_):
        self._remove_from_loop(for_)


class WhileLoopItemsRemover(_LoopItemsRemover):

    def start_while(self, while_):
        self._remove_from_loop(while_)


class WaitUntilKeywordSucceedsRemover(_KeywordRemover):
    _message = '%d failing step%s removed using --RemoveKeywords option.'

    def start_keyword(self, kw):
        if kw.libname == 'BuiltIn' and kw.kwname == 'Wait Until Keyword Succeeds':
            before = len(kw.body)
            self._remove_keywords(kw.body)
            self._removal_message.set_if_removed(kw, before)

    def _remove_keywords(self, body):
        keywords = body.filter(messages=False)
        if keywords:
            include_from_end = 2 if keywords[-1].passed else 1
            for kw in keywords[:-include_from_end]:
                if not self._warning_or_error(kw):
                    body.remove(kw)


class WarningAndErrorFinder(SuiteVisitor):

    def __init__(self):
        self.found = False

    def start_suite(self, suite):
        return not self.found

    def start_test(self, test):
        return not self.found

    def start_keyword(self, keyword):
        return not self.found

    def visit_message(self, msg):
        if msg.level in ('WARN', 'ERROR'):
            self.found = True


class RemovalMessage:

    def __init__(self, message):
        self._message = message

    def set_if_removed(self, kw, len_before):
        removed = len_before - len(kw.body)
        if removed:
            self.set(kw, self._message % (removed, plural_or_not(removed)))

    def set(self, kw, message=None):
        kw.doc = ('%s\n\n_%s_' % (kw.doc, message or self._message)).strip()
