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

import sys
from xml.sax.saxutils import XMLGenerator
from xml.sax.xmlreader import AttributesImpl

from abstractxmlwriter import AbstractXmlWriter


class XmlWriter(AbstractXmlWriter):

    def __init__(self, path):
        self.path = path
        self._output = open(path, 'wb')
        self._writer = XMLGenerator(self._output, encoding='UTF-8')
        self._writer.startDocument()
        self.closed = False

    def start(self, name, attributes={}, newline=True):
        self._writer.startElement(name, AttributesImpl(attributes))
        if newline:
            self.content('\n')

    def content(self, content):
        if content is not None:
            self._writer.characters(self._encode(content))

    def end(self, name, newline=True):
        self._writer.endElement(name)
        if newline:
            self.content('\n')

    def close(self):
        self._writer.endDocument()
        self._output.close()
        self.closed = True

    # Workaround for http://ironpython.codeplex.com/workitem/29474
    if sys.platform == 'cli':
        def _encode(self, content):
            return AbstractXmlWriter._encode(self, content).encode('UTF-8')
