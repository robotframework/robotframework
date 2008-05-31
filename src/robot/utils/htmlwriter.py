#  Copyright 2008 Nokia Siemens Networks Oyj
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


from types import UnicodeType

from abstractxmlwriter import AbstractXmlWriter, BINARY_DATA_ERROR
from htmlutils import html_escape, html_attr_escape
from robottypes import unic


class HtmlWriter(AbstractXmlWriter):
 
    def __init__(self, output):
        """'output' is an open file object.
        
        Given 'output' must have been opened with 'wb' to be able to write into
        it with UTF-8 encoding.
        
        'self.output.name' is later used by serializers
        """
        self.output = output
        
    def start_element(self, name, attrs=None, newline=True):
        self._start_element(name, attrs, close=False, newline=newline)
        
    def start_and_end_element(self, name, attrs=None, newline=True):
        self._start_element(name, attrs, close=True, newline=newline) 
                
    def content(self, content=None, escape=True):
        if content is not None:
            if escape:
                content = self._escape_content(content)
            self._write(content)

    def end_element(self, name, newline=True):
        elem = '</%s>' % name
        if newline:
            elem += '\n'
        self._write(elem)
            
    def whole_element(self, name, content=None, attrs=None, escape=True,
                      newline=True):
        self.start_element(name, attrs, newline=False)
        self.content(content, escape)
        self.end_element(name, newline)
    
    def start_elements(self, names, newline=True):
        for name in names:
            self.start_element(name, newline=newline)
            
    def end_elements(self, names, newline=True):
        for name in names:
            self.end_element(name, newline)

    def _start_element(self, name, attrs, close=False, newline=True):
        elem = '<%s' % name
        attrs = self._process_attrs(attrs)
        if attrs:
            elem += ' ' + attrs
        elem += (close and ' />' or '>')
        if newline:
            elem += '\n'
        self._write(elem)            
            
    def _process_attrs(self, attrs):
        if attrs is None:
            return ''
        attrs = attrs.items()
        attrs.sort()
        attrs = [ '%s="%s"' % (name, html_attr_escape(value))
                  for name, value in attrs ]
        return ' '.join(attrs)
    
    def _escape_content(self, content):
        if type(content) is not UnicodeType:
            try:
                content = unic(content)
            except:
                content = BINARY_DATA_ERROR
        return html_escape(content)

    def _write(self, text):
        self.output.write(text.encode('UTF-8'))
