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

from ..lexer import Token
from ..model import TestCase, Keyword, For, If


class Parser(object):
    """Base class for parsers."""

    def __init__(self, model):
        self.model = model

    def handles(self, statement):
        raise NotImplementedError

    def parse(self, statement):
        raise NotImplementedError


class BlockParser(Parser):
    unhandled_tokens = Token.HEADER_TOKENS | frozenset((Token.TESTCASE_NAME,
                                                        Token.KEYWORD_NAME))

    def __init__(self, model):
        Parser.__init__(self, model)
        self.nested_parsers = {Token.FOR: ForParser, Token.IF: IfParser}

    def handles(self, statement):
        return statement.type not in self.unhandled_tokens

    def parse(self, statement):
        parser_class = self.nested_parsers.get(statement.type)
        if parser_class:
            parser = parser_class(statement)
            self.model.body.append(parser.model)
            return parser
        self.model.body.append(statement)
        return None


class TestCaseParser(BlockParser):

    def __init__(self, header):
        BlockParser.__init__(self, TestCase(header))


class KeywordParser(BlockParser):

    def __init__(self, header):
        BlockParser.__init__(self, Keyword(header))


class NestedBlockParser(BlockParser):

    def handles(self, statement):
        return BlockParser.handles(self, statement) and not self.model.end

    def parse(self, statement):
        if statement.type == Token.END:
            self.model.end = statement
            return None
        return BlockParser.parse(self, statement)


class ForParser(NestedBlockParser):

    def __init__(self, header):
        NestedBlockParser.__init__(self, For(header))


class IfParser(NestedBlockParser):

    def __init__(self, header):
        NestedBlockParser.__init__(self, If(header))

    def parse(self, statement):
        if statement.type in (Token.ELSE_IF, Token.ELSE):
            parser = OrElseParser(statement)
            self.model.orelse = parser.model
            return parser
        return NestedBlockParser.parse(self, statement)


class OrElseParser(IfParser):

    def handles(self, statement):
        return IfParser.handles(self, statement) and statement.type != Token.END
