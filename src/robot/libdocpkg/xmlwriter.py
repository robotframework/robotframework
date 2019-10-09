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

    def write(self, libdoc, outfile):
        formatter = DocToHtml(libdoc.doc_format) \
            if self._html_doc_format \
            else lambda doc: doc
        writer = XmlWriter(outfile)
        self._write_start(writer, libdoc, formatter)
        self._write_keywords(writer, 'init', libdoc.inits, formatter)
        self._write_keywords(writer, 'kw', libdoc.keywords, formatter)
        self._write_end(writer)

    def _write_start(self, writer, libdoc, formatter):
        doc_format = 'HTML' if self._html_doc_format else libdoc.doc_format
        lib_attrs = {'name': libdoc.name,
                     'type': libdoc.type,
                     'format': doc_format,
                     'generated': get_timestamp(millissep=None)}
        writer.start('keywordspec', lib_attrs)
        writer.element('version', libdoc.version)
        writer.element('scope', libdoc.scope)
        writer.element('namedargs', 'yes' if libdoc.named_args else 'no')
        writer.element('doc', formatter(libdoc.doc))

    def _write_keywords(self, writer, type, keywords, formatter):
        for kw in keywords:
            writer.start(type, {'name': kw.name} if type == 'kw' else {})
            writer.start('arguments')
            for arg in kw.args:
                writer.element('arg', arg)
            writer.end('arguments')
            writer.element('doc', formatter(kw.doc))
            writer.start('tags')
            for tag in kw.tags:
                writer.element('tag', tag)
            writer.end('tags')
            writer.end(type)

    def _write_end(self, writer):
        writer.end('keywordspec')
        writer.close()
