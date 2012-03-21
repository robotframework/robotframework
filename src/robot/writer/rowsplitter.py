#  Copyright 2008-2012 Nokia Siemens Networks Oyj
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

import itertools


class RowSplitter(object):
    _comment_mark = '#'
    _empty_cell_escape = '${EMPTY}'
    _line_continuation = '...'

    def __init__(self, cols=8):
        self._cols = cols

    def split(self, row, indented_table=False):
        if not row:
            return [[]]
        return self._split_to_rows(row, indented_table)

    def _split_to_rows(self, data, indented_table):
        indent = len(list(itertools.takewhile(lambda x: x == '', data)))
        if indented_table:
            indent = max(indent, 1)
        rows = []
        while data:
            current, data = self._split(data)
            rows.append(self._escape_last_empty_cell(current))
            if data and indent + 1 < self._cols:
                data = self._indent(data, indent)
        return rows

    def _split(self, data):
        row, rest = data[:self._cols], data[self._cols:]
        self._in_comment = any(c for c in row if c.startswith( self._comment_mark))
        rest = self._add_line_continuation(rest)
        return row, rest

    def _escape_last_empty_cell(self, row):
        if not row[-1].strip():
            row[-1] = self._empty_cell_escape
        return row

    def _add_line_continuation(self, data):
        if data:
            if self._in_comment:
                data[0] = self._comment_mark + data[0]
            data = [self._line_continuation] + data
        return data

    def _indent(self, row, indent):
        return [''] * indent + row
