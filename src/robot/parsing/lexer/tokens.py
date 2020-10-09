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

from robot.utils import py2to3
from robot.variables import VariableIterator


@py2to3
class Token(object):
    """Token representing piece of Robot Framework data.

    Each token has type, value, line number, column offset and end column
    offset in :attr:`type`, :attr:`value`, :attr:`lineno`, :attr:`col_offset`
    and :attr:`end_col_offset` attributes, respectively. Tokens representing
    error also have their error message in :attr:`error` attribute.

    Token types are declared as class attributes.
    """

    SETTING_HEADER = 'SETTING_HEADER'
    VARIABLE_HEADER = 'VARIABLE_HEADER'
    TESTCASE_HEADER = 'TESTCASE_HEADER'
    KEYWORD_HEADER = 'KEYWORD_HEADER'
    COMMENT_HEADER = 'COMMENT_HEADER'

    TESTCASE_NAME = 'TESTCASE_NAME'
    KEYWORD_NAME = 'KEYWORD_NAME'

    DOCUMENTATION = 'DOCUMENTATION'
    SUITE_SETUP = 'SUITE_SETUP'
    SUITE_TEARDOWN = 'SUITE_TEARDOWN'
    METADATA = 'METADATA'
    TEST_SETUP = 'TEST_SETUP'
    TEST_TEARDOWN = 'TEST_TEARDOWN'
    TEST_TEMPLATE = 'TEST_TEMPLATE'
    TEST_TIMEOUT = 'TEST_TIMEOUT'
    FORCE_TAGS = 'FORCE_TAGS'
    DEFAULT_TAGS = 'DEFAULT_TAGS'
    LIBRARY = 'LIBRARY'
    RESOURCE = 'RESOURCE'
    VARIABLES = 'VARIABLES'
    SETUP = 'SETUP'
    TEARDOWN = 'TEARDOWN'
    TEMPLATE = 'TEMPLATE'
    TIMEOUT = 'TIMEOUT'
    TAGS = 'TAGS'
    ARGUMENTS = 'ARGUMENTS'
    RETURN = 'RETURN'

    NAME = 'NAME'
    VARIABLE = 'VARIABLE'
    ARGUMENT = 'ARGUMENT'
    ASSIGN = 'ASSIGN'
    KEYWORD = 'KEYWORD'
    WITH_NAME = 'WITH_NAME'
    FOR = 'FOR'
    FOR_SEPARATOR = 'FOR_SEPARATOR'
    OLD_FOR_INDENT = 'OLD_FOR_INDENT'
    END = 'END'

    SEPARATOR = 'SEPARATOR'
    COMMENT = 'COMMENT'
    CONTINUATION = 'CONTINUATION'
    EOL = 'EOL'
    EOS = 'EOS'

    ERROR = 'ERROR'
    FATAL_ERROR = 'FATAL_ERROR'

    NON_DATA_TOKENS = (
        SEPARATOR,
        COMMENT,
        CONTINUATION,
        EOL,
        EOS
    )
    SETTING_TOKENS = (
        DOCUMENTATION,
        SUITE_SETUP,
        SUITE_TEARDOWN,
        METADATA,
        TEST_SETUP,
        TEST_TEARDOWN,
        TEST_TEMPLATE,
        TEST_TIMEOUT,
        FORCE_TAGS,
        DEFAULT_TAGS,
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
    )
    HEADER_TOKENS = (
        SETTING_HEADER,
        VARIABLE_HEADER,
        TESTCASE_HEADER,
        KEYWORD_HEADER,
        COMMENT_HEADER
    )
    ALLOW_VARIABLES = (
        NAME,
        ARGUMENT,
        TESTCASE_NAME,
        KEYWORD_NAME
    )

    __slots__ = ['type', 'value', 'lineno', 'col_offset', 'error']

    def __init__(self, type=None, value='', lineno=-1, col_offset=-1, error=None):
        self.type = type
        self.value = value
        self.lineno = lineno
        self.col_offset = col_offset
        self.error = error

    @property
    def end_col_offset(self):
        if self.col_offset == -1:
            return -1
        return self.col_offset + len(self.value)

    def set_error(self, error, fatal=False):
        self.type = Token.ERROR if not fatal else Token.FATAL_ERROR
        self.error = error

    def tokenize_variables(self):
        """Tokenizes possible variables in token value.

        Yields the token itself if the token does not allow variables (see
        :attr:`Token.ALLOW_VARIABLES`) or its value does not contain
        variables. Otherwise yields variable tokens as well as tokens
        before, after, or between variables so that they have the same
        type as the original token.
        """
        if self.type not in Token.ALLOW_VARIABLES:
            return self._tokenize_no_variables()
        variables = VariableIterator(self.value)
        if not variables:
            return self._tokenize_no_variables()
        return self._tokenize_variables(variables)

    def _tokenize_no_variables(self):
        yield self

    def _tokenize_variables(self, variables):
        lineno = self.lineno
        col_offset = self.col_offset
        remaining = ''
        for before, variable, remaining in variables:
            if before:
                yield Token(self.type, before, lineno, col_offset)
                col_offset += len(before)
            yield Token(Token.VARIABLE, variable, lineno, col_offset)
            col_offset += len(variable)
        if remaining:
            yield Token(self.type, remaining, lineno, col_offset)

    def __unicode__(self):
        return self.value

    def __repr__(self):
        error = '' if not self.error else ', %r' % self.error
        return 'Token(%s, %r, %s, %s%s)' % (self.type, self.value,
                                            self.lineno, self.col_offset,
                                            error)

    def __eq__(self, other):
        if not isinstance(other, Token):
            return False
        return (self.type == other.type and
                self.value == other.value and
                self.lineno == other.lineno and
                self.col_offset == other.col_offset and
                self.error == other.error)

    def __ne__(self, other):
        return not self == other


class EOS(Token):
    """Token representing end of statement."""
    __slots__ = []

    def __init__(self, lineno=-1, col_offset=-1):
        Token.__init__(self, Token.EOS, '', lineno, col_offset)

    @classmethod
    def from_token(cls, token):
        return EOS(lineno=token.lineno, col_offset=token.end_col_offset)
