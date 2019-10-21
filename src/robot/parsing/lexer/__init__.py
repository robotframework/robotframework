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

from .context import TestCaseFileContext, ResourceFileContext
from .lexers import FileLexer
from .splitter import Splitter
from .tokens import EOS, Token


class BaseLexer(object):
    context_class = None

    def __init__(self, data_only=True):
        self.lexer = FileLexer()
        self.statements = []
        self._data_only = data_only

    def input(self, content):
        for statement in Splitter().split(content, data_only=self._data_only):
            if not statement:
                continue
            self.statements.append(statement)
            if self._data_only:
                data = statement[:]
            else:
                data = [t for t in statement if t.type == t.DATA]
            self.lexer.input(data)

    def get_tokens(self):
        self.lexer.lex(self.context_class(self._data_only))
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
        for statement in statements:
            name_token = last_token = None
            for token in statement:
                if token.type in ignore:
                    continue
                if name_token:
                    yield EOS.from_token(name_token)
                    name_token = None
                if token.type == Token.NAME:
                    name_token = token
                last_token = token
                yield token
            if last_token:
                yield EOS.from_token(last_token)

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
        for tok in statement:
            current.append(tok)
            if tok.type == tok.EOL:
                yield current
                current = []
        if current:
            yield current


class TestCaseFileLexer(BaseLexer):
    context_class = TestCaseFileContext


class ResourceFileLexer(BaseLexer):
    context_class = ResourceFileContext
