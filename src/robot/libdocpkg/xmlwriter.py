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

from robot.utils import XmlWriter, get_timestamp

from .htmlwriter import DocToHtml


class LibdocXmlWriter(object):

    def __init__(self, html_doc_format=False):
        self._html_doc_format = html_doc_format
        self._formatter = None
        self._writer = None

    def write(self, libdoc, outfile):
        self._formatter = DocToHtml(libdoc.doc_format) if self._html_doc_format else self.raw_format
        self._writer = XmlWriter(outfile)
        self._write_start(libdoc)
        self._write_keywords('init', libdoc.inits)
        self._write_keywords('kw', libdoc.keywords)
        self._write_end()

    def _write_start(self, libdoc):
        self._writer.start('keywordspec', {'name': libdoc.name,
                                           'type': libdoc.type,
                                           'format': 'HTML' if self._html_doc_format else libdoc.doc_format,
                                           'generated': get_timestamp(millissep=None)})
        self._writer.element('version', libdoc.version)
        self._writer.element('scope', libdoc.scope)
        self._writer.element('namedargs', 'yes' if libdoc.named_args else 'no')
        self._writer.element('doc', self._formatter(libdoc.doc))

    def _write_keywords(self, type, keywords):
        for kw in keywords:
            self._writer.start(type, {'name': kw.name} if type == 'kw' else {})
            self._writer.start('arguments')
            for arg in kw.args:
                self._writer.element('arg', arg)
            self._writer.end('arguments')
            self._writer.element('doc', self._formatter(kw.doc))
            self._writer.start('tags')
            for tag in kw.tags:
                self._writer.element('tag', tag)
            self._writer.end('tags')
            self._writer.end(type)

    def _write_end(self):
        self._writer.end('keywordspec')
        self._writer.close()

    def raw_format(self, doc):
        return doc
