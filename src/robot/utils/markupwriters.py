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

import os

from .markuputils import html_escape, xml_escape, attribute_escape


class _MarkupWriter(object):

    def __init__(self, output, line_separator=os.linesep, encoding=None):
        """
        :param output: Either an opened, file like object, or a path to the
            desired output file. In the latter case, the file is created
            and clients should use :py:meth:`close` method to close it.
        :param line_separator: Defines the used line separator.
        :param encoding: Encoding to be used to encode all text written to the
            output file. If `None`, text will not be encoded.
        """
        if isinstance(output, basestring):
            output = open(output, 'w')
        self.output = output
        self._line_separator = line_separator
        self._encode = self._create_encoder(encoding)
        self._preamble()

    def _create_encoder(self, encoding):
        if encoding is None:
            return lambda text: text
        return lambda text: text.encode(encoding)

    def start(self, name, attrs=None, newline=True):
        self._write('<%s %s>' % (name, self._format_attrs(attrs))
                    if attrs else '<%s>' % name, newline)

    def _format_attrs(self, attrs):
        return ' '.join('%s="%s"' % (name, attribute_escape(attrs[name]))
                        for name in self._order_attrs(attrs))

    def content(self, content=None, escape=True):
        if content:
            self._write(self._escape(content) if escape else content)

    def end(self, name, newline=True):
        self._write('</%s>' % name, newline)

    def element(self, name, content=None, attrs=None, escape=True,
                newline=True):
        self.start(name, attrs, newline=False)
        self.content(content, escape)
        self.end(name, newline)

    def close(self):
        """Closes the underlying output file."""
        self.output.close()

    def _write(self, text, newline=False):
        self.output.write(self._encode(text))
        if newline:
            self.output.write(self._line_separator)


class HtmlWriter(_MarkupWriter):

    def _preamble(self):
        pass

    def _escape(self, content):
        return html_escape(content)

    def _order_attrs(self, attrs):
        return sorted(attrs)  # eases testing


class XmlWriter(_MarkupWriter):

    def _preamble(self):
        self._write('<?xml version="1.0" encoding="UTF-8"?>', newline=True)

    def _escape(self, text):
        return xml_escape(text)

    def _order_attrs(self, attrs):
        return attrs


class NullMarkupWriter(object):
    """Null implementation of _MarkupWriter interface"""
    __init__ = start = content = element = end = close = lambda *args: None
