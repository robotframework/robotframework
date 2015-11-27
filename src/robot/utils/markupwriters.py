#  Copyright 2008-2015 Nokia Solutions and Networks
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

from .markuputils import attribute_escape, html_escape, xml_escape
from .robottypes import is_string
from .robotio import file_writer


class _MarkupWriter(object):

    def __init__(self, output, write_empty=True):
        """
        :param output: Either an opened, file like object, or a path to the
            desired output file. In the latter case, the file is created
            and clients should use :py:meth:`close` method to close it.
        :param write_empty: Whether to write empty elements and attributes.
        """
        if is_string(output):
            output = file_writer(output)
        self.output = output
        self._write_empty = write_empty
        self._preamble()

    def _preamble(self):
        pass

    def start(self, name, attrs=None, newline=True):
        attrs = self._format_attrs(attrs)
        self._start(name, attrs, newline)

    def _start(self, name, attrs, newline):
        self._write('<%s %s>' % (name, attrs) if attrs else '<%s>' % name,
                    newline)

    def _format_attrs(self, attrs):
        if not attrs:
            return ''
        attrs = [(k, attribute_escape(attrs[k] or ''))
                 for k in self._order_attrs(attrs)]
        write_empty = self._write_empty
        return ' '.join('%s="%s"' % a for a in attrs if write_empty or a[1])

    def _order_attrs(self, attrs):
        return attrs

    def content(self, content=None, escape=True, newline=False):
        if content:
            self._write(self._escape(content) if escape else content, newline)

    def _escape(self, content):
        raise NotImplementedError

    def end(self, name, newline=True):
        self._write('</%s>' % name, newline)

    def element(self, name, content=None, attrs=None, escape=True,
                newline=True, replace_newlines=False):
        attrs = self._format_attrs(attrs)
        if self._write_empty or content or attrs:
            self._start(name, attrs, newline=False)
            self.content(content, escape, replace_newlines)
            self.end(name, newline)

    def close(self):
        """Closes the underlying output file."""
        self.output.close()

    def _write(self, text, newline=False):
        self.output.write(text)
        if newline:
            self.output.write('\n')


class HtmlWriter(_MarkupWriter):

    def _order_attrs(self, attrs):
        return sorted(attrs)  # eases testing

    def _escape(self, content):
        return html_escape(content)


class XmlWriter(_MarkupWriter):

    def _preamble(self):
        self._write('<?xml version="1.0" encoding="UTF-8"?>', newline=True)

    def _escape(self, text):
        return xml_escape(text)


class NullMarkupWriter(object):
    """Null implementation of _MarkupWriter interface."""
    __init__ = start = content = element = end = close = lambda *args: None
