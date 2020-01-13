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

from itertools import chain

from robot.errors import DataError
from robot.utils import get_error_message, FileReader

from .context import TestCaseFileContext, ResourceFileContext
from .lexers import FileLexer
from .splitter import Splitter
from .tokens import EOS, Token


def get_tokens(source, data_only=False):
    """Parses the given source to tokens.

    :param source: The source where to read the data. Can be a path to
        a source file as a string or as ``pathlib.Path`` object, an already
        opened file object, or Unicode text containing the date directly.
        Source files must be UTF-8 encoded.
    :param data_only: When ``False`` (default), returns all tokens. When set
        to ``True``, omits separators, comments, continuations, and other
        non-data tokens.

    Returns a generator that yields :class:`~robot.parsing.lexer.tokens.Token`
    instances.
    """
    reader = TestCaseFileReader(data_only)
    reader.input(source)
    return reader.get_tokens()


def get_resource_tokens(source, data_only=False):
    """Parses the given source to resource file tokens.

    Otherwise same as :func:`get_tokens` but the source is considered to be
    a resource file. This affects, for example, what settings are valid.
    """
    reader = ResourceFileReader(data_only)
    reader.input(source)
    return reader.get_tokens()


# TODO: Rename classes and module from readers to tokenizers?

class BaseReader(object):
    context_class = None

    def __init__(self, data_only=False):
        self.data_only = data_only
        self.lexer = FileLexer()
        self.statements = []

    def input(self, source):
        content = self._read(source)
        for statement in Splitter().split(content, data_only=self.data_only):
            # Store all tokens but pass only DATA tokens to lexer.
            self.statements.append(statement)
            if self.data_only:
                data = statement[:]
            else:
                data = [t for t in statement if t.type == t.DATA]
            self.lexer.input(data)

    def _read(self, source):
        try:
            with FileReader(source, accept_text=True) as reader:
                return reader.read()
        except:
            raise DataError(get_error_message())

    def get_tokens(self):
        self.lexer.lex(self.context_class())
        if self.data_only:
            ignore = {Token.IGNORE, Token.COMMENT_HEADER, Token.COMMENT,
                      Token.OLD_FOR_INDENT}
        else:
            ignore = {Token.IGNORE}
        statements = self._handle_old_for(self.statements)
        if not self.data_only:
            statements = chain.from_iterable(
                self._split_trailing_commented_and_empty_lines(s)
                for s in statements
            )
        # Setting local variables is performance optimization to avoid
        # unnecessary lookups and attribute access.
        name_type = Token.NAME
        separator_type = Token.SEPARATOR
        eol_type = Token.EOL
        for statement in statements:
            name_seen = False
            separator_after_name = None
            prev_token = None
            for token in statement:
                type = token.type     # Performance optimization.
                if type in ignore:
                    continue
                if name_seen:
                    if type == separator_type:
                        separator_after_name = token
                        continue
                    if type != eol_type:
                        yield EOS.from_token(prev_token)
                    if separator_after_name:
                        yield separator_after_name
                    name_seen = False
                if type == name_type:
                    name_seen = True
                prev_token = token
                yield token
            if prev_token:
                yield EOS.from_token(prev_token)

    def _handle_old_for(self, statements):
        end_statement = [Token(Token.SEPARATOR), Token(Token.END)]
        old_for = False
        for statement in statements:
            marker = self._get_first_data_token(statement)
            if marker:
                if marker.type == Token.OLD_FOR_INDENT:
                    old_for = True
                elif old_for:
                    if marker.type == Token.END:
                        # We get here if block has been indented with '\' but
                        # there is also 'END'. The former is deprecated and
                        # removing the value causes a deprecation warning.
                        marker.value = ''
                    else:
                        yield end_statement
                    old_for = False
            yield statement
        if old_for:
            yield end_statement

    def _get_first_data_token(self, statement):
        for token in statement:
            if token.type not in Token.NON_DATA_TOKENS:
                return token
        return None

    def _split_trailing_commented_and_empty_lines(self, statement):
        lines = list(self._split_to_lines(statement))
        commented_or_empty = []
        for line in reversed(lines):
            if not self._is_commented_or_empty(line):
                break
            commented_or_empty.append(line)
            lines.pop()
        yield list(chain.from_iterable(lines))
        for line in reversed(commented_or_empty):
            yield line

    def _split_to_lines(self, statement):
        current = []
        for token in statement:
            current.append(token)
            if token.type == Token.EOL:
                yield current
                current = []
        if current:
            yield current

    def _is_commented_or_empty(self, line):
        separator_or_ignore = (Token.SEPARATOR, Token.IGNORE)
        comment_or_eol = (Token.COMMENT, Token.EOL)
        for token in line:
            if token.type not in separator_or_ignore:
                return token.type in comment_or_eol
        return False


class TestCaseFileReader(BaseReader):
    context_class = TestCaseFileContext


class ResourceFileReader(BaseReader):
    context_class = ResourceFileContext
