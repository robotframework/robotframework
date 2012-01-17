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

import os

from .htmlutils import html_escape, html_attr_escape


class HtmlWriter(object):

    def __init__(self, output, line_separator=os.linesep, encoding=None):
        self.output = output
        self._line_separator = line_separator
        self._encoding = encoding

    def start(self, name, attrs=None, newline=True):
        self._write('<%s%s>%s' % (name, self._get_attrs(attrs),
                                  self._line_separator if newline else ''))

    def content(self, content=None, escape=True):
        if content:
            self._write(html_escape(content) if escape else content)

    def end(self, name, newline=True):
        self._write('</%s>%s' % (name, self._line_separator if newline else ''))

    def element(self, name, content=None, attrs=None, escape=True, newline=True):
        self.start(name, attrs, newline=False)
        self.content(content, escape)
        self.end(name, newline)

    def close(self):
        self.output.close()

    def _write(self, text):
        self.output.write(self._encode(text))

    def _encode(self, text):
        return text.encode(self._encoding) if self._encoding else text

    def _get_attrs(self, attrs):
        if not attrs:
            return ''
        return ' ' + ' '.join('%s="%s"' % (name, html_attr_escape(attrs[name]))
                              for name in sorted(attrs))
