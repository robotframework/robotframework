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

import re

from .tokens import Token


class Splitter(object):
    # TODO: Split using spaces but normalize non-break space.
    _space_splitter = re.compile(r'(\s{2,}|\t)', re.UNICODE)
    _pipe_splitter = re.compile(r'((?:\A|\s+)\|(?:\s+|\Z))', re.UNICODE)
    _trailing_whitespace = re.compile(r'\s+$', re.UNICODE)

    def split(self, data, data_only=False):
        current = None
        for lineno, line in enumerate(data.splitlines(not data_only), start=1):
            tokens = list(self._split_line(line, lineno, data_only))
            tokens, starts_new = self._cleanup_tokens(tokens, data_only)
            if starts_new:
                if current is not None:
                    yield current
                current = tokens
            else:
                current.extend(tokens)
        if current is not None:
            yield current

    def _split_line(self, line, lineno, data_only=False):
        if line[:1] != '|':
            splitter = self._split_from_spaces
        else:
            splitter = self._split_from_pipes
        columnno = 1
        data, sepa = Token.DATA, Token.SEPARATOR
        trailing_whitespace = self._trailing_whitespace.search(line)
        for value, is_data in splitter(line.rstrip()):
            if is_data or not data_only:
                yield Token(data if is_data else sepa, value, lineno, columnno)
            columnno += len(value)
        if trailing_whitespace and not data_only:
            yield Token(sepa, trailing_whitespace.group(), lineno, columnno)

    def _split_from_spaces(self, line):
        for index, value in enumerate(self._space_splitter.split(line)):
            yield value, index % 2 == 0

    def _split_from_pipes(self, line):
        _, separator, rest = self._pipe_splitter.split(line, 1)
        yield separator, False
        while self._pipe_splitter.search(rest):
            token, separator, rest = self._pipe_splitter.split(rest, 1)
            yield token, True
            yield separator, False
        yield rest, True

    def _cleanup_tokens(self, tokens, data_only):
        has_data = self._handle_comments(tokens)
        continues = self._handle_continuation(tokens)
        self._remove_trailing_empty(tokens)
        if continues:
            self._remove_leading_empty(tokens)
            self._ensure_data_after_continuation(tokens)
        if data_only:
            tokens = self._remove_non_data(tokens)
        return tokens, has_data and not continues

    def _handle_comments(self, tokens):
        has_data = False
        commented = False
        for token in tokens:
            if token.type == token.DATA:
                if token.value.startswith('#') or commented:
                    token.type = token.COMMENT
                    commented = True
                elif token.value:
                    has_data = True
        return has_data

    def _handle_continuation(self, tokens):
        for token in tokens:
            if token.value == '...' and token.type == token.DATA:
                token.type = token.CONTINUATION
                return True
            elif token.value and token.type != token.SEPARATOR:
                return False
        return False

    def _remove_trailing_empty(self, tokens):
        for token in reversed(tokens):
            if not token.value:
                tokens.remove(token)
            elif token.type == token.DATA:
                return

    def _remove_leading_empty(self, tokens):
        # TODO: dropwhile - also above
        for token in list(tokens):
            if not token.value:
                tokens.remove(token)
            elif token.type in (token.DATA, token.CONTINUATION):
                return

    def _ensure_data_after_continuation(self, tokens):
        if not any(t.type == t.DATA for t in tokens):
            cont = self._find_continuation(tokens)
            data = Token(Token.DATA, '', cont.lineno, cont.columnno + 3)
            tokens.insert(tokens.index(cont) + 1, data)

    def _find_continuation(self, tokens):
        for token in tokens:
            if token.type == token.CONTINUATION:
                return token

    def _remove_non_data(self, tokens):
        return [t for t in tokens if t.type == t.DATA]
