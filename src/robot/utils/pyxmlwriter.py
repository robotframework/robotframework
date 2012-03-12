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

import sys
from xml.sax.saxutils import XMLGenerator
from xml.sax.xmlreader import AttributesImpl

from .abstractxmlwriter import AbstractXmlWriter


class XmlWriter(AbstractXmlWriter):

    def __init__(self, output):
        self._output = self._create_output(output)
        self._writer = XMLGenerator(self._output, encoding='UTF-8')
        self._writer.startDocument()
        self.closed = False

    def _create_output(self, output):
        return open(output, 'w') \
            if isinstance(output, basestring) else output

    def _start(self, name, attrs):
        self._writer.startElement(name, AttributesImpl(attrs))

    def _content(self, content):
        self._writer.characters(content)

    def _end(self, name):
        self._writer.endElement(name)

    def _newline(self):
        self._output.write('\n')

    # Workaround for http://ironpython.codeplex.com/workitem/29474
    if sys.platform == 'cli':
        def _escape(self, content):
            return AbstractXmlWriter._escape(self, content).encode('UTF-8')
