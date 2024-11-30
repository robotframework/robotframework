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
import warnings
from abc import ABC, abstractmethod
from collections.abc import Iterator, Sequence
from typing import cast, ClassVar, Literal, overload, TYPE_CHECKING, Type, TypeVar

from robot.conf import Language
from robot.running.arguments import UserKeywordArgumentParser
from robot.utils import normalize_whitespace, seq2str, split_from_equals, test_or_task
from robot.variables import (contains_variable, is_scalar_assign, is_dict_variable,
                             search_variable)

from ..lexer import Token

if TYPE_CHECKING:
    from .blocks import ValidationContext


T = TypeVar('T', bound='Statement')
FOUR_SPACES = '    '
EOL = '\n'


class Node(ast.AST, ABC):
    _attributes = ('lineno', 'col_offset', 'end_lineno', 'end_col_offset', 'errors')
    lineno: int
    col_offset: int
    end_lineno: int
    end_col_offset: int
    errors: 'tuple[str, ...]' = ()


class Statement(Node, ABC):
    _attributes = ('type', 'tokens') + Node._attributes
    type: str
    handles_types: 'ClassVar[tuple[str, ...]]' = ()
    statement_handlers: 'ClassVar[dict[str, Type[Statement]]]' = {}
    # Accepted configuration options. If the value is a tuple, it lists accepted
    # values. If the used value contains a variable, it cannot be validated.
    options: 'dict[str, tuple|None]' = {}

    def __init__(self, tokens: 'Sequence[Token]', errors: 'Sequence[str]' = ()):
        self.tokens = tuple(tokens)
        self.errors = tuple(errors)

    @property
    def lineno(self) -> int:
        return self.tokens[0].lineno if self.tokens else -1

    @property
    def col_offset(self) -> int:
        return self.tokens[0].col_offset if self.tokens else -1

    @property
    def end_lineno(self) -> int:
        return self.tokens[-1].lineno if self.tokens else -1

    @property
    def end_col_offset(self) -> int:
        return self.tokens[-1].end_col_offset if self.tokens else -1

    @classmethod
    def register(cls, subcls: Type[T]) -> Type[T]:
        types = subcls.handles_types or (subcls.type,)
        for typ in types:
            cls.statement_handlers[typ] = subcls
        return subcls

    @classmethod
    def from_tokens(cls, tokens: 'Sequence[Token]') -> 'Statement':
        """Create a statement from given tokens.

        Statement type is got automatically from token types.

        This classmethod should be called from :class:`Statement`, not from
        its subclasses. If you know the subclass to use, simply create an
        instance of it directly.
        """
        handlers = cls.statement_handlers
        for token in tokens:
            if token.type in handlers:
                return handlers[token.type](tokens)
        if any(token.type == Token.ASSIGN for token in tokens):
            return KeywordCall(tokens)
        return EmptyLine(tokens)

    @classmethod
    @abstractmethod
    def from_params(cls, *args, **kwargs) -> 'Statement':
        """Create a statement from passed parameters.

        Required and optional arguments in general match class properties.
        Values are used to create matching tokens.

        Most implementations support following general properties:

        - ``separator`` whitespace inserted between each token. Default is four spaces.
        - ``indent`` whitespace inserted before first token. Default is four spaces.
        - ``eol`` end of line sign. Default is ``'\\n'``.

        This classmethod should be called from the :class:`Statement` subclass
        to create, not from the :class:`Statement` class itself.
        """
        raise NotImplementedError

    @property
    def data_tokens(self) -> 'list[Token]':
        return [t for t in self.tokens if t.type not in Token.NON_DATA_TOKENS]

    def get_token(self, *types: str) -> 'Token|None':
        """Return a token with any of the given ``types``.

        If there are no matches, return ``None``. If there are multiple
        matches, return the first match.
        """
        for token in self.tokens:
            if token.type in types:
                return token
        return None

    def get_tokens(self, *types: str) -> 'list[Token]':
        """Return tokens having any of the given ``types``."""
        return [t for t in self.tokens if t.type in types]

    @overload
    def get_value(self, type: str, default: str) -> str:
        ...

    @overload
    def get_value(self, type: str, default: None = None) -> 'str|None':
        ...

    def get_value(self, type: str, default: 'str|None' = None) -> 'str|None':
        """Return value of a token with the given ``type``.

        If there are no matches, return ``default``. If there are multiple
        matches, return the value of the first match.
        """
        token = self.get_token(type)
        return token.value if token else default

    def get_values(self, *types: str) -> 'tuple[str, ...]':
        """Return values of tokens having any of the given ``types``."""
        return tuple(t.value for t in self.tokens if t.type in types)

    def get_option(self, name: str, default: 'str|None' = None) -> 'str|None':
        """Return value of a configuration option with the given ``name``.

        If the option has not been used, return ``default``.

        If the option has been used multiple times, values are joined together.
        This is typically an error situation and validated elsewhere.

        New in Robot Framework 6.1.
        """
        return self._get_options().get(name, default)

    def _get_options(self) -> 'dict[str, str]':
        return dict(opt.split('=', 1) for opt in self.get_values(Token.OPTION))

    @property
    def lines(self) -> 'Iterator[list[Token]]':
        line = []
        for token in self.tokens:
            line.append(token)
            if token.type == Token.EOL:
                yield line
                line = []
        if line:
            yield line

    def validate(self, ctx: 'ValidationContext'):
        pass

    def _validate_options(self):
        for name, value in self._get_options().items():
            if self.options[name] is not None:
                expected = self.options[name]
                if value.upper() not in expected and not contains_variable(value):
                    self.errors += (f"{self.type} option '{name}' does not accept "
                                    f"value '{value}'. Valid values are "
                                    f"{seq2str(expected)}.",)

    def __iter__(self) -> 'Iterator[Token]':
        return iter(self.tokens)

    def __len__(self) -> int:
        return len(self.tokens)

    def __getitem__(self, item) -> Token:
        return self.tokens[item]

    def __repr__(self) -> str:
        name = type(self).__name__
        tokens = f'tokens={list(self.tokens)}'
        errors = f', errors={list(self.errors)}' if self.errors else ''
        return f'{name}({tokens}{errors})'


class DocumentationOrMetadata(Statement, ABC):

    @property
    def value(self) -> str:
        return ''.join(self._get_lines()).rstrip()

    def _get_lines(self) -> 'Iterator[str]':
        base_offset = -1
        for tokens in self._get_line_tokens():
            yield from self._get_line_values(tokens, base_offset)
            first = tokens[0]
            if base_offset < 0 or 0 < first.col_offset < base_offset and first.value:
                base_offset = first.col_offset

    def _get_line_tokens(self) -> 'Iterator[list[Token]]':
        line: 'list[Token]' = []
        lineno = -1
        # There are no EOLs during execution or if data has been parsed with
        # `data_only=True` otherwise, so we need to look at line numbers to
        # know when lines change. If model is created programmatically using
        # `from_params` or otherwise, line numbers may not be set, but there
        # ought to be EOLs. If both EOLs and line numbers are missing,
        # everything is considered to be on the same line.
        for token in self.get_tokens(Token.ARGUMENT, Token.EOL):
            eol = token.type == Token.EOL
            if token.lineno != lineno or eol:
                if line:
                    yield line
                line = []
            if not eol:
                line.append(token)
            lineno = token.lineno
        if line:
            yield line

    def _get_line_values(self, tokens: 'list[Token]', offset: int) -> 'Iterator[str]':
        token = None
        for index, token in enumerate(tokens):
            if token.col_offset > offset > 0:
                yield ' ' * (token.col_offset - offset)
            elif index > 0:
                yield ' '
            yield self._remove_trailing_backslash(token.value)
            offset = token.end_col_offset
        if token and not self._has_trailing_backslash_or_newline(token.value):
            yield '\n'

    def _remove_trailing_backslash(self, value: str) -> str:
        if value and value[-1] == '\\':
            match = re.search(r'(\\+)$', value)
            if match and len(match.group(1)) % 2 == 1:
                value = value[:-1]
        return value

    def _has_trailing_backslash_or_newline(self, line: str) -> bool:
        match = re.search(r'(\\+)n?$', line)
        return bool(match and len(match.group(1)) % 2 == 1)


class SingleValue(Statement, ABC):

    @property
    def value(self) -> 'str|None':
        values = self.get_values(Token.NAME, Token.ARGUMENT)
        if values and values[0].upper() != 'NONE':
            return values[0]
        return None


class MultiValue(Statement, ABC):

    @property
    def values(self) -> 'tuple[str, ...]':
        return self.get_values(Token.ARGUMENT)


class Fixture(Statement, ABC):

    @property
    def name(self) -> str:
        return self.get_value(Token.NAME, '')

    @property
    def args(self) -> 'tuple[str, ...]':
        return self.get_values(Token.ARGUMENT)


@Statement.register
class SectionHeader(Statement):
    handles_types = (Token.SETTING_HEADER, Token.VARIABLE_HEADER,
                     Token.TESTCASE_HEADER, Token.TASK_HEADER,
                     Token.KEYWORD_HEADER, Token.COMMENT_HEADER,
                     Token.INVALID_HEADER)

    @classmethod
    def from_params(cls, type: str, name: 'str|None' = None,
                    eol: str = EOL) -> 'SectionHeader':
        if not name:
            names = ('Settings', 'Variables', 'Test Cases', 'Tasks',
                     'Keywords', 'Comments')
            name = dict(zip(cls.handles_types, names))[type]
        name = cast(str, name)
        header = f'*** {name} ***' if not name.startswith('*') else name
        return cls([
            Token(type, header),
            Token(Token.EOL, eol)
        ])

    @property
    def type(self) -> str:
        token = self.get_token(*self.handles_types)
        return token.type    # type: ignore

    @property
    def name(self) -> str:
        token = self.get_token(*self.handles_types)
        return normalize_whitespace(token.value).strip('* ') if token else ''


@Statement.register
class LibraryImport(Statement):
    type = Token.LIBRARY

    @classmethod
    def from_params(cls, name: str, args: 'Sequence[str]' = (), alias: 'str|None' = None,
                    separator: str = FOUR_SPACES, eol: str = EOL) -> 'LibraryImport':
        tokens = [Token(Token.LIBRARY, 'Library'),
                  Token(Token.SEPARATOR, separator),
                  Token(Token.NAME, name)]
        for arg in args:
            tokens.extend([Token(Token.SEPARATOR, separator),
                           Token(Token.ARGUMENT, arg)])
        if alias is not None:
            tokens.extend([Token(Token.SEPARATOR, separator),
                           Token(Token.AS),
                           Token(Token.SEPARATOR, separator),
                           Token(Token.NAME, alias)])
        tokens.append(Token(Token.EOL, eol))
        return cls(tokens)

    @property
    def name(self) -> str:
        return self.get_value(Token.NAME, '')

    @property
    def args(self) -> 'tuple[str, ...]':
        return self.get_values(Token.ARGUMENT)

    @property
    def alias(self) -> 'str|None':
        separator = self.get_token(Token.AS)
        return self.get_tokens(Token.NAME)[-1].value if separator else None


@Statement.register
class ResourceImport(Statement):
    type = Token.RESOURCE

    @classmethod
    def from_params(cls, name: str, separator: str = FOUR_SPACES,
                    eol: str = EOL) -> 'ResourceImport':
        return cls([
            Token(Token.RESOURCE, 'Resource'),
            Token(Token.SEPARATOR, separator),
            Token(Token.NAME, name),
            Token(Token.EOL, eol)
        ])

    @property
    def name(self) -> str:
        return self.get_value(Token.NAME, '')


@Statement.register
class VariablesImport(Statement):
    type = Token.VARIABLES

    @classmethod
    def from_params(cls, name: str, args: 'Sequence[str]' = (),
                    separator: str = FOUR_SPACES, eol: str = EOL) -> 'VariablesImport':
        tokens = [Token(Token.VARIABLES, 'Variables'),
                  Token(Token.SEPARATOR, separator),
                  Token(Token.NAME, name)]
        for arg in args:
            tokens.extend([Token(Token.SEPARATOR, separator),
                           Token(Token.ARGUMENT, arg)])
        tokens.append(Token(Token.EOL, eol))
        return cls(tokens)

    @property
    def name(self) -> str:
        return self.get_value(Token.NAME, '')

    @property
    def args(self) -> 'tuple[str, ...]':
        return self.get_values(Token.ARGUMENT)


@Statement.register
class Documentation(DocumentationOrMetadata):
    type = Token.DOCUMENTATION

    @classmethod
    def from_params(cls, value: str, indent: str = FOUR_SPACES,
                    separator: str = FOUR_SPACES, eol: str = EOL,
                    settings_section: bool = True) -> 'Documentation':
        if settings_section:
            tokens = [Token(Token.DOCUMENTATION, 'Documentation'),
                      Token(Token.SEPARATOR, separator)]
        else:
            tokens = [Token(Token.SEPARATOR, indent),
                      Token(Token.DOCUMENTATION, '[Documentation]'),
                      Token(Token.SEPARATOR, separator)]
        multiline_separator = ' ' * (len(tokens[-2].value) + len(separator) - 3)
        doc_lines = value.splitlines()
        if doc_lines:
            tokens.extend([Token(Token.ARGUMENT, doc_lines[0]),
                           Token(Token.EOL, eol)])
        for line in doc_lines[1:]:
            if not settings_section:
                tokens.append(Token(Token.SEPARATOR, indent))
            tokens.append(Token(Token.CONTINUATION))
            if line:
                tokens.append(Token(Token.SEPARATOR, multiline_separator))
            tokens.extend([Token(Token.ARGUMENT, line),
                           Token(Token.EOL, eol)])
        return cls(tokens)


@Statement.register
class Metadata(DocumentationOrMetadata):
    type = Token.METADATA

    @classmethod
    def from_params(cls, name: str, value: str, separator: str = FOUR_SPACES,
                    eol: str = EOL) -> 'Metadata':
        tokens = [Token(Token.METADATA, 'Metadata'),
                  Token(Token.SEPARATOR, separator),
                  Token(Token.NAME, name)]
        metadata_lines = value.splitlines()
        if metadata_lines:
            tokens.extend([Token(Token.SEPARATOR, separator),
                           Token(Token.ARGUMENT, metadata_lines[0]),
                           Token(Token.EOL, eol)])
        for line in metadata_lines[1:]:
            tokens.extend([Token(Token.CONTINUATION),
                           Token(Token.SEPARATOR, separator),
                           Token(Token.ARGUMENT, line),
                           Token(Token.EOL, eol)])
        return cls(tokens)

    @property
    def name(self) -> str:
        return self.get_value(Token.NAME, '')


@Statement.register
class TestTags(MultiValue):
    type = Token.TEST_TAGS

    @classmethod
    def from_params(cls, values: 'Sequence[str]', separator: str = FOUR_SPACES,
                    eol: str = EOL) -> 'TestTags':
        tokens = [Token(Token.TEST_TAGS, 'Test Tags')]
        for tag in values:
            tokens.extend([Token(Token.SEPARATOR, separator),
                           Token(Token.ARGUMENT, tag)])
        tokens.append(Token(Token.EOL, eol))
        return cls(tokens)


@Statement.register
class DefaultTags(MultiValue):
    type = Token.DEFAULT_TAGS

    @classmethod
    def from_params(cls, values: 'Sequence[str]', separator: str = FOUR_SPACES,
                    eol: str = EOL) -> 'DefaultTags':
        tokens = [Token(Token.DEFAULT_TAGS, 'Default Tags')]
        for tag in values:
            tokens.extend([Token(Token.SEPARATOR, separator),
                           Token(Token.ARGUMENT, tag)])
        tokens.append(Token(Token.EOL, eol))
        return cls(tokens)


@Statement.register
class KeywordTags(MultiValue):
    type = Token.KEYWORD_TAGS

    @classmethod
    def from_params(cls, values: 'Sequence[str]', separator: str = FOUR_SPACES,
                    eol: str = EOL) -> 'KeywordTags':
        tokens = [Token(Token.KEYWORD_TAGS, 'Keyword Tags')]
        for tag in values:
            tokens.extend([Token(Token.SEPARATOR, separator),
                           Token(Token.ARGUMENT, tag)])
        tokens.append(Token(Token.EOL, eol))
        return cls(tokens)


@Statement.register
class SuiteName(SingleValue):
    type = Token.SUITE_NAME

    @classmethod
    def from_params(cls, value: str, separator: str = FOUR_SPACES,
                    eol: str = EOL) -> 'SuiteName':
        return cls([
            Token(Token.SUITE_NAME, 'Name'),
            Token(Token.SEPARATOR, separator),
            Token(Token.NAME, value),
            Token(Token.EOL, eol)
        ])


@Statement.register
class SuiteSetup(Fixture):
    type = Token.SUITE_SETUP

    @classmethod
    def from_params(cls, name: str, args: 'Sequence[str]' = (),
                    separator: str = FOUR_SPACES, eol: str = EOL) -> 'SuiteSetup':
        tokens = [Token(Token.SUITE_SETUP, 'Suite Setup'),
                  Token(Token.SEPARATOR, separator),
                  Token(Token.NAME, name)]
        for arg in args:
            tokens.extend([Token(Token.SEPARATOR, separator),
                           Token(Token.ARGUMENT, arg)])
        tokens.append(Token(Token.EOL, eol))
        return cls(tokens)


@Statement.register
class SuiteTeardown(Fixture):
    type = Token.SUITE_TEARDOWN

    @classmethod
    def from_params(cls, name: str, args: 'Sequence[str]' = (),
                    separator: str = FOUR_SPACES, eol: str = EOL) -> 'SuiteTeardown':
        tokens = [Token(Token.SUITE_TEARDOWN, 'Suite Teardown'),
                  Token(Token.SEPARATOR, separator),
                  Token(Token.NAME, name)]
        for arg in args:
            tokens.extend([Token(Token.SEPARATOR, separator),
                           Token(Token.ARGUMENT, arg)])
        tokens.append(Token(Token.EOL, eol))
        return cls(tokens)


@Statement.register
class TestSetup(Fixture):
    type = Token.TEST_SETUP

    @classmethod
    def from_params(cls, name: str, args: 'Sequence[str]' = (),
                    separator: str = FOUR_SPACES, eol: str = EOL) -> 'TestSetup':
        tokens = [Token(Token.TEST_SETUP, 'Test Setup'),
                  Token(Token.SEPARATOR, separator),
                  Token(Token.NAME, name)]
        for arg in args:
            tokens.extend([Token(Token.SEPARATOR, separator),
                           Token(Token.ARGUMENT, arg)])
        tokens.append(Token(Token.EOL, eol))
        return cls(tokens)


@Statement.register
class TestTeardown(Fixture):
    type = Token.TEST_TEARDOWN

    @classmethod
    def from_params(cls, name: str, args: 'Sequence[str]' = (),
                    separator: str = FOUR_SPACES, eol: str = EOL) -> 'TestTeardown':
        tokens = [Token(Token.TEST_TEARDOWN, 'Test Teardown'),
                  Token(Token.SEPARATOR, separator),
                  Token(Token.NAME, name)]
        for arg in args:
            tokens.extend([Token(Token.SEPARATOR, separator),
                           Token(Token.ARGUMENT, arg)])
        tokens.append(Token(Token.EOL, eol))
        return cls(tokens)


@Statement.register
class TestTemplate(SingleValue):
    type = Token.TEST_TEMPLATE

    @classmethod
    def from_params(cls, value: str, separator: str = FOUR_SPACES,
                    eol: str = EOL) -> 'TestTemplate':
        return cls([
            Token(Token.TEST_TEMPLATE, 'Test Template'),
            Token(Token.SEPARATOR, separator),
            Token(Token.NAME, value),
            Token(Token.EOL, eol)
        ])


@Statement.register
class TestTimeout(SingleValue):
    type = Token.TEST_TIMEOUT

    @classmethod
    def from_params(cls, value: str, separator: str = FOUR_SPACES,
                    eol: str = EOL) -> 'TestTimeout':
        return cls([
            Token(Token.TEST_TIMEOUT, 'Test Timeout'),
            Token(Token.SEPARATOR, separator),
            Token(Token.ARGUMENT, value),
            Token(Token.EOL, eol)
        ])


@Statement.register
class Variable(Statement):
    type = Token.VARIABLE
    options = {
        'separator': None
    }

    @classmethod
    def from_params(cls, name: str,
                    value: 'str|Sequence[str]',
                    value_separator: 'str|None' = None,
                    separator: str = FOUR_SPACES,
                    eol: str = EOL) -> 'Variable':
        values = [value] if isinstance(value, str) else value
        tokens = [Token(Token.VARIABLE, name)]
        for value in values:
            tokens.extend([Token(Token.SEPARATOR, separator),
                           Token(Token.ARGUMENT, value)])
        if value_separator is not None:
            tokens.extend([Token(Token.SEPARATOR, separator),
                           Token(Token.OPTION, f'separator={value_separator}')])
        tokens.append(Token(Token.EOL, eol))
        return cls(tokens)

    @property
    def name(self) -> str:
        name = self.get_value(Token.VARIABLE, '')
        if name.endswith('='):
            return name[:-1].rstrip()
        return name

    @property
    def value(self) -> 'tuple[str, ...]':
        return self.get_values(Token.ARGUMENT)

    @property
    def separator(self) -> 'str|None':
        return self.get_option('separator')

    def validate(self, ctx: 'ValidationContext'):
        VariableValidator().validate(self)
        self._validate_options()


@Statement.register
class TestCaseName(Statement):
    type = Token.TESTCASE_NAME

    @classmethod
    def from_params(cls, name: str, eol: str = EOL) -> 'TestCaseName':
        tokens = [Token(Token.TESTCASE_NAME, name)]
        if eol:
            tokens.append(Token(Token.EOL, eol))
        return cls(tokens)

    @property
    def name(self) -> str:
        return self.get_value(Token.TESTCASE_NAME, '')

    def validate(self, ctx: 'ValidationContext'):
        if not self.name:
            self.errors += (test_or_task('{Test} name cannot be empty.', ctx.tasks),)


@Statement.register
class KeywordName(Statement):
    type = Token.KEYWORD_NAME

    @classmethod
    def from_params(cls, name: str, eol: str = EOL) -> 'KeywordName':
        tokens = [Token(Token.KEYWORD_NAME, name)]
        if eol:
            tokens.append(Token(Token.EOL, eol))
        return cls(tokens)

    @property
    def name(self) -> str:
        return self.get_value(Token.KEYWORD_NAME, '')

    def validate(self, ctx: 'ValidationContext'):
        if not self.name:
            self.errors += ('User keyword name cannot be empty.',)


@Statement.register
class Setup(Fixture):
    type = Token.SETUP

    @classmethod
    def from_params(cls, name: str, args: 'Sequence[str]' = (),
                    indent: str = FOUR_SPACES, separator: str = FOUR_SPACES,
                    eol: str = EOL) -> 'Setup':
        tokens = [Token(Token.SEPARATOR, indent),
                  Token(Token.SETUP, '[Setup]'),
                  Token(Token.SEPARATOR, separator),
                  Token(Token.NAME, name)]
        for arg in args:
            tokens.extend([Token(Token.SEPARATOR, separator),
                           Token(Token.ARGUMENT, arg)])
        tokens.append(Token(Token.EOL, eol))
        return cls(tokens)


@Statement.register
class Teardown(Fixture):
    type = Token.TEARDOWN

    @classmethod
    def from_params(cls, name: str, args: 'Sequence[str]' = (),
                    indent: str = FOUR_SPACES, separator: str = FOUR_SPACES,
                    eol: str = EOL) -> 'Teardown':
        tokens = [Token(Token.SEPARATOR, indent),
                  Token(Token.TEARDOWN, '[Teardown]'),
                  Token(Token.SEPARATOR, separator),
                  Token(Token.NAME, name)]
        for arg in args:
            tokens.extend([Token(Token.SEPARATOR, separator),
                           Token(Token.ARGUMENT, arg)])
        tokens.append(Token(Token.EOL, eol))
        return cls(tokens)


@Statement.register
class Tags(MultiValue):
    type = Token.TAGS

    @classmethod
    def from_params(cls, values: 'Sequence[str]', indent: str = FOUR_SPACES,
                    separator: str = FOUR_SPACES, eol: str = EOL) -> 'Tags':
        tokens = [Token(Token.SEPARATOR, indent),
                  Token(Token.TAGS, '[Tags]')]
        for tag in values:
            tokens.extend([Token(Token.SEPARATOR, separator),
                           Token(Token.ARGUMENT, tag)])
        tokens.append(Token(Token.EOL, eol))
        return cls(tokens)


@Statement.register
class Template(SingleValue):
    type = Token.TEMPLATE

    @classmethod
    def from_params(cls, value: str, indent: str = FOUR_SPACES,
                    separator: str = FOUR_SPACES, eol: str = EOL) -> 'Template':
        return cls([
            Token(Token.SEPARATOR, indent),
            Token(Token.TEMPLATE, '[Template]'),
            Token(Token.SEPARATOR, separator),
            Token(Token.NAME, value),
            Token(Token.EOL, eol)
        ])


@Statement.register
class Timeout(SingleValue):
    type = Token.TIMEOUT

    @classmethod
    def from_params(cls, value: str, indent: str = FOUR_SPACES,
                    separator: str = FOUR_SPACES, eol: str = EOL) -> 'Timeout':
        return cls([
            Token(Token.SEPARATOR, indent),
            Token(Token.TIMEOUT, '[Timeout]'),
            Token(Token.SEPARATOR, separator),
            Token(Token.ARGUMENT, value),
            Token(Token.EOL, eol)
        ])


@Statement.register
class Arguments(MultiValue):
    type = Token.ARGUMENTS

    @classmethod
    def from_params(cls, args: 'Sequence[str]', indent: str = FOUR_SPACES,
                    separator: str = FOUR_SPACES, eol: str = EOL) -> 'Arguments':
        tokens = [Token(Token.SEPARATOR, indent),
                  Token(Token.ARGUMENTS, '[Arguments]')]
        for arg in args:
            tokens.extend([Token(Token.SEPARATOR, separator),
                           Token(Token.ARGUMENT, arg)])
        tokens.append(Token(Token.EOL, eol))
        return cls(tokens)

    def validate(self, ctx: 'ValidationContext'):
        errors: 'list[str]' = []
        UserKeywordArgumentParser(error_reporter=errors.append).parse(self.values)
        self.errors = tuple(errors)


@Statement.register
class ReturnSetting(MultiValue):
    """Represents the deprecated ``[Return]`` setting.

    This class was named ``Return`` prior to Robot Framework 7.0. A forward
    compatible ``ReturnSetting`` alias existed already in Robot Framework 6.1.
    """
    type = Token.RETURN

    @classmethod
    def from_params(cls, args: 'Sequence[str]', indent: str = FOUR_SPACES,
                    separator: str = FOUR_SPACES, eol: str = EOL) -> 'ReturnSetting':
        tokens = [Token(Token.SEPARATOR, indent),
                  Token(Token.RETURN, '[Return]')]
        for arg in args:
            tokens.extend([Token(Token.SEPARATOR, separator),
                           Token(Token.ARGUMENT, arg)])
        tokens.append(Token(Token.EOL, eol))
        return cls(tokens)


@Statement.register
class KeywordCall(Statement):
    type = Token.KEYWORD

    @classmethod
    def from_params(cls, name: str, assign: 'Sequence[str]' = (),
                    args: 'Sequence[str]' = (), indent: str = FOUR_SPACES,
                    separator: str = FOUR_SPACES, eol: str = EOL) -> 'KeywordCall':
        tokens = [Token(Token.SEPARATOR, indent)]
        for assignment in assign:
            tokens.extend([Token(Token.ASSIGN, assignment),
                           Token(Token.SEPARATOR, separator)])
        tokens.append(Token(Token.KEYWORD, name))
        for arg in args:
            tokens.extend([Token(Token.SEPARATOR, separator),
                           Token(Token.ARGUMENT, arg)])
        tokens.append(Token(Token.EOL, eol))
        return cls(tokens)

    @property
    def keyword(self) -> str:
        return self.get_value(Token.KEYWORD, '')

    @property
    def args(self) -> 'tuple[str, ...]':
        return self.get_values(Token.ARGUMENT)

    @property
    def assign(self) -> 'tuple[str, ...]':
        return self.get_values(Token.ASSIGN)


@Statement.register
class TemplateArguments(Statement):
    type = Token.ARGUMENT

    @classmethod
    def from_params(cls, args: 'Sequence[str]', indent: str = FOUR_SPACES,
                    separator: str = FOUR_SPACES, eol: str = EOL) -> 'TemplateArguments':
        tokens = []
        for index, arg in enumerate(args):
            tokens.extend([Token(Token.SEPARATOR, separator if index else indent),
                           Token(Token.ARGUMENT, arg)])
        tokens.append(Token(Token.EOL, eol))
        return cls(tokens)

    @property
    def args(self) -> 'tuple[str, ...]':
        return self.get_values(self.type)


@Statement.register
class ForHeader(Statement):
    type = Token.FOR
    options = {
        'start': None,
        'mode': ('STRICT', 'SHORTEST', 'LONGEST'),
        'fill': None
    }

    @classmethod
    def from_params(cls, assign: 'Sequence[str]',
                    values: 'Sequence[str]',
                    flavor: Literal['IN', 'IN RANGE', 'IN ENUMERATE', 'IN ZIP'] = 'IN',
                    indent: str = FOUR_SPACES,
                    separator: str = FOUR_SPACES,
                    eol: str = EOL) -> 'ForHeader':
        tokens = [Token(Token.SEPARATOR, indent),
                  Token(Token.FOR),
                  Token(Token.SEPARATOR, separator)]
        for variable in assign:
            tokens.extend([Token(Token.VARIABLE, variable),
                           Token(Token.SEPARATOR, separator)])
        tokens.append(Token(Token.FOR_SEPARATOR, flavor))
        for value in values:
            tokens.extend([Token(Token.SEPARATOR, separator),
                           Token(Token.ARGUMENT, value)])
        tokens.append(Token(Token.EOL, eol))
        return cls(tokens)

    @property
    def assign(self) -> 'tuple[str, ...]':
        return self.get_values(Token.VARIABLE)

    @property
    def variables(self) -> 'tuple[str, ...]':    # TODO: Remove in RF 8.0.
        warnings.warn("'ForHeader.variables' is deprecated and will be removed in "
                      "Robot Framework 8.0. Use 'ForHeader.assign' instead.")
        return self.assign

    @property
    def values(self) -> 'tuple[str, ...]':
        return self.get_values(Token.ARGUMENT)

    @property
    def flavor(self) -> 'str|None':
        separator = self.get_token(Token.FOR_SEPARATOR)
        return normalize_whitespace(separator.value) if separator else None

    @property
    def start(self) -> 'str|None':
        return self.get_option('start') if self.flavor == 'IN ENUMERATE' else None

    @property
    def mode(self) -> 'str|None':
        return self.get_option('mode') if self.flavor == 'IN ZIP' else None

    @property
    def fill(self) -> 'str|None':
        return self.get_option('fill') if self.flavor == 'IN ZIP' else None

    def validate(self, ctx: 'ValidationContext'):
        if not self.assign:
            self._add_error('no loop variables')
        if not self.flavor:
            self._add_error("no 'IN' or other valid separator")
        else:
            for var in self.assign:
                if not is_scalar_assign(var):
                    self._add_error(f"invalid loop variable '{var}'")
            if not self.values:
                self._add_error('no loop values')
        self._validate_options()

    def _add_error(self, error: str):
        self.errors += (f'FOR loop has {error}.',)


class IfElseHeader(Statement, ABC):

    @property
    def condition(self) -> 'str|None':
        values = self.get_values(Token.ARGUMENT)
        return ', '.join(values) if values else None

    @property
    def assign(self) -> 'tuple[str, ...]':
        return self.get_values(Token.ASSIGN)

    def validate(self, ctx: 'ValidationContext'):
        conditions = self.get_tokens(Token.ARGUMENT)
        if not conditions:
            self.errors += (f'{self.type} must have a condition.',)
        if len(conditions) > 1:
            self.errors += (f'{self.type} cannot have more than one condition, '
                            f'got {seq2str(c.value for c in conditions)}.',)


@Statement.register
class IfHeader(IfElseHeader):
    type = Token.IF

    @classmethod
    def from_params(cls, condition: str, indent: str = FOUR_SPACES,
                    separator: str = FOUR_SPACES, eol: str = EOL) -> 'IfHeader':
        return cls([
            Token(Token.SEPARATOR, indent),
            Token(cls.type),
            Token(Token.SEPARATOR, separator),
            Token(Token.ARGUMENT, condition),
            Token(Token.EOL, eol)
        ])


@Statement.register
class InlineIfHeader(IfElseHeader):
    type = Token.INLINE_IF

    @classmethod
    def from_params(cls, condition: str, assign: 'Sequence[str]' = (),
                    indent: str = FOUR_SPACES,
                    separator: str = FOUR_SPACES) -> 'InlineIfHeader':
        tokens = [Token(Token.SEPARATOR, indent)]
        for assignment in assign:
            tokens.extend([Token(Token.ASSIGN, assignment),
                           Token(Token.SEPARATOR, separator)])
        tokens.extend([Token(Token.INLINE_IF),
                       Token(Token.SEPARATOR, separator),
                       Token(Token.ARGUMENT, condition)])
        return cls(tokens)


@Statement.register
class ElseIfHeader(IfElseHeader):
    type = Token.ELSE_IF

    @classmethod
    def from_params(cls, condition: str, indent: str = FOUR_SPACES,
                    separator: str = FOUR_SPACES, eol: str = EOL) -> 'ElseIfHeader':
        return cls([
            Token(Token.SEPARATOR, indent),
            Token(Token.ELSE_IF),
            Token(Token.SEPARATOR, separator),
            Token(Token.ARGUMENT, condition),
            Token(Token.EOL, eol)
        ])


@Statement.register
class ElseHeader(IfElseHeader):
    type = Token.ELSE

    @classmethod
    def from_params(cls, indent: str = FOUR_SPACES, eol: str = EOL) -> 'ElseHeader':
        return cls([
            Token(Token.SEPARATOR, indent),
            Token(Token.ELSE),
            Token(Token.EOL, eol)
        ])

    def validate(self, ctx: 'ValidationContext'):
        if self.get_tokens(Token.ARGUMENT):
            values = self.get_values(Token.ARGUMENT)
            self.errors += (f'ELSE does not accept arguments, got {seq2str(values)}.',)


class NoArgumentHeader(Statement, ABC):

    @classmethod
    def from_params(cls, indent: str = FOUR_SPACES, eol: str = EOL):
        return cls([
            Token(Token.SEPARATOR, indent),
            Token(cls.type),
            Token(Token.EOL, eol)
        ])

    def validate(self, ctx: 'ValidationContext'):
        if self.get_tokens(Token.ARGUMENT):
            self.errors += (f'{self.type} does not accept arguments, got '
                            f'{seq2str(self.values)}.',)

    @property
    def values(self) -> 'tuple[str, ...]':
        return self.get_values(Token.ARGUMENT)


@Statement.register
class TryHeader(NoArgumentHeader):
    type = Token.TRY


@Statement.register
class ExceptHeader(Statement):
    type = Token.EXCEPT
    options = {
        'type': ('GLOB', 'REGEXP', 'START', 'LITERAL')
    }

    @classmethod
    def from_params(cls, patterns: 'Sequence[str]' = (), type: 'str|None' = None,
                    assign: 'str|None' = None, indent: str = FOUR_SPACES,
                    separator: str = FOUR_SPACES, eol: str = EOL) -> 'ExceptHeader':
        tokens = [Token(Token.SEPARATOR, indent),
                  Token(Token.EXCEPT)]
        for pattern in patterns:
            tokens.extend([Token(Token.SEPARATOR, separator),
                           Token(Token.ARGUMENT, pattern)])
        if type:
            tokens.extend([Token(Token.SEPARATOR, separator),
                           Token(Token.OPTION, f'type={type}')])
        if assign:
            tokens.extend([Token(Token.SEPARATOR, separator),
                           Token(Token.AS),
                           Token(Token.SEPARATOR, separator),
                           Token(Token.VARIABLE, assign)])
        tokens.append(Token(Token.EOL, eol))
        return cls(tokens)

    @property
    def patterns(self) -> 'tuple[str, ...]':
        return self.get_values(Token.ARGUMENT)

    @property
    def pattern_type(self) -> 'str|None':
        return self.get_option('type')

    @property
    def assign(self) -> 'str|None':
        return self.get_value(Token.VARIABLE)

    @property
    def variable(self) -> 'str|None':    # TODO: Remove in RF 8.0.
        warnings.warn("'ExceptHeader.variable' is deprecated and will be removed in "
                      "Robot Framework 8.0. Use 'ExceptHeader.assigns' instead.")
        return self.assign

    def validate(self, ctx: 'ValidationContext'):
        as_token = self.get_token(Token.AS)
        if as_token:
            assign = self.get_tokens(Token.VARIABLE)
            if not assign:
                self.errors += ("EXCEPT AS requires a value.",)
            elif len(assign) > 1:
                self.errors += ("EXCEPT AS accepts only one value.",)
            elif not is_scalar_assign(assign[0].value):
                self.errors += (f"EXCEPT AS variable '{assign[0].value}' is invalid.",)
        self._validate_options()


@Statement.register
class FinallyHeader(NoArgumentHeader):
    type = Token.FINALLY


@Statement.register
class End(NoArgumentHeader):
    type = Token.END


@Statement.register
class WhileHeader(Statement):
    type = Token.WHILE
    options = {
        'limit': None,
        'on_limit': ('PASS', 'FAIL'),
        'on_limit_message': None
    }

    @classmethod
    def from_params(cls, condition: str, limit: 'str|None' = None,
                    on_limit: 'str|None ' = None, on_limit_message: 'str|None' = None,
                    indent: str = FOUR_SPACES, separator: str = FOUR_SPACES,
                    eol: str = EOL) -> 'WhileHeader':
        tokens = [Token(Token.SEPARATOR, indent),
                  Token(Token.WHILE),
                  Token(Token.SEPARATOR, separator),
                  Token(Token.ARGUMENT, condition)]
        if limit:
            tokens.extend([Token(Token.SEPARATOR, separator),
                           Token(Token.OPTION, f'limit={limit}')])
        if on_limit:
            tokens.extend([Token(Token.SEPARATOR, separator),
                           Token(Token.OPTION, f'on_limit={on_limit}')])
        if on_limit_message:
            tokens.extend([Token(Token.SEPARATOR, separator),
                           Token(Token.OPTION, f'on_limit_message={on_limit_message}')])
        tokens.append(Token(Token.EOL, eol))
        return cls(tokens)

    @property
    def condition(self) -> str:
        return ', '.join(self.get_values(Token.ARGUMENT))

    @property
    def limit(self) -> 'str|None':
        return self.get_option('limit')

    @property
    def on_limit(self) -> 'str|None':
        return self.get_option('on_limit')

    @property
    def on_limit_message(self) -> 'str|None':
        return self.get_option('on_limit_message')

    def validate(self, ctx: 'ValidationContext'):
        conditions = self.get_values(Token.ARGUMENT)
        if len(conditions) > 1:
            self.errors += (f"WHILE accepts only one condition, got {len(conditions)} "
                            f"conditions {seq2str(conditions)}.",)
        if self.on_limit and not self.limit:
            self.errors += ("WHILE option 'on_limit' cannot be used without 'limit'.",)
        self._validate_options()


@Statement.register
class GroupHeader(Statement):
    type = Token.GROUP

    @classmethod
    def from_params(cls, name: str = '',
                    indent: str = FOUR_SPACES, separator: str = FOUR_SPACES,
                    eol: str = EOL) -> 'GroupHeader':
        tokens = [Token(Token.SEPARATOR, indent),
                  Token(Token.GROUP)]
        if name:
            tokens.extend(
                [Token(Token.SEPARATOR, separator),
                Token(Token.ARGUMENT, name)]
            )
        tokens.append(Token(Token.EOL, eol))
        return cls(tokens)

    @property
    def name(self) -> str:
        return ', '.join(self.get_values(Token.ARGUMENT))

    def validate(self, ctx: 'ValidationContext'):
        names = self.get_values(Token.ARGUMENT)
        if len(names) > 1:
            self.errors += (f"GROUP accepts only one argument as name, got {len(names)} "
                            f"arguments {seq2str(names)}.",)


@Statement.register
class Var(Statement):
    type = Token.VAR
    options = {
        'scope': ('LOCAL', 'TEST', 'TASK', 'SUITE', 'SUITES', 'GLOBAL'),
        'separator': None
    }

    @classmethod
    def from_params(cls, name: str,
                    value: 'str|Sequence[str]',
                    scope: 'str|None' = None,
                    value_separator: 'str|None' = None,
                    indent: str = FOUR_SPACES,
                    separator: str = FOUR_SPACES,
                    eol: str = EOL) -> 'Var':
        tokens = [Token(Token.SEPARATOR, indent),
                  Token(Token.VAR),
                  Token(Token.SEPARATOR, separator),
                  Token(Token.VARIABLE, name)]
        values = [value] if isinstance(value, str) else value
        for value in values:
            tokens.extend([Token(Token.SEPARATOR, separator),
                           Token(Token.ARGUMENT, value)])
        if scope:
            tokens.extend([Token(Token.SEPARATOR, separator),
                           Token(Token.OPTION, f'scope={scope}')])
        if value_separator:
            tokens.extend([Token(Token.SEPARATOR, separator),
                           Token(Token.OPTION, f'separator={value_separator}')])
        tokens.append(Token(Token.EOL, eol))
        return cls(tokens)

    @property
    def name(self) -> str:
        name = self.get_value(Token.VARIABLE, '')
        if name.endswith('='):
            return name[:-1].rstrip()
        return name

    @property
    def value(self) -> 'tuple[str, ...]':
        return self.get_values(Token.ARGUMENT)

    @property
    def scope(self) -> 'str|None':
        return self.get_option('scope')

    @property
    def separator(self) -> 'str|None':
        return self.get_option('separator')

    def validate(self, ctx: 'ValidationContext'):
        VariableValidator().validate(self)
        self._validate_options()


@Statement.register
class Return(Statement):
    """Represents the RETURN statement.

    This class named ``ReturnStatement`` prior to Robot Framework 7.0.
    The old name still exists as a backwards compatible alias.
    """
    type = Token.RETURN_STATEMENT

    @classmethod
    def from_params(cls, values: 'Sequence[str]' = (), indent: str = FOUR_SPACES,
                    separator: str = FOUR_SPACES, eol: str = EOL) -> 'Return':
        tokens = [Token(Token.SEPARATOR, indent),
                  Token(Token.RETURN_STATEMENT)]
        for value in values:
            tokens.extend([Token(Token.SEPARATOR, separator),
                           Token(Token.ARGUMENT, value)])
        tokens.append(Token(Token.EOL, eol))
        return cls(tokens)

    @property
    def values(self) -> 'tuple[str, ...]':
        return self.get_values(Token.ARGUMENT)

    def validate(self, ctx: 'ValidationContext'):
        if not ctx.in_keyword:
            self.errors += ('RETURN can only be used inside a user keyword.',)
        if ctx.in_finally:
            self.errors += ('RETURN cannot be used in FINALLY branch.',)


# Backwards compatibility with RF < 7.
ReturnStatement = Return


class LoopControl(NoArgumentHeader, ABC):

    def validate(self, ctx: 'ValidationContext'):
        super().validate(ctx)
        if not ctx.in_loop:
            self.errors += (f'{self.type} can only be used inside a loop.',)
        if ctx.in_finally:
            self.errors += (f'{self.type} cannot be used in FINALLY branch.',)


@Statement.register
class Continue(LoopControl):
    type = Token.CONTINUE


@Statement.register
class Break(LoopControl):
    type = Token.BREAK


@Statement.register
class Comment(Statement):
    type = Token.COMMENT

    @classmethod
    def from_params(cls, comment: str, indent: str = FOUR_SPACES,
                    eol: str = EOL) -> 'Comment':
        return cls([
            Token(Token.SEPARATOR, indent),
            Token(Token.COMMENT, comment),
            Token(Token.EOL, eol)
        ])


@Statement.register
class Config(Statement):
    type = Token.CONFIG

    @classmethod
    def from_params(cls, config: str, eol: str = EOL) -> 'Config':
        return cls([
            Token(Token.CONFIG, config),
            Token(Token.EOL, eol)
        ])

    @property
    def language(self) -> 'Language|None':
        value = ' '.join(self.get_values(Token.CONFIG))
        lang = value.split(':', 1)[1].strip()
        return Language.from_name(lang) if lang else None


@Statement.register
class Error(Statement):
    type = Token.ERROR
    _errors: 'tuple[str, ...]' = ()

    @classmethod
    def from_params(cls, error: str, value: str = '', indent: str = FOUR_SPACES,
                    eol: str = EOL) -> 'Error':
        return cls([
            Token(Token.SEPARATOR, indent),
            Token(Token.ERROR, value, error=error),
            Token(Token.EOL, eol)
        ])

    @property
    def values(self) -> 'list[str]':
        return [token.value for token in self.data_tokens]

    @property
    def errors(self) -> 'tuple[str, ...]':
        """Errors got from the underlying ``ERROR``token.

        Errors can be set also explicitly. When accessing errors, they are returned
        along with errors got from tokens.
        """
        tokens = self.get_tokens(Token.ERROR)
        return tuple(t.error or '' for t in tokens) + self._errors

    @errors.setter
    def errors(self, errors: 'Sequence[str]'):
        self._errors = tuple(errors)


class EmptyLine(Statement):
    type = Token.EOL

    @classmethod
    def from_params(cls, eol: str = EOL):
        return cls([Token(Token.EOL, eol)])


class VariableValidator:

    def validate(self, statement: Statement):
        name = statement.get_value(Token.VARIABLE, '')
        match = search_variable(name, ignore_errors=True)
        if not match.is_assign(allow_assign_mark=True, allow_nested=True):
            statement.errors += (f"Invalid variable name '{name}'.",)
        if match.identifier == '&':
            self._validate_dict_items(statement)

    def _validate_dict_items(self, statement: Statement):
        for item in statement.get_values(Token.ARGUMENT):
            if not self._is_valid_dict_item(item):
                statement.errors += (
                    f"Invalid dictionary variable item '{item}'. Items must use "
                    f"'name=value' syntax or be dictionary variables themselves.",
                )

    def _is_valid_dict_item(self, item: str) -> bool:
        name, value = split_from_equals(item)
        return value is not None or is_dict_variable(item)
