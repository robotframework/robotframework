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

from abc import ABC

from robot.errors import DataError
from robot.model import SuiteVisitor, TagPattern
from robot.utils import html_escape, Matcher, plural_or_not


class KeywordRemover(SuiteVisitor, ABC):
    message = 'Content removed using the --remove-keywords option.'

    def __init__(self):
        self.removal_message = RemovalMessage(self.message)

    @classmethod
    def from_config(cls, conf):
        upper = conf.upper()
        if upper.startswith('NAME:'):
            return ByNameKeywordRemover(pattern=conf[5:])
        if upper.startswith('TAG:'):
            return ByTagKeywordRemover(pattern=conf[4:])
        try:
            return {'ALL': AllKeywordsRemover,
                    'PASSED': PassedKeywordRemover,
                    'FOR': ForLoopItemsRemover,
                    'WHILE': WhileLoopItemsRemover,
                    'WUKS': WaitUntilKeywordSucceedsRemover}[upper]()
        except KeyError:
            raise DataError(f"Expected 'ALL', 'PASSED', 'NAME:<pattern>', "
                            f"'TAG:<pattern>', 'FOR' or 'WUKS', got '{conf}'.")

    def _clear_content(self, item):
        if item.body:
            item.body.clear()
            self.removal_message.set_to(item)

    def _failed_or_warning_or_error(self, item):
        return not item.passed or self._warning_or_error(item)

    def _warning_or_error(self, item):
        finder = WarningAndErrorFinder()
        item.visit(finder)
        return finder.found


class AllKeywordsRemover(KeywordRemover):

    def start_body_item(self, item):
        self._clear_content(item)

    def start_if(self, item):
        pass

    def start_if_branch(self, item):
        self._clear_content(item)

    def start_try(self, item):
        pass

    def start_try_branch(self, item):
        self._clear_content(item)


class PassedKeywordRemover(KeywordRemover):

    def start_suite(self, suite):
        if not suite.statistics.failed:
            self._remove_setup_and_teardown(suite)

    def visit_test(self, test):
        if not self._failed_or_warning_or_error(test):
            for item in test.body:
                self._clear_content(item)
            self._remove_setup_and_teardown(test)

    def visit_keyword(self, keyword):
        pass

    def _remove_setup_and_teardown(self, item):
        if item.has_setup:
            if not self._warning_or_error(item.setup):
                self._clear_content(item.setup)
        if item.has_teardown:
            if not self._warning_or_error(item.teardown):
                self._clear_content(item.teardown)


class ByNameKeywordRemover(KeywordRemover):

    def __init__(self, pattern):
        super().__init__()
        self._matcher = Matcher(pattern, ignore='_')

    def start_keyword(self, kw):
        if self._matcher.match(kw.full_name) and not self._warning_or_error(kw):
            self._clear_content(kw)


class ByTagKeywordRemover(KeywordRemover):

    def __init__(self, pattern):
        super().__init__()
        self._pattern = TagPattern.from_string(pattern)

    def start_keyword(self, kw):
        if self._pattern.match(kw.tags) and not self._warning_or_error(kw):
            self._clear_content(kw)


class LoopItemsRemover(KeywordRemover, ABC):
    message = '{count} passing item{s} removed using the --remove-keywords option.'

    def _remove_from_loop(self, loop):
        before = len(loop.body)
        self._remove_keywords(loop.body)
        self.removal_message.set_to_if_removed(loop, before)

    def _remove_keywords(self, body):
        iterations = body.filter(messages=False)
        for it in iterations[:-1]:
            if not self._failed_or_warning_or_error(it):
                body.remove(it)


class ForLoopItemsRemover(LoopItemsRemover):

    def start_for(self, for_):
        self._remove_from_loop(for_)


class WhileLoopItemsRemover(LoopItemsRemover):

    def start_while(self, while_):
        self._remove_from_loop(while_)


class WaitUntilKeywordSucceedsRemover(KeywordRemover):
    message = '{count} failing item{s} removed using the --remove-keywords option.'

    def start_keyword(self, kw):
        if kw.owner == 'BuiltIn' and kw.name == 'Wait Until Keyword Succeeds':
            before = len(kw.body)
            self._remove_keywords(kw.body)
            self.removal_message.set_to_if_removed(kw, before)

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
        self.message = message

    def set_to_if_removed(self, item, len_before):
        removed = len_before - len(item.body)
        if removed:
            message = self.message.format(count=removed, s=plural_or_not(removed))
            self.set_to(item, message)

    def set_to(self, item, message=None):
        if not item.message:
            start = ''
        elif item.message.startswith('*HTML*'):
            start = item.message[6:].strip() + '<hr>'
        else:
            start = html_escape(item.message) + '<hr>'
        message = message or self.message
        item.message = f'*HTML* {start}<span class="robot-note">{message}</span>'
