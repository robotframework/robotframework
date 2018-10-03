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

from robot.output import LOGGER
from robot.utils import PY2

if PY2:
    from htmlentitydefs import entitydefs
    from HTMLParser import HTMLParser

else:
    from html.entities import entitydefs
    from html.parser import HTMLParser

    unichr = chr


NON_BREAKING_SPACE = u'\xA0'


class HtmlReader(HTMLParser):
    IGNORE = 0
    INITIAL = 1
    PROCESS = 2

    def __init__(self):
        HTMLParser.__init__(self)
        self._encoding = 'ISO-8859-1'
        self._handlers = {'table_start' : self.table_start,
                          'table_end'   : self.table_end,
                          'tr_start'    : self.tr_start,
                          'tr_end'      : self.tr_end,
                          'td_start'    : self.td_start,
                          'td_end'      : self.td_end,
                          'th_start'    : self.td_start,
                          'th_end'      : self.td_end,
                          'br_start'    : self.br_start,
                          'meta_start'  : self.meta_start}

    def read(self, htmlfile, populator, path=None):
        self.populator = populator
        self.state = self.IGNORE
        self.current_row = None
        self.current_cell = None
        for line in htmlfile.readlines():
            self.feed(self._decode(line))
        # Calling close is required by the HTMLParser but may cause problems
        # if the same instance of our HtmlParser is reused. Currently it's
        # used only once so there's no problem.
        self.close()
        if self.populator.eof():
            LOGGER.warn("Using test data in HTML format is deprecated. "
                        "Convert '%s' to plain text format."
                        % (path or htmlfile.name))

    def _decode(self, line):
        return line.decode(self._encoding)

    def handle_starttag(self, tag, attrs):
        handler = self._handlers.get(tag+'_start')
        if handler is not None:
            handler(attrs)

    def handle_endtag(self, tag):
        handler = self._handlers.get(tag+'_end')
        if handler is not None:
            handler()

    def handle_data(self, data):
        if self.state == self.IGNORE or self.current_cell is None:
            return
        if NON_BREAKING_SPACE in data:
            data = data.replace(NON_BREAKING_SPACE, ' ')
        self.current_cell.append(data)

    def handle_entityref(self, name):
        value = self._handle_entityref(name)
        self.handle_data(value)

    def _handle_entityref(self, name):
        if name == 'apos':  # missing from entitydefs
            return "'"
        try:
            value = entitydefs[name]
        except KeyError:
            return '&'+name+';'
        if value.startswith('&#'):
            return unichr(int(value[2:-1]))
        if PY2:
            return value.decode('ISO-8859-1')
        return value

    def handle_charref(self, number):
        value = self._handle_charref(number)
        self.handle_data(value)

    def _handle_charref(self, number):
        if number.startswith(('x', 'X')):
            base = 16
            number = number[1:]
        else:
            base = 10
        try:
            return unichr(int(number, base))
        except ValueError:
            return '&#'+number+';'

    def unknown_decl(self, data):
        # Ignore everything even if it's invalid. This kind of stuff comes
        # at least from MS Excel
        pass

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
            accepted = self.populator.start_table(self.current_row)
            self.state = self.PROCESS if accepted else self.IGNORE
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
        self.handle_data('\n')

    def meta_start(self, attrs):
        encoding = self._get_encoding_from_meta(attrs)
        if encoding:
            self._encoding = encoding

    def _get_encoding_from_meta(self, attrs):
        valid_http_equiv = False
        encoding = None
        for name, value in attrs:
            name = name.lower()
            if name == 'charset':  # html5
                return value
            if name == 'http-equiv' and value.lower() == 'content-type':
                valid_http_equiv = True
            if name == 'content':
                encoding = self._get_encoding_from_content_attr(value)
        return encoding if valid_http_equiv else None

    def _get_encoding_from_content_attr(self, value):
        for token in value.split(';'):
            token = token.strip()
            if token.lower().startswith('charset='):
                return token[8:]

    def handle_pi(self, data):
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
