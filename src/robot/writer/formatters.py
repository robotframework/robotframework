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


class TsvFormatter(object):
    _padding = ''

    def __init__(self, cols=8):
        self._cols = cols
        self._formatter = Formatter(self._padding, self._cols)

    def format(self, row, indent):
        return [self._pad(row) for row in self._formatter.format(row, indent)]

    def _pad(self, row):
        return row + [self._padding] * (self._cols - len(row))


class TxtFormatter(object):
    _padding = ''

    def __init__(self, cols=8):
        self._cols = cols
        self._formatter = Formatter(self._padding, self._cols)

    def format(self, row, indent=0, justifications=[]):
        rows = self._formatter.format(row, indent)
        return self._justify(self._escape(rows), justifications)

    def _escape(self, rows):
        for index, row in enumerate(rows):
            if len(row) >= 2 and row[0] == '' and row[1] == '':
                row[1] = '\\'
            rows[index] = [re.sub('\s\s+(?=[^\s])', lambda match: '\\'.join(match.group(0)), item) for item in row]
        return rows

    def _justify(self, rows, justifications):
        for row in rows:
            for index, col in enumerate(row[:-1]):
                if len(justifications) <= index:
                    continue
                row[index] = row[index].ljust(justifications[index])
        return rows


class PipeFormatter(TxtFormatter):
    _padding = '  '


class HtmlFormatter(object):

    def __init__(self):
        self._formatter = Formatter(cols=5)
        self._padding = ''
        self._cols = 5

    def format(self, row, indent, colspan):
        return [self._pad(row, colspan) for row in self._formatter.format(row, indent)]

    def _pad(self, row, colspan):
        if colspan:
            return row
        return row + [self._padding] * (self._cols - len(row))


class Formatter(object):

    def __init__(self, padding='', cols=8):
        self._cols = cols
        self._padding = padding

    def format(self, row, indent):
        return [self._encode(r) for r in self._split_to_rows(row, indent)]

    def _encode(self, row):
        return [cell.encode('UTF-8').replace('\n', ' ') for cell in row]

    def _split_to_rows(self, data, indent=0):
        if not data:
            return [[]]
        rows = []
        while data:
            current, data = self._split(data, indent)
            rows.append(self._escape_last_empty_cell(current))
            data = self._add_line_continuation(data)
        return rows

    def _split(self, data, indent):
        data = self._indent(data, indent)
        return data[:self._cols], data[self._cols:]

    def _escape_last_empty_cell(self, row):
        if not row[-1].strip():
            row[-1] = '${EMPTY}'
        return row

    def _add_line_continuation(self, data):
        if data:
            data = ['...'] + data
        return data

    def _indent(self, row, indent):
        return [self._padding]*indent + row
