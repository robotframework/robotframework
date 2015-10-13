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

from robot.utils import XmlWriter, get_timestamp


class LibdocXmlWriter(object):

    def write(self, libdoc, outfile):
        writer = XmlWriter(outfile)
        writer.start('keywordspec', {'name': libdoc.name, 'type': libdoc.type,
                                     'format': libdoc.doc_format,
                                     'generated': get_timestamp(millissep=None)})
        writer.element('version', libdoc.version)
        writer.element('scope', libdoc.scope)
        writer.element('namedargs', 'yes' if libdoc.named_args else 'no')
        writer.element('doc', libdoc.doc)
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
            writer.element('doc', kw.doc)
            writer.start('tags')
            for tag in kw.tags:
                writer.element('tag', tag)
            writer.end('tags')
            writer.end(type)
