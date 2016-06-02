#  Copyright 2008-2015 Nokia Networks
#  Copyright 2016-     Robot Framework Foundation
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

from .tsvreader import TsvReader


class TxtReader(TsvReader):
    _space_splitter = re.compile(' {2,}')
    _pipe_splitter = re.compile(' \|(?= )')
    _pipe_starts = ('|', '| ')

    @classmethod
    def split_row(cls, row):
        if '\t' in row:
            row = row.replace('\t', '  ')
        if row[:2] in cls._pipe_starts:
            row = row[1:-1] if row.endswith(' |') else row[1:]
            return [cell.strip() for cell in cls._pipe_splitter.split(row)]
        return cls._space_splitter.split(row)

    def _process_cell(self, cell):
        return cell
