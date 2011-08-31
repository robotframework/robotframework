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

import HTMLParser
from htmlentitydefs import entitydefs
import sys

extra_entitydefs = {'nbsp': ' ',  'apos': "'", 'tilde': '~'}


# Workaround for following bug in Python 2.6: http://bugs.python.org/issue3932
if sys.version_info[:2] > (2, 5):
    def _unescape_from_py25(self, s):
        if '&' not in s:
            return s
        s = s.replace("&lt;", "<")
        s = s.replace("&gt;", ">")
        s = s.replace("&apos;", "'")
        s = s.replace("&quot;", '"')
        s = s.replace("&amp;", "&") # Must be last
        return s

    HTMLParser.HTMLParser.unescape = _unescape_from_py25


class RobotHtmlParser(HTMLParser.HTMLParser):

    def __init__(self, reader):
        HTMLParser.HTMLParser.__init__(self)
        self._reader = reader
        self._handlers = {'table_start' : reader.table_start,
                          'table_end'   : reader.table_end,
                          'tr_start'    : reader.tr_start,
                          'tr_end'      : reader.tr_end,
                          'td_start'    : reader.td_start,
                          'td_end'      : reader.td_end,
                          'th_start'    : reader.td_start,
                          'th_end'      : reader.td_end,
                          'br_start'    : reader.br_start,
                          'meta_start'  : reader.meta_start}

    def parse(self, htmlfile):
        for line in htmlfile.readlines():
            self.feed(line)
        self.close()

    def handle_starttag(self, tag, attrs):
        handler = self._handlers.get(tag+'_start')
        if handler is not None:
            handler(attrs)

    def handle_endtag(self, tag):
        handler = self._handlers.get(tag+'_end')
        if handler is not None:
            handler()

    def handle_data(self, data, decode=True):
        self._reader.data(data, decode)

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
        self._reader.pi(data)

    def unknown_decl(self, data):
        # Ignore everything even if it's invalid. This kind of stuff comes
        # at least from MS Excel
        pass
