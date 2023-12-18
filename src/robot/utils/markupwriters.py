#  Copyright 2008-2015 Nokia Networks
#  Copyright 2016-     Robot Framework Foundation
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
from .robottypes import is_string, is_pathlike
from .robotio import file_writer


class _MarkupWriter:

    def __init__(self, output, write_empty=True, usage=None, preamble=True):
        """
        :param output: Either an opened, file like object, or a path to the
            desired output file. In the latter case, the file is created
            and clients should use :py:meth:`close` method to close it.
        :param write_empty: Whether to write empty elements and attributes.
        """
        if is_string(output) or is_pathlike(output):
            output = file_writer(output, usage=usage)
        self.output = output
        self._write_empty = write_empty
        if preamble:
            self._preamble()

    def _preamble(self):
        pass

    def start(self, name, attrs=None, newline=True, write_empty=None):
        attrs = self._format_attrs(attrs, write_empty)
        self._start(name, attrs, newline)

    def _start(self, name, attrs, newline):
        self._write(f'<{name} {attrs}>' if attrs else f'<{name}>', newline)

    def _format_attrs(self, attrs, write_empty):
        if not attrs:
            return ''
        if write_empty is None:
            write_empty = self._write_empty
        return ' '.join(f"{name}=\"{attribute_escape(value or '')}\""
                        for name, value in self._order_attrs(attrs)
                        if write_empty or value)

    def _order_attrs(self, attrs):
        return attrs.items()

    def content(self, content=None, escape=True, newline=False):
        if content:
            self._write(self._escape(content) if escape else content, newline)

    def _escape(self, content):
        raise NotImplementedError

    def end(self, name, newline=True):
        self._write(f'</{name}>', newline)

    def element(self, name, content=None, attrs=None, escape=True, newline=True,
                write_empty=None):
        attrs = self._format_attrs(attrs, write_empty)
        if write_empty is None:
            write_empty = self._write_empty
        if write_empty or content or attrs:
            self._start(name, attrs, newline=False)
            self.content(content, escape)
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
        return sorted(attrs.items())  # eases testing

    def _escape(self, content):
        return html_escape(content)


class XmlWriter(_MarkupWriter):

    def _preamble(self):
        self._write('<?xml version="1.0" encoding="UTF-8"?>', newline=True)

    def _escape(self, text):
        return xml_escape(text)

    def element(self, name, content=None, attrs=None, escape=True, newline=True,
                write_empty=None):
        if content:
            super().element(name, content, attrs, escape, newline, write_empty)
        else:
            self._self_closing_element(name, attrs, newline, write_empty)

    def _self_closing_element(self, name, attrs, newline, write_empty):
        attrs = self._format_attrs(attrs, write_empty)
        if write_empty is None:
            write_empty = self._write_empty
        if write_empty or attrs:
            self._write(f'<{name} {attrs}/>' if attrs else f'<{name}/>', newline)


class NullMarkupWriter:
    """Null implementation of the _MarkupWriter interface."""

    __init__ = start = content = element = end = close = lambda *args, **kwargs: None
