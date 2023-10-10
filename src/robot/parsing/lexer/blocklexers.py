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
from collections.abc import Iterator

from robot.utils import normalize_whitespace

from .context import (FileContext, KeywordContext, LexingContext, SuiteFileContext,
                      TestCaseContext)
from .statementlexers import (BreakLexer, CommentLexer, CommentSectionHeaderLexer,
                              ContinueLexer, ElseHeaderLexer, ElseIfHeaderLexer,
                              EndLexer, ExceptHeaderLexer, FinallyHeaderLexer,
                              ForHeaderLexer, IfHeaderLexer, ImplicitCommentLexer,
                              InlineIfHeaderLexer, InvalidSectionHeaderLexer,
                              KeywordCallLexer, KeywordSectionHeaderLexer,
                              KeywordSettingLexer, Lexer, ReturnLexer, SettingLexer,
                              SettingSectionHeaderLexer, SyntaxErrorLexer,
                              TaskSectionHeaderLexer, TestCaseSectionHeaderLexer,
                              TestCaseSettingLexer, TryHeaderLexer, VarLexer,
                              VariableLexer, VariableSectionHeaderLexer,
                              WhileHeaderLexer)
from .tokens import StatementTokens, Token


class BlockLexer(Lexer, ABC):

    def __init__(self, ctx: LexingContext):
        super().__init__(ctx)
        self.lexers: 'list[Lexer]' = []

    def accepts_more(self, statement: StatementTokens) -> bool:
        return True

    def input(self, statement: StatementTokens):
        if self.lexers and self.lexers[-1].accepts_more(statement):
            lexer = self.lexers[-1]
        else:
            lexer = self.lexer_for(statement)
            self.lexers.append(lexer)
        lexer.input(statement)

    def lexer_for(self, statement: StatementTokens) -> Lexer:
        for cls in self.lexer_classes():
            lexer = cls(self.ctx)
            if lexer.handles(statement):
                return lexer
        raise TypeError(f"{type(self).__name__} does not have lexer for "
                        f"statement {statement}.")

    def lexer_classes(self) -> 'tuple[type[Lexer], ...]':
        return ()

    def lex(self):
        for lexer in self.lexers:
            lexer.lex()

    def _lex_with_priority(self, priority: 'type[Lexer]'):
        for lexer in self.lexers:
            if isinstance(lexer, priority):
                lexer.lex()
        for lexer in self.lexers:
            if not isinstance(lexer, priority):
                lexer.lex()


class FileLexer(BlockLexer):

    def lex(self):
        self._lex_with_priority(priority=SettingSectionLexer)

    def lexer_classes(self) -> 'tuple[type[Lexer], ...]':
        return (SettingSectionLexer, VariableSectionLexer,
                TestCaseSectionLexer, TaskSectionLexer,
                KeywordSectionLexer, CommentSectionLexer,
                InvalidSectionLexer, ImplicitCommentSectionLexer)


class SectionLexer(BlockLexer, ABC):
    ctx: FileContext

    def accepts_more(self, statement: StatementTokens) -> bool:
        return not statement[0].value.startswith('*')


class SettingSectionLexer(SectionLexer):

    def handles(self, statement: StatementTokens) -> bool:
        return self.ctx.setting_section(statement)

    def lexer_classes(self) -> 'tuple[type[Lexer], ...]':
        return (SettingSectionHeaderLexer, SettingLexer)


class VariableSectionLexer(SectionLexer):

    def handles(self, statement: StatementTokens) -> bool:
        return self.ctx.variable_section(statement)

    def lexer_classes(self) -> 'tuple[type[Lexer], ...]':
        return (VariableSectionHeaderLexer, VariableLexer)


class TestCaseSectionLexer(SectionLexer):

    def handles(self, statement: StatementTokens) -> bool:
        return self.ctx.test_case_section(statement)

    def lexer_classes(self) -> 'tuple[type[Lexer], ...]':
        return (TestCaseSectionHeaderLexer, TestCaseLexer)


class TaskSectionLexer(SectionLexer):

    def handles(self, statement: StatementTokens) -> bool:
        return self.ctx.task_section(statement)

    def lexer_classes(self) -> 'tuple[type[Lexer], ...]':
        return (TaskSectionHeaderLexer, TestCaseLexer)


class KeywordSectionLexer(SettingSectionLexer):

    def handles(self, statement: StatementTokens) -> bool:
        return self.ctx.keyword_section(statement)

    def lexer_classes(self) -> 'tuple[type[Lexer], ...]':
        return (KeywordSectionHeaderLexer, KeywordLexer)


class CommentSectionLexer(SectionLexer):

    def handles(self, statement: StatementTokens) -> bool:
        return self.ctx.comment_section(statement)

    def lexer_classes(self) -> 'tuple[type[Lexer], ...]':
        return (CommentSectionHeaderLexer, CommentLexer)


class ImplicitCommentSectionLexer(SectionLexer):

    def handles(self, statement: StatementTokens) -> bool:
        return True

    def lexer_classes(self) -> 'tuple[type[Lexer], ...]':
        return (ImplicitCommentLexer,)


class InvalidSectionLexer(SectionLexer):

    def handles(self, statement: StatementTokens) -> bool:
        return bool(statement and statement[0].value.startswith('*'))

    def lexer_classes(self) -> 'tuple[type[Lexer], ...]':
        return (InvalidSectionHeaderLexer, CommentLexer)


class TestOrKeywordLexer(BlockLexer, ABC):
    name_type: str
    _name_seen = False

    def accepts_more(self, statement: StatementTokens) -> bool:
        return not statement[0].value

    def input(self, statement: StatementTokens):
        self._handle_name_or_indentation(statement)
        if statement:
            super().input(statement)

    def _handle_name_or_indentation(self, statement: StatementTokens):
        if not self._name_seen:
            name_token = statement.pop(0)
            name_token.type = self.name_type
            if statement:
                name_token._add_eos_after = True
            self._name_seen = True
        else:
            while statement and not statement[0].value:
                statement.pop(0).type = None    # These tokens will be ignored


class TestCaseLexer(TestOrKeywordLexer):
    name_type = Token.TESTCASE_NAME

    def __init__(self, ctx: SuiteFileContext):
        super().__init__(ctx.test_case_context())

    def lex(self):
        self._lex_with_priority(priority=TestCaseSettingLexer)

    def lexer_classes(self) -> 'tuple[type[Lexer], ...]':
        return (TestCaseSettingLexer, ForLexer, InlineIfLexer, IfLexer, TryLexer,
                WhileLexer, VarLexer, SyntaxErrorLexer, KeywordCallLexer)


class KeywordLexer(TestOrKeywordLexer):
    name_type = Token.KEYWORD_NAME

    def __init__(self, ctx: FileContext):
        super().__init__(ctx.keyword_context())

    def lexer_classes(self) -> 'tuple[type[Lexer], ...]':
        return (KeywordSettingLexer, ForLexer, InlineIfLexer, IfLexer, TryLexer,
                WhileLexer, VarLexer, ReturnLexer, SyntaxErrorLexer, KeywordCallLexer)


class NestedBlockLexer(BlockLexer, ABC):
    ctx: 'TestCaseContext|KeywordContext'

    def __init__(self, ctx: 'TestCaseContext|KeywordContext'):
        super().__init__(ctx)
        self._block_level = 0

    def accepts_more(self, statement: StatementTokens) -> bool:
        return self._block_level > 0

    def input(self, statement: StatementTokens):
        super().input(statement)
        lexer = self.lexers[-1]
        if isinstance(lexer, (ForHeaderLexer, IfHeaderLexer, TryHeaderLexer,
                              WhileHeaderLexer)):
            self._block_level += 1
        if isinstance(lexer, EndLexer):
            self._block_level -= 1


class ForLexer(NestedBlockLexer):

    def handles(self, statement: StatementTokens) -> bool:
        return ForHeaderLexer(self.ctx).handles(statement)

    def lexer_classes(self) -> 'tuple[type[Lexer], ...]':
        return (ForHeaderLexer, InlineIfLexer, IfLexer, TryLexer, WhileLexer, EndLexer,
                VarLexer, ReturnLexer, ContinueLexer, BreakLexer, SyntaxErrorLexer,
                KeywordCallLexer)


class WhileLexer(NestedBlockLexer):

    def handles(self, statement: StatementTokens) -> bool:
        return WhileHeaderLexer(self.ctx).handles(statement)

    def lexer_classes(self) -> 'tuple[type[Lexer], ...]':
        return (WhileHeaderLexer, ForLexer, InlineIfLexer, IfLexer, TryLexer, EndLexer,
                VarLexer, ReturnLexer, ContinueLexer, BreakLexer, SyntaxErrorLexer,
                KeywordCallLexer)


class TryLexer(NestedBlockLexer):

    def handles(self, statement: StatementTokens) -> bool:
        return TryHeaderLexer(self.ctx).handles(statement)

    def lexer_classes(self) -> 'tuple[type[Lexer], ...]':
        return (TryHeaderLexer, ExceptHeaderLexer, ElseHeaderLexer, FinallyHeaderLexer,
                ForLexer, InlineIfLexer, IfLexer, WhileLexer, EndLexer, VarLexer,
                ReturnLexer, BreakLexer, ContinueLexer, SyntaxErrorLexer,
                KeywordCallLexer)


class IfLexer(NestedBlockLexer):

    def handles(self, statement: StatementTokens) -> bool:
        return IfHeaderLexer(self.ctx).handles(statement)

    def lexer_classes(self) -> 'tuple[type[Lexer], ...]':
        return (InlineIfLexer, IfHeaderLexer, ElseIfHeaderLexer, ElseHeaderLexer,
                ForLexer, TryLexer, WhileLexer, EndLexer, VarLexer, ReturnLexer,
                ContinueLexer, BreakLexer, SyntaxErrorLexer, KeywordCallLexer)


class InlineIfLexer(NestedBlockLexer):

    def handles(self, statement: StatementTokens) -> bool:
        if len(statement) <= 2:
            return False
        return InlineIfHeaderLexer(self.ctx).handles(statement)

    def accepts_more(self, statement: StatementTokens) -> bool:
        return False

    def lexer_classes(self) -> 'tuple[type[Lexer], ...]':
        return (InlineIfHeaderLexer, ElseIfHeaderLexer, ElseHeaderLexer, VarLexer,
                ReturnLexer, ContinueLexer, BreakLexer, KeywordCallLexer)

    def input(self, statement: StatementTokens):
        for part in self._split(statement):
            if part:
                super().input(part)

    def _split(self, statement: StatementTokens) -> 'Iterator[StatementTokens]':
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
