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

import re
try:
    from urllib import quote
except ImportError:
    from urllib.parse import quote

from robot.errors import DataError
from robot.htmldata import HtmlFileWriter, ModelWriter, JsonWriter, LIBDOC
from robot.utils import get_timestamp, html_escape, html_format, NormalizedDict
from robot.utils.htmlformatters import HeaderFormatter


class LibdocHtmlWriter(object):

    def write(self, libdoc, output):
        model_writer = LibdocModelWriter(output, libdoc)
        HtmlFileWriter(output, model_writer).write(LIBDOC)


class LibdocModelWriter(ModelWriter):

    def __init__(self, output, libdoc):
        self._output = output
        formatter = DocFormatter(libdoc.keywords, libdoc.doc, libdoc.doc_format)
        self._libdoc = JsonConverter(formatter).convert(libdoc)

    def write(self, line):
        self._output.write('<script type="text/javascript">\n')
        self.write_data()
        self._output.write('</script>\n')

    def write_data(self):
        JsonWriter(self._output).write_json('libdoc = ', self._libdoc)


class JsonConverter(object):

    def __init__(self, doc_formatter):
        self._doc_formatter = doc_formatter

    def convert(self, libdoc):
        return {
            'name': libdoc.name,
            'doc': self._doc_formatter.html(libdoc.doc, intro=True),
            'version': libdoc.version,
            'named_args': libdoc.named_args,
            'scope': libdoc.scope,
            'generated': get_timestamp(daysep='-', millissep=None),
            'inits': self._get_keywords(libdoc.inits),
            'keywords': self._get_keywords(libdoc.keywords),
            'all_tags': tuple(libdoc.all_tags),
            'contains_tags': bool(libdoc.all_tags)
        }

    def _get_keywords(self, keywords):
        return [self._convert_keyword(kw) for kw in keywords]

    def _convert_keyword(self, kw):
        return {
            'name': kw.name,
            'args': kw.args,
            'doc': self._doc_formatter.html(kw.doc),
            'shortdoc': kw.shortdoc,
            'tags': tuple(kw.tags),
            'matched': True
        }


class DocFormatter(object):
    _header_regexp = re.compile(r'<h([234])>(.+?)</h\1>')
    _name_regexp = re.compile('`(.+?)`')

    def __init__(self, keywords, introduction, doc_format='ROBOT'):
        self._doc_to_html = DocToHtml(doc_format)
        self._targets = self._get_targets(keywords, introduction,
                                          robot_format=doc_format == 'ROBOT')

    def _get_targets(self, keywords, introduction, robot_format):
        targets = {
            'introduction': 'Introduction',
            'library introduction': 'Introduction',
            'importing': 'Importing',
            'library importing': 'Importing',
            'shortcuts': 'Shortcuts',
            'keywords': 'Keywords'
        }
        for kw in keywords:
            targets[kw.name] = kw.name
        if robot_format:
            for header in self._yield_header_targets(introduction):
                targets[header] = header
        return self._escape_and_encode_targets(targets)

    def _yield_header_targets(self, introduction):
        headers = HeaderFormatter()
        for line in introduction.splitlines():
            match = headers.match(line)
            if match:
                yield match.group(2)

    def _escape_and_encode_targets(self, targets):
        return NormalizedDict((html_escape(key), self._encode_uri_component(value))
                              for key, value in targets.items())

    def _encode_uri_component(self, value):
        # Emulates encodeURIComponent javascript function
        return quote(value.encode('UTF-8'), safe="-_.!~*'()")

    def html(self, doc, intro=False):
        doc = self._doc_to_html(doc)
        if intro:
            doc = self._header_regexp.sub(r'<h\1 id="\2">\2</h\1>', doc)
        return self._name_regexp.sub(self._link_keywords, doc)

    def _link_keywords(self, match):
        name = match.group(1)
        if name in self._targets:
            return '<a href="#%s" class="name">%s</a>' % (self._targets[name], name)
        return '<span class="name">%s</span>' % name


class DocToHtml(object):

    def __init__(self, doc_format):
        self._formatter = self._get_formatter(doc_format)

    def _get_formatter(self, doc_format):
        try:
            return {'ROBOT': html_format,
                    'TEXT': self._format_text,
                    'HTML': self._format_html,
                    'REST': self._format_rest}[doc_format]
        except KeyError:
            raise DataError("Invalid documentation format '%s'." % doc_format)

    def _format_text(self, doc):
        return '<p style="white-space: pre-wrap">%s</p>' % html_escape(doc)

    def _format_html(self, doc):
        return '<div style="margin: 0">%s</div>' % doc

    def _format_rest(self, doc):
        try:
            from docutils.core import publish_parts
        except ImportError:
            raise DataError("reST format requires 'docutils' module to be installed.")
        parts = publish_parts(doc, writer_name='html')
        return self._format_html(parts['html_body'])

    def __call__(self, doc):
        return self._formatter(doc)
