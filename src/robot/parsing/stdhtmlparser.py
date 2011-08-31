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
        self._encoding = 'ISO-8859-1'

    def parse(self, htmlfile):
        for line in htmlfile:
            self.feed(line)
        self.close()

    def handle_starttag(self, tag, attrs):
        if tag == 'meta':
            self._set_encoding(self._get_encoding_from_meta(attrs))
        else:
            self._reader.start(tag)

    def _set_encoding(self, encoding):
        if encoding:
            self._encoding = encoding

    def handle_endtag(self, tag):
        self._reader.end(tag)

    def handle_data(self, data, decode=True):
        if decode:
            data = data.decode(self._encoding)
        self._reader.data(data)

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
        self._set_encoding(self._get_encoding_from_pi(data))

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

    def unknown_decl(self, data):
        # Ignore everything even if it's invalid. This kind of stuff comes
        # at least from MS Excel
        pass

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

