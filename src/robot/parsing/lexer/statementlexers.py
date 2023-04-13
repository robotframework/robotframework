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
from robot.utils import normalize_whitespace
from robot.variables import is_assign

from .context import FileContext, LexingContext, TestOrKeywordContext
from .tokens import Token


class Lexer:
    """Base class for lexers."""

    def __init__(self, ctx: LexingContext):
        self.ctx = ctx

    @classmethod
    def handles(cls, statement: list, ctx: LexingContext):
        return True

    def accepts_more(self, statement: list):
        raise NotImplementedError

    def input(self, statement: list):
        raise NotImplementedError

    def lex(self):
        raise NotImplementedError


class StatementLexer(Lexer):
    token_type = None

    def __init__(self, ctx: FileContext):
        super().__init__(ctx)
        self.statement = None

    def accepts_more(self, statement: list):
        return False

    def input(self, statement: list):
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
    ctx: FileContext

    @classmethod
    def handles(cls, statement: list, ctx: FileContext):
        return statement[0].value.startswith('*')


class SettingSectionHeaderLexer(SectionHeaderLexer):
    token_type = Token.SETTING_HEADER


class VariableSectionHeaderLexer(SectionHeaderLexer):
    token_type = Token.VARIABLE_HEADER


class TestCaseSectionHeaderLexer(SectionHeaderLexer):
    token_type = Token.TESTCASE_HEADER


class TaskSectionHeaderLexer(SectionHeaderLexer):
    token_type = Token.TASK_HEADER


class KeywordSectionHeaderLexer(SectionHeaderLexer):
    token_type = Token.KEYWORD_HEADER


class CommentSectionHeaderLexer(SectionHeaderLexer):
    token_type = Token.COMMENT_HEADER


class InvalidSectionHeaderLexer(SectionHeaderLexer):
    token_type = Token.INVALID_HEADER

    def lex(self):
        self.ctx.lex_invalid_section(self.statement)


class CommentLexer(SingleType):
    token_type = Token.COMMENT


class ImplicitCommentLexer(CommentLexer):
    ctx: FileContext

    def input(self, statement: list):
        super().input(statement)
        if len(statement) == 1 and statement[0].value.lower().startswith('language:'):
            lang = statement[0].value.split(':', 1)[1].strip()
            try:
                self.ctx.add_language(lang)
            except DataError:
                statement[0].set_error(
                    f"Invalid language configuration: "
                    f"Language '{lang}' not found nor importable as a language module."
                )
            else:
                statement[0].type = Token.CONFIG

    def lex(self):
        for token in self.statement:
            if not token.type:
                token.type = self.token_type


class SettingLexer(StatementLexer):

    def lex(self):
        self.ctx.lex_setting(self.statement)


class TestOrKeywordSettingLexer(SettingLexer):

    @classmethod
    def handles(cls, statement: list, ctx: TestOrKeywordContext):
        marker = statement[0].value
        return marker and marker[0] == '[' and marker[-1] == ']'


class VariableLexer(TypeAndArguments):
    token_type = Token.VARIABLE


class KeywordCallLexer(StatementLexer):
    ctx: TestOrKeywordContext

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

    @classmethod
    def handles(cls, statement: list, ctx: TestOrKeywordContext):
        return statement[0].value == 'FOR'

    def lex(self):
        self.statement[0].type = Token.FOR
        separator = None
        for token in self.statement[1:]:
            if separator:
                token.type = Token.ARGUMENT
            elif normalize_whitespace(token.value) in self.separators:
                token.type = Token.FOR_SEPARATOR
                separator = normalize_whitespace(token.value)
            else:
                token.type = Token.VARIABLE
        if (separator == 'IN ENUMERATE'
                and self.statement[-1].value.startswith('start=')):
            self.statement[-1].type = Token.OPTION
        elif separator == 'IN ZIP':
            for token in reversed(self.statement):
                if not token.value.startswith(('mode=', 'fill=')):
                    break
                token.type = Token.OPTION


class IfHeaderLexer(TypeAndArguments):
    token_type = Token.IF

    @classmethod
    def handles(cls, statement: list, ctx: TestOrKeywordContext):
        return statement[0].value == 'IF' and len(statement) <= 2


class InlineIfHeaderLexer(StatementLexer):
    token_type = Token.INLINE_IF

    @classmethod
    def handles(cls, statement: list, ctx: TestOrKeywordContext):
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

    @classmethod
    def handles(cls, statement: list, ctx: TestOrKeywordContext):
        return normalize_whitespace(statement[0].value) == 'ELSE IF'


class ElseHeaderLexer(TypeAndArguments):
    token_type = Token.ELSE

    @classmethod
    def handles(cls, statement: list, ctx: TestOrKeywordContext):
        return statement[0].value == 'ELSE'


class TryHeaderLexer(TypeAndArguments):
    token_type = Token.TRY

    @classmethod
    def handles(cls, statement: list, ctx: TestOrKeywordContext):
        return statement[0].value == 'TRY'


class ExceptHeaderLexer(StatementLexer):
    token_type = Token.EXCEPT

    @classmethod
    def handles(cls, statement: list, ctx: TestOrKeywordContext):
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

    @classmethod
    def handles(cls, statement: list, ctx: TestOrKeywordContext):
        return statement[0].value == 'FINALLY'


class WhileHeaderLexer(StatementLexer):
    token_type = Token.WHILE

    @classmethod
    def handles(cls, statement: list, ctx: TestOrKeywordContext):
        return statement[0].value == 'WHILE'

    def lex(self):
        self.statement[0].type = Token.WHILE
        for token in self.statement[1:]:
            token.type = Token.ARGUMENT
        for token in reversed(self.statement):
            if not token.value.startswith(('limit=', 'on_limit=',
                                           'on_limit_message=')):
                break
            token.type = Token.OPTION


class EndLexer(TypeAndArguments):
    token_type = Token.END

    @classmethod
    def handles(cls, statement: list, ctx: TestOrKeywordContext):
        return statement[0].value == 'END'


class ReturnLexer(TypeAndArguments):
    token_type = Token.RETURN_STATEMENT

    @classmethod
    def handles(cls, statement: list, ctx: TestOrKeywordContext):
        return statement[0].value == 'RETURN'


class ContinueLexer(TypeAndArguments):
    token_type = Token.CONTINUE

    @classmethod
    def handles(cls, statement: list, ctx: TestOrKeywordContext):
        return statement[0].value == 'CONTINUE'


class BreakLexer(TypeAndArguments):
    token_type = Token.BREAK

    @classmethod
    def handles(cls, statement: list, ctx: TestOrKeywordContext):
        return statement[0].value == 'BREAK'


class SyntaxErrorLexer(TypeAndArguments):
    token_type = Token.ERROR

    @classmethod
    def handles(cls, statement: list, ctx: TestOrKeywordContext):
        return statement[0].value in {'ELSE', 'ELSE IF', 'EXCEPT', 'FINALLY',
                                      'BREAK', 'CONTINUE', 'RETURN', 'END'}

    def lex(self):
        token = self.statement[0]
        token.set_error(f'{token.value} is not allowed in this context.')
        for t in self.statement[1:]:
            t.type = Token.ARGUMENT
