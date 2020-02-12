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

from robot.utils import normalize_whitespace

from .tokens import Token
from .statementlexers import (Lexer,
                              SettingSectionHeaderLexer, SettingLexer,
                              VariableSectionHeaderLexer, VariableLexer,
                              TestCaseSectionHeaderLexer,
                              KeywordSectionHeaderLexer,
                              CommentSectionHeaderLexer, CommentLexer,
                              ErrorSectionHeaderLexer,
                              TestOrKeywordSettingLexer,
                              KeywordCallLexer,
                              ForLoopHeaderLexer,
                              EndLexer)


class BlockLexer(Lexer):

    def __init__(self):
        self.lexers = []

    def accepts_more(self, statement):
        return True

    def input(self, statement):
        lexer = self.lexer_for(statement)
        lexer.input(statement)
        if not self.lexers or self.lexers[-1] is not lexer:
            self.lexers.append(lexer)

    def lexer_for(self, statement):
        if self.lexers and self.lexers[-1].accepts_more(statement):
            return self.lexers[-1]
        for cls in self.lexer_classes():
            if cls.handles(statement):
                return cls()
        raise TypeError("No lexer found for '%s'." % type(self).__name__)

    def lexer_classes(self):
        return ()

    def lex(self, ctx):
        for lexer in self.lexers:
            lexer.lex(ctx)

    def _lex_with_priority(self, ctx, priority):
        for lexer in self.lexers:
            if isinstance(lexer, priority):
                lexer.lex(ctx)
        for lexer in self.lexers:
            if not isinstance(lexer, priority):
                lexer.lex(ctx)


class FileLexer(BlockLexer):

    def lex(self, ctx):
        self._lex_with_priority(ctx, priority=SettingSectionLexer)

    def lexer_classes(self):
        return (SettingSectionLexer, VariableSectionLexer,
                TestCaseSectionLexer, KeywordSectionLexer,
                CommentSectionLexer, ErrorSectionLexer,
                ImplicitCommentSectionLexer)


class SectionLexer(BlockLexer):
    markers = ()
    has_header = True

    @classmethod
    def handles(cls, statement):
        if not statement:
            return False
        marker = statement[0].value
        return (marker.startswith('*') and
                cls._normalize(marker) in cls.markers)

    @classmethod
    def _normalize(cls, marker):
        return normalize_whitespace(marker).strip('* ').title()

    def accepts_more(self, statement):
        return not statement[0].value.startswith('*')


class SettingSectionLexer(SectionLexer):
    markers = ('Setting', 'Settings')

    def lexer_classes(self):
        return (SettingSectionHeaderLexer, SettingLexer)


class VariableSectionLexer(SectionLexer):
    markers = ('Variable', 'Variables')

    def lexer_classes(self):
        return (VariableSectionHeaderLexer, VariableLexer)


class TestCaseSectionLexer(SectionLexer):
    markers = ('Test Case', 'Test Cases', 'Task', 'Tasks')

    def lexer_classes(self):
        return (TestCaseSectionHeaderLexer, TestCaseLexer)


class KeywordSectionLexer(SettingSectionLexer):
    markers = ('Keyword', 'Keywords')

    def lexer_classes(self):
        return (KeywordSectionHeaderLexer, KeywordLexer)


class CommentSectionLexer(SectionLexer):
    markers = ('Comment', 'Comments')

    def lexer_classes(self):
        return (CommentSectionHeaderLexer, CommentLexer)


class ImplicitCommentSectionLexer(SectionLexer):

    @classmethod
    def handles(cls, statement):
        return True

    def lexer_classes(self):
        return (CommentLexer,)


class ErrorSectionLexer(SectionLexer):

    @classmethod
    def handles(cls, statement):
        return statement and statement[0].value.startswith('*')

    def lexer_classes(self):
        return (ErrorSectionHeaderLexer, CommentLexer)


class TestOrKeywordLexer(BlockLexer):
    name_type = NotImplemented
    _in_for_loop = False
    _old_style_for = None
    _name_set = False

    def accepts_more(self, statement):
        return not statement[0].value

    def input(self, statement):
        self._handle_name_or_indentation(statement)
        if statement:
            lexer = self.lexer_for(statement)
            self._handle_old_style_for_loop(statement, lexer)
            self.lexers.append(lexer)
            lexer.input(statement)

    def _handle_name_or_indentation(self, statement):
        if not self._name_set:
            statement.pop(0).type = self.name_type
            self._name_set = True
        else:
            while statement and not statement[0].value:
                statement.pop(0).type = Token.IGNORE

    def _handle_old_style_for_loop(self, statement, lexer):
        if isinstance(lexer, ForLoopHeaderLexer):
            self._in_for_loop = True
        elif isinstance(lexer, EndLexer):
            self._in_for_loop = False
            self._old_style_for = None
        elif self._in_for_loop and self._old_style_for is not False:
            if statement[0].value == '\\':
                statement.pop(0).type = Token.OLD_FOR_INDENT
                self._old_style_for = True
            elif self._old_style_for is None:
                self._old_style_for = False
            elif self._old_style_for is True:
                self._in_for_loop = False
                self._old_style_for = None

    def lexer_classes(self):
        return (TestOrKeywordSettingLexer, ForLoopHeaderLexer, EndLexer,
                KeywordCallLexer)


class TestCaseLexer(TestOrKeywordLexer):
    name_type = Token.TESTCASE_NAME

    def lex(self, ctx):
        ctx = ctx.test_case_context()
        self._lex_with_priority(ctx, priority=TestOrKeywordSettingLexer)


class KeywordLexer(TestOrKeywordLexer):
    name_type = Token.KEYWORD_NAME

    def lex(self, ctx):
        ctx = ctx.keyword_context()
        TestOrKeywordLexer.lex(self, ctx)
