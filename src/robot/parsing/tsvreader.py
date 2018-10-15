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

from itertools import dropwhile

from robot.output import LOGGER

from .robotreader import RobotReader


class TsvReader(RobotReader):

    def __init__(self):
        self._warned_empty = set()
        self._warned_escaping = set()

    @classmethod
    def split_row(cls, row):
        return row.split('\t')

    def _deprecate_empty_data_cells_in_tsv_format(self, cells, path):
        data_cells = dropwhile(lambda c: not c, cells)
        if not all(data_cells) and path not in self._warned_empty:
            LOGGER.warn("Empty cells in TSV files are deprecated. "
                        "Escape them with '${EMPTY}' in '%s'." % path)
            self._warned_empty.add(path)

    def _process_cell(self, cell, path):
        if len(cell) > 1 and cell[0] == cell[-1] == '"':
            cell = cell[1:-1].replace('""', '"')
            if path not in self._warned_escaping:
                LOGGER.warn("Un-escaping quotes in TSV files is deprecated. "
                            "Change cells in '%s' to not contain surrounding "
                            "quotes." % path)
                self._warned_escaping.add(path)
        return cell
