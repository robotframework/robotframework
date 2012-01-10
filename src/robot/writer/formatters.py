#  Copyright 2008-2011 Nokia Siemens Networks Oyj
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
from robot.writer.tableformatters import SingleLineHtmlFormatter

from .tableformatters import (RowSplittingFormatter, SplittingHtmlFormatter,
    ColumnAligner, SettingTableAligner, NameCell, HeaderCell, HtmlCell)


class _TestDataFileFormatter(object):

    def variable_rows(self, variables):
        for row in self._variable_table_formatter().format_simple_table(variables):
            yield self._format_row(row)

    def setting_rows(self, settings):
        for row in self._setting_table_formatter().format_simple_table(settings):
            yield self._format_row(row)

    def test_rows(self, tests):
        for row in self._test_table_formatter(tests).format_indented_table(tests):
            yield self._format_row(row)

    def keyword_rows(self, keywords):
        for row in self._keyword_table_formatter(keywords).format_indented_table(keywords):
            yield self._format_row(row)

    def empty_row(self):
        return self._format_row([])

    def _format_row(self, row):
        return row

    def _should_align_columns(self, table):
        return table.type in ['test case', 'keyword'] and bool(table.header[1:])


class TsvFormatter(_TestDataFileFormatter):

    def __init__(self, cols=8):
        self._cols = cols
        self._formatter = RowSplittingFormatter(self._cols)

    def _variable_table_formatter(self):
        return self._formatter

    def _setting_table_formatter(self):
        return self._formatter

    def _test_table_formatter(self, tests):
        return self._formatter

    def _keyword_table_formatter(self, keywords):
        return self._formatter

    def header_row(self, table):
        return self._format_row(['*%s*' % cell for cell in table.header])

    def _format_row(self, row):
        return self._pad(row)

    def _pad(self, row):
        row = [cell.replace('\n', ' ') for cell in row]
        return row + [''] * (self._cols - len(row))


class TxtFormatter(_TestDataFileFormatter):
    _FIRST_COL_WIDTH = 18
    _SETTING_NAME_WIDTH = 14
    _align_last_column = False

    def __init__(self, cols=8):
        self._cols = cols

    def _variable_table_formatter(self):
        return SettingTableAligner(self._cols, self._SETTING_NAME_WIDTH)

    def _setting_table_formatter(self):
        return SettingTableAligner(self._cols, self._SETTING_NAME_WIDTH)

    def _test_table_formatter(self, tests):
        return self._indented_table_formatter(tests)

    def _keyword_table_formatter(self, keywords):
        return self._indented_table_formatter(keywords)

    def header_row(self, table):
        header = ['*** %s ***' % table.header[0]] + table.header[1:]
        if self._should_align_columns(table):
            return ColumnAligner(self._FIRST_COL_WIDTH, table,
                                 self._align_last_column).align_row(header)
        return header

    def _indented_table_formatter(self, table):
        if self._should_align_columns(table):
            return ColumnAligner(self._FIRST_COL_WIDTH, table,
                                 self._align_last_column)
        return RowSplittingFormatter(self._cols)

    def _format_row(self, row):
        return self._escape(row)

    def _escape(self, row):
        return self._escape_consecutive_whitespace(
            self._escape_empty_cell_from_start(row))

    def _escape_empty_cell_from_start(self, row):
        if len(row) >= 2 and row[0] == '' and row[1] == '':
            row[1] = '\\'
        return row

    def _escape_consecutive_whitespace(self, row):
        return [re.sub('\s\s+(?=[^\s])',
                lambda match: '\\'.join(match.group(0)), item.replace('\n', ' ')) for item in row]


class PipeFormatter(TxtFormatter):
    _align_last_column = True

    def _escape(self, row):
        row = self._format_empty_cells(row)
        return self._escape_consecutive_whitespace(self._escape_pipes(row))

    def _format_empty_cells(self, row):
        return ['  ' if not cell else cell for cell in row]

    def _escape_pipes(self, row):
        return [self._escape_pipes_from_cell(cell) for cell in row]

    def _escape_pipes_from_cell(self, cell):
        cell = cell.replace(' | ', ' \\| ')
        if cell.startswith('| '):
            cell = '\\' + cell
        if cell.endswith(' |'):
            cell = cell[:-1] + '\\|'
        return cell


class HtmlFormatter(_TestDataFileFormatter):

    def __init__(self):
        self._default_cols = 5
        self._cols = self._default_cols
        self._formatter = SplittingHtmlFormatter(self._default_cols)

    def empty_row(self):
        return [NameCell('')] + [HtmlCell('') for _ in range(self._cols-1)]

    def _setting_table_formatter(self):
        self._cols = self._default_cols
        return self._formatter

    def _variable_table_formatter(self):
        self._cols = self._default_cols
        return self._formatter

    def _test_table_formatter(self, tests):
        return self._dynamic_width_formatter(tests)

    def _keyword_table_formatter(self, keywords):
        return self._dynamic_width_formatter(keywords)

    def _dynamic_width_formatter(self, table):
        if len(table.header) == 1:
            self._cols = self._default_cols
            return SplittingHtmlFormatter(self._cols)
        self._cols = max(self._max_column_count(table), len(table.header))
        return SingleLineHtmlFormatter(self._cols)

    def header_row(self, table):
        if not self._should_align_columns(table) or len(table.header) == 1:
            return [HeaderCell(table.header[0], self._default_cols)]
        headers = self._pad_header(table)
        return [HeaderCell(hdr) for hdr in headers]

    def _pad_header(self, table):
        return table.header + [''] * (self._max_column_count(table) - len(table.header))

    def _max_column_count(self, table):
        count = 0
        for item in table:
            for child in item:
                count = max(count, len(child.as_list()) + 1)
        return count
