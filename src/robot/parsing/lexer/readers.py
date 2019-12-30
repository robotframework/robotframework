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
from .tokens import EOL, EOS, Token


def get_tokens(source, data_only=False):
    reader = TestCaseFileReader(data_only)
    reader.input(source)
    return reader.get_tokens()


def get_resource_tokens(source, data_only=False):
    reader = ResourceFileReader(data_only)
    reader.input(source)
    return reader.get_tokens()


class BaseReader(object):
    context_class = None

    def __init__(self, data_only=False):
        self.lexer = FileLexer()
        self.statements = []
        self._data_only = data_only

    def input(self, source):
        content = self._read(source)
        for statement in Splitter().split(content, data_only=self._data_only):
            # Store all tokens but pass only DATA tokens to lexer.
            self.statements.append(statement)
            if self._data_only:
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
        if self._data_only:
            ignore = {Token.IGNORE, Token.COMMENT_HEADER, Token.COMMENT,
                      Token.OLD_FOR_INDENT}
        else:
            ignore = {Token.IGNORE}
        statements = self._handle_old_for(self.statements)
        if not self._data_only:
            statements = chain.from_iterable(
                self._split_trailing_comment_and_empty_lines(s)
                for s in statements
            )
        # Setting local variables, including 'type' below, is performance
        # optimization to avoid unnecessary lookups and attribute access.
        name_type = Token.NAME
        separator_or_eol_type = (Token.EOL, Token.SEPARATOR)
        for statement in statements:
            name_seen = False
            prev_token = None
            for token in statement:
                type = token.type     # Performance optimization.
                if type in ignore:
                    continue
                if name_seen and type not in separator_or_eol_type:
                    yield EOS.from_token(prev_token)
                    name_seen = False
                if type == name_type:
                    name_seen = True
                prev_token = token
                yield token
            if prev_token:
                yield EOS.from_token(prev_token)

    def _handle_old_for(self, statements):
        end_statement = [Token(Token.END)]
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

    def _split_trailing_comment_and_empty_lines(self, statement):
        lines = list(self._split_to_lines(statement))
        split_statements = []
        for line in reversed(lines):
            is_split = False
            for token in line:
                if token.type not in (token.IGNORE, token.SEPARATOR):
                    is_split = token.type in (token.EOL, token.COMMENT)
                    break
            if not is_split:
                break
            split_statements.append(line)
            lines.pop()
        yield list(chain.from_iterable(lines))
        for split in reversed(split_statements):
            yield split

    def _split_to_lines(self, statement):
        current = []
        eol = Token.EOL
        for token in statement:
            current.append(token)
            if token.type == eol:
                yield current
                current = []
        if current:
            if current[-1].type != eol:
                current.append(EOL.from_token(current[-1]))
            yield current


class TestCaseFileReader(BaseReader):
    context_class = TestCaseFileContext


class ResourceFileReader(BaseReader):
    context_class = ResourceFileContext
