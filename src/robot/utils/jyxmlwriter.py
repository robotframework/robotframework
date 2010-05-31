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


from java.io import FileOutputStream
from javax.xml.transform.sax import SAXTransformerFactory
from javax.xml.transform.stream import StreamResult
from org.xml.sax.helpers import AttributesImpl

from abstractxmlwriter import AbstractXmlWriter


class XmlWriter(AbstractXmlWriter):

    def __init__(self, path):
        self.path = path
        self._output = FileOutputStream(path)
        self._writer = SAXTransformerFactory.newInstance().newTransformerHandler()
        self._writer.setResult(StreamResult(self._output))
        self._writer.startDocument()
        self.content('\n')
        self.closed = False

    def start(self, name, attributes={}, newline=True):
        attrs = AttributesImpl()
        for attrname, attrvalue in attributes.items():
            attrs.addAttribute('', '', attrname, '', attrvalue)
        self._writer.startElement('', '', name, attrs)
        if newline:
            self.content('\n')

    def content(self, content):
        if content is not None:
            content = self._encode(content)
            self._writer.characters(content, 0, len(content))

    def end(self, name, newline=True):
        self._writer.endElement('', '', name)
        if newline:
            self.content('\n')

    def close(self):
        self._writer.endDocument()
        self._output.close()
        self.closed = True
