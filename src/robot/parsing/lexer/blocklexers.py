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
                              IfHeaderLexer, ElseIfHeaderLexer, ElseHeaderLexer,
                              InlineIfHeaderLexer, EndLexer,
                              TryHeaderLexer, ExceptHeaderLexer, FinallyHeaderLexer,
                              ForHeaderLexer, WhileHeaderLexer,
                              ContinueLexer, BreakLexer, ReturnLexer)


class BlockLexer(Lexer):

    def __init__(self, ctx):
        """:type ctx: :class:`robot.parsing.lexer.context.FileContext`"""
        super().__init__(ctx)
        self.lexers = []

    def accepts_more(self, statement):
        return True

    def input(self, statement):
        if self.lexers and self.lexers[-1].accepts_more(statement):
            lexer = self.lexers[-1]
        else:
            lexer = self.lexer_for(statement)
            self.lexers.append(lexer)
        lexer.input(statement)
        return lexer

    def lexer_for(self, statement):
        for cls in self.lexer_classes():
            lexer = cls(self.ctx)
            if lexer.handles(statement):
                return lexer
        raise TypeError("%s did not find lexer for statement %s."
                        % (type(self).__name__, statement))

    def lexer_classes(self):
        return ()

    def lex(self):
        for lexer in self.lexers:
            lexer.lex()

    def _lex_with_priority(self, priority):
        for lexer in self.lexers:
            if isinstance(lexer, priority):
                lexer.lex()
        for lexer in self.lexers:
            if not isinstance(lexer, priority):
                lexer.lex()


class FileLexer(BlockLexer):

    def lex(self):
        self._lex_with_priority(priority=SettingSectionLexer)

    def lexer_classes(self):
        return (SettingSectionLexer, VariableSectionLexer,
                TestCaseSectionLexer, KeywordSectionLexer,
                CommentSectionLexer, ErrorSectionLexer,
                ImplicitCommentSectionLexer)


class SectionLexer(BlockLexer):

    def accepts_more(self, statement):
        return not statement[0].value.startswith('*')


class SettingSectionLexer(SectionLexer):

    def handles(self, statement):
        return self.ctx.setting_section(statement)

    def lexer_classes(self):
        return (SettingSectionHeaderLexer, SettingLexer)


class VariableSectionLexer(SectionLexer):

    def handles(self, statement):
        return self.ctx.variable_section(statement)

    def lexer_classes(self):
        return (VariableSectionHeaderLexer, VariableLexer)


class TestCaseSectionLexer(SectionLexer):

    def handles(self, statement):
        return self.ctx.test_case_section(statement)

    def lexer_classes(self):
        return (TestCaseSectionHeaderLexer, TestCaseLexer)


class KeywordSectionLexer(SettingSectionLexer):

    def handles(self, statement):
        return self.ctx.keyword_section(statement)

    def lexer_classes(self):
        return (KeywordSectionHeaderLexer, KeywordLexer)


class CommentSectionLexer(SectionLexer):

    def handles(self, statement):
        return self.ctx.comment_section(statement)

    def lexer_classes(self):
        return (CommentSectionHeaderLexer, CommentLexer)


class ImplicitCommentSectionLexer(SectionLexer):

    def handles(self, statement):
        return True

    def lexer_classes(self):
        return (CommentLexer,)


class ErrorSectionLexer(SectionLexer):

    def handles(self, statement):
        return statement and statement[0].value.startswith('*')

    def lexer_classes(self):
        return (ErrorSectionHeaderLexer, CommentLexer)


class TestOrKeywordLexer(BlockLexer):
    name_type = NotImplemented
    _name_seen = False

    def accepts_more(self, statement):
        return not statement[0].value

    def input(self, statement):
        self._handle_name_or_indentation(statement)
        if statement:
            super().input(statement)

    def _handle_name_or_indentation(self, statement):
        if not self._name_seen:
            token = statement.pop(0)
            token.type = self.name_type
            if statement:
                token._add_eos_after = True
            self._name_seen = True
        else:
            while statement and not statement[0].value:
                statement.pop(0).type = None    # These tokens will be ignored

    def lexer_classes(self):
        return (TestOrKeywordSettingLexer, BreakLexer, ContinueLexer,
                ForLexer, InlineIfLexer, IfLexer, ReturnLexer, TryLexer,
                WhileLexer, KeywordCallLexer)


class TestCaseLexer(TestOrKeywordLexer):
    name_type = Token.TESTCASE_NAME

    def __init__(self, ctx):
        """:type ctx: :class:`robot.parsing.lexer.context.TestCaseFileContext`"""
        super().__init__(ctx.test_case_context())

    def lex(self,):
        self._lex_with_priority(priority=TestOrKeywordSettingLexer)


class KeywordLexer(TestOrKeywordLexer):
    name_type = Token.KEYWORD_NAME

    def __init__(self, ctx):
        super().__init__(ctx.keyword_context())


class NestedBlockLexer(BlockLexer):

    def __init__(self, ctx):
        super().__init__(ctx)
        self._block_level = 0

    def accepts_more(self, statement):
        return self._block_level > 0

    def input(self, statement):
        lexer = super().input(statement)
        if isinstance(lexer, (ForHeaderLexer, IfHeaderLexer, TryHeaderLexer,
                              WhileHeaderLexer)):
            self._block_level += 1
        if isinstance(lexer, EndLexer):
            self._block_level -= 1


class ForLexer(NestedBlockLexer):

    def handles(self, statement):
        return ForHeaderLexer(self.ctx).handles(statement)

    def lexer_classes(self):
        return (ForHeaderLexer, InlineIfLexer, IfLexer, TryLexer, WhileLexer, EndLexer,
                ReturnLexer, ContinueLexer, BreakLexer, KeywordCallLexer)


class WhileLexer(NestedBlockLexer):

    def handles(self, statement):
        return WhileHeaderLexer(self.ctx).handles(statement)

    def lexer_classes(self):
        return (WhileHeaderLexer, ForLexer, InlineIfLexer, IfLexer, TryLexer, EndLexer,
                ReturnLexer, ContinueLexer, BreakLexer, KeywordCallLexer)


class IfLexer(NestedBlockLexer):

    def handles(self, statement):
        return IfHeaderLexer(self.ctx).handles(statement)

    def lexer_classes(self):
        return (InlineIfLexer, IfHeaderLexer, ElseIfHeaderLexer, ElseHeaderLexer,
                ForLexer, TryLexer, WhileLexer, EndLexer, ReturnLexer, ContinueLexer,
                BreakLexer, KeywordCallLexer)


class InlineIfLexer(BlockLexer):

    def handles(self, statement):
        if len(statement) <= 2:
            return False
        return InlineIfHeaderLexer(self.ctx).handles(statement)

    def accepts_more(self, statement):
        return False

    def lexer_classes(self):
        return (InlineIfHeaderLexer, ElseIfHeaderLexer, ElseHeaderLexer,
                ReturnLexer, ContinueLexer, BreakLexer, KeywordCallLexer)

    def input(self, statement):
        for part in self._split(statement):
            if part:
                super().input(part)
        return self

    def _split(self, statement):
        current = []
        expect_condition = False
        for token in statement:
            if expect_condition:
                if token is not statement[-1]:
                    token._add_eos_after = True
                current.append(token)
                yield current
                current = []
                expect_condition = False
            elif token.value == 'IF':
                current.append(token)
                expect_condition = True
            elif normalize_whitespace(token.value) == 'ELSE IF':
                token._add_eos_before = True
                yield current
                current = [token]
                expect_condition = True
            elif token.value == 'ELSE':
                token._add_eos_before = True
                if token is not statement[-1]:
                    token._add_eos_after = True
                yield current
                current = []
                yield [token]
            else:
                current.append(token)
        yield current


class TryLexer(NestedBlockLexer):

    def handles(self, statement):
        return TryHeaderLexer(self.ctx).handles(statement)

    def lexer_classes(self):
        return (TryHeaderLexer, ExceptHeaderLexer, ElseHeaderLexer, FinallyHeaderLexer,
                ForLexer, InlineIfLexer, IfLexer, WhileLexer, EndLexer, ReturnLexer,
                BreakLexer, ContinueLexer, KeywordCallLexer)
