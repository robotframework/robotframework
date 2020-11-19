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

from ..lexer import Token
from ..model import (File, CommentSection, SettingSection, VariableSection,
                     TestCaseSection, KeywordSection)

from .blockparsers import Parser, TestCaseParser, KeywordParser


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

    def handles(self, statement):
        return True

    def parse(self, statement):
        parser_class = {
            Token.SETTING_HEADER: SettingSectionParser,
            Token.VARIABLE_HEADER: VariableSectionParser,
            Token.TESTCASE_HEADER: TestCaseSectionParser,
            Token.KEYWORD_HEADER: KeywordSectionParser,
            Token.COMMENT_HEADER: CommentSectionParser,
            Token.COMMENT: ImplicitCommentSectionParser,
            Token.ERROR: ImplicitCommentSectionParser,
            Token.EOL: ImplicitCommentSectionParser
        }[statement.type]
        parser = parser_class(statement)
        self.model.sections.append(parser.model)
        return parser


class SectionParser(Parser):
    subsection_parsers = {}
    section_class = None

    def __init__(self, header):
        Parser.__init__(self, self.section_class(header))

    def handles(self, statement):
        return statement.type not in Token.HEADER_TOKENS

    def parse(self, statement):
        parser_class = self.subsection_parsers.get(statement.type)
        if parser_class:
            parser = parser_class(statement)
            self.model.body.append(parser.model)
            return parser
        self.model.body.append(statement)


class SettingSectionParser(SectionParser):
    section_class = SettingSection


class VariableSectionParser(SectionParser):
    section_class = VariableSection


class CommentSectionParser(SectionParser):
    section_class = CommentSection


class ImplicitCommentSectionParser(SectionParser):

    def section_class(self, statement):
        return CommentSection(body=[statement])


class TestCaseSectionParser(SectionParser):
    subsection_parsers = {Token.TESTCASE_NAME: TestCaseParser}
    section_class = TestCaseSection


class KeywordSectionParser(SectionParser):
    subsection_parsers = {Token.KEYWORD_NAME: KeywordParser}
    section_class = KeywordSection
