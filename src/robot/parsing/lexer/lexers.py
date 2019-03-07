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

from robot.variables import is_var

from .tokens import Token


class Lexer(object):

    @classmethod
    def handles(cls, statement):
        return True

    def accepts_more(self, statement):
        raise NotImplementedError

    def input(self, statement):
        raise NotImplementedError

    def lex(self, ctx):
        raise NotImplementedError


class StatementLexer(Lexer):
    token_type = None

    def __init__(self, statement=None):
        self.statement = statement

    def accepts_more(self, statement):
        return False

    def input(self, statement):
        self.statement = statement

    def lex(self, ctx):
        for token in self.statement:
            token.type = self.token_type


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
        raise RuntimeError('TODO: %s' % type(self).__name__)

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


class TestCaseFileLexer(BlockLexer):

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
        # TODO: Non-ASCII spaces
        marker = statement[0].value
        return (marker.startswith('*') and
                marker.strip('* ').title() in cls.markers)

    def accepts_more(self, statement):
        return not statement[0].value.startswith('*')


class SectionHeaderLexer(StatementLexer):

    @classmethod
    def handles(cls, statement):
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

    def lex(self, ctx):
        self.statement[0].type = Token.ERROR
        self.statement[0].error = (
            "Unrecognized table header '%s'. Available headers for data: "
            "'Setting(s)', 'Variable(s)', 'Test Case(s)', 'Task(s)' and "
            "'Keyword(s)'. Use 'Comment(s)' to embedded additional data."
            % self.statement[0].value.strip('*').strip()
        )
        for token in self.statement[1:]:
            token.type = Token.COMMENT


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


class CommentLexer(StatementLexer):
    token_type = Token.COMMENT


class ErrorSectionLexer(SectionLexer):

    @classmethod
    def handles(cls, statement):
        return statement[0].value.startswith('*')

    def lexer_classes(self):
        return (ErrorSectionHeaderLexer, CommentLexer)


class SettingSectionLexer(SectionLexer):
    markers = ('Setting', 'Settings')

    def lexer_classes(self):
        return (SettingSectionHeaderLexer, SettingLexer)


class SettingLexer(StatementLexer):

    def lex(self, ctx):
        self.statement[0].type = ctx.tokenize_setting(self.statement)
        for token in self.statement[1:]:
            token.type = Token.ARGUMENT


class VariableSectionLexer(SectionLexer):
    markers = ('Variable', 'Variables')

    def lexer_classes(self):
        return (VariableSectionHeaderLexer, VariableLexer)


class VariableLexer(StatementLexer):

    def lex(self, ctx):
        # TODO: Validation?
        self.statement[0].type = Token.VARIABLE
        for token in self.statement[1:]:
            token.type = Token.ARGUMENT


class TestCaseSectionLexer(SectionLexer):
    markers = ('Test Case', 'Test Cases', 'Task', 'Tasks')

    def lexer_classes(self):
        return (TestCaseSectionHeaderLexer, TestCaseLexer)


class KeywordSectionLexer(SettingSectionLexer):
    markers = ('Keyword', 'Keywords')

    def lexer_classes(self):
        return (KeywordSectionHeaderLexer, KeywordLexer)


class TestOrKeywordLexer(BlockLexer):
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
        # TODO: Use dedicated lexers?
        if not self._name_set:
            statement.pop(0).type = Token.NAME
            self._name_set = True
        while statement and not statement[0].value:
            statement.pop(0).type = Token.IGNORE

    def _handle_old_style_for_loop(self, statement, lexer):
        # TODO: Deprecation
        if isinstance(lexer, ForLoopLexer):
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
        return (TestOrKeywordSettingLexer, ForLoopLexer, EndLexer,
                KeywordCallLexer)


class TestCaseLexer(TestOrKeywordLexer):

    def lex(self, ctx):
        ctx = ctx.test_case_context()
        self._lex_with_priority(ctx, priority=TestOrKeywordSettingLexer)


class KeywordLexer(TestOrKeywordLexer):

    def lex(self, ctx):
        ctx = ctx.keyword_context()
        TestOrKeywordLexer.lex(self, ctx)


class TestOrKeywordSettingLexer(SettingLexer):

    @classmethod
    def handles(cls, statement):
        marker = statement[0].value
        return marker[0] == '[' and marker[-1] == ']'


class ForLoopLexer(StatementLexer):

    @classmethod
    def handles(cls, statement):
        marker = statement[0].value
        return (marker == 'FOR' or
                marker[0] == ':' and marker.lstrip(': ').upper() == 'FOR')

    def lex(self, ctc):
        separator_seen = False
        self.statement[0].type = Token.FOR
        for token in self.statement[1:]:
            if self._is_separator(token.value) and not separator_seen:
                token.type = Token.FOR_SEPARATOR
                separator_seen = True
            else:
                token.type = Token.ARGUMENT

    def _is_separator(self, value):
        return value in ('IN', 'IN RANGE', 'IN ENUMERATE', 'IN ZIP')


class EndLexer(StatementLexer):

    @classmethod
    def handles(cls, statement):
        return len(statement) == 1 and statement[0].value == 'END'

    def lex(self, ctx):
        self.statement[0].type = Token.END


class KeywordCallLexer(StatementLexer):

    def lex(self, ctx):
        if ctx.template_set:
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
            elif self._is_assign(token.value):
                token.type = Token.ASSIGN
            else:
                token.type = Token.KEYWORD
                keyword_seen = True

    def _is_assign(self, value):
        return (is_var(value) or
                value.endswith('=') and is_var(value[:-1].rstrip()))
