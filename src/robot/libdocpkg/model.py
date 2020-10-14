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

from itertools import chain
import re

from robot.model import Tags
from robot.utils import getshortdoc, get_timestamp, Sortable, setter

from .htmlutils import HtmlToText, DocFormatter
from .writer import LibdocWriter
from .output import LibdocOutput


class LibraryDoc(object):

    def __init__(self, name='', doc='', version='', type='LIBRARY',
                 scope='TEST', named_args=True, doc_format='ROBOT',
                 source=None, lineno=-1):
        self.name = name
        self._doc = doc
        self.version = version
        self.type = type
        self.scope = scope
        self.named_args = named_args
        self.doc_format = doc_format
        self.source = source
        self.lineno = lineno
        self.inits = []
        self.keywords = []

    @property
    def doc(self):
        if self.doc_format == 'ROBOT' and '%TOC%' in self._doc:
            return self._add_toc(self._doc)
        return self._doc

    def _add_toc(self, doc):
        toc = self._create_toc(doc)
        return '\n'.join(line if line.strip() != '%TOC%' else toc
                         for line in doc.splitlines())

    def _create_toc(self, doc):
        entries = re.findall(r'^\s*=\s+(.+?)\s+=\s*$', doc, flags=re.MULTILINE)
        if self.inits:
            entries.append('Importing')
        entries.append('Keywords')
        return '\n'.join('- `%s`' % entry for entry in entries)

    @setter
    def doc_format(self, format):
        return format or 'ROBOT'

    @setter
    def inits(self, inits):
        return self._add_parent(inits)

    @setter
    def keywords(self, kws):
        return self._add_parent(kws)

    def _add_parent(self, kws):
        for keyword in kws:
            keyword.parent = self
        return sorted(kws)

    @property
    def all_tags(self):
        return Tags(chain.from_iterable(kw.tags for kw in self.keywords))

    def save(self, output=None, format='HTML'):
        with LibdocOutput(output, format) as outfile:
            LibdocWriter(format).write(self, outfile)

    def convert_doc_to_html(self):
        formatter = DocFormatter(self.keywords, self.doc, self.doc_format)
        self._doc = formatter.html(self.doc, intro=True)
        self.doc_format = 'HTML'
        for init in self.inits:
            init.doc = formatter.html(init.doc)
        for keyword in self.keywords:
            keyword.doc = formatter.html(keyword.doc)

    def to_dictionary(self):
        return {
            'name': self.name,
            'doc': self.doc,
            'version': self.version,
            'type': self.type,
            'scope': self.scope,
            'named_args': self.named_args,
            'doc_format': self.doc_format,
            'source': self.source,
            'lineno': self.lineno,
            'inits': [init.to_dictionary() for init in self.inits],
            'keywords': [kw.to_dictionary() for kw in self.keywords],
            'generated': get_timestamp(daysep='-', millissep=None),
            'all_tags': tuple(self.all_tags),
            'contains_tags': bool(self.all_tags)
        }


class KeywordDoc(Sortable):

    def __init__(self, name='', args=(), doc='', tags=(), source=None,
                 lineno=-1, parent=None):
        self.name = name
        self.args = args
        self.doc = doc
        self.tags = Tags(tags)
        self.source = source
        self.lineno = lineno
        self.parent = parent

    @property
    def shortdoc(self):
        doc = self.doc
        if self.parent and self.parent.doc_format == 'HTML':
            doc = HtmlToText().get_shortdoc_from_html(doc)
        return ' '.join(getshortdoc(doc).splitlines())

    @property
    def deprecated(self):
        return self.doc.startswith('*DEPRECATED') and '*' in self.doc[1:]

    @property
    def _sort_key(self):
        return self.name.lower()

    def to_dictionary(self):
        return {
            'name': self.name,
            'args': self.args,
            'doc': self.doc,
            'shortdoc': self.shortdoc,
            'tags': tuple(self.tags),
            'source': self.source,
            'lineno': self.lineno,
            'matched': True
        }
