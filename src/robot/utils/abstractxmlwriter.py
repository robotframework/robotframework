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
import re

from unic import unic


_ILLEGAL_CHARS_IN_XML = u'\x00\x01\x02\x03\x04\x05\x06\x07\x08\x0b\x0c\x0e' \
    + u'\x0f\x10\x11\x12\x13\x14\x15\x16\x17\x18\x19\x1a\x1b\x1c\x1d\x1e\x1f\ufffe'
_ILLEGAL_CHARS_IN_XML_PATTERN = re.compile('['+_ILLEGAL_CHARS_IN_XML+']')

class AbstractXmlWriter:

    def start(self, name, attributes={}, newline=True):
        self._start(name, self._escape_attrs(attributes))
        if newline:
            self.content('\n')

    def _start(self, name, attrs):
        raise NotImplementedError

    def _escape_attrs(self, attrs):
        return dict((n, self._escape(v)) for n, v in attrs.items())

    def _escape(self, content):
        content = unic(content)
        # Avoid bug http://ironpython.codeplex.com/workitem/29402
        return _ILLEGAL_CHARS_IN_XML_PATTERN.sub('', content)

    def content(self, content):
        if content is not None:
            self._content(self._escape(content))

    def _content(self, content):
        raise NotImplementedError

    def end(self, name, newline=True):
        self._end(name)
        if newline:
            self.content('\n')

    def _end(self, name):
        raise NotImplementedError

    def element(self, name, content=None, attributes={}, newline=True):
        self.start(name, attributes, newline=False)
        self.content(content)
        self.end(name, newline)

    def close(self):
        self._close()
        self.closed = True

    def _close(self):
        self._writer.endDocument()
        self._output.close()
