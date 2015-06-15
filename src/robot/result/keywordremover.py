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
                'WUKS': WaitUntilKeywordSucceedsRemover}[upper]()
    except KeyError:
        raise DataError("Expected 'ALL', 'PASSED', 'NAME:<pattern>', 'FOR', "
                        "or 'WUKS' but got '%s'." % how)


class _KeywordRemover(SuiteVisitor):
    _message = 'Keyword data removed using --RemoveKeywords option.'

    def __init__(self):
        self._removal_message = RemovalMessage(self._message)

    def _clear_content(self, kw):
        kw.keywords = []
        kw.messages = []
        self._removal_message.set(kw)

    def _failed_or_warning_or_error(self, item):
        return not item.passed or self._warning_or_error(item)

    def _warning_or_error(self, item):
        finder = WarningAndErrorFinder()
        item.visit(finder)
        return finder.found


class AllKeywordsRemover(_KeywordRemover):

    def visit_keyword(self, keyword):
        self._clear_content(keyword)


class PassedKeywordRemover(_KeywordRemover):

    def start_suite(self, suite):
        if not suite.statistics.all.failed:
            for keyword in suite.keywords:
                if not self._warning_or_error(keyword):
                    self._clear_content(keyword)

    def visit_test(self, test):
        if not self._failed_or_warning_or_error(test):
            for keyword in test.keywords:
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
        self._pattern = TagPattern(pattern)

    def start_keyword(self, kw):
        if self._pattern.match(kw.tags) and not self._warning_or_error(kw):
            self._clear_content(kw)


class ForLoopItemsRemover(_KeywordRemover):
    _message = '%d passing step%s removed using --RemoveKeywords option.'

    def start_keyword(self, kw):
        if kw.type == kw.FOR_LOOP_TYPE:
            before = len(kw.keywords)
            kw.keywords = self._remove_keywords(kw.keywords)
            self._removal_message.set_if_removed(kw, before)

    def _remove_keywords(self, keywords):
        return [kw for kw in keywords
                if self._failed_or_warning_or_error(kw) or kw is keywords[-1]]


class WaitUntilKeywordSucceedsRemover(_KeywordRemover):
    _message = '%d failing step%s removed using --RemoveKeywords option.'

    def start_keyword(self, kw):
        if kw.name == 'BuiltIn.Wait Until Keyword Succeeds' and kw.keywords:
            before = len(kw.keywords)
            kw.keywords = self._remove_keywords(list(kw.keywords))
            self._removal_message.set_if_removed(kw, before)

    def _remove_keywords(self, keywords):
        include_from_end = 2 if keywords[-1].passed else 1
        return self._kws_with_warnings(keywords[:-include_from_end]) \
            + keywords[-include_from_end:]

    def _kws_with_warnings(self, keywords):
        return [kw for kw in keywords if self._warning_or_error(kw)]


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


class RemovalMessage(object):

    def __init__(self, message):
        self._message = message

    def set_if_removed(self, kw, len_before):
        removed = len_before - len(kw.keywords)
        if removed:
            self.set(kw, self._message % (removed, plural_or_not(removed)))

    def set(self, kw, message=None):
        kw.doc = ('%s\n\n_%s_' % (kw.doc, message or self._message)).strip()
