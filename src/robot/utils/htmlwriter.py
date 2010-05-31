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


from abstractxmlwriter import AbstractXmlWriter
from htmlutils import html_escape, html_attr_escape
from unic import unic


class HtmlWriter(AbstractXmlWriter):

    def __init__(self, output):
        """'output' is an open file object.

        Given 'output' must have been opened with 'wb' to be able to
        write into it with UTF-8 encoding.

        'self.output.name' is later used by serializers
        """
        self.output = output

    def start(self, name, attrs=None, newline=True):
        self._start(name, attrs, close=False, newline=newline)

    def start_and_end(self, name, attrs=None, newline=True):
        self._start(name, attrs, close=True, newline=newline)

    def content(self, content=None, escape=True):
        """Given content doesn't need to be a string"""
        if content is not None:
            if escape:
                content = self._escape_content(content)
            self._write(content)

    def end(self, name, newline=True):
        elem = '</%s>' % name
        if newline:
            elem += '\n'
        self._write(elem)

    def element(self, name, content=None, attrs=None, escape=True,
                newline=True):
        self.start(name, attrs, newline=False)
        self.content(content, escape)
        self.end(name, newline)

    def start_many(self, names, newline=True):
        for name in names:
            self.start(name, newline=newline)

    def end_many(self, names, newline=True):
        for name in names:
            self.end(name, newline)

    def _start(self, name, attrs, close=False, newline=True):
        elem = '<%s' % name
        elem = self._add_attrs(elem, attrs)
        elem += (close and ' />' or '>')
        if newline:
            elem += '\n'
        self._write(elem)

    def _add_attrs(self, elem, attrs):
        if not attrs:
            return elem
        attrs = attrs.items()
        attrs.sort()
        attrs = [ '%s="%s"' % (name, html_attr_escape(value))
                  for name, value in attrs ]
        return '%s %s' % (elem, ' '.join(attrs))

    def _escape_content(self, content):
        return html_escape(unic(content))

    def _write(self, text):
        self.output.write(text.encode('UTF-8'))
