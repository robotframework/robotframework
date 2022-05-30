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


class Tokenizer:
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
        if line[:1] == '|' and line[:2].strip() == '|':
            splitter = self._split_from_pipes
        else:
            splitter = self._split_from_spaces
        for value, is_data in splitter(line.rstrip()):
            if is_data:
                append(Token(None, value, lineno, offset))
            elif include_separators:
                append(Token(Token.SEPARATOR, value, lineno, offset))
            offset += len(value)
        if include_separators:
            trailing_whitespace = line[len(line.rstrip()):]
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
        # Handle comments
        has_data = False

        iter_in_tokens = iter(tokens)
        for token in iter_in_tokens:
            if token.type is None:
                # lstrip needed to strip possible leading space from first token.
                # Other leading/trailing spaces have been consumed as separators.
                value = token.value.lstrip()
                if value:
                    if value[0] == '#':
                        # When we find a #, consume iterator and mark remaining
                        # tokens as comments.
                        token.type = Token.COMMENT
                        for token in iter_in_tokens:
                            if token.type is None:
                                token.type = Token.COMMENT
                    else:
                        has_data = True

        # Handle continuation
        continues = False
        for token in tokens:
            if token.value == '...' and token.type is None:
                token.type = Token.CONTINUATION
                continues = True
                break
            elif token.value and token.type != Token.SEPARATOR:
                continues = False
                break

        # Remove trailing empty
        for token in reversed(tokens):
            if not token.value and token.type != Token.EOL:
                tokens.remove(token)
            elif token.type is None:
                break

        if continues:
            self._remove_leading_empty(tokens)
            self._ensure_data_after_continuation(tokens)
        if data_only:
            # Remove non data
            tokens = [t for t in tokens if t.type is None]
        return tokens, has_data and not continues

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

