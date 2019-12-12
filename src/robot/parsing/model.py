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

"""Model used by tools such as tidy, not used for test execution"""

import os

from robot.errors import DataError
from robot.utils import Utf8Reader, get_error_message

from .lexer import TestCaseFileLexer, ResourceFileLexer, Token
from .nodes import (File, SettingSection, VariableSection, TestCaseSection,
                    KeywordSection, CommentSection, TestCase, Keyword, ForLoop)
from .restreader import read_rest
from .statements import Statement

header_types = (
    Token.SETTING_HEADER, Token.VARIABLE_HEADER,
    Token.TESTCASE_HEADER, Token.KEYWORD_HEADER
)


PROCESS_CURDIR = True


class Builder(object):

    def __init__(self, model):
        self.model = model

    def handles(self, statement):
        return True

    def statement(self, statement):
        raise NotImplementedError


class FileBuilder(Builder):

    def statement(self, statement):
        try:
            section_class, builder_class = {
                Token.SETTING_HEADER: (SettingSection, SectionBuilder),
                Token.VARIABLE_HEADER: (VariableSection, SectionBuilder),
                Token.TESTCASE_HEADER: (TestCaseSection, TestCaseSectionBuilder),
                Token.KEYWORD_HEADER: (KeywordSection, KeywordSectionBuilder),
                Token.COMMENT_HEADER: (CommentSection, SectionBuilder)
            }[statement.type]
            section = section_class(statement)
        except KeyError:
            section = CommentSection(body=[statement])
            builder_class = SectionBuilder
        self.model.sections.append(section)
        return builder_class(section)


class SectionBuilder(Builder):

    def handles(self, statement):
        return statement.type not in header_types

    def statement(self, statement):
        self.model.body.add(statement)


class TestCaseSectionBuilder(SectionBuilder):

    def statement(self, statement):
        if statement.type == Token.EOL:
            return self
        model = TestCase(statement)
        self.model.body.add(model)
        return TestOrKeywordBuilder(model)


class KeywordSectionBuilder(SectionBuilder):

    def statement(self, statement):
        if statement.type == Token.EOL:
            return self
        model = Keyword(statement)
        self.model.body.add(model)
        return TestOrKeywordBuilder(model)


class TestOrKeywordBuilder(Builder):

    def handles(self, statement):
        return statement.type not in header_types + (Token.NAME,)

    def statement(self, statement):
        if statement.type == Token.FOR:
            model = ForLoop(statement)
            self.model.body.add(model)
            return ForLoopBuilder(model)
        else:
            self.model.body.add(statement)


class ForLoopBuilder(Builder):

    def __init__(self, model):
        Builder.__init__(self, model)
        self._end = False

    def handles(self, statement):
        return not self._end and statement.type != Token.NAME

    def statement(self, statement):
        if statement.type == Token.END:
            self.model.end = statement
            self._end = True
        else:
            self.model.body.add(statement)


# TODO: is this public API, name?
def Model(source, process_curdir=True):
    return build(source, TestCaseFileLexer, process_curdir)


def ResourceModel(source, process_curdir=True):
    return build(source, ResourceFileLexer, process_curdir)


def build(source, lexer, process_curdir=True):
    builder = FileBuilder(File())
    stack = [builder]
    for statement in get_statements(source, lexer, process_curdir):
        while not stack[-1].handles(statement):
            stack.pop()
        builder = stack[-1].statement(statement)
        if builder:
            stack.append(builder)

    return stack[0].model


def get_statements(source, lexer_cls, process_curdir):
    lexer = lexer_cls(data_only=False)
    lexer.input(_read(source))
    statement = []
    for t in lexer.get_tokens():
        if process_curdir:
            curdir = os.path.dirname(source).replace('\\', '\\\\')
            if t and '${CURDIR}' in t.value:
                t.value = t.value.replace('${CURDIR}', curdir)
        if t.type != t.EOS:
            statement.append(t)
        else:
            yield Statement.from_tokens(statement)
            statement = []


def _read(path):
    try:
        # IronPython handles BOM incorrectly if not using binary mode:
        # https://ironpython.codeplex.com/workitem/34655
        with open(path, 'rb') as data:
            if os.path.splitext(path)[1].lower() in ('.rest', '.rst'):
                return read_rest(data)
            return Utf8Reader(data).read()
    except:
        raise DataError(get_error_message())
