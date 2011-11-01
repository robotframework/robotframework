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

from robot.result.visitor import Visitor, SkipAllVisitor


def KeywordRemover(how):
    how = how and how.upper()
    if how == 'PASSED':
        return PassedKeywordRemover()
    if how == 'ALL':
        return AllKeywordsRemover()
    return SkipAllVisitor()


def _remove_messages_and_keywords(kw):
    kw.messages = []
    kw.keywords = []


class AllKeywordsRemover(Visitor):

    def visit_keyword(self, keyword):
        _remove_messages_and_keywords(keyword)


class PassedKeywordRemover(Visitor):

    def visit_keyword(self, keyword):
        if keyword.status == 'PASS':
            _remove_messages_and_keywords(keyword)

    def visit_test(self, test):
        if test.status == 'PASS' and not test.contains_warning:
            for keyword in test.keywords:
                _remove_messages_and_keywords(keyword)


