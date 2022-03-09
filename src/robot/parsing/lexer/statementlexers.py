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
from robot.variables import is_assign

from .tokens import Token


class Lexer:
    """Base class for lexers."""

    def __init__(self, ctx):
        self.ctx = ctx

    def handles(self, statement):
        return True

    def accepts_more(self, statement):
        raise NotImplementedError

    def input(self, statement):
        raise NotImplementedError

    def lex(self):
        raise NotImplementedError


class StatementLexer(Lexer):
    token_type = None

    def __init__(self, ctx):
        super().__init__(ctx)
        self.statement = None

    def accepts_more(self, statement):
        return False

    def input(self, statement):
        self.statement = statement

    def lex(self):
        raise NotImplementedError


class SingleType(StatementLexer):

    def lex(self):
        for token in self.statement:
            token.type = self.token_type


class TypeAndArguments(StatementLexer):

    def lex(self):
        self.statement[0].type = self.token_type
        for token in self.statement[1:]:
            token.type = Token.ARGUMENT


class SectionHeaderLexer(SingleType):

    def handles(self, statement):
        return statement[0].value.startswith('*')


class SettingSectionHeaderLexer(SectionHeaderLexer):
    token_type = Token.SETTING_HEADER


class VariableSectionHeaderLexer(SectionHeaderLexer):
    token_type = Token.VARIABLE_HEADER


class TestCaseSectionHeaderLexer(SectionHeaderLexer):
    token_type = Token.TESTCASE_HEADER


class KeywordSectionHeaderLexer(SectionHeaderLexer):
    token_type = Token.KEYWORD_HEADER


class CommentSectionHeaderLexer(SectionHeaderLexer):
    token_type = Token.COMMENT_HEADER


class ErrorSectionHeaderLexer(SectionHeaderLexer):

    def lex(self):
        self.ctx.lex_invalid_section(self.statement)


class CommentLexer(SingleType):
    token_type = Token.COMMENT


class SettingLexer(StatementLexer):

    def lex(self):
        self.ctx.lex_setting(self.statement)


class TestOrKeywordSettingLexer(SettingLexer):

    def handles(self, statement):
        marker = statement[0].value
        return marker and marker[0] == '[' and marker[-1] == ']'


class VariableLexer(TypeAndArguments):
    token_type = Token.VARIABLE


class KeywordCallLexer(StatementLexer):

    def lex(self):
        if self.ctx.template_set:
            self._lex_as_template()
        else:
            self._lex_as_keyword_call()

    def _lex_as_template(self):
        for token in self.statement:
            token.type = Token.ARGUMENT

    def _lex_as_keyword_call(self):
        keyword_seen = False
        for token in self.statement:
            if keyword_seen:
                token.type = Token.ARGUMENT
            elif is_assign(token.value, allow_assign_mark=True):
                token.type = Token.ASSIGN
            else:
                token.type = Token.KEYWORD
                keyword_seen = True


class ForHeaderLexer(StatementLexer):
    separators = ('IN', 'IN RANGE', 'IN ENUMERATE', 'IN ZIP')

    def handles(self, statement):
        return statement[0].value == 'FOR'

    def lex(self):
        self.statement[0].type = Token.FOR
        separator_seen = False
        for token in self.statement[1:]:
            if separator_seen:
                token.type = Token.ARGUMENT
            elif normalize_whitespace(token.value) in self.separators:
                token.type = Token.FOR_SEPARATOR
                separator_seen = True
            else:
                token.type = Token.VARIABLE


class IfHeaderLexer(TypeAndArguments):
    token_type = Token.IF

    def handles(self, statement):
        return statement[0].value == 'IF' and len(statement) <= 2


class InlineIfHeaderLexer(StatementLexer):
    token_type = Token.INLINE_IF

    def handles(self, statement):
        for token in statement:
            if token.value == 'IF':
                return True
            if not is_assign(token.value, allow_assign_mark=True):
                return False
        return False

    def lex(self):
        if_seen = False
        for token in self.statement:
            if if_seen:
                token.type = Token.ARGUMENT
            elif token.value == 'IF':
                token.type = Token.INLINE_IF
                if_seen = True
            else:
                token.type = Token.ASSIGN


class ElseIfHeaderLexer(TypeAndArguments):
    token_type = Token.ELSE_IF

    def handles(self, statement):
        return normalize_whitespace(statement[0].value) == 'ELSE IF'


class ElseHeaderLexer(TypeAndArguments):
    token_type = Token.ELSE

    def handles(self, statement):
        return statement[0].value == 'ELSE'


class TryHeaderLexer(TypeAndArguments):
    token_type = Token.TRY

    def handles(self, statement):
        return statement[0].value == 'TRY'


class ExceptHeaderLexer(StatementLexer):
    token_type = Token.EXCEPT

    def handles(self, statement):
        return statement[0].value == 'EXCEPT'

    def lex(self):
        self.statement[0].type = Token.EXCEPT
        last_pattern = None
        as_seen = False
        for token in self.statement[1:]:
            if token.value == 'AS':
                token.type = Token.AS
                as_seen = True
            elif as_seen:
                token.type = Token.VARIABLE
            else:
                token.type = Token.ARGUMENT
                last_pattern = token
        if last_pattern and last_pattern.value.startswith('type='):
            last_pattern.type = Token.OPTION


class FinallyHeaderLexer(TypeAndArguments):
    token_type = Token.FINALLY

    def handles(self, statement):
        return statement[0].value == 'FINALLY'


class WhileHeaderLexer(StatementLexer):
    token_type = Token.WHILE

    def handles(self, statement):
        return statement[0].value == 'WHILE'

    def lex(self):
        self.statement[0].type = Token.WHILE
        for token in self.statement[1:]:
            token.type = Token.ARGUMENT
        if self.statement[-1].value.startswith('limit='):
            self.statement[-1].type = Token.OPTION


class EndLexer(TypeAndArguments):
    token_type = Token.END

    def handles(self, statement):
        return statement[0].value == 'END'


class ReturnLexer(TypeAndArguments):
    token_type = Token.RETURN_STATEMENT

    def handles(self, statement):
        return statement[0].value == 'RETURN'


class ContinueLexer(TypeAndArguments):
    token_type = Token.CONTINUE

    def handles(self, statement):
        return statement[0].value == 'CONTINUE'


class BreakLexer(TypeAndArguments):
    token_type = Token.BREAK

    def handles(self, statement):
        return statement[0].value == 'BREAK'
