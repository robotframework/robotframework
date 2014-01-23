#  Copyright 2008-2014 Nokia Solutions and Networks
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

from robot.utils import Utf8Reader


NBSP = u'\xA0'


class TsvReader(object):

    def read(self, tsvfile, populator):
        process = False
        for row in Utf8Reader(tsvfile).readlines():
            row = self._process_row(row)
            cells = [self._process_cell(cell) for cell in self.split_row(row)]
            if cells and cells[0].strip().startswith('*') and \
                    populator.start_table([c.replace('*', '') for c in cells]):
                process = True
            elif process:
                populator.add(cells)
        populator.eof()

    def _process_row(self, row):
        if NBSP in row:
            row = row.replace(NBSP, ' ')
        return row.rstrip()

    @classmethod
    def split_row(cls, row):
        return row.split('\t')

    def _process_cell(self, cell):
        if len(cell) > 1 and cell[0] == cell[-1] == '"':
            cell = cell[1:-1].replace('""', '"')
        return cell
