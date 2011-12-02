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


class TableWriter(object):

    def __init__(self, output, separator):
        self._output = output
        self._separator = separator
        self._has_headers = False

    def add_headers(self, headers):
        self._col_writer = ColumnWriter(self._output, headers, self._separator)

    def add_tcuk_name(self, name):
        self._col_writer.add_tcuk_name(name)

    def add_row(self, row):
        self._col_writer.add_row(row)

    def write(self):
        self._col_writer.write()


def SpaceSeparator(line_separator='\n',
                   number_of_spaces=4):
    return _Separator(' '*number_of_spaces,
                      line_separator,
                      align_separator='  ')

def PipeSeparator(line_separator='\n'):
    return _Separator(' | ',
                      line_separator,
                      line_prefix='| ',
                      line_postfix=' |',
                      align_separator=' | ')


def ColumnWriter(output, headers, separator):
    if headers[1:]:
        return _AlignedColumnWriter(output, headers, separator)
    else:
        return _FixedColumnWriter(output, headers, separator)


class _Separator(object):

    def __init__(self,
                 cell_separator,
                 line_separator,
                 line_prefix='',
                 line_postfix='',
                 align_separator=''):
        self.cell_separator = cell_separator
        self.line_separator = line_separator
        self.line_prefix = line_prefix
        self.line_postfix = line_postfix
        self.align_separator=align_separator

class _TableColumnWriter(object):

    def __init__(self,
                 output,
                 headers,
                 separator):
        self._output = output
        self._separator = separator
        self._headers = headers
        self._data = []

    def add_row(self, row):
        self._data += [row]

    def write(self):
        for row in [self._headers]+self._data:
            self._write_row(row, self._separator.cell_separator)

    def add_tcuk_name(self, name):
        self.add_row([name])


class _FixedColumnWriter(_TableColumnWriter):

    def _write_row(self, row, col_separator):
        if row:
            if '|' in self._separator.cell_separator and not row[0]:
                row = row[:]
                row[0] = '  '
            self._output.write(self._separator.line_prefix)
            self._output.write(col_separator.join(row))
            self._output.write(self._separator.line_postfix)
        self._output.write(self._separator.line_separator)


class _AlignedColumnWriter(_TableColumnWriter):

    _tcuk_name_in_cache = None

    def _write_row(self, row, col_separator):
        if row:
            self._output.write(self._separator.line_prefix)
            for column, value in enumerate(row[:-1]):
                self._output.write(value.ljust(self._get_column_justifications(column)))
                self._output.write(self._separator.align_separator)
            self._output.write(row[-1])
            self._output.write(self._separator.line_postfix)
            self._output.write(self._separator.line_separator)

    def _get_column_justifications(self, col):
        result = 0
        for row in [self._headers]+self._data:
            if len(row) <= max(col, 1):
                continue
            result = max(len(row[col]), result)
        return result

    def add_tcuk_name(self, name):
        if self._tcuk_name_in_cache:
            self.add_row([])
        self._tcuk_name_in_cache = name

    def add_row(self, row):
        if self._tcuk_name_in_cache:
            self._add_name_row(row)
        else:
            self._data += [row]

    def write(self):
        if self._tcuk_name_in_cache:
            self.add_row([])
        _TableColumnWriter.write(self)
        self._output.write(self._separator.line_separator)

    def _add_name_row(self, row):
        name = self._tcuk_name_in_cache
        self._tcuk_name_in_cache = None
        if len(name) > 24:
            self.add_row([name])
            self.add_row(row)
        else:
            self.add_row([name]+row[1:])
