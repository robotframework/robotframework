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

from stdhtmlparser import RobotHtmlParser


class HtmlReader(object):
    IGNORE = 0
    INITIAL = 1
    PROCESS = 2

    def __init__(self):
        self._encoding = 'ISO-8859-1'
        self._parser = RobotHtmlParser(self)
        self._start_handlers = {'table': self.table_start,
                                'tr': self.tr_start,
                                'td': self.td_start,
                                'th': self.td_start,
                                'br': self.br_start,
                                'meta': self.meta_start}
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

    def start(self, tag, attrs):
        handler = self._start_handlers.get(tag)
        if handler:
            handler(attrs)

    def end(self, tag):
        handler = self._end_handlers.get(tag)
        if handler:
            handler()

    def table_start(self, attrs=None):
        self.state = self.INITIAL
        self.current_row = None
        self.current_cell = None

    def table_end(self):
        if self.current_row is not None:
            self.tr_end()
        self.state = self.IGNORE

    def tr_start(self, attrs=None):
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

    def td_start(self, attrs=None):
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

    def br_start(self, attrs=None):
        if self.current_cell is not None and self.state != self.IGNORE:
            self.current_cell.append('\n')

    def meta_start(self, attrs):
        encoding = self._get_encoding_from_meta(attrs)
        if encoding:
            self._encoding = encoding

    def _get_encoding_from_meta(self, attrs):
        valid_http_equiv = False
        encoding = None
        for name, value in attrs:
            name = name.lower()
            if name == 'http-equiv' and value.lower() == 'content-type':
                valid_http_equiv = True
            if name == 'content':
                for token in value.split(';'):
                    token = token.strip()
                    if token.lower().startswith('charset='):
                        encoding = token[8:]
        return encoding if valid_http_equiv else None

    def data(self, data, decode=True):
        if self.state == self.IGNORE or self.current_cell is None:
            return
        if decode:
            data = data.decode(self._encoding)
        self.current_cell.append(data)

    def pi(self, data):
        encoding = self._get_encoding_from_pi(data)
        if encoding:
            self._encoding = encoding

    def _get_encoding_from_pi(self, data):
        data = data.strip()
        if not data.lower().startswith('xml '):
            return None
        if data.endswith('?'):
            data = data[:-1]
        for token in data.split():
            if token.lower().startswith('encoding='):
                encoding = token[9:]
                if encoding.startswith("'") or encoding.startswith('"'):
                    encoding = encoding[1:-1]
                return encoding
        return None
