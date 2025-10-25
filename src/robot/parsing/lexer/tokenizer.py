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
from collections.abc import Iterator

from .tokens import Token


class Tokenizer:
    _space_splitter = re.compile(r"(\s{2,}|\t)", re.UNICODE)
    _pipe_splitter = re.compile(r"((?:\A|\s+)\|(?:\s+|\Z))", re.UNICODE)

    def tokenize(self, data: str, data_only: bool = False) -> "Iterator[list[Token]]":
        current: "list[Token]" = []
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

    def _tokenize_line(self, line: str, lineno: int, include_separators: bool):
        # Performance optimized code.
        tokens: "list[Token]" = []
        append = tokens.append
        offset = 0
        if line[:1] == "|" and line[:2].strip() == "|":
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
            trailing_whitespace = line[len(line.rstrip()) :]
            append(Token(Token.EOL, trailing_whitespace, lineno, offset))
        return tokens

    def _split_from_spaces(self, line: str) -> "Iterator[tuple[str, bool]]":
        is_data = True
        for value in self._space_splitter.split(line):
            yield value, is_data
            is_data = not is_data

    def _split_from_pipes(self, line) -> "Iterator[tuple[str, bool]]":
        splitter = self._pipe_splitter
        _, separator, rest = splitter.split(line, 1)
        yield separator, False
        while splitter.search(rest):
            token, separator, rest = splitter.split(rest, 1)
            yield token, True
            yield separator, False
        yield rest, True

    def _cleanup_tokens(self, tokens: "list[Token]", data_only: bool):
        has_data, comments, continues = self._handle_comments_and_continuation(tokens)
        self._remove_trailing_empty(tokens)
        if continues:
            self._remove_leading_empty(tokens)
            if not has_data:
                self._ensure_data_after_continuation(tokens)
            starts_new = False
        else:
            starts_new = has_data
        if data_only and (comments or continues):
            tokens = [t for t in tokens if t.type is None]
        return tokens, starts_new

    def _handle_comments_and_continuation(
        self,
        tokens: "list[Token]",
    ) -> "tuple[bool, bool, bool]":
        has_data = False
        commented = False
        continues = False
        for index, token in enumerate(tokens):
            if token.type is None:
                # lstrip needed to strip possible leading space from first token.
                # Other leading/trailing spaces have been consumed as separators.
                value = token.value if index else token.value.lstrip()
                if commented:
                    token.type = Token.COMMENT
                elif value:
                    if value[0] == "#":
                        token.type = Token.COMMENT
                        commented = True
                    elif not has_data:
                        if value == "..." and not continues:
                            token.type = Token.CONTINUATION
                            continues = True
                        else:
                            has_data = True
        return has_data, commented, continues

    def _remove_trailing_empty(self, tokens: "list[Token]"):
        for token in reversed(tokens):
            if not token.value and token.type != Token.EOL:
                tokens.remove(token)
            elif token.type is None:
                break

    def _remove_leading_empty(self, tokens: "list[Token]"):
        data_or_continuation = (None, Token.CONTINUATION)
        for token in list(tokens):
            if not token.value:
                tokens.remove(token)
            elif token.type in data_or_continuation:
                break

    def _ensure_data_after_continuation(self, tokens: "list[Token]"):
        cont = self._find_continuation(tokens)
        token = Token(lineno=cont.lineno, col_offset=cont.end_col_offset)
        tokens.insert(tokens.index(cont) + 1, token)

    def _find_continuation(self, tokens: "list[Token]") -> Token:
        for token in tokens:
            if token.type == Token.CONTINUATION:
                return token
        raise ValueError("Continuation not found.")
