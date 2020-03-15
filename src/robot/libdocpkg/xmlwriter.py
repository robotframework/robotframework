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

    def __init__(self, force_html_doc=False):
        self._force_html_doc = force_html_doc

    def write(self, libdoc, outfile):
        formatter = DocFormatter(libdoc.doc_format, self._force_html_doc)
        writer = XmlWriter(outfile, usage='Libdoc output')
        self._write_start(libdoc, writer, formatter)
        self._write_keywords('init', libdoc.inits, writer, formatter)
        self._write_keywords('kw', libdoc.keywords, writer, formatter)
        self._write_end(writer)

    def _write_start(self, libdoc, writer, formatter):
        lib_attrs = {'name': libdoc.name,
                     'type': libdoc.type,
                     'format': formatter.format,
                     'generated': get_timestamp(millissep=None)}
        writer.start('keywordspec', lib_attrs)
        writer.element('version', libdoc.version)
        writer.element('scope', libdoc.scope)
        writer.element('namedargs', 'yes' if libdoc.named_args else 'no')
        writer.element('doc', formatter(libdoc.doc))

    def _write_keywords(self, kw_type, keywords, writer, formatter):
        for kw in keywords:
            writer.start(kw_type, self._get_start_attrs(kw_type, kw))
            writer.start('arguments')
            for arg in kw.args:
                writer.element('arg', arg)
            writer.end('arguments')
            writer.element('doc', formatter(kw.doc))
            writer.start('tags')
            for tag in kw.tags:
                writer.element('tag', tag)
            writer.end('tags')
            writer.end(kw_type)

    def _get_start_attrs(self, kw_type, kw):
        if kw_type == 'init':
            return {}
        return {'name': kw.name,
                'deprecated': 'true' if kw.deprecated else 'false'}

    def _write_end(self, writer):
        writer.end('keywordspec')
        writer.close()


class DocFormatter(object):

    def __init__(self, doc_format, force_html=False):
        if force_html:
            self._formatter = DocToHtml(doc_format)
            self.format = 'HTML'
        else:
            self._formatter = lambda doc: doc
            self.format = doc_format

    def __call__(self, doc):
        return self._formatter(doc)
