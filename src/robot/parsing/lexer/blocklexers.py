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
                              EndLexer, IfStatementLexer, ElseLexer, ElseIfStatementLexer)


class BlockLexer(Lexer):

    def __init__(self, ctx):
        """:type ctx: :class:`robot.parsing.lexer.context.FileContext`"""
        Lexer.__init__(self, ctx)
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
            BlockLexer.input(self, statement)

    def _handle_name_or_indentation(self, statement):
        if not self._name_seen:
            statement.pop(0).type = self.name_type
            self._name_seen = True
        else:
            while statement and not statement[0].value:
                statement.pop(0).type = None    # These tokens will be ignored

    def lexer_classes(self):
        return (TestOrKeywordSettingLexer, ForLoopLexer, IfBlockLexer, KeywordCallLexer)


class TestCaseLexer(TestOrKeywordLexer):
    name_type = Token.TESTCASE_NAME

    def __init__(self, ctx):
        TestOrKeywordLexer.__init__(self, ctx.test_case_context())

    def lex(self,):
        self._lex_with_priority(priority=TestOrKeywordSettingLexer)


class KeywordLexer(TestOrKeywordLexer):
    name_type = Token.KEYWORD_NAME

    def __init__(self, ctx):
        TestOrKeywordLexer.__init__(self, ctx.keyword_context())


class ForLoopLexer(BlockLexer):

    def __init__(self, ctx):
        BlockLexer.__init__(self, ctx)
        self._block_level = 0

    def handles(self, statement):
        return ForLoopHeaderLexer(self.ctx).handles(statement)

    def accepts_more(self, statement):
        return self._block_level > 0

    def input(self, statement):
        lexer = BlockLexer.input(self, statement)
        if isinstance(lexer, (IfStatementLexer, ForLoopHeaderLexer)):
            self._block_level += 1
        if isinstance(lexer, EndLexer):
            self._block_level -= 1

    def lexer_classes(self):
        return (ForLoopHeaderLexer, IfBlockLexer, EndLexer, KeywordCallLexer)


class IfBlockLexer(BlockLexer):

    def __init__(self, ctx):
        BlockLexer.__init__(self, ctx)
        self._end_seen = False
        self._else_seen = False
        self._block_level = 0
        self._last_block_has_content = False

    def handles(self, statement):
        return IfStatementLexer(self.ctx).handles(statement)

    def accepts_more(self, statement):
        return not self._end_seen

    def input(self, statement):
        lexer = BlockLexer.input(self, statement)
        if isinstance(lexer, (IfStatementLexer, ForLoopHeaderLexer)):
            self._block_level += 1
            self._last_block_has_content = self._block_level > 1
        elif isinstance(lexer, EndLexer):
            if not self._last_block_has_content:
                raise DataError("line [%s] : Empty block detected" % lexer.lineno)
            self._last_block_has_content = self._block_level > 1
            self._end_seen = self._block_level == 1
            self._block_level -= 1
        elif isinstance(lexer, ElseLexer):
            if not self._last_block_has_content:
                raise DataError("line [%s] : Empty block detected" % lexer.lineno)
            self._last_block_has_content = False
            if self._else_seen:
                raise DataError("line [%s] : Invalid second ELSE detected" % lexer.lineno)
            self._else_seen = True
        elif isinstance(lexer, ElseIfStatementLexer):
            if not self._last_block_has_content:
                raise DataError("line [%s] : Empty block detected" % lexer.lineno)
            self._last_block_has_content = False
            if self._else_seen:
                raise DataError("line [%s] : Invalid ELSE IF detected after ELSE" % lexer.lineno)
        else:
            self._last_block_has_content = True

    def lexer_classes(self):
        return (IfStatementLexer, ElseIfStatementLexer, ElseLexer, ForLoopLexer, EndLexer, KeywordCallLexer)