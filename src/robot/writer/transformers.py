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

import ast

from robot.parsing.lexer import Token


class SeparatorRemover(ast.NodeVisitor):
    separator_tokens = (Token.EOL, Token.SEPARATOR, Token.OLD_FOR_INDENT)

    def visit_Statement(self, statement):
        statement.tokens = [t for t in statement.tokens if
                            t.type not in self.separator_tokens]


class ColumnAligner(ast.NodeVisitor):

    def __init__(self, ctx, widths):
        self.ctx = ctx
        self.widths = widths
        self.test_name_len = 0
        self.indent = 0
        self.first_statement_after_name_seen = False

    def visit_TestOrKeyword(self, node):
        self.first_statement_after_name_seen = False
        self.generic_visit(node)

    def visit_ForLoop(self, statement):
        self.indent += 1
        self.generic_visit(statement)
        self.indent -= 1

    def visit_Statement(self, statement):
        if statement.type == Token.NAME:
            self.test_name_len = len(statement.tokens[0].value)
        elif statement.type == Token.TESTCASE_HEADER:
            self.align_header(statement)
        else:
            self.align_statement(statement)

    def align_header(self, statement):
        for token, width in zip(statement.tokens, self.widths):
            token.value = token.value.ljust(width)

    def align_statement(self, statement):
        for line in statement.lines:
            line_pos = 0
            exp_pos = 0
            widths = self.widths_for_line(line)
            for token, width in zip(line, widths):
                exp_pos += width
                if self.should_write_content_after_name(line_pos):
                    exp_pos -= self.test_name_len
                    self.first_statement_after_name_seen = True
                token.value = (exp_pos - line_pos) * ' ' + token.value
                line_pos += len(token.value)

    def widths_for_line(self, line):
        # FIXME: breaks with Token.ASSIGNMENT, Token.CONTINUATION
        if self.indent > 0 and line[0].type == Token.KEYWORD:
            widths = self.widths[1:]
            widths[0] = widths[0] + self.widths[0]
            return widths
        return self.widths

    def should_write_content_after_name(self, line_pos):
        return line_pos == 0 and not self.first_statement_after_name_seen \
               and self.test_name_len < self.ctx.short_test_name_length


class ColumnWidthCounter(ast.NodeVisitor):

    def __init__(self):
        self.widths = []

    def visit_Statement(self, statement):
        if statement.type == Token.TESTCASE_HEADER:
            self._count_widths_from_statement(statement)
        elif statement.type != Token.NAME:
            self._count_widths_from_statement(statement, indent=1)

    def _count_widths_from_statement(self, statement, indent=0):
        for line in statement.lines:
            for index, token in enumerate(line, start=indent):
                if index >= len(self.widths):
                    self.widths.append(len(token.value))
                elif len(token.value) > self.widths[index]:
                    self.widths[index] = len(token.value)


class Aligner(ast.NodeVisitor):

    def __init__(self, ctx):
        self.ctx = ctx

    def visit_Section(self, section):
        if section.type in (Token.SETTING_HEADER, Token.VARIABLE_HEADER):
            self.generic_visit(section)
        elif section.type == Token.TESTCASE_HEADER and len(section.header) > 1:
            counter = ColumnWidthCounter()
            counter.visit(section)
            ColumnAligner(self.ctx, counter.widths).visit(section)

    def visit_Statement(self, statement):
        for line in statement.lines:
            line[0].value = line[0].value.ljust(
                self.ctx.setting_and_variable_name_length)


class SettingCleaner(ast.NodeVisitor):

    def visit_Statement(self, statement):
        if statement.type in Token.SETTING_TOKENS:
            name = statement.tokens[0].value
            if name.startswith('['):
                cleaned = '[%s]' % name[1:-1].strip().title()
            else:
                cleaned = name.title()
            statement.tokens[0].value = cleaned


class ForLoopCleaner(ast.NodeVisitor):

    def visit_ForLoop(self, forloop):
        forloop.header[0].value = 'FOR'
        forloop.end[0].value = 'END'


class Formatter(ast.NodeVisitor):

    def __init__(self, ctx, row_writer):
        self.ctx = ctx
        self.writer = row_writer
        self.indent = 0
        self.section_seen = False
        self.test_or_kw_seen = False
        self.has_custom_headers = False

    def visit_Section(self, section):
        if self.section_seen:
            self._write_newline()
        if section.type == Token.TESTCASE_HEADER:
            if len(section.header) > 1:
                self.has_custom_headers = True
        self.generic_visit(section)
        self.section_seen = True
        self.test_or_kw_seen = False
        self.has_custom_headers = False

    def visit_TestOrKeyword(self, node):
        if self.test_or_kw_seen:
            self._write_newline()
        self._write_name(node.name)
        self.indent += 1
        self.generic_visit(node.body)
        self.indent -= 1
        self.test_or_kw_seen = True

    def _write_name(self, name):
        want_content_on_name_row = self.has_custom_headers and \
            len(name.tokens[0].value) < self.ctx.short_test_name_length
        self._write_statement(name, write_newline=not want_content_on_name_row)

    def visit_ForLoop(self, node):
        self._write_statement(node.header)
        self.indent += 1
        self.generic_visit(node.body)
        self.indent -= 1
        self._write_statement(node.end)

    def visit_Statement(self, statement):
        self._write_statement(statement)

    def _write_statement(self, statement, write_newline=True):
        for line in statement.lines:
            self.writer.write(line, self.indent)
            if write_newline:
                self._write_newline()

    def _write_newline(self):
        self.writer.write_newline()


