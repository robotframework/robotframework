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

try:
    from lxmlhtmlparser import RobotHtmlParser
except ImportError:
    from stdhtmlparser import RobotHtmlParser


class HtmlReader(object):
    IGNORE = 0
    INITIAL = 1
    PROCESS = 2

    def __init__(self, parser=RobotHtmlParser):
        self._parser = parser(self)
        self._start_handlers = {'table': self.table_start,
                                'tr': self.tr_start,
                                'td': self.td_start,
                                'th': self.td_start,
                                'br': self.br_start}
        self._end_handlers = {'table': self.table_end,
                              'tr': self.tr_end,
                              'td': self.td_end,
                              'th': self.td_end}

    def read(self, htmlfile, populator):
        self.populator = populator
        self.state = self.IGNORE
        self.current_row = None
        self.current_cell = None
        self._parser.parse(htmlfile)
        self.populator.eof()

    def start(self, tag):
        handler = self._start_handlers.get(tag)
        if handler:
            handler()

    def end(self, tag):
        handler = self._end_handlers.get(tag)
        if handler:
            handler()

    def table_start(self):
        self.state = self.INITIAL
        self.current_row = None
        self.current_cell = None

    def table_end(self):
        if self.current_row is not None:
            self.tr_end()
        self.state = self.IGNORE

    def tr_start(self):
        if self.current_row is not None:
            self.tr_end()
        self.current_row = []

    def tr_end(self):
        if self.current_row is None:
            return
        if self.current_cell is not None:
            self.td_end()
        if self.state == self.INITIAL:
            if self.current_row:
                if self.populator.start_table(self.current_row):
                    self.state = self.PROCESS
                else:
                    self.state = self.IGNORE
            else:
                self.state = self.IGNORE
        elif self.state == self.PROCESS:
            self.populator.add(self.current_row)
        self.current_row = None

    def td_start(self):
        if self.current_cell is not None:
            self.td_end()
        if self.current_row is None:
            self.tr_start()
        self.current_cell = []

    def td_end(self):
        if self.current_cell is not None and self.state != self.IGNORE:
            cell = ''.join(self.current_cell)
            self.current_row.append(cell)
        self.current_cell = None

    def br_start(self):
        if self.current_cell is not None and self.state != self.IGNORE:
            self.current_cell.append('\n')

    def data(self, data):
        if self.current_cell is not None and self.state != self.IGNORE:
            self.current_cell.append(data)
