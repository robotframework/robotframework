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

from itertools import takewhile

from robot.parsing import Token, ModelTransformer
from robot.parsing.model.statements import EmptyLine, End
from robot.utils import normalize_whitespace


class Cleaner(ModelTransformer):
    """Clean up and normalize data.

    Following transformations are made:
    1) section headers are normalized to format `***  Section Name ***`
    2) setting names are normalize in setting table and in test cases and
       user keywords to format `Setting Name` or `[Setting Name]`
    3) settings without values are removed
    4) Empty lines after section headers and within items are removed
    5) For loop declaration and end tokens are normalized to `FOR` and `END`
    6) Old style for loop indent (i.e. a cell with only a `\\`) are removed
    """

    def __init__(self):
        self.in_data_section = False

    def visit_CommentSection(self, section):
        self.generic_visit(section)
        return section

    def visit_Section(self, section):
        self.in_data_section = True
        self._normalize_section_header(section)
        self.generic_visit(section)
        return section

    def _normalize_section_header(self, section):
        header_token = section.header.data_tokens[0]
        normalized = self._normalize_name(header_token.value, remove='*')
        header_token.value = '*** %s ***' % normalized

    def visit_Statement(self, statement):
        statement.tokens = list(self._remove_old_for_loop_indent(statement))
        if statement.type in Token.SETTING_TOKENS:
            self._normalize_setting_name(statement)
        self.generic_visit(statement)
        if self._is_setting_without_value(statement) or \
                self._is_empty_line_in_data(statement):
            return None
        if self.in_data_section:
            self._remove_empty_lines_within_statement(statement)
        return statement

    def _remove_old_for_loop_indent(self, statement):
        prev_was_for_indent = False
        for t in statement.tokens:
            if t.type == Token.OLD_FOR_INDENT:
                prev_was_for_indent = True
                continue
            elif prev_was_for_indent and t.type == Token.SEPARATOR:
                prev_was_for_indent = False
                continue
            else:
                yield t

    def _normalize_setting_name(self, statement):
        name = statement.data_tokens[0].value
        if name.startswith('['):
            cleaned = '[%s]' % self._normalize_name(name[1:-1])
        else:
            cleaned = self._normalize_name(name)
        statement.data_tokens[0].value = cleaned

    def _normalize_name(self, marker, remove=None):
        if remove:
            marker = marker.replace(remove, '')
        return normalize_whitespace(marker).strip().title()

    def _is_setting_without_value(self, statement):
        return statement.type in Token.SETTING_TOKENS and \
               len(statement.data_tokens) == 1

    def _is_empty_line_in_data(self, statement):
        return self.in_data_section and statement.type == Token.EOL

    def _remove_empty_lines_within_statement(self, statement):
        new_tokens = []
        for line in statement.lines:
            if len(line) == 1 and line[0].type == Token.EOL:
                continue
            new_tokens.extend(line)
        statement.tokens = new_tokens

    def visit_ForLoop(self, loop):
        loop.header.data_tokens[0].value = 'FOR'
        if loop.end:
            loop.end.data_tokens[0].value = 'END'
        else:
            loop.end = End([Token(Token.SEPARATOR), Token(Token.END, 'END')])
        self.generic_visit(loop)
        return loop


class NewlineNormalizer(ModelTransformer):
    """Normalize new lines in test data

    After this transformation, there is exactly one empty line between each
    section and between each test or user keyword.
    """

    def __init__(self, newline, short_test_name_length):
        self.newline = newline
        self.short_test_name_length = short_test_name_length
        self.custom_test_section_headers = False
        self.last_test = None
        self.last_keyword = None
        self.last_section = None

    def visit_File(self, node):
        self.last_section = node.sections[-1] if node.sections else None
        return self.generic_visit(node)

    def visit_Section(self, node):
        if node is not self.last_section:
            node.body.append(EmptyLine.from_value(self.newline))
        return self.generic_visit(node)

    def visit_CommentSection(self, node):
        return self.generic_visit(node)

    def visit_TestCaseSection(self, node):
        self.last_test = node.body[-1] if node.body else None
        self.custom_test_section_headers = len(node.header.data_tokens) > 1
        section = self.visit_Section(node)
        self.custom_test_section_headers = False
        return section

    def visit_TestCase(self, node):
        if not node.body or node is not self.last_test:
            node.body.append(EmptyLine.from_value(self.newline))
        return self.generic_visit(node)

    def visit_KeywordSection(self, node):
        self.last_keyword = node.body[-1] if node.body else None
        return self.visit_Section(node)

    def visit_Keyword(self, node):
        if not node.body or node is not self.last_keyword:
            node.body.append(EmptyLine.from_value(self.newline))
        return self.generic_visit(node)

    def visit_Statement(self, statement):
        if statement[-1].type != Token.EOL:
            if not self._should_write_content_after_name(statement):
                statement.tokens.append(Token(Token.EOL, self.newline))
        for line in statement.lines:
            if line[-1].type == Token.EOL:
                line[-1].value = self.newline
        return statement

    def _should_write_content_after_name(self, statement):
        return (statement.type in (Token.TESTCASE_NAME, Token.KEYWORD_NAME) and
                self.custom_test_section_headers and
                len(statement.tokens[0].value) < self.short_test_name_length)


class SeparatorNormalizer(ModelTransformer):
    """Make separators and indentation consistent."""

    def __init__(self, use_pipes, space_count):
        self.use_pipes = use_pipes
        self.space_count = space_count
        self.indent = 0

    def visit_TestCase(self, node):
        self.visit_Statement(node.header)
        self.indent += 1
        node.body = [self.visit(item) for item in node.body]
        self.indent -= 1
        return node

    def visit_Keyword(self, node):
        self.visit_Statement(node.header)
        self.indent += 1
        node.body = [self.visit(item) for item in node.body]
        self.indent -= 1
        return node

    def visit_ForLoop(self, node):
        self.visit_Statement(node.header)
        self.indent += 1
        node.body = [self.visit(item) for item in node.body]
        self.indent -= 1
        self.visit_Statement(node.end)
        return node

    def visit_Statement(self, statement):
        has_pipes = statement.tokens[0].value.startswith('|')
        if self.use_pipes:
            return self._handle_pipes(statement, has_pipes)
        return self._handle_spaces(statement, has_pipes)

    def _handle_spaces(self, statement, has_pipes=False):
        new_tokens = []
        for line in statement.lines:
            if has_pipes and len(line) > 1:
                line = self._remove_consecutive_separators(line)
            new_tokens.extend([self._normalize_spaces(i, t, len(line))
                               for i, t in enumerate(line)])
        statement.tokens = new_tokens
        self.generic_visit(statement)
        return statement

    def _remove_consecutive_separators(self, line):
        sep_count = len(list(
            takewhile(lambda t: t.type == Token.SEPARATOR, line)
        ))
        return line[sep_count - 1:]

    def _normalize_spaces(self, index, token, line_length):
        if token.type == Token.SEPARATOR:
            spaces = self.space_count * self.indent \
                if index == 0 else self.space_count
            token.value = ' ' * spaces
        # The last token is always EOL, this removes all dangling whitespace
        # from the token before the EOL
        if index == line_length - 2:
            token.value = token.value.rstrip()
        return token

    def _handle_pipes(self, statement, has_pipes=False):
        new_tokens = []
        for line in statement.lines:
            if len(line) == 1 and line[0].type == Token.EOL:
                new_tokens.extend(line)
                continue

            if not has_pipes:
                line = self._insert_leading_and_trailing_separators(line)
            for index, token in enumerate(line):
                if token.type == Token.SEPARATOR:
                    if index == 0:
                        if self.indent:
                            token.value = '|   '
                        else:
                            token.value = '| '
                    elif index < self.indent:
                        token.value = ' |   '
                    elif len(line) > 1 and index == len(line) - 2:
                        # This is the separator before EOL.
                        token.value = ' |'
                    else:
                        token.value = ' | '
            new_tokens.extend(line)
        statement.tokens = new_tokens
        return statement

    def _insert_leading_and_trailing_separators(self, line):
        """Add missing separators to the beginning and the end of the line.

        When converting from spaces to pipes, a separator token is needed
        in the beginning of the line, for each indent level and in the
        end of the line.
        """
        separators_needed = 1
        if self.indent > 1:
            # Space format has 1 separator token regardless of the indent level.
            # With pipes, we need to add one separator for each indent level
            # beyond 1.
            separators_needed += self.indent - 1
        for _ in range(separators_needed):
            line = [Token(Token.SEPARATOR, '')] + line
        if len(line) > 1:
            if line[-2].type != Token.SEPARATOR:
                line = line[:-1] + [Token(Token.SEPARATOR, ''), line[-1]]
        return line


class ColumnAligner(ModelTransformer):

    def __init__(self, short_test_name_length, widths):
        self.short_test_name_length = short_test_name_length
        self.widths = widths
        self.test_name_len = 0
        self.indent = 0
        self.first_statement_after_name_seen = False

    def visit_TestCase(self, node):
        self.first_statement_after_name_seen = False
        return self.generic_visit(node)

    def visit_ForLoop(self, node):
        self.indent += 1
        self.generic_visit(node)
        self.indent -= 1
        return node

    def visit_Statement(self, statement):
        if statement.type == Token.TESTCASE_NAME:
            self.test_name_len = len(statement.tokens[0].value)
        elif statement.type == Token.TESTCASE_HEADER:
            self.align_header(statement)
        else:
            self.align_statement(statement)
        return statement

    def align_header(self, statement):
        for token, width in zip(statement.data_tokens[:-1], self.widths):
            token.value = token.value.ljust(width)

    def align_statement(self, statement):
        for line in statement.lines:
            line = [t for t in line if t.type
                    not in (Token.SEPARATOR, Token.EOL)]
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
        if self.indent > 0 and self._should_be_indented(line):
            widths = self.widths[1:]
            widths[0] = widths[0] + self.widths[0]
            return widths
        return self.widths

    def _should_be_indented(self, line):
        return line[0].type in (Token.KEYWORD, Token.ASSIGN,
                                Token.CONTINUATION)

    def should_write_content_after_name(self, line_pos):
        return line_pos == 0 and not self.first_statement_after_name_seen \
               and self.test_name_len < self.short_test_name_length


class ColumnWidthCounter(ModelTransformer):

    def __init__(self):
        self.widths = []

    def visit_Statement(self, statement):
        if statement.type == Token.TESTCASE_HEADER:
            self._count_widths_from_statement(statement)
        elif statement.type != Token.TESTCASE_NAME:
            self._count_widths_from_statement(statement, indent=1)
        return statement

    def _count_widths_from_statement(self, statement, indent=0):
        for line in statement.lines:
            line = [t for t in line if t.type not in (Token.SEPARATOR, Token.EOL)]
            for index, token in enumerate(line, start=indent):
                if index >= len(self.widths):
                    self.widths.append(len(token.value))
                elif len(token.value) > self.widths[index]:
                    self.widths[index] = len(token.value)


class Aligner(ModelTransformer):

    def __init__(self, short_test_name_length,
                 setting_and_variable_name_length, pipes_mode):
        self.short_test_name_length = short_test_name_length
        self.setting_and_variable_name_length = \
            setting_and_variable_name_length
        self.pipes_mode = pipes_mode

    def visit_TestCaseSection(self, section):
        if len(section.header.data_tokens) > 1:
            counter = ColumnWidthCounter()
            counter.visit(section)
            ColumnAligner(self.short_test_name_length,
                          counter.widths).visit(section)
        return section

    def visit_KeywordSection(self, section):
        return section

    def visit_Statement(self, statement):
        for line in statement.lines:
            value_tokens = [t for t in line if t.type
                            not in (Token.SEPARATOR, Token.EOL)]
            if self._should_be_aligned(value_tokens):
                first = value_tokens[0]
                first.value = first.value.ljust(
                    self.setting_and_variable_name_length
                )
        return statement

    def _should_be_aligned(self, tokens):
        if not tokens:
            return False
        if len(tokens) == 1:
            return self.pipes_mode
        if len(tokens) == 2:
            return tokens[0].type != Token.CONTINUATION or tokens[1].value
        return True
