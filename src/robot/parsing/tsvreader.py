#  Copyright 2008 Nokia Siemens Networks Oyj
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


class TsvReader:
        
    def read(self, tsvfile, rawdata):
        process = False
        for row in tsvfile.readlines():
            cells = self._get_cells(row)
            name = len(cells) > 0 and cells[0].strip() or ''
            if name.startswith('*') and rawdata.start_table(name.replace('*','')):
                process = True
            elif process:
                rawdata.add_row(cells)

    def _get_cells(self, row):
        if row.endswith('\n'):
            row = row[:-1]
        return [ self._process_cell(cell) for cell in row.split('\t') ]
    
    def _process_cell(self, cell):
        if len(cell) > 1 and cell[0] == cell[-1] == '"':
            cell = cell[1:-1].replace('""','"')
        return cell.decode('UTF-8')
