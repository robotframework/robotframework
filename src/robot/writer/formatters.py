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

from .aligners import FirstColumnAligner, ColumnAligner
from .dataextractor import DataExtractor
from .rowsplitter import RowSplitter


class _DataFileFormatter(object):
    _want_names_on_first_content_row = False

    def __init__(self, cols):
        self._splitter = RowSplitter(cols)
        self._cols = cols
        self._current_table = None
        self._extractor = DataExtractor(self._want_names_on_first_content_row)

    def empty_row(self):
        return self._format_row([])

    def setting_table(self, settings):
        self._current_table = settings
        return self._simple_table()

    def variable_table(self, variables):
        self._current_table = variables
        return self._simple_table()

    def _simple_table(self):
        return self._format_rows(self._extractor.rows_from_simple_table(self._current_table))

    def test_table(self, tests):
        self._current_table = tests
        return self._indented_table()

    def keyword_table(self, keywords):
        self._current_table = keywords
        return self._indented_table()

    def _indented_table(self):
        return self._format_rows(self._extractor.rows_from_indented_table(self._current_table))

    def _format_rows(self, rows):
        if self._should_split_rows():
            return self._split_rows(rows)
        return [self._format_row(r) for r in rows]

    def _should_split_rows(self):
        return True

    def _split_rows(self, rows):
        for row in rows:
            for r in self._splitter.split(row, self._is_indented_table(self._current_table)):
                yield self._format_row(r)

    def _should_align_columns(self, table):
        return self._is_indented_table(table) and bool(table.header[1:])

    def _is_indented_table(self, table):
        return table.type in ['test case', 'keyword']

    def _format_row(self, row):
        return row


class TsvFormatter(_DataFileFormatter):

    def __init__(self, cols=8):
        _DataFileFormatter.__init__(self, cols)
        self._cols = cols

    def header_row(self, table):
        return self._format_row(['*%s*' % cell for cell in table.header])

    def _format_row(self, row):
        return self._pad(row)

    def _pad(self, row):
        row = [cell.replace('\n', ' ') for cell in row]
        return row + [''] * (self._cols - len(row))


class TxtFormatter(_DataFileFormatter):
    _test_or_keyword_name_width = 18
    _setting_and_variable_name_width = 14
    _align_last_column = False

    def __init__(self, cols=8):
        _DataFileFormatter.__init__(self, cols)
        self._simple_aligner = FirstColumnAligner(cols,
            self._setting_and_variable_name_width)
        self._aligner = None

    def _format_row(self, row):
        row = self._escape(row)
        if self._aligner:
            return self._aligner.align_row(row)
        return row

    def header_row(self, table):
        header = ['*** %s ***' % table.header[0]] + table.header[1:]
        if self._should_align_columns(table):
            aligner = ColumnAligner(self._test_or_keyword_name_width, table,
                self._align_last_column)
            return aligner.align_row(header)
        return header

    def _should_split_rows(self):
        if self._should_align_columns(self._current_table):
            self._aligner = ColumnAligner(self._test_or_keyword_name_width,
                                          self._current_table, self._align_last_column)
            return False
        elif self._is_indented_table(self._current_table):
            self._aligner = None
            return True
        self._aligner = self._simple_aligner
        return True

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

