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

    @classmethod
    def split_row(cls, row):
        return [cls._strip_whitespace(cell) for cell in row.split('\t')]

    def _check_deprecations(self, cells, path, line_number):
        cells = RobotReader._check_deprecations(self, cells, path, line_number)
        cells = [self._deprecate_quoting(c, path, line_number) for c in cells]
        self._deprecate_empty_data_cells(cells, path, line_number)
        return cells

    def _deprecate_quoting(self, cell, path, line_number):
        if len(cell) > 1 and cell[0] == cell[-1] == '"':
            LOGGER.warn("TSV file '%s' has quotes around cells which is "
                        "deprecated and must be fixed. Remove quotes "
                        "from '%s' on line %d."
                        % (path, cell, line_number))
            return cell[1:-1].replace('""', '"').strip()
        return cell

    def _deprecate_empty_data_cells(self, cells, path, line_number):
        data_cells = dropwhile(lambda c: not c, cells)
        if not all(data_cells):
            LOGGER.warn("TSV file '%s' has empty data cells which is "
                        "deprecated and must be fixed. Escape empty cells "
                        "on line %d with '${EMPTY}'." % (path, line_number))
