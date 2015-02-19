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

from .dataextractor import DataExtractor


class _Aligner(object):

    def __init__(self, widths=None):
        self._widths = widths or []

    def align_rows(self, rows):
        return [self.align_row(r) for r in rows]

    def align_row(self, row):
        for index, col in enumerate(row):
            if len(self._widths) <= index:
                break
            row[index] = row[index].ljust(self._widths[index])
        return row


class FirstColumnAligner(_Aligner):

    def __init__(self, first_column_width):
        _Aligner.__init__(self, [first_column_width])


class ColumnAligner(_Aligner):

    def __init__(self, first_column_width, table):
        _Aligner.__init__(self, self._count_widths(first_column_width, table))

    def _count_widths(self, first_column_width, table):
        result = [first_column_width] + [len(h) for h in table.header[1:]]
        for row in DataExtractor().rows_from_table(table):
            for index, col in enumerate(row[1:]):
                index += 1
                if len(result) <= index:
                    result.append(len(col))
                else:
                    result[index] = max(len(col), result[index])
        return result


class NullAligner(_Aligner):

    def align_rows(self, rows):
        return rows

    def align_row(self, row):
        return row
