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

from robot.errors import DataError
from robot.utils import XmlWriter, get_timestamp
from .htmlwriter import DocToHtml


class LibdocXmlWriter(object):

    def __init__(self, output_doc_format=None):
        self.output_doc_format = output_doc_format
        self.formatter = None

    def write(self, libdoc, outfile):
        if not self.output_doc_format:
            doc_format = libdoc.doc_format
            doc = libdoc.doc
        else:
            if self.output_doc_format == 'HTML':
                self.formatter = DocToHtml(libdoc.doc_format)
                doc_format = self.output_doc_format
                doc = self.formatter(libdoc.doc)
            else:
                raise DataError("Output doc format must be either 'HTML' or not set, got '%s'." % self.output_doc_format)

        writer = XmlWriter(outfile)
        writer.start('keywordspec', {'name': libdoc.name, 'type': libdoc.type,
                                     'format': doc_format,
                                     'generated': get_timestamp(millissep=None)})
        writer.element('version', libdoc.version)
        writer.element('scope', libdoc.scope)
        writer.element('namedargs', 'yes' if libdoc.named_args else 'no')
        writer.element('doc', doc)
        self._write_keywords('init', libdoc.inits, writer)
        self._write_keywords('kw', libdoc.keywords, writer)
        writer.end('keywordspec')
        writer.close()

    def _write_keywords(self, type, keywords, writer):
        for kw in keywords:
            writer.start(type, {'name': kw.name} if type == 'kw' else {})
            writer.start('arguments')
            for arg in kw.args:
                writer.element('arg', arg)
            writer.end('arguments')
            writer.element('doc', self.formatter(kw.doc) if self.output_doc_format else kw.doc)
            writer.start('tags')
            for tag in kw.tags:
                writer.element('tag', tag)
            writer.end('tags')
            writer.end(type)
