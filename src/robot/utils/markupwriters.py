#  Copyright 2008-2014 Nokia Solutions and Networks
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

from .markuputils import html_escape, xml_escape, attribute_escape


class _MarkupWriter(object):

    def __init__(self, output, line_separator='\n', encoding='UTF-8'):
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
        self._encoding = encoding
        self._preamble()

    def _preamble(self):
        pass

    def start(self, name, attrs=None, newline=True):
        self._write('<%s %s>' % (name, self._format_attrs(attrs))
                    if attrs else '<%s>' % name, newline)

    def _format_attrs(self, attrs):
        return ' '.join('%s="%s"' % (name, attribute_escape(attrs[name]))
                        for name in self._order_attrs(attrs))

    def _order_attrs(self, attrs):
        return attrs

    def content(self, content=None, escape=True, newline=False,
                replace_newlines=False):
        if content:
            if replace_newlines:
                content = content.replace('\n', self._line_separator)
            self._write(self._escape(content) if escape else content, newline)

    def _escape(self, content):
        raise NotImplementedError

    def end(self, name, newline=True):
        self._write('</%s>' % name, newline)

    def element(self, name, content=None, attrs=None, escape=True,
                newline=True, replace_newlines=False):
        self.start(name, attrs, newline=False)
        self.content(content, escape, replace_newlines)
        self.end(name, newline)

    def close(self):
        """Closes the underlying output file."""
        self.output.close()

    def _write(self, text, newline=False):
        self.output.write(self._encode(text))
        if newline:
            self.output.write(self._line_separator)

    def _encode(self, text):
        return text.encode(self._encoding) if self._encoding else text


class HtmlWriter(_MarkupWriter):

    def _order_attrs(self, attrs):
        return sorted(attrs)  # eases testing

    def _escape(self, content):
        return html_escape(content)


class XmlWriter(_MarkupWriter):

    def _preamble(self):
        self._write('<?xml version="1.0" encoding="%s"?>' % self._encoding,
                    newline=True)

    def _escape(self, text):
        return xml_escape(text)


class NullMarkupWriter(object):
    """Null implementation of _MarkupWriter interface"""
    __init__ = start = content = element = end = close = lambda *args: None
