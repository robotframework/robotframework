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
from ..model import TestCase, Keyword, ForLoop
from ..model.blocks import IfBlock


class Parser(object):
    """Base class for parsers."""

    def __init__(self, model):
        self.model = model

    def handles(self, statement):
        raise NotImplementedError

    def parse(self, statement):
        raise NotImplementedError


class StepsParser(Parser):

    def __init__(self, model, unhandled_tokens):
        Parser.__init__(self, model)
        self._subsection_parser_classes = {Token.FOR: ForLoopParser, Token.IF: IfParser}
        self._unhandled_tokens = unhandled_tokens

    def handles(self, statement):
        return statement.type not in self._unhandled_tokens

    def parse(self, statement):
        parser_class = self._subsection_parser_classes.get(statement.type)
        if parser_class:
            parser = parser_class(statement)
            self.model.body.append(parser.model)
            return parser
        self.model.body.append(statement)


def TestCaseParser(header):
    return StepsParser(TestCase(header), Token.HEADER_TOKENS + (Token.TESTCASE_NAME,))


def KeywordParser(header):
    return StepsParser(Keyword(header), Token.HEADER_TOKENS + (Token.KEYWORD_NAME,))


class StepsWithEndParser(StepsParser):

    def __init__(self, model):
        StepsParser.__init__(self, model, Token.HEADER_TOKENS + (Token.TESTCASE_NAME, Token.KEYWORD_NAME))

    def handles(self, statement):
        if self.model.end:
            return False
        return StepsParser.handles(self, statement)

    def parse(self, statement):
        if statement.type == Token.END:
            self.model.end = statement
            return
        return StepsParser.parse(self, statement)


def ForLoopParser(header):
    return StepsWithEndParser(ForLoop(header))
