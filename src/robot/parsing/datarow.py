#  Copyright 2008-2010 Nokia Siemens Networks Oyj
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


class DataRow(object):
    _row_continuation_marker = '...'
    _whitespace_regexp = re.compile('\s+')
    _ye_olde_metadata_prefix = 'meta:'

    def __init__(self, cells):
        self.cells, self.comments = self._parse(cells)

    @property
    def head(self):
        return self.cells[0] if self.cells else None

    @property
    def tail(self):
        return self.cells[1:] if self.cells else None

    @property
    def all(self):
        return self.cells

    def dedent(self):
        datarow = DataRow([])
        datarow.cells = self.tail
        datarow.comments = self.comments
        return datarow

    def startswith(self, value):
        return self.head() == value

    def handle_old_style_metadata(self):
        if self._is_metadata_with_olde_prefix(self.head):
            self.cells = self._convert_to_new_style_metadata()

    def _is_metadata_with_olde_prefix(self, value):
        return value.lower().startswith(self._ye_olde_metadata_prefix)

    def _convert_to_new_style_metadata(self):
        return ['Metadata'] + [self.head.split(':', 1)[1].strip()] + self.tail

    def starts_for_loop(self):
        if self.head and self.head.startswith(':'):
            return self.head.replace(':', '').upper().strip() == 'FOR'
        return False

    def starts_test_or_user_keyword_setting(self):
        head = self.head
        return head and head[0] == '[' and head[-1] == ']'

    def is_indented(self):
        return self.head == ''

    def is_continuing(self):
        return self.head == self._row_continuation_marker

    def is_commented(self):
        return bool(not self.cells and self.comments)

    def test_or_user_keyword_setting_name(self):
        return self.head[1:-1].strip()

    def _parse(self, row):
        row = [self._collapse_whitespace(cell) for cell in row]
        return self._purge_empty_cells(self._extract_data(row)), \
            self._extract_comments(row)

    def _collapse_whitespace(self, value):
        return self._whitespace_regexp.sub(' ', value).strip()

    def _extract_comments(self, row):
        if not row:
            return []
        comments = []
        for c in row:
            if c.startswith('#') and not comments:
                comments.append(c[1:])
            elif comments:
                comments.append(c)
        return comments

    def _extract_data(self, row):
        if not row:
            return []
        data = []
        for c in row:
            if c.startswith('#'):
                return data
            data.append(c)
        return data

    def _purge_empty_cells(self, data):
        while data and not data[-1]:
            data.pop()
        # Cells with only a single backslash are considered empty
        return [ cell if cell != '\\' else '' for cell in data]

    def __nonzero__(self):
        return bool(self.cells or self.comments)
