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
        """Creates new _MarkupWriter.

        :param output: Either an opened, file like object, or a path to the
            desired output file. In the latter case, the file is created.
        :param line_separator: Defines the used line separator.
        :param encoding: Encoding to be used to encode all text written to the
            output file. If `None`, text will not be encoded.
        """
        if isinstance(output, basestring):
            output = open(output, 'w')
        self.output = output
        self._line_separator = line_separator
        self._encode = self._create_encoder(encoding)

    def _create_encoder(self, encoding):
        if encoding is None:
            return lambda text: text
        return lambda text: text.encode(encoding)

    def start(self, name, attrs=None, newline=True):
        self._write('<%s%s>%s' % (name, self._get_attrs(attrs),
                                  self._line_separator if newline else ''))

    def content(self, content=None, escape=True):
        if content:
            self._write(self._escape(content) if escape else content)

    def end(self, name, newline=True):
        self._write('</%s>%s' % (name, self._line_separator if newline else ''))

    def element(self, name, content=None, attrs=None, escape=True,
                newline=True):
        self.start(name, attrs, newline=False)
        self.content(content, escape)
        self.end(name, newline)

    def close(self):
        self.output.close()

    def _write(self, text):
        self.output.write(self._encode(text))

    def _get_attrs(self, attrs):
        if not attrs:
            return ''
        return ' ' + ' '.join(self._format_attributes(attrs))


class HtmlWriter(_MarkupWriter):

    def _escape(self, content):
        return html_escape(content)

    def _format_attributes(self, attrs):
        return ('%s="%s"' % (name, attribute_escape(attrs[name]))
                             for name in sorted(attrs))


class XmlWriter(_MarkupWriter):

    def __init__(self, output, line_separator=os.linesep, encoding=None):
        _MarkupWriter.__init__(self, output, line_separator, encoding)
        self._preamble()

    def _preamble(self):
        self.content('<?xml version="1.0" encoding="UTF-8"?>\n', escape=False)

    def _escape(self, text):
        return xml_escape(text)

    def _format_attributes(self, attrs):
        return ('%s="%s"' % (name, attribute_escape(attrs[name]))
                             for name in attrs)
