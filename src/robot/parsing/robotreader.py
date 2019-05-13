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

from robot.output import LOGGER
from robot.utils import JYTHON, Utf8Reader, prepr


NBSP = u'\xa0'


class RobotReader(object):
    _space_splitter = re.compile(u'[ \t\xa0]{2,}|\t+')
    _pipe_splitter = re.compile(u'[ \t\xa0]+\|(?=[ \t\xa0]+)')
    _pipe_starts = ('|', '| ', '|\t', u'|\xa0')
    _pipe_ends = (' |', '\t|', u'\xa0|')

    def read(self, file, populator, path=None):
        path = path or getattr(file, 'name', '<file-like object>')
        process = False
        for lineno, line in enumerate(Utf8Reader(file).readlines(), start=1):
            cells = self.split_row(line.rstrip())
            cells = list(self._check_deprecations(cells, path, lineno))
            if cells and cells[0].strip().startswith('*') and \
                    populator.start_table([c.replace('*', '').strip()
                                           for c in cells]):
                process = True
            elif process:
                populator.add(cells)
        return populator.eof()

    @classmethod
    def split_row(cls, row):
        if row[:2] in cls._pipe_starts:
            row = row[1:-1] if row[-2:] in cls._pipe_ends else row[1:]
            return [cls._strip_whitespace(cell)
                    for cell in cls._pipe_splitter.split(row)]
        return cls._space_splitter.split(row)

    def _check_deprecations(self, cells, path, line_number):
        for original in cells:
            normalized = self._normalize_whitespace(original)
            if normalized != original:
                if len(normalized) != len(original):
                    msg = 'Collapsing consecutive whitespace'
                else:
                    msg = 'Converting whitespace characters to ASCII spaces'
                LOGGER.warn("%s during parsing is deprecated. Fix %s in file "
                            "'%s' on line %d."
                            % (msg, prepr(original), path, line_number))
            yield normalized

    # Jython has issues with non-ASCII spaces https://bugs.jython.org/issue2772
    if JYTHON:

        _whitespace = re.compile(u'\\s+', re.UNICODE)
        _trailing_whitespace = re.compile(u'\\s+$', re.UNICODE)

        @classmethod
        def _strip_whitespace(cls, string):
            match = cls._whitespace.match(string)
            if match:
                string = string[match.end():]
            match = cls._trailing_whitespace.search(string)
            if match:
                string = string[:match.start()]
            return string

        def _normalize_whitespace(self, string):
            return ' '.join(self._whitespace.split(string))

    else:

        @classmethod
        def _strip_whitespace(cls, string):
            return string.strip()

        def _normalize_whitespace(self, string):
            return ' '.join(string.split())
