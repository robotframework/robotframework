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
from typing import TYPE_CHECKING

from robot.conf import Language
from robot.running.arguments import UserKeywordArgumentParser
from robot.utils import is_list_like, normalize_whitespace, seq2str, split_from_equals
from robot.variables import is_scalar_assign, is_dict_variable, search_variable

from ..lexer import Token

if TYPE_CHECKING:
    from .blocks import ValidationContext


FOUR_SPACES = '    '
EOL = '\n'


class Statement(ast.AST):
    type = None
    handles_types = ()
    _fields = ('type', 'tokens')
    _attributes = ('lineno', 'col_offset', 'end_lineno', 'end_col_offset', 'errors')
    _statement_handlers = {}

    def __init__(self, tokens, errors=()):
        self.tokens = tuple(tokens)
        self.errors = errors

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
        types = subcls.handles_types or (subcls.type,)
        for typ in types:
            cls._statement_handlers[typ] = subcls
        return subcls

    @classmethod
    def from_tokens(cls, tokens):
        handlers = cls._statement_handlers
        for token in tokens:
            if token.type in handlers:
                return handlers[token.type](tokens)
        if any(token.type == Token.ASSIGN for token in tokens):
            return KeywordCall(tokens)
        return EmptyLine(tokens)

    @classmethod
    def from_params(cls, *args, **kwargs):
        """Create a statement from passed parameters.

        Required and optional arguments in general match class properties.
        Values are used to create matching tokens.

        Most implementations support following general properties:

        - ``separator`` whitespace inserted between each token. Default is four spaces.
        - ``indent`` whitespace inserted before first token. Default is four spaces.
        - ``eol`` end of line sign. Default is ``'\\n'``.
        """
        raise NotImplementedError

    @property
    def data_tokens(self):
        return [t for t in self.tokens if t.type not in Token.NON_DATA_TOKENS]

    def get_token(self, *types):
        """Return a token with any of the given ``types``.

        If there are no matches, return ``None``. If there are multiple
        matches, return the first match.
        """
        for token in self.tokens:
            if token.type in types:
                return token
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

    def get_option(self, name, default=None):
        """Return value of a configuration option with the given ``name``.

        If the option has not been used, return ``default``.

        New in Robot Framework 6.1.
        """
        options = dict(opt.split('=', 1) for opt in self.get_values(Token.OPTION))
        return options.get(name, default)

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

    def validate(self, ctx: 'ValidationContext'):
        pass

    def __iter__(self):
        return iter(self.tokens)

    def __len__(self):
        return len(self.tokens)

    def __getitem__(self, item):
        return self.tokens[item]

    def __repr__(self):
        name = type(self).__name__
        tokens = f'tokens={list(self.tokens)}'
        errors = f', errors={list(self.errors)}' if self.errors else ''
        return f'{name}({tokens}{errors})'


class DocumentationOrMetadata(Statement):

    @property
    def value(self):
        return ''.join(self._get_lines()).rstrip()

    def _get_lines(self):
        base_offset = -1
        for tokens in self._get_line_tokens():
            yield from self._get_line_values(tokens, base_offset)
            first = tokens[0]
            if base_offset < 0 or 0 < first.col_offset < base_offset and first.value:
                base_offset = first.col_offset

    def _get_line_tokens(self):
        line = []
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

    def _get_line_values(self, tokens, offset):
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

    def _remove_trailing_backslash(self, value):
        if value and value[-1] == '\\':
            match = re.search(r'(\\+)$', value)
            if len(match.group(1)) % 2 == 1:
                value = value[:-1]
        return value

    def _has_trailing_backslash_or_newline(self, line):
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


@Statement.register
class SectionHeader(Statement):
    handles_types = (Token.SETTING_HEADER, Token.VARIABLE_HEADER,
                     Token.TESTCASE_HEADER, Token.TASK_HEADER,
                     Token.KEYWORD_HEADER, Token.COMMENT_HEADER,
                     Token.INVALID_HEADER)

    @classmethod
    def from_params(cls, type, name=None, eol=EOL):
        if not name:
            names = ('Settings', 'Variables', 'Test Cases', 'Tasks',
                     'Keywords', 'Comments')
            name = dict(zip(cls.handles_types, names))[type]
        if not name.startswith('*'):
            name = f'*** {name} ***'
        return cls([
            Token(type, name),
            Token('EOL', '\n')
        ])

    @property
    def type(self):
        token = self.get_token(*self.handles_types)
        return token.type

    @property
    def name(self):
        token = self.get_token(*self.handles_types)
        return normalize_whitespace(token.value).strip('* ')


@Statement.register
class LibraryImport(Statement):
    type = Token.LIBRARY

    @classmethod
    def from_params(cls, name, args=(), alias=None, separator=FOUR_SPACES, eol=EOL):
        tokens = [Token(Token.LIBRARY, 'Library'),
                  Token(Token.SEPARATOR, separator),
                  Token(Token.NAME, name)]
        for arg in args:
            tokens.extend([Token(Token.SEPARATOR, separator),
                           Token(Token.ARGUMENT, arg)])
        if alias is not None:
            tokens.extend([Token(Token.SEPARATOR, separator),
                           Token(Token.WITH_NAME),
                           Token(Token.SEPARATOR, separator),
                           Token(Token.NAME, alias)])
        tokens.append(Token(Token.EOL, eol))
        return cls(tokens)

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

    @classmethod
    def from_params(cls, name, separator=FOUR_SPACES, eol=EOL):
        return cls([
            Token(Token.RESOURCE, 'Resource'),
            Token(Token.SEPARATOR, separator),
            Token(Token.NAME, name),
            Token(Token.EOL, eol)
        ])

    @property
    def name(self):
        return self.get_value(Token.NAME)


@Statement.register
class VariablesImport(Statement):
    type = Token.VARIABLES

    @classmethod
    def from_params(cls, name, args=(), separator=FOUR_SPACES, eol=EOL):
        tokens = [Token(Token.VARIABLES, 'Variables'),
                  Token(Token.SEPARATOR, separator),
                  Token(Token.NAME, name)]
        for arg in args:
            tokens.extend([Token(Token.SEPARATOR, separator),
                           Token(Token.ARGUMENT, arg)])
        tokens.append(Token(Token.EOL, eol))
        return cls(tokens)

    @property
    def name(self):
        return self.get_value(Token.NAME)

    @property
    def args(self):
        return self.get_values(Token.ARGUMENT)


@Statement.register
class Documentation(DocumentationOrMetadata):
    type = Token.DOCUMENTATION

    @classmethod
    def from_params(cls, value, indent=FOUR_SPACES, separator=FOUR_SPACES,
                    eol=EOL, settings_section=True):
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
    def from_params(cls, name, value, separator=FOUR_SPACES, eol=EOL):
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
    def name(self):
        return self.get_value(Token.NAME)


@Statement.register
class ForceTags(MultiValue):
    type = Token.FORCE_TAGS

    @classmethod
    def from_params(cls, values, separator=FOUR_SPACES, eol=EOL):
        tokens = [Token(Token.FORCE_TAGS, 'Force Tags')]
        for tag in values:
            tokens.extend([Token(Token.SEPARATOR, separator),
                           Token(Token.ARGUMENT, tag)])
        tokens.append(Token(Token.EOL, eol))
        return cls(tokens)


@Statement.register
class DefaultTags(MultiValue):
    type = Token.DEFAULT_TAGS

    @classmethod
    def from_params(cls, values, separator=FOUR_SPACES, eol=EOL):
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
    def from_params(cls, values, separator=FOUR_SPACES, eol=EOL):
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
    def from_params(cls, value, separator=FOUR_SPACES, eol=EOL):
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
    def from_params(cls, name, args=(), separator=FOUR_SPACES, eol=EOL):
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
    def from_params(cls, name, args=(), separator=FOUR_SPACES, eol=EOL):
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
    def from_params(cls, name, args=(), separator=FOUR_SPACES, eol=EOL):
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
    def from_params(cls, name, args=(), separator=FOUR_SPACES, eol=EOL):
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
    def from_params(cls, value, separator=FOUR_SPACES, eol=EOL):
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
    def from_params(cls, value, separator=FOUR_SPACES, eol=EOL):
        return cls([
            Token(Token.TEST_TIMEOUT, 'Test Timeout'),
            Token(Token.SEPARATOR, separator),
            Token(Token.ARGUMENT, value),
            Token(Token.EOL, eol)
        ])


@Statement.register
class Variable(Statement):
    type = Token.VARIABLE

    @classmethod
    def from_params(cls, name, value, separator=FOUR_SPACES, eol=EOL):
        """``value`` can be given either as a string or as a list of strings."""
        values = value if is_list_like(value) else [value]
        tokens = [Token(Token.VARIABLE, name)]
        for value in values:
            tokens.extend([Token(Token.SEPARATOR, separator),
                           Token(Token.ARGUMENT, value)])
        tokens.append(Token(Token.EOL, eol))
        return cls(tokens)

    @property
    def name(self):
        name = self.get_value(Token.VARIABLE)
        if name.endswith('='):
            return name[:-1].rstrip()
        return name

    @property
    def value(self):
        return self.get_values(Token.ARGUMENT)

    def validate(self, ctx: 'ValidationContext'):
        name = self.get_value(Token.VARIABLE)
        match = search_variable(name, ignore_errors=True)
        if not match.is_assign(allow_assign_mark=True, allow_nested=True):
            self.errors += (f"Invalid variable name '{name}'.",)
        if match.is_dict_assign(allow_assign_mark=True):
            self._validate_dict_items()

    def _validate_dict_items(self):
        for item in self.get_values(Token.ARGUMENT):
            if not self._is_valid_dict_item(item):
                self.errors += (
                    f"Invalid dictionary variable item '{item}'. "
                    f"Items must use 'name=value' syntax or be dictionary "
                    f"variables themselves.",
                )

    def _is_valid_dict_item(self, item):
        name, value = split_from_equals(item)
        return value is not None or is_dict_variable(item)


@Statement.register
class TestCaseName(Statement):
    type = Token.TESTCASE_NAME

    @classmethod
    def from_params(cls, name, eol=EOL):
        tokens = [Token(Token.TESTCASE_NAME, name)]
        if eol:
            tokens.append(Token(Token.EOL, eol))
        return cls(tokens)

    @property
    def name(self):
        return self.get_value(Token.TESTCASE_NAME)

    def validate(self, ctx: 'ValidationContext'):
        if not self.name:
            self.errors += ('Test name cannot be empty.',)


@Statement.register
class KeywordName(Statement):
    type = Token.KEYWORD_NAME

    @classmethod
    def from_params(cls, name, eol=EOL):
        tokens = [Token(Token.KEYWORD_NAME, name)]
        if eol:
            tokens.append(Token(Token.EOL, eol))
        return cls(tokens)

    @property
    def name(self):
        return self.get_value(Token.KEYWORD_NAME)


@Statement.register
class Setup(Fixture):
    type = Token.SETUP

    @classmethod
    def from_params(cls, name, args=(), indent=FOUR_SPACES, separator=FOUR_SPACES,
                    eol=EOL):
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
    def from_params(cls, name, args=(), indent=FOUR_SPACES, separator=FOUR_SPACES,
                    eol=EOL):
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
    def from_params(cls, values, indent=FOUR_SPACES, separator=FOUR_SPACES, eol=EOL):
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
    def from_params(cls, value, indent=FOUR_SPACES, separator=FOUR_SPACES, eol=EOL):
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
    def from_params(cls, value, indent=FOUR_SPACES, separator=FOUR_SPACES, eol=EOL):
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
    def from_params(cls, args, indent=FOUR_SPACES, separator=FOUR_SPACES, eol=EOL):
        tokens = [Token(Token.SEPARATOR, indent),
                  Token(Token.ARGUMENTS, '[Arguments]')]
        for arg in args:
            tokens.extend([Token(Token.SEPARATOR, separator),
                           Token(Token.ARGUMENT, arg)])
        tokens.append(Token(Token.EOL, eol))
        return cls(tokens)

    def validate(self, ctx: 'ValidationContext'):
        errors = []
        UserKeywordArgumentParser(error_reporter=errors.append).parse(self.values)
        self.errors = tuple(errors)


# TODO: Change Return to mean ReturnStatement in RF 7.0
# - Rename current Return to ReturnSetting
# - Rename current ReturnStatement to Return
# - Add backwards compatible ReturnStatement alias
# - Change Token.RETURN to mean Token.RETURN_STATEMENT
# - Update also ModelVisitor
@Statement.register
class Return(MultiValue):
    """Represents the deprecated ``[Return]`` setting.

    In addition to the ``[Return]`` setting itself, also the ``Return`` node
    in the parsing model is deprecated and :class:`ReturnSetting` (new in
    Robot Framework 6.1) should be used instead. :class:`ReturnStatement` will
    be renamed to ``Return`` in Robot Framework 7.0.

    Eventually ``[Return]`` and ``ReturnSetting`` will be removed altogether.
    """
    type = Token.RETURN

    @classmethod
    def from_params(cls, args, indent=FOUR_SPACES, separator=FOUR_SPACES, eol=EOL):
        tokens = [Token(Token.SEPARATOR, indent),
                  Token(Token.RETURN, '[Return]')]
        for arg in args:
            tokens.extend([Token(Token.SEPARATOR, separator),
                           Token(Token.ARGUMENT, arg)])
        tokens.append(Token(Token.EOL, eol))
        return cls(tokens)


# Forward compatible alias for Return.
ReturnSetting = Return


@Statement.register
class KeywordCall(Statement):
    type = Token.KEYWORD

    @classmethod
    def from_params(cls, name, assign=(), args=(), indent=FOUR_SPACES,
                    separator=FOUR_SPACES, eol=EOL):
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

    @classmethod
    def from_params(cls, args, indent=FOUR_SPACES, separator=FOUR_SPACES, eol=EOL):
        tokens = []
        for index, arg in enumerate(args):
            tokens.extend([Token(Token.SEPARATOR, separator if index else indent),
                           Token(Token.ARGUMENT, arg)])
        tokens.append(Token(Token.EOL, eol))
        return cls(tokens)

    @property
    def args(self):
        return self.get_values(self.type)


@Statement.register
class ForHeader(Statement):
    type = Token.FOR

    @classmethod
    def from_params(cls, variables, values, flavor='IN', indent=FOUR_SPACES,
                    separator=FOUR_SPACES, eol=EOL):
        tokens = [Token(Token.SEPARATOR, indent),
                  Token(Token.FOR),
                  Token(Token.SEPARATOR, separator)]
        for variable in variables:
            tokens.extend([Token(Token.VARIABLE, variable),
                           Token(Token.SEPARATOR, separator)])
        tokens.append(Token(Token.FOR_SEPARATOR, flavor))
        for value in values:
            tokens.extend([Token(Token.SEPARATOR, separator),
                           Token(Token.ARGUMENT, value)])
        tokens.append(Token(Token.EOL, eol))
        return cls(tokens)

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
    def start(self):
        return self.get_option('start') if self.flavor == 'IN ENUMERATE' else None

    @property
    def mode(self):
        return self.get_option('mode') if self.flavor == 'IN ZIP' else None

    @property
    def fill(self):
        return self.get_option('fill') if self.flavor == 'IN ZIP' else None

    def validate(self, ctx: 'ValidationContext'):
        if not self.variables:
            self._add_error('no loop variables')
        if not self.flavor:
            self._add_error("no 'IN' or other valid separator")
        else:
            for var in self.variables:
                if not is_scalar_assign(var):
                    self._add_error(f"invalid loop variable '{var}'")
            if not self.values:
                self._add_error('no loop values')

    def _add_error(self, error):
        self.errors += (f'FOR loop has {error}.',)


class IfElseHeader(Statement):

    @property
    def condition(self):
        return None

    @property
    def assign(self):
        return None


@Statement.register
class IfHeader(IfElseHeader):
    type = Token.IF

    @classmethod
    def from_params(cls, condition, indent=FOUR_SPACES, separator=FOUR_SPACES, eol=EOL):
        tokens = [Token(Token.SEPARATOR, indent),
                  Token(cls.type),
                  Token(Token.SEPARATOR, separator),
                  Token(Token.ARGUMENT, condition)]
        if cls.type != Token.INLINE_IF:
            tokens.append(Token(Token.EOL, eol))
        return cls(tokens)

    @property
    def condition(self):
        values = self.get_values(Token.ARGUMENT)
        if len(values) != 1:
            return ', '.join(values) if values else None
        return values[0]

    def validate(self, ctx: 'ValidationContext'):
        conditions = len(self.get_tokens(Token.ARGUMENT))
        if conditions == 0:
            self.errors += (f'{self.type} must have a condition.',)
        if conditions > 1:
            self.errors += (f'{self.type} cannot have more than one condition.',)


@Statement.register
class InlineIfHeader(IfHeader):
    type = Token.INLINE_IF

    @property
    def assign(self):
        return self.get_values(Token.ASSIGN)


@Statement.register
class ElseIfHeader(IfHeader):
    type = Token.ELSE_IF


@Statement.register
class ElseHeader(IfElseHeader):
    type = Token.ELSE

    @classmethod
    def from_params(cls, indent=FOUR_SPACES, eol=EOL):
        return cls([
            Token(Token.SEPARATOR, indent),
            Token(Token.ELSE),
            Token(Token.EOL, eol)
        ])

    def validate(self, ctx: 'ValidationContext'):
        if self.get_tokens(Token.ARGUMENT):
            values = self.get_values(Token.ARGUMENT)
            self.errors += (f'ELSE does not accept arguments, got {seq2str(values)}.',)


class NoArgumentHeader(Statement):

    @classmethod
    def from_params(cls, indent=FOUR_SPACES, eol=EOL):
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
    def values(self):
        return self.get_values(Token.ARGUMENT)


@Statement.register
class TryHeader(NoArgumentHeader):
    type = Token.TRY


@Statement.register
class ExceptHeader(Statement):
    type = Token.EXCEPT

    @classmethod
    def from_params(cls, patterns=(), type=None, variable=None, indent=FOUR_SPACES,
                    separator=FOUR_SPACES, eol=EOL):
        tokens = [Token(Token.SEPARATOR, indent),
                  Token(Token.EXCEPT)]
        for pattern in patterns:
            tokens.extend([Token(Token.SEPARATOR, separator),
                           Token(Token.ARGUMENT, pattern)]),
        if type:
            tokens.extend([Token(Token.SEPARATOR, separator),
                           Token(Token.OPTION, f'type={type}')])
        if variable:
            tokens.extend([Token(Token.SEPARATOR, separator),
                           Token(Token.AS),
                           Token(Token.SEPARATOR, separator),
                           Token(Token.VARIABLE, variable)])
        tokens.append(Token(Token.EOL, eol))
        return cls(tokens)

    @property
    def patterns(self):
        return self.get_values(Token.ARGUMENT)

    @property
    def pattern_type(self):
        return self.get_option('type')

    @property
    def variable(self):
        return self.get_value(Token.VARIABLE)

    def validate(self, ctx: 'ValidationContext'):
        as_token = self.get_token(Token.AS)
        if as_token:
            variables = self.get_tokens(Token.VARIABLE)
            if not variables:
                self.errors += ("EXCEPT's AS requires variable.",)
            elif len(variables) > 1:
                self.errors += ("EXCEPT's AS accepts only one variable.",)
            elif not is_scalar_assign(variables[0].value):
                self.errors += (f"EXCEPT's AS variable '{variables[0].value}' is invalid.",)


@Statement.register
class FinallyHeader(NoArgumentHeader):
    type = Token.FINALLY


@Statement.register
class End(NoArgumentHeader):
    type = Token.END


@Statement.register
class WhileHeader(Statement):
    type = Token.WHILE

    @classmethod
    def from_params(cls, condition, limit=None, on_limit=None, on_limit_message=None,
                    indent=FOUR_SPACES, separator=FOUR_SPACES, eol=EOL):
        tokens = [Token(Token.SEPARATOR, indent),
                  Token(cls.type),
                  Token(Token.SEPARATOR, separator),
                  Token(Token.ARGUMENT, condition)]
        if limit:
            tokens.extend([Token(Token.SEPARATOR, indent),
                           Token(Token.OPTION, f'limit={limit}')])
        if on_limit_message:
            tokens.extend([Token(Token.SEPARATOR, indent),
                           Token(Token.OPTION,
                                 f'on_limit_message={on_limit_message}')])
        tokens.append(Token(Token.EOL, eol))
        return cls(tokens)

    @property
    def condition(self):
        return ', '.join(self.get_values(Token.ARGUMENT))

    @property
    def limit(self):
        return self.get_option('limit')

    @property
    def on_limit(self):
        return self.get_option('on_limit')

    @property
    def on_limit_message(self):
        return self.get_option('on_limit_message')

    def validate(self, ctx: 'ValidationContext'):
        values = self.get_values(Token.ARGUMENT)
        if len(values) > 1:
            self.errors += (f'WHILE cannot have more than one condition, got {seq2str(values)}.',)
        if self.on_limit and not self.limit:
            self.errors += ('WHILE on_limit option cannot be used without limit.',)


@Statement.register
class ReturnStatement(Statement):
    type = Token.RETURN_STATEMENT

    @property
    def values(self):
        return self.get_values(Token.ARGUMENT)

    @classmethod
    def from_params(cls, values=(), indent=FOUR_SPACES, separator=FOUR_SPACES, eol=EOL):
        tokens = [Token(Token.SEPARATOR, indent),
                  Token(Token.RETURN_STATEMENT)]
        for value in values:
            tokens.extend([Token(Token.SEPARATOR, separator),
                           Token(Token.ARGUMENT, value)])
        tokens.append(Token(Token.EOL, eol))
        return cls(tokens)

    def validate(self, ctx: 'ValidationContext'):
        if not ctx.in_keyword:
            self.errors += ('RETURN can only be used inside a user keyword.',)
        if ctx.in_finally:
            self.errors += ('RETURN cannot be used in FINALLY branch.',)


class LoopControl(NoArgumentHeader):

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
    def from_params(cls, comment, indent=FOUR_SPACES, eol=EOL):
        return cls([
            Token(Token.SEPARATOR, indent),
            Token(Token.COMMENT, comment),
            Token(Token.EOL, eol)
        ])


@Statement.register
class Config(Statement):
    type = Token.CONFIG

    @classmethod
    def from_params(cls, config, eol=EOL):
        return cls([
            Token(Token.CONFIG, config),
            Token(Token.EOL, eol)
        ])

    @property
    def language(self):
        value = self.get_value(Token.CONFIG)
        return Language.from_name(value[len('language:'):]) if value else None


@Statement.register
class Error(Statement):
    type = Token.ERROR
    _errors = ()

    @property
    def values(self):
        return [t.value for t in self.data_tokens]

    @property
    def errors(self):
        """Errors got from the underlying ``ERROR``token.

        Errors can be set also explicitly. When accessing errors, they are returned
        along with errors got from tokens.
        """
        tokens = self.get_tokens(Token.ERROR)
        return tuple(t.error for t in tokens) + self._errors

    @errors.setter
    def errors(self, errors):
        self._errors = tuple(errors)


class EmptyLine(Statement):
    type = Token.EOL

    @classmethod
    def from_params(cls, eol=EOL):
        return cls([Token(Token.EOL, eol)])
