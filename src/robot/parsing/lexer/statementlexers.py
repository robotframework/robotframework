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

from abc import ABC, abstractmethod

from robot.errors import DataError
from robot.utils import normalize_whitespace
from robot.variables import is_assign

from .context import FileContext, KeywordContext, LexingContext, TestCaseContext
from .tokens import StatementTokens, Token


class Lexer(ABC):

    def __init__(self, ctx: LexingContext):
        self.ctx = ctx

    def handles(self, statement: StatementTokens) -> bool:
        return True

    @abstractmethod
    def accepts_more(self, statement: StatementTokens) -> bool:
        raise NotImplementedError

    @abstractmethod
    def input(self, statement: StatementTokens):
        raise NotImplementedError

    @abstractmethod
    def lex(self):
        raise NotImplementedError


class StatementLexer(Lexer, ABC):
    token_type: str

    def __init__(self, ctx: LexingContext):
        super().__init__(ctx)
        self.statement: StatementTokens = []

    def accepts_more(self, statement: StatementTokens) -> bool:
        return False

    def input(self, statement: StatementTokens):
        self.statement = statement

    @abstractmethod
    def lex(self):
        raise NotImplementedError

    def _lex_options(self, *names: str, end_index: "int|None" = None):
        seen = set()
        for token in reversed(self.statement[:end_index]):
            if "=" in token.value:
                name = token.value.split("=")[0]
                if name in names and name not in seen:
                    token.type = Token.OPTION
                    seen.add(name)
                    continue
            break


class SingleType(StatementLexer, ABC):

    def lex(self):
        for token in self.statement:
            token.type = self.token_type


class TypeAndArguments(StatementLexer, ABC):

    def lex(self):
        self.statement[0].type = self.token_type
        for token in self.statement[1:]:
            token.type = Token.ARGUMENT


class SectionHeaderLexer(SingleType, ABC):
    ctx: FileContext

    def handles(self, statement: StatementTokens) -> bool:
        return statement[0].value.startswith("*")


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

    def input(self, statement: StatementTokens):
        super().input(statement)
        if statement[0].value.lower().startswith("language:"):
            value = " ".join(token.value for token in statement)
            lang = value.split(":", 1)[1].strip()
            try:
                self.ctx.add_language(lang)
            except DataError:
                for token in statement:
                    token.set_error(
                        f"Invalid language configuration: Language '{lang}' "
                        f"not found nor importable as a language module."
                    )
            else:
                for token in statement:
                    token.type = Token.CONFIG

    def lex(self):
        for token in self.statement:
            if not token.type:
                token.type = self.token_type


class SettingLexer(StatementLexer):
    ctx: FileContext

    def lex(self):
        self.ctx.lex_setting(self.statement)


class TestCaseSettingLexer(StatementLexer):
    ctx: TestCaseContext

    def lex(self):
        self.ctx.lex_setting(self.statement)

    def handles(self, statement: StatementTokens) -> bool:
        marker = statement[0].value
        return bool(marker and marker[0] == "[" and marker[-1] == "]")


class KeywordSettingLexer(StatementLexer):
    ctx: KeywordContext

    def lex(self):
        self.ctx.lex_setting(self.statement)

    def handles(self, statement: StatementTokens) -> bool:
        marker = statement[0].value
        return bool(marker and marker[0] == "[" and marker[-1] == "]")


class VariableLexer(TypeAndArguments):
    ctx: FileContext
    token_type = Token.VARIABLE

    def lex(self):
        super().lex()
        if self.statement[0].value[:1] == "$":
            self._lex_options("separator")


class KeywordCallLexer(StatementLexer):
    ctx: "TestCaseContext|KeywordContext"

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
            elif is_assign(
                token.value, allow_assign_mark=True, allow_nested=True, allow_items=True
            ):
                token.type = Token.ASSIGN
            else:
                token.type = Token.KEYWORD
                keyword_seen = True


class ForHeaderLexer(StatementLexer):
    separators = ("IN", "IN RANGE", "IN ENUMERATE", "IN ZIP")

    def handles(self, statement: StatementTokens) -> bool:
        return statement[0].value == "FOR"

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
        if separator == "IN ENUMERATE":
            self._lex_options("start")
        elif separator == "IN ZIP":
            self._lex_options("mode", "fill")


class IfHeaderLexer(TypeAndArguments):
    token_type = Token.IF

    def handles(self, statement: StatementTokens) -> bool:
        return statement[0].value == "IF" and len(statement) <= 2


class InlineIfHeaderLexer(StatementLexer):
    token_type = Token.INLINE_IF

    def handles(self, statement: StatementTokens) -> bool:
        for token in statement:
            if token.value == "IF":
                return True
            if not is_assign(
                token.value, allow_assign_mark=True, allow_nested=True, allow_items=True
            ):
                return False
        return False

    def lex(self):
        if_seen = False
        for token in self.statement:
            if if_seen:
                token.type = Token.ARGUMENT
            elif token.value == "IF":
                token.type = Token.INLINE_IF
                if_seen = True
            else:
                token.type = Token.ASSIGN


class ElseIfHeaderLexer(TypeAndArguments):
    token_type = Token.ELSE_IF

    def handles(self, statement: StatementTokens) -> bool:
        return normalize_whitespace(statement[0].value) == "ELSE IF"


class ElseHeaderLexer(TypeAndArguments):
    token_type = Token.ELSE

    def handles(self, statement: StatementTokens) -> bool:
        return statement[0].value == "ELSE"


class TryHeaderLexer(TypeAndArguments):
    token_type = Token.TRY

    def handles(self, statement: StatementTokens) -> bool:
        return statement[0].value == "TRY"


class ExceptHeaderLexer(StatementLexer):
    token_type = Token.EXCEPT

    def handles(self, statement: StatementTokens) -> bool:
        return statement[0].value == "EXCEPT"

    def lex(self):
        self.statement[0].type = Token.EXCEPT
        as_index: "int|None" = None
        for index, token in enumerate(self.statement[1:], start=1):
            if token.value == "AS":
                token.type = Token.AS
                as_index = index
            elif as_index:
                token.type = Token.VARIABLE
            else:
                token.type = Token.ARGUMENT
        self._lex_options("type", end_index=as_index)


class FinallyHeaderLexer(TypeAndArguments):
    token_type = Token.FINALLY

    def handles(self, statement: StatementTokens) -> bool:
        return statement[0].value == "FINALLY"


class WhileHeaderLexer(StatementLexer):
    token_type = Token.WHILE

    def handles(self, statement: StatementTokens) -> bool:
        return statement[0].value == "WHILE"

    def lex(self):
        self.statement[0].type = Token.WHILE
        for token in self.statement[1:]:
            token.type = Token.ARGUMENT
        self._lex_options("limit", "on_limit", "on_limit_message")


class GroupHeaderLexer(TypeAndArguments):
    token_type = Token.GROUP

    def handles(self, statement: StatementTokens) -> bool:
        return statement[0].value == "GROUP"


class EndLexer(TypeAndArguments):
    token_type = Token.END

    def handles(self, statement: StatementTokens) -> bool:
        return statement[0].value == "END"


class VarLexer(StatementLexer):
    token_type = Token.VAR

    def handles(self, statement: StatementTokens) -> bool:
        return statement[0].value == "VAR"

    def lex(self):
        self.statement[0].type = Token.VAR
        if len(self.statement) > 1:
            name, *values = self.statement[1:]
            name.type = Token.VARIABLE
            for value in values:
                value.type = Token.ARGUMENT
            options = ["scope", "separator"] if name.value[:1] == "$" else ["scope"]
            self._lex_options(*options)


class ReturnLexer(TypeAndArguments):
    token_type = Token.RETURN_STATEMENT

    def handles(self, statement: StatementTokens) -> bool:
        return statement[0].value == "RETURN"


class ContinueLexer(TypeAndArguments):
    token_type = Token.CONTINUE

    def handles(self, statement: StatementTokens) -> bool:
        return statement[0].value == "CONTINUE"


class BreakLexer(TypeAndArguments):
    token_type = Token.BREAK

    def handles(self, statement: StatementTokens) -> bool:
        return statement[0].value == "BREAK"


class SyntaxErrorLexer(TypeAndArguments):
    token_type = Token.ERROR

    def handles(self, statement: StatementTokens) -> bool:
        return statement[0].value in {
            "ELSE",
            "ELSE IF",
            "EXCEPT",
            "FINALLY",
            "BREAK",
            "CONTINUE",
            "RETURN",
            "END",
        }

    def lex(self):
        token = self.statement[0]
        token.set_error(f"{token.value} is not allowed in this context.")
        for t in self.statement[1:]:
            t.type = Token.ARGUMENT
