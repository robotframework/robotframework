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
from itertools import dropwhile, takewhile

from robot.utils import normalize_whitespace

from ..lexer import Token


def get_statements(tokens, curdir=None):
    statement = []
    for t in tokens:
        if curdir and '${CURDIR}' in t.value:
            t.value = t.value.replace('${CURDIR}', curdir)
        if t.type != t.EOS:
            statement.append(t)
        else:
            yield Statement.from_tokens(statement)
            statement = []


class Statement(ast.AST):
    type = None
    _fields = ('type', 'tokens')

    def __init__(self, tokens):
        self.tokens = tokens

    @classmethod
    def from_tokens(cls, tokens):
        type = cls._get_type(tokens)
        for sub in cls.__subclasses__():
            if sub.type == type:
                return sub(tokens)
            try:
                return sub.from_tokens(tokens)
            except TypeError:
                pass
        raise TypeError("Invalid statement type '%s'." % type)

    @staticmethod
    def _get_type(statement):
        if len(statement) == 1 and statement[0].type == Token.EOL:
            return Token.EOL
        for token in statement:
            if token.type == Token.ASSIGN:
                return Token.KEYWORD
            if token.type not in (Token.SEPARATOR, Token.OLD_FOR_INDENT,
                                  Token.CONTINUATION, Token.EOL):
                return token.type

    @property
    def data_tokens(self):
        return [t for t in self.tokens if t.type not in Token.NON_DATA_TOKENS]

    def _value(self, type):
        for t in self.tokens:
            if t.type == type:
                return t.value
        return None

    def _values(self, *types):
        return [t.value for t in self.tokens if t.type in types]

    def _tokens(self, *types):
        return [t for t in self.tokens if t.type in types]

    @property
    def lines(self):
        if self.type in Token.SETTING_TOKENS and len(self.tokens) == 1:
            return
        line = []
        for token in self.tokens:
            if token.type != Token.CONTINUATION:
                line.append(token)
            else:
                yield line
                line = [token]
        if line:
            yield line

    def __len__(self):
        return len(self.tokens)

    def __getitem__(self, item):
        return self.tokens[item]


class DocumentationOrMetadata(Statement):

    def _join_value(self, tokens):
        def lines_with_newlines():
            lines = self._get_lines(tokens)
            last_index = len(lines) - 1
            for index, line in enumerate(lines):
                yield line
                if index < last_index:
                    match = re.search(r'(\\+)n?$', line)
                    escaped_or_has_newline = match and len(match.group(1)) % 2 == 1
                    if not escaped_or_has_newline:
                        yield '\n'
        return ''.join(lines_with_newlines())

    def _get_lines(self, tokens):
        lines = []
        line = []
        for t in tokens:
            if t.type == Token.EOL:
                lines.append(' '.join(line))
                line = []
            else:
                line.append(t.value)
        if line:
            lines.append(' '.join(line))
        return list(dropwhile(lambda l: not l, lines))


class SingleValue(Statement):

    @property
    def value(self):
        values = self._values(Token.ARGUMENT)
        if values and values[0].upper() != 'NONE':
            return values[0]
        return None


class MultiValue(Statement):

    @property
    def values(self):
        return tuple(self._values(Token.ARGUMENT))


class Fixture(Statement):

    @property
    def name(self):
        return self._value(Token.ARGUMENT)

    @property
    def args(self):
        return tuple(self._values(Token.ARGUMENT)[1:])


class SettingSectionHeader(Statement):
    type = Token.SETTING_HEADER


class VariableSectionHeader(Statement):
    type = Token.VARIABLE_HEADER


class TestCaseSectionHeader(Statement):
    type = Token.TESTCASE_HEADER


class KeywordSectionHeader(Statement):
    type = Token.KEYWORD_HEADER


class CommentSectionHeader(Statement):
    type = Token.COMMENT_HEADER


class LibraryImport(Statement):
    type = Token.LIBRARY

    @property
    def name(self):
        return self._value(Token.ARGUMENT)

    @property
    def args(self):
        return self._get_args_and_alias()[0]

    @property
    def alias(self):
        return self._get_args_and_alias()[1]

    def _get_args_and_alias(self):
        args = tuple(self._values(Token.ARGUMENT)[1:])
        if len(args) > 1 and normalize_whitespace(args[-2]) == 'WITH NAME':
            return args[:-2], args[-1]
        return args, None


class ResourceImport(Statement):
    type = Token.RESOURCE

    @property
    def name(self):
        return self._value(Token.ARGUMENT)


class VariablesImport(Statement):
    type = Token.VARIABLES

    @property
    def name(self):
        return self._value(Token.ARGUMENT)

    @property
    def args(self):
        return self._values(Token.ARGUMENT)[1:]


class Documentation(DocumentationOrMetadata):
    type = Token.DOCUMENTATION

    @property
    def value(self):
        tokens = self._tokens(Token.ARGUMENT, Token.EOL)
        return self._join_value(tokens)


class Metadata(DocumentationOrMetadata):
    type = Token.METADATA

    @property
    def name(self):
        return self._value(Token.ARGUMENT)

    @property
    def value(self):
        tokens = self._tokens(Token.ARGUMENT, Token.EOL)[1:]
        return self._join_value(tokens)


class ForceTags(MultiValue):
    type = Token.FORCE_TAGS


class DefaultTags(MultiValue):
    type = Token.DEFAULT_TAGS


class SuiteSetup(Fixture):
    type = Token.SUITE_SETUP


class SuiteTeardown(Fixture):
    type = Token.SUITE_TEARDOWN


class TestSetup(Fixture):
    type = Token.TEST_SETUP


class TestTeardown(Fixture):
    type = Token.TEST_TEARDOWN


class TestTemplate(SingleValue):
    type = Token.TEST_TEMPLATE


class TestTimeout(SingleValue):
    type = Token.TEST_TIMEOUT


class Variable(Statement):
    type = Token.VARIABLE

    @property
    def name(self):
        name = self._value(Token.VARIABLE)
        if name.endswith('='):
            return name[:-1].rstrip()
        return name

    @property
    def value(self):
        return self._values(Token.ARGUMENT)


class Name(Statement):
    type = Token.NAME

    @property
    def name(self):
        return self._value(Token.NAME)


class Setup(Fixture):
    type = Token.SETUP


class Teardown(Fixture):
    type = Token.TEARDOWN


class Tags(MultiValue):
    type = Token.TAGS


class Template(SingleValue):
    type = Token.TEMPLATE


class Timeout(SingleValue):
    type = Token.TIMEOUT


class Arguments(MultiValue):
    type = Token.ARGUMENTS


class Return(MultiValue):
    type = Token.RETURN


class KeywordCall(Statement):
    type = Token.KEYWORD

    @property
    def keyword(self):
        return self._value(Token.KEYWORD)

    @property
    def args(self):
        return tuple(self._values(Token.ARGUMENT))

    @property
    def assign(self):
        return tuple(self._values(Token.ASSIGN))


class TemplateArguments(Statement):
    type = Token.ARGUMENT

    @property
    def args(self):
        return self._values(self.type)


class ForLoopHeader(Statement):
    type = Token.FOR

    @property
    def variables(self):
        data = self.data_tokens[1:]
        return tuple(t.value for t in
                     takewhile(lambda t: t.type != Token.FOR_SEPARATOR, data))

    @property
    def values(self):
        data = self.data_tokens[1:]
        return tuple(t.value for t in
                     dropwhile(lambda t: t.type != Token.FOR_SEPARATOR, data))[1:]

    @property
    def flavor(self):
        value = self._value(Token.FOR_SEPARATOR)
        return normalize_whitespace(value) if value is not None else None

    @property
    def _header(self):
        return self.data_tokens[0].value


class End(Statement):
    type = Token.END

    @property
    def value(self):
        return self.data_tokens[0].value


class Comment(Statement):
    type = Token.COMMENT


class EmptyLine(Statement):
    type = Token.EOL


class Error(Statement):
    type = Token.ERROR

    @property
    def error(self):
        return self.data_tokens[0].error
