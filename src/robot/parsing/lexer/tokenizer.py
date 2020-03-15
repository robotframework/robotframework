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

from robot.utils import rstrip

from .tokens import Token


class Tokenizer(object):
    _space_splitter = re.compile(r'(\s{2,}|\t)', re.UNICODE)
    _pipe_splitter = re.compile(r'((?:\A|\s+)\|(?:\s+|\Z))', re.UNICODE)

    def tokenize(self, data, data_only=False):
        current = []
        for lineno, line in enumerate(data.splitlines(not data_only), start=1):
            tokens = self._tokenize_line(line, lineno, not data_only)
            tokens, starts_new = self._cleanup_tokens(tokens, data_only)
            if starts_new:
                if current:
                    yield current
                current = tokens
            else:
                current.extend(tokens)
        yield current

    def _tokenize_line(self, line, lineno, include_separators=True):
        # Performance optimized code.
        tokens = []
        append = tokens.append
        offset = 0
        if line[:1] != '|':
            splitter = self._split_from_spaces
        else:
            splitter = self._split_from_pipes
        for value, is_data in splitter(rstrip(line)):
            if is_data:
                append(Token(None, value, lineno, offset))
            elif include_separators:
                append(Token(Token.SEPARATOR, value, lineno, offset))
            offset += len(value)
        if include_separators:
            trailing_whitespace = line[len(rstrip(line)):]
            append(Token(Token.EOL, trailing_whitespace, lineno, offset))
        return tokens

    def _split_from_spaces(self, line):
        is_data = True
        for value in self._space_splitter.split(line):
            yield value, is_data
            is_data = not is_data

    def _split_from_pipes(self, line):
        splitter = self._pipe_splitter
        _, separator, rest = splitter.split(line, 1)
        yield separator, False
        while splitter.search(rest):
            token, separator, rest = splitter.split(rest, 1)
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
            if token.type is None:
                if token.value.startswith('#') or commented:
                    token.type = Token.COMMENT
                    commented = True
                elif token.value:
                    has_data = True
        return has_data

    def _handle_continuation(self, tokens):
        for token in tokens:
            if token.value == '...' and token.type is None:
                token.type = Token.CONTINUATION
                return True
            elif token.value and token.type != Token.SEPARATOR:
                return False
        return False

    def _remove_trailing_empty(self, tokens):
        # list() needed w/ IronPython, otherwise reversed() alone is enough.
        # https://github.com/IronLanguages/ironpython2/issues/699
        for token in reversed(list(tokens)):
            if not token.value and token.type != Token.EOL:
                tokens.remove(token)
            elif token.type is None:
                break

    def _remove_leading_empty(self, tokens):
        data_or_continuation = (None, Token.CONTINUATION)
        for token in list(tokens):
            if not token.value:
                tokens.remove(token)
            elif token.type in data_or_continuation:
                break

    def _ensure_data_after_continuation(self, tokens):
        if not any(t.type is None for t in tokens):
            cont = self._find_continuation(tokens)
            token = Token(lineno=cont.lineno, col_offset=cont.end_col_offset)
            tokens.insert(tokens.index(cont) + 1, token)

    def _find_continuation(self, tokens):
        for token in tokens:
            if token.type == Token.CONTINUATION:
                return token

    def _remove_non_data(self, tokens):
        return [t for t in tokens if t.type is None]
