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


class _Aligner(object):

    def __init__(self, widths, align_last_column=False):
        self._widths = widths
        self._align_last_column = align_last_column

    def align_rows(self, rows):
        return [self.align_row(r) for r in rows]

    def align_row(self, row):
        for index, col in enumerate(row[:self._last_aligned_column(row)]):
            if len(self._widths) <= index:
                continue
            row[index] = row[index].ljust(self._widths[index])
        return row

    def _last_aligned_column(self, row):
        return len(row) if self._align_last_column else -1


class FirstColumnAligner(_Aligner):

    def __init__(self, cols, first_column_width):
        _Aligner.__init__(self, [first_column_width])


class ColumnAligner(_Aligner):

    def __init__(self, first_column_width, table, align_last_column):
        self._first_column_width = first_column_width
        _Aligner.__init__(self, self._count_justifications(table),
            align_last_column)

    def _count_justifications(self, table):
        result = [self._first_column_width] + [len(h) for h in table.header[1:]]
        for element in [list(kw) for kw in list(table)]:
            for step in element:
                for index, col in enumerate(step.as_list()):
                    index += 1
                    if len(result) <= index:
                        result.append(0)
                    result[index] = max(len(col), result[index])
        return result
