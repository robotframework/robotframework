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

from collections.abc import Iterator
from typing import cast, List

from robot.variables import VariableMatches


# Type alias to ease typing elsewhere
StatementTokens = List['Token']


class Token:
    """Token representing piece of Robot Framework data.

    Each token has type, value, line number, column offset and end column
    offset in :attr:`type`, :attr:`value`, :attr:`lineno`, :attr:`col_offset`
    and :attr:`end_col_offset` attributes, respectively. Tokens representing
    error also have their error message in :attr:`error` attribute.

    Token types are declared as class attributes such as :attr:`SETTING_HEADER`
    and :attr:`EOL`. Values of these constants have changed slightly in Robot
    Framework 4.0, and they may change again in the future. It is thus safer
    to use the constants, not their values, when types are needed. For example,
    use ``Token(Token.EOL)`` instead of ``Token('EOL')`` and
    ``token.type == Token.EOL`` instead of ``token.type == 'EOL'``.

    If :attr:`value` is not given and :attr:`type` is a special marker like
    :attr:`IF` or `:attr:`EOL`, the value is set automatically.
    """

    SETTING_HEADER = 'SETTING HEADER'
    VARIABLE_HEADER = 'VARIABLE HEADER'
    TESTCASE_HEADER = 'TESTCASE HEADER'
    TASK_HEADER = 'TASK HEADER'
    KEYWORD_HEADER = 'KEYWORD HEADER'
    COMMENT_HEADER = 'COMMENT HEADER'
    INVALID_HEADER = 'INVALID HEADER'
    FATAL_INVALID_HEADER = 'FATAL INVALID HEADER'    # TODO: Remove in RF 8.

    TESTCASE_NAME = 'TESTCASE NAME'
    KEYWORD_NAME = 'KEYWORD NAME'
    SUITE_NAME = 'SUITE NAME'
    DOCUMENTATION = 'DOCUMENTATION'
    SUITE_SETUP = 'SUITE SETUP'
    SUITE_TEARDOWN = 'SUITE TEARDOWN'
    METADATA = 'METADATA'
    TEST_SETUP = 'TEST SETUP'
    TEST_TEARDOWN = 'TEST TEARDOWN'
    TEST_TEMPLATE = 'TEST TEMPLATE'
    TEST_TIMEOUT = 'TEST TIMEOUT'
    TEST_TAGS = 'TEST TAGS'
    FORCE_TAGS = TEST_TAGS    # TODO: Remove in RF 8.
    DEFAULT_TAGS = 'DEFAULT TAGS'
    KEYWORD_TAGS = 'KEYWORD TAGS'
    LIBRARY = 'LIBRARY'
    RESOURCE = 'RESOURCE'
    VARIABLES = 'VARIABLES'
    SETUP = 'SETUP'
    TEARDOWN = 'TEARDOWN'
    TEMPLATE = 'TEMPLATE'
    TIMEOUT = 'TIMEOUT'
    TAGS = 'TAGS'
    ARGUMENTS = 'ARGUMENTS'
    RETURN = 'RETURN'          # TODO: Change to mean RETURN statement in RF 8.
    RETURN_SETTING = RETURN    # TODO: Remove in RF 8.

    AS = 'AS'
    WITH_NAME = AS             # TODO: Remove in RF 8.

    NAME = 'NAME'
    VARIABLE = 'VARIABLE'
    ARGUMENT = 'ARGUMENT'
    ASSIGN = 'ASSIGN'
    KEYWORD = 'KEYWORD'
    FOR = 'FOR'
    FOR_SEPARATOR = 'FOR SEPARATOR'
    END = 'END'
    IF = 'IF'
    INLINE_IF = 'INLINE IF'
    ELSE_IF = 'ELSE IF'
    ELSE = 'ELSE'
    TRY = 'TRY'
    EXCEPT = 'EXCEPT'
    FINALLY = 'FINALLY'
    WHILE = 'WHILE'
    VAR = 'VAR'
    RETURN_STATEMENT = 'RETURN STATEMENT'
    CONTINUE = 'CONTINUE'
    BREAK = 'BREAK'
    OPTION = 'OPTION'
    GROUP = 'GROUP'

    SEPARATOR = 'SEPARATOR'
    COMMENT = 'COMMENT'
    CONTINUATION = 'CONTINUATION'
    CONFIG = 'CONFIG'
    EOL = 'EOL'
    EOS = 'EOS'
    ERROR = 'ERROR'
    FATAL_ERROR = 'FATAL ERROR'    # TODO: Remove in RF 8.

    NON_DATA_TOKENS = frozenset((
        SEPARATOR,
        COMMENT,
        CONTINUATION,
        EOL,
        EOS
    ))
    SETTING_TOKENS = frozenset((
        DOCUMENTATION,
        SUITE_NAME,
        SUITE_SETUP,
        SUITE_TEARDOWN,
        METADATA,
        TEST_SETUP,
        TEST_TEARDOWN,
        TEST_TEMPLATE,
        TEST_TIMEOUT,
        TEST_TAGS,
        DEFAULT_TAGS,
        KEYWORD_TAGS,
        LIBRARY,
        RESOURCE,
        VARIABLES,
        SETUP,
        TEARDOWN,
        TEMPLATE,
        TIMEOUT,
        TAGS,
        ARGUMENTS,
        RETURN
    ))
    HEADER_TOKENS = frozenset((
        SETTING_HEADER,
        VARIABLE_HEADER,
        TESTCASE_HEADER,
        TASK_HEADER,
        KEYWORD_HEADER,
        COMMENT_HEADER,
        INVALID_HEADER
    ))
    ALLOW_VARIABLES = frozenset((
        NAME,
        ARGUMENT,
        TESTCASE_NAME,
        KEYWORD_NAME
    ))
    __slots__ = ['type', 'value', 'lineno', 'col_offset', 'error',
                 '_add_eos_before', '_add_eos_after']

    def __init__(self, type: 'str|None' = None, value: 'str|None' = None,
                 lineno: int = -1, col_offset: int = -1, error: 'str|None' = None):
        self.type = type
        if value is None:
            value = {
                Token.IF: 'IF', Token.INLINE_IF: 'IF', Token.ELSE_IF: 'ELSE IF',
                Token.ELSE: 'ELSE', Token.FOR: 'FOR', Token.WHILE: 'WHILE',
                Token.TRY: 'TRY', Token.EXCEPT: 'EXCEPT', Token.FINALLY: 'FINALLY',
                Token.END: 'END', Token.VAR: 'VAR', Token.CONTINUE: 'CONTINUE',
                Token.BREAK: 'BREAK', Token.RETURN_STATEMENT: 'RETURN',
                Token.CONTINUATION: '...', Token.EOL: '\n', Token.WITH_NAME: 'AS',
                Token.AS: 'AS', Token.GROUP: 'GROUP'
            }.get(type, '')    # type: ignore
        self.value = cast(str, value)
        self.lineno = lineno
        self.col_offset = col_offset
        self.error = error
        # Used internally be lexer to indicate that EOS is needed before/after.
        self._add_eos_before = False
        self._add_eos_after = False

    @property
    def end_col_offset(self) -> int:
        if self.col_offset == -1:
            return -1
        return self.col_offset + len(self.value)

    def set_error(self, error: str):
        self.type = Token.ERROR
        self.error = error

    def tokenize_variables(self) -> 'Iterator[Token]':
        """Tokenizes possible variables in token value.

        Yields the token itself if the token does not allow variables (see
        :attr:`Token.ALLOW_VARIABLES`) or its value does not contain
        variables. Otherwise, yields variable tokens as well as tokens
        before, after, or between variables so that they have the same
        type as the original token.
        """
        if self.type not in Token.ALLOW_VARIABLES:
            return self._tokenize_no_variables()
        matches = VariableMatches(self.value)
        if not matches:
            return self._tokenize_no_variables()
        return self._tokenize_variables(matches)

    def _tokenize_no_variables(self) -> 'Iterator[Token]':
        yield self

    def _tokenize_variables(self, matches) -> 'Iterator[Token]':
        lineno = self.lineno
        col_offset = self.col_offset
        after = ''
        for match in matches:
            if match.before:
                yield Token(self.type, match.before, lineno, col_offset)
            yield Token(Token.VARIABLE, match.match, lineno, col_offset + match.start)
            col_offset += match.end
            after = match.after
        if after:
            yield Token(self.type, after, lineno, col_offset)

    def __str__(self) -> str:
        return self.value

    def __repr__(self) -> str:
        typ = self.type.replace(' ', '_') if self.type else 'None'
        error = '' if not self.error else f', {self.error!r}'
        return f'Token({typ}, {self.value!r}, {self.lineno}, {self.col_offset}{error})'

    def __eq__(self, other) -> bool:
        return (isinstance(other, Token)
                and self.type == other.type
                and self.value == other.value
                and self.lineno == other.lineno
                and self.col_offset == other.col_offset
                and self.error == other.error)


class EOS(Token):
    """Token representing end of a statement."""
    __slots__ = []

    def __init__(self, lineno: int = -1, col_offset: int = -1):
        super().__init__(Token.EOS, '', lineno, col_offset)

    @classmethod
    def from_token(cls, token: Token, before: bool = False) -> 'EOS':
        col_offset = token.col_offset if before else token.end_col_offset
        return cls(token.lineno, col_offset)


class END(Token):
    """Token representing END token used to signify block ending.

    Virtual END tokens have '' as their value, with "real" END tokens the
    value is 'END'.
    """
    __slots__ = []

    def __init__(self, lineno: int = -1, col_offset: int = -1, virtual: bool = False):
        value = 'END' if not virtual else ''
        super().__init__(Token.END, value, lineno, col_offset)

    @classmethod
    def from_token(cls, token: Token, virtual: bool = False) -> 'END':
        return cls(token.lineno, token.end_col_offset, virtual)
