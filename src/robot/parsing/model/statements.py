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

import ast
import re

from robot.utils import normalize_whitespace

from ..lexer import Token


class Statement(ast.AST):
    type = None
    _fields = ('type', 'tokens')
    _attributes = ('lineno', 'col_offset', 'end_lineno', 'end_col_offset')
    _statement_handlers = {}

    def __init__(self, tokens):
        self.tokens = tuple(tokens)

    @property
    def lineno(self):
        return self.tokens[0].lineno if self.tokens else -1

    @property
    def col_offset(self):
        return self.tokens[0].col_offset if self.tokens else -1

    @property
    def end_lineno(self):
        return self.tokens[-1].lineno if self.tokens else -1

    @property
    def end_col_offset(self):
        return self.tokens[-1].end_col_offset if self.tokens else -1

    @classmethod
    def register(cls, subcls):
        cls._statement_handlers[subcls.type] = subcls
        if subcls.type == Token.KEYWORD:
            cls._statement_handlers[Token.ASSIGN] = subcls
        if subcls.type == Token.ERROR:
            cls._statement_handlers[Token.FATAL_ERROR] = subcls
        return subcls

    @classmethod
    def from_tokens(cls, tokens):
        handlers = cls._statement_handlers
        for token in tokens:
            if token.type in handlers:
                return handlers[token.type](tokens)
        return EmptyLine(tokens)

    @property
    def data_tokens(self):
        return [t for t in self.tokens if t.type not in Token.NON_DATA_TOKENS]

    def get_token(self, type):
        """Return a token with the given ``type``.

        If there are no matches, return ``None``. If there are multiple
        matches, return the first match.
        """
        for t in self.tokens:
            if t.type == type:
                return t
        return None

    def get_tokens(self, *types):
        """Return tokens having any of the given ``types``."""
        return [t for t in self.tokens if t.type in types]

    def get_value(self, type, default=None):
        """Return value of a token with the given ``type``.

        If there are no matches, return ``default``. If there are multiple
        matches, return the value of the first match.
        """
        token = self.get_token(type)
        return token.value if token else default

    def get_values(self, *types):
        """Return values of tokens having any of the given ``types``."""
        return tuple(t.value for t in self.tokens if t.type in types)

    @property
    def lines(self):
        line = []
        for token in self.tokens:
            line.append(token)
            if token.type == Token.EOL:
                yield line
                line = []
        if line:
            yield line

    @property
    def error(self):
        tokens = self.get_tokens(Token.ERROR, Token.FATAL_ERROR)
        if not tokens:
            return None
        if len(tokens) == 1:
            return tokens[0].error
        errors = ['%d) %s' % (i+1, t.error) for i, t in enumerate(tokens)]
        return '\n\n'.join(['Multiple errors:'] + errors)

    def __len__(self):
        return len(self.tokens)

    def __getitem__(self, item):
        return self.tokens[item]


class DocumentationOrMetadata(Statement):

    def _join_value(self, tokens):
        lines = self._get_lines(tokens)
        return ''.join(self._yield_lines_with_newlines(lines))

    def _get_lines(self, tokens):
        lines = []
        line = None
        lineno = -1
        for t in tokens:
            if t.lineno != lineno:
                line = []
                lines.append(line)
            line.append(t.value)
            lineno = t.lineno
        return [' '.join(line) for line in lines]

    def _yield_lines_with_newlines(self, lines):
        last_index = len(lines) - 1
        for index, line in enumerate(lines):
            yield line
            if index < last_index and not self._escaped_or_has_newline(line):
                yield '\n'

    def _escaped_or_has_newline(self, line):
        match = re.search(r'(\\+)n?$', line)
        return match and len(match.group(1)) % 2 == 1


class SingleValue(Statement):

    @property
    def value(self):
        values = self.get_values(Token.NAME, Token.ARGUMENT)
        if values and values[0].upper() != 'NONE':
            return values[0]
        return None


class MultiValue(Statement):

    @property
    def values(self):
        return self.get_values(Token.ARGUMENT)


class Fixture(Statement):

    @property
    def name(self):
        return self.get_value(Token.NAME)

    @property
    def args(self):
        return self.get_values(Token.ARGUMENT)


class SectionHeader(Statement):

    @property
    def name(self):
        header = self.get_token(self.type)
        return normalize_whitespace(header.value).strip('* ')


@Statement.register
class SettingSectionHeader(SectionHeader):
    type = Token.SETTING_HEADER


@Statement.register
class VariableSectionHeader(SectionHeader):
    type = Token.VARIABLE_HEADER


@Statement.register
class TestCaseSectionHeader(SectionHeader):
    type = Token.TESTCASE_HEADER


@Statement.register
class KeywordSectionHeader(SectionHeader):
    type = Token.KEYWORD_HEADER


@Statement.register
class CommentSectionHeader(SectionHeader):
    type = Token.COMMENT_HEADER


@Statement.register
class LibraryImport(Statement):
    type = Token.LIBRARY

    @property
    def name(self):
        return self.get_value(Token.NAME)

    @property
    def args(self):
        return self.get_values(Token.ARGUMENT)

    @property
    def alias(self):
        with_name = self.get_token(Token.WITH_NAME)
        return self.get_tokens(Token.NAME)[-1].value if with_name else None


@Statement.register
class ResourceImport(Statement):
    type = Token.RESOURCE

    @property
    def name(self):
        return self.get_value(Token.NAME)


@Statement.register
class VariablesImport(Statement):
    type = Token.VARIABLES

    @property
    def name(self):
        return self.get_value(Token.NAME)

    @property
    def args(self):
        return self.get_values(Token.ARGUMENT)


@Statement.register
class Documentation(DocumentationOrMetadata):
    type = Token.DOCUMENTATION

    @property
    def value(self):
        tokens = self.get_tokens(Token.ARGUMENT)
        return self._join_value(tokens)


@Statement.register
class Metadata(DocumentationOrMetadata):
    type = Token.METADATA

    @property
    def name(self):
        return self.get_value(Token.NAME)

    @property
    def value(self):
        tokens = self.get_tokens(Token.ARGUMENT)
        return self._join_value(tokens)


@Statement.register
class ForceTags(MultiValue):
    type = Token.FORCE_TAGS


@Statement.register
class DefaultTags(MultiValue):
    type = Token.DEFAULT_TAGS


@Statement.register
class SuiteSetup(Fixture):
    type = Token.SUITE_SETUP


@Statement.register
class SuiteTeardown(Fixture):
    type = Token.SUITE_TEARDOWN


@Statement.register
class TestSetup(Fixture):
    type = Token.TEST_SETUP


@Statement.register
class TestTeardown(Fixture):
    type = Token.TEST_TEARDOWN


@Statement.register
class TestTemplate(SingleValue):
    type = Token.TEST_TEMPLATE


@Statement.register
class TestTimeout(SingleValue):
    type = Token.TEST_TIMEOUT


@Statement.register
class Variable(Statement):
    type = Token.VARIABLE

    @property
    def name(self):
        name = self.get_value(Token.VARIABLE)
        if name.endswith('='):
            return name[:-1].rstrip()
        return name

    @property
    def value(self):
        return self.get_values(Token.ARGUMENT)


@Statement.register
class TestCaseName(Statement):
    type = Token.TESTCASE_NAME

    @property
    def name(self):
        return self.get_value(Token.TESTCASE_NAME)


@Statement.register
class KeywordName(Statement):
    type = Token.KEYWORD_NAME

    @property
    def name(self):
        return self.get_value(Token.KEYWORD_NAME)


@Statement.register
class Setup(Fixture):
    type = Token.SETUP


@Statement.register
class Teardown(Fixture):
    type = Token.TEARDOWN


@Statement.register
class Tags(MultiValue):
    type = Token.TAGS


@Statement.register
class Template(SingleValue):
    type = Token.TEMPLATE


@Statement.register
class Timeout(SingleValue):
    type = Token.TIMEOUT


@Statement.register
class Arguments(MultiValue):
    type = Token.ARGUMENTS


@Statement.register
class Return(MultiValue):
    type = Token.RETURN


@Statement.register
class KeywordCall(Statement):
    type = Token.KEYWORD

    @property
    def keyword(self):
        return self.get_value(Token.KEYWORD)

    @property
    def args(self):
        return self.get_values(Token.ARGUMENT)

    @property
    def assign(self):
        return self.get_values(Token.ASSIGN)


@Statement.register
class TemplateArguments(Statement):
    type = Token.ARGUMENT

    @property
    def args(self):
        return self.get_values(self.type)


@Statement.register
class ForLoopHeader(Statement):
    type = Token.FOR

    @property
    def variables(self):
        return self.get_values(Token.VARIABLE)

    @property
    def values(self):
        return self.get_values(Token.ARGUMENT)

    @property
    def flavor(self):
        separator = self.get_token(Token.FOR_SEPARATOR)
        return normalize_whitespace(separator.value) if separator else None

    @property
    def _header(self):
        return self.get_value(Token.FOR)


@Statement.register
class End(Statement):
    type = Token.END

    @property
    def value(self):
        return self.get_value(Token.END)


@Statement.register
class Comment(Statement):
    type = Token.COMMENT


@Statement.register
class Error(Statement):
    type = Token.ERROR


class EmptyLine(Statement):
    type = Token.EOL

    @classmethod
    def from_value(cls, value):
        return EmptyLine([Token(Token.EOL, value)])
