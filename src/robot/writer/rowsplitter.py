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
            return self._split_empty_row()
        indent = self._get_indent(row, indented_table)
        return self._split_row(row, indent)

    def _split_empty_row(self):
        yield []

    def _get_indent(self, row, indented_table):
        indent = len(list(itertools.takewhile(lambda x: x == '', row)))
        min_indent = 1 if indented_table else 0
        return max(indent, min_indent)

    def _split_row(self, row, indent):
        while row:
            current, row = self._split(row)
            yield self._escape_last_empty_cell(current)
            if row and indent + 1 < self._cols:
                row = self._indent(row, indent)

    def _split(self, data):
        row, rest = data[:self._cols], data[self._cols:]
        self._in_comment = any(c.startswith(self._comment_mark) for c in row)
        rest = self._add_line_continuation(rest)
        return row, rest

    def _add_line_continuation(self, data):
        if data:
            if self._in_comment:
                data[0] = self._comment_mark + data[0]
            data = [self._line_continuation] + data
        return data

    def _escape_last_empty_cell(self, row):
        if not row[-1].strip():
            row[-1] = self._empty_cell_escape
        return row

    def _indent(self, row, indent):
        return [''] * indent + row
