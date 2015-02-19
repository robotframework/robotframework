#  Copyright 2008-2015 Nokia Solutions and Networks
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

from .aligners import FirstColumnAligner, ColumnAligner, NullAligner
from .dataextractor import DataExtractor
from .rowsplitter import RowSplitter


class _DataFileFormatter(object):
    _whitespace = re.compile('\s{2,}')
    _split_multiline_doc = True

    def __init__(self, column_count):
        self._splitter = RowSplitter(column_count, self._split_multiline_doc)
        self._column_count = column_count
        self._extractor = DataExtractor(self._want_names_on_first_content_row)

    def _want_names_on_first_content_row(self, table, name):
        return True

    def empty_row_after(self, table):
        return self._format_row([], table)

    def format_header(self, table):
        header = self._format_row(table.header)
        return self._format_header(header, table)

    def format_table(self, table):
        rows = self._extractor.rows_from_table(table)
        if self._should_split_rows(table):
            rows = self._split_rows(rows, table)
        return (self._format_row(r, table) for r in rows)

    def _should_split_rows(self, table):
        return not self._should_align_columns(table)

    def _split_rows(self, original_rows, table):
        for original in original_rows:
            for split in self._splitter.split(original, table.type):
                yield split

    def _should_align_columns(self, table):
        return self._is_indented_table(table) and bool(table.header[1:])

    def _is_indented_table(self, table):
        return table is not None and table.type in ['test case', 'keyword']

    def _escape_consecutive_whitespace(self, row):
        return [self._whitespace.sub(self._whitespace_escaper,
                                     cell.replace('\n', ' ')) for cell in row]

    def _whitespace_escaper(self, match):
        return '\\'.join(match.group(0))

    def _format_row(self, row, table=None):
        raise NotImplementedError

    def _format_header(self, header, table):
        raise NotImplementedError


class TsvFormatter(_DataFileFormatter):

    def _format_header(self, header, table):
        return [self._format_header_cell(cell) for cell in header]

    def _format_header_cell(self, cell):
        return '*%s*' % cell if cell else ''

    def _format_row(self, row, table=None):
        return self._pad(self._escape(row))

    def _escape(self, row):
        return self._escape_consecutive_whitespace(self._escape_tabs(row))

    def _escape_tabs(self, row):
        return [c.replace('\t', '\\t') for c in row]

    def _pad(self, row):
        row = [cell.replace('\n', ' ') for cell in row]
        return row + [''] * (self._column_count - len(row))


class TxtFormatter(_DataFileFormatter):
    _test_or_keyword_name_width = 18
    _setting_and_variable_name_width = 14

    def _format_row(self, row, table=None):
        row = self._escape(row)
        aligner = self._aligner_for(table)
        return aligner.align_row(row)

    def _aligner_for(self, table):
        if table and table.type in ['setting', 'variable']:
            return FirstColumnAligner(self._setting_and_variable_name_width)
        if self._should_align_columns(table):
            return ColumnAligner(self._test_or_keyword_name_width, table)
        return NullAligner()

    def _format_header(self, header, table):
        header = ['*** %s ***' % header[0]] + header[1:]
        aligner = self._aligner_for(table)
        return aligner.align_row(header)

    def _want_names_on_first_content_row(self, table, name):
        return self._should_align_columns(table) and \
                len(name) <= self._test_or_keyword_name_width

    def _escape(self, row):
        if not row:
            return row
        return self._escape_cells(self._escape_consecutive_whitespace(row))

    def _escape_cells(self, row):
        return [row[0]] + [self._escape_empty(cell) for cell in row[1:]]

    def _escape_empty(self, cell):
        return cell or '\\'


class PipeFormatter(TxtFormatter):

    def _escape_cells(self, row):
        return [self._escape_empty(self._escape_pipes(cell)) for cell in row]

    def _escape_empty(self, cell):
        return cell or '  '

    def _escape_pipes(self, cell):
        if ' | ' in cell:
            cell = cell.replace(' | ', ' \\| ')
        if cell.startswith('| '):
            cell = '\\' + cell
        if cell.endswith(' |'):
            cell = cell[:-1] + '\\|'
        return cell
