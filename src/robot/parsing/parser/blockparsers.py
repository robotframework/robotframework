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


class Parser(object):
    """Base class for parsers."""

    def __init__(self, model):
        self.model = model

    def handles(self, statement):
        raise NotImplementedError

    def parse(self, statement):
        raise NotImplementedError


class TestCaseParser(Parser):

    def __init__(self, header):
        Parser.__init__(self, TestCase(header))

    def handles(self, statement):
        if statement.type == Token.TESTCASE_NAME:
            return False
        return statement.type not in Token.HEADER_TOKENS

    def parse(self, statement):
        if statement.type == Token.FOR:
            parser = ForLoopParser(statement)
            model = parser.model
        else:
            parser = None
            model = statement
        self.model.body.append(model)
        return parser


class KeywordParser(Parser):

    def __init__(self, header):
        Parser.__init__(self, Keyword(header))

    def handles(self, statement):
        if statement.type == Token.KEYWORD_NAME:
            return False
        return statement.type not in Token.HEADER_TOKENS

    def parse(self, statement):
        if statement.type == Token.FOR:
            parser = ForLoopParser(statement)
            model = parser.model
        else:
            parser = None
            model = statement
        self.model.body.append(model)
        return parser


class ForLoopParser(Parser):

    def __init__(self, header):
        Parser.__init__(self, ForLoop(header))
        self.end_seen = False

    def handles(self, statement):
        if self.end_seen:
            return False
        name_tokens = (Token.TESTCASE_NAME, Token.KEYWORD_NAME)
        return statement.type not in Token.HEADER_TOKENS + name_tokens

    def parse(self, statement):
        if statement.type == Token.END:
            self.model.end = statement
            self.end_seen = True
        else:
            self.model.body.append(statement)
