#  Copyright 2008-2012 Nokia Siemens Networks Oyj
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

from .unic import unic


class AbstractXmlWriter:
    _illegal_chars = re.compile(u'[\x00-\x08\x0B\x0C\x0E-\x1F\uFFFE\uFFFF]')

    def start(self, name, attributes=None, newline=True):
        self._start(name, self._escape_attrs(attributes))
        if newline:
            self._newline()

    def _start(self, name, attrs):
        raise NotImplementedError

    def _escape_attrs(self, attrs):
        if not attrs:
            return {}
        return dict((n, self._escape(v)) for n, v in attrs.items())

    def _escape(self, content):
        return self._illegal_chars.sub('', unic(content))

    def content(self, content):
        if content is not None:
            self._content(self._escape(content))

    def _content(self, content):
        raise NotImplementedError

    def end(self, name, newline=True):
        self._end(name)
        if newline:
            self._newline()

    def _end(self, name):
        raise NotImplementedError

    def element(self, name, content=None, attributes={}, newline=True):
        self.start(name, attributes, newline=False)
        self.content(content)
        self.end(name, newline)

    def close(self, close_output=True):
        if not self.closed:
            self._writer.endDocument()
            if close_output:
                self._output.close()
            self.closed = True
