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
import re

from robot.errors import DataError
from robot.htmldata import HtmlFileWriter, ModelWriter, JsonWriter, LIBDOC
from robot import utils


class LibdocHtmlWriter(object):

    def write(self, libdoc, output):
        model_writer = LibdocModelWriter(output, libdoc)
        HtmlFileWriter(output, model_writer).write(LIBDOC)


class LibdocModelWriter(ModelWriter):

    def __init__(self, output, libdoc):
        self._output = output
        self._libdoc = libdoc

    def write(self, line):
        self._output.write('<script type="text/javascript">' + os.linesep)
        self.write_data()
        self._output.write('</script>' + os.linesep)

    def write_data(self):
        formatter = DocFormatter(self._libdoc.keywords, self._libdoc.doc,
                                 self._libdoc.doc_format)
        libdoc = JsonConverter(formatter).convert(self._libdoc)
        JsonWriter(self._output).write_json('libdoc = ', libdoc)


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
            'generated': utils.get_timestamp(daysep='-', millissep=None),
            'inits': self._get_keywords(libdoc.inits),
            'keywords': self._get_keywords(libdoc.keywords)
        }

    def _get_keywords(self, keywords):
        return [self._convert_keyword(kw) for kw in keywords]

    def _convert_keyword(self, kw):
        return {
            'name': kw.name,
            'args': ', '.join(kw.args),
            'doc': self._doc_formatter.html(kw.doc),
            'shortdoc': kw.shortdoc
        }


class DocFormatter(object):
    _header_regexp = re.compile(r'<h2>(.+?)</h2>')
    _name_regexp = re.compile('`(.+?)`')

    def __init__(self, keywords, introduction, doc_format='ROBOT'):
        self._doc_to_html = DocToHtml(doc_format)
        self._targets = self._get_targets(keywords, introduction,
                                          doc_format == 'ROBOT')

    def _get_targets(self, keywords, introduction, robot_format):
        targets = utils.NormalizedDict({
            'introduction': 'introduction',
            'library introduction': 'introduction',
            'importing': 'importing',
            'library importing': 'importing',
            'shortcuts': 'shortcuts',
            'keywords': 'keywords'
        })
        for kw in keywords:
            targets[kw.name] = kw.name
        if robot_format:
            for header in self._yield_header_targets(introduction):
                targets[header] = header
        return targets

    def _yield_header_targets(self, introduction):
        for line in introduction.splitlines():
            line = line.strip()
            if line.startswith('= ') and line.endswith(' ='):
                yield line[1:-1].strip()

    def html(self, doc, intro=False):
        doc = self._doc_to_html(doc)
        if intro:
            doc = self._header_regexp.sub(r'<h2 id="\1">\1</h2>', doc)
        return self._name_regexp.sub(self._link_keywords, doc)

    def _link_keywords(self, match):
        name = match.group(1)
        if name in self._targets:
            return '<a href="#%s" class="name">%s</a>' % (self._targets[name], name)
        return '<span class="name">%s</span>' % name


class DocToHtml(object):

    def __init__(self, format):
        self._formatter =  self._get_formatter(format)


    def _get_formatter(self, format):
        try:
            return {'ROBOT': utils.html_format,
                    'TEXT': self._format_text,
                    'HTML': self._format_html,
                    'REST': self._format_rest}[format]
        except KeyError:
            raise DataError("Invalid documentation format '%s'." % format)

    def _format_text(self, doc):
        return '<p style="white-space: pre-wrap">%s</p>' % utils.html_escape(doc)

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
