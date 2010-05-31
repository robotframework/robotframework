#  Copyright 2008-2010 Nokia Siemens Networks Oyj
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


import HTMLParser
import sys
from htmlentitydefs import entitydefs

extra_entitydefs = {'nbsp': ' ',  'apos': "'", 'tilde': '~'}


class HtmlReader(HTMLParser.HTMLParser):
    IGNORE = 0
    INITIAL = 1
    PROCESS = 2

    def __init__(self):
        HTMLParser.HTMLParser.__init__(self)
        self._encoding = 'ISO-8859-1'
        self._handlers = { 'table_start' : self.table_start,
                           'table_end'   : self.table_end,
                           'tr_start'    : self.tr_start,
                           'tr_end'      : self.tr_end,
                           'td_start'    : self.td_start,
                           'td_end'      : self.td_end,
                           'th_start'    : self.td_start,
                           'th_end'      : self.td_end,
                           'br_start'    : self.br_start,
                           'meta_start'  : self.meta_start }

    def read(self, htmlfile, populator):
        self.populator = populator
        self.state = self.IGNORE
        self.current_row = None
        self.current_cell = None
        for line in htmlfile.readlines():
            self.feed(line)
        # Calling close is required by the HTMLParser but may cause problems
        # if the same instance of our HtmlParser is reused. Currently it's
        # used only once so there's no problem.
        self.close()
        self.populator.eof()

    def handle_starttag(self, tag, attrs):
        handler = self._handlers.get(tag+'_start')
        if handler is not None:
            handler(attrs)

    def handle_endtag(self, tag):
        handler = self._handlers.get(tag+'_end')
        if handler is not None:
            handler()

    def handle_data(self, data, decode=True):
        if self.state == self.IGNORE or self.current_cell is None:
            return
        if decode:
            data = data.decode(self._encoding)
        self.current_cell.append(data)

    def handle_entityref(self, name):
        value = self._handle_entityref(name)
        self.handle_data(value, decode=False)

    def _handle_entityref(self, name):
        if extra_entitydefs.has_key(name):
            return extra_entitydefs[name]
        try:
            value = entitydefs[name]
        except KeyError:
            return '&'+name+';'
        if value.startswith('&#'):
            return unichr(int(value[2:-1]))
        return value.decode('ISO-8859-1')

    def handle_charref(self, number):
        value = self._handle_charref(number)
        self.handle_data(value, decode=False)

    def _handle_charref(self, number):
        try:
            return unichr(int(number))
        except ValueError:
            return '&#'+number+';'

    def handle_pi(self, data):
        encoding = self._get_encoding_from_pi(data)
        if encoding:
            self._encoding = encoding

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
            if len(self.current_row) > 0:
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
        return valid_http_equiv and encoding or None

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


# Workaround for following bug in Python 2.6: http://bugs.python.org/issue3932
if sys.version_info[:2] > (2, 5):
    def unescape_from_py25(self, s):
        if '&' not in s:
            return s
        s = s.replace("&lt;", "<")
        s = s.replace("&gt;", ">")
        s = s.replace("&apos;", "'")
        s = s.replace("&quot;", '"')
        s = s.replace("&amp;", "&") # Must be last
        return s

    HTMLParser.HTMLParser.unescape = unescape_from_py25
