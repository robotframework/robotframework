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

from java.io import FileOutputStream, Writer
from javax.xml.transform.sax import SAXTransformerFactory
from javax.xml.transform.stream import StreamResult
from org.xml.sax.helpers import AttributesImpl
from array import array

from abstractxmlwriter import AbstractXmlWriter


class XmlWriter(AbstractXmlWriter):

    def __init__(self, output):
        self.path = output
        self._output = self._create_output(output)
        self._writer = SAXTransformerFactory.newInstance().newTransformerHandler()
        self._writer.setResult(StreamResult(self._output))
        self._writer.startDocument()
        self.content('\n')
        self.closed = False

    def _create_output(self, output):
        if isinstance(output, basestring):
            return FileOutputStream(output)
        return OutputWriter(output)

    def _start(self, name, attrs):
        self._writer.startElement('', '', name, self._get_attrs_impl(attrs))

    def _get_attrs_impl(self, attrs):
        ai = AttributesImpl()
        for name, value in attrs.items():
            ai.addAttribute('', '', name, '', value)
        return ai

    def _content(self, content):
        self._writer.characters(content, 0, len(content))

    def _end(self, name):
        self._writer.endElement('', '', name)


class OutputWriter(Writer):

    def __init__(self, output):
        self._output = output

    def close(self): # abstract method of java.io.Writer
        pass

    def flush(self): # abstract method of java.io.Writer
        pass

    def write(self, *args):
        # There are 5 overloaded version of #write() in java.io.Writer,
        # the three that TransformHandler uses are handled below.
        value = args[0]
        if isinstance(value, array):
            value = args[0].tostring()
        if isinstance(value, int):
            value = chr(value)
        self._output.write(value)
