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

from robot.htmldata import HtmlFileWriter, ModelWriter, JsonWriter
from robot import utils


class LibdocHtmlWriter(object):

    def write(self, libdoc, output):
        model_writer = LibdocModelWriter(output, libdoc)
        HtmlFileWriter(output, model_writer).write('libdoc.html')


class LibdocModelWriter(ModelWriter):

    def __init__(self, output, libdoc):
        self._output = output
        self._libdoc = libdoc

    def write(self, line):
        self._output.write('<script type="text/javascript">' + os.linesep)
        self._write_data()
        self._output.write('</script>' + os.linesep)

    def _write_data(self):
        formatter = DocFormatter(self._libdoc.keywords)
        libdoc = JsonConverter(formatter).convert(self._libdoc)
        JsonWriter(self._output).write_json('libdoc = ', libdoc)


class JsonConverter(object):

    def __init__(self, doc_formatter):
        self._doc_formatter = doc_formatter

    def convert(self, libdoc):
        return {
            'name': libdoc.name,
            'doc': self._doc_formatter.html(libdoc.doc),
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
    _name_regexp = re.compile('`(.+?)`')

    def __init__(self, keywords):
        self._targets = utils.NormalizedDict({
            'introduction': 'introduction',
            'library introduction': 'introduction',
            'importing': 'importing',
            'library importing': 'importing'
        })
        for kw in keywords:
            self._targets[kw.name] = kw.name

    def html(self, doc):
        doc = utils.html_format(doc)
        return self._name_regexp.sub(self._link_keywords, doc)

    def _link_keywords(self, res):
        name = res.group(1)
        if name in self._targets:
            return '<a href="#%s" class="name">%s</a>' % (self._targets[name], name)
        return '<span class="name">%s</span>' % name
