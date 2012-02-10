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

from robot.reporting.htmlfilewriter import HtmlFileWriter, ModelWriter
from robot.reporting.jsonwriter import JsonWriter
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
        libdoc = LibdocJsonConverter().convert(self._libdoc)
        JsonWriter(self._output).write_json('libdoc = ', libdoc)


class LibdocJsonConverter(object):

    def convert(self, libdoc):
        return {
            'name': libdoc.name,
            'doc': libdoc.doc,
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
            'args': kw.args,
            'doc': kw.doc,
            'shortdoc': kw.shortdoc
        }
