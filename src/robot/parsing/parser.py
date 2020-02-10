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

import os.path

from robot.utils import is_pathlike, is_string

from .lexer import Token, get_tokens, get_resource_tokens
from .model import (File, SettingSection, VariableSection, TestCaseSection,
                    KeywordSection, CommentSection, TestCase, Keyword, ForLoop,
                    Statement)


def get_model(source, data_only=False, curdir=None):
    """FIXME: Documentation missing.

    Mention TestSuite.from_model when docs are written.
    """
    tokens = get_tokens(source, data_only)
    statements = _tokens_to_statements(tokens, curdir)
    return _statements_to_model(statements, source)


def get_resource_model(source, data_only=False, curdir=None):
    """Parses the given source to a resource file model.

    Otherwise same as :func:`get_model` but the source is considered to be
    a resource file. This affects, for example, what settings are valid.
    """
    tokens = get_resource_tokens(source, data_only)
    statements = _tokens_to_statements(tokens, curdir)
    return _statements_to_model(statements, source)


def _tokens_to_statements(tokens, curdir=None):
    statement = []
    EOS = Token.EOS
    for t in tokens:
        if curdir and '${CURDIR}' in t.value:
            t.value = t.value.replace('${CURDIR}', curdir)
        if t.type != EOS:
            statement.append(t)
        else:
            yield Statement.from_tokens(statement)
            statement = []


def _statements_to_model(statements, source=None):
    parser = FileParser(source=source)
    stack = [parser]
    for statement in statements:
        while not stack[-1].handles(statement):
            stack.pop()
        parser = stack[-1].parse(statement)
        if parser:
            stack.append(parser)
    return stack[0].model


class Parser(object):

    def __init__(self, model):
        self.model = model

    def handles(self, statement):
        return True

    def parse(self, statement):
        raise NotImplementedError


class FileParser(Parser):

    def __init__(self, source=None):
        Parser.__init__(self, File(source=self._get_path(source)))

    def _get_path(self, source):
        if not source:
            return None
        if is_string(source) and '\n' not in source and os.path.isfile(source):
            return source
        if is_pathlike(source) and source.is_file():
            return str(source)
        return None

    def parse(self, statement):
        try:
            section_class, parser_class = {
                Token.SETTING_HEADER: (SettingSection, SectionParser),
                Token.VARIABLE_HEADER: (VariableSection, SectionParser),
                Token.TESTCASE_HEADER: (TestCaseSection, TestCaseSectionParser),
                Token.KEYWORD_HEADER: (KeywordSection, KeywordSectionParser),
                Token.COMMENT_HEADER: (CommentSection, SectionParser)
            }[statement.type]
            section = section_class(statement)
        except KeyError:
            section = CommentSection(body=[statement])
            parser_class = SectionParser
        self.model.sections.append(section)
        return parser_class(section)


class SectionParser(Parser):

    def handles(self, statement):
        return statement.type not in Token.HEADER_TOKENS

    def parse(self, statement):
        self.model.body.add(statement)


class TestCaseSectionParser(SectionParser):

    def parse(self, statement):
        if statement.type == Token.EOL:
            if self.model.body.items:
                self.model.body.add(statement)
            return self
        model = TestCase(statement)
        self.model.body.add(model)
        return TestOrKeywordParser(model)


class KeywordSectionParser(SectionParser):

    def parse(self, statement):
        if statement.type == Token.EOL:
            if self.model.body.items:
                self.model.body.add(statement)
            return self
        model = Keyword(statement)
        self.model.body.add(model)
        return TestOrKeywordParser(model)


class TestOrKeywordParser(Parser):

    def handles(self, statement):
        name_types = (Token.TESTCASE_NAME, Token.KEYWORD_NAME)
        return statement.type not in Token.HEADER_TOKENS + name_types

    def parse(self, statement):
        if statement.type == Token.FOR:
            model = ForLoop(statement)
            self.model.body.add(model)
            return ForLoopParser(model)
        else:
            self.model.body.add(statement)


class ForLoopParser(Parser):

    def __init__(self, model):
        Parser.__init__(self, model)
        self._end = False

    def handles(self, statement):
        name_types = (Token.TESTCASE_NAME, Token.KEYWORD_NAME)
        return not self._end and statement.type not in name_types

    def parse(self, statement):
        if statement.type == Token.END:
            self.model.end = statement
            self._end = True
        else:
            self.model.body.add(statement)
