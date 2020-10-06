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
from robot.utils import getshortdoc, Sortable, setter

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
        for init in inits:
            init.parent = self
        return sorted(inits)

    @setter
    def keywords(self, kws):
        for keyword in kws:
            keyword.parent = self
        return sorted(kws)

    @property
    def all_tags(self):
        return Tags(chain.from_iterable(kw.tags for kw in self.keywords))

    def save(self, output=None, format='HTML'):
        with LibdocOutput(output, format) as outfile:
            LibdocWriter(format).write(self, outfile)


class KeywordDoc(Sortable):

    def __init__(self, name='', args=(), doc='', tags=(), source=None,
                 lineno=-1):
        self.name = name
        self.args = args
        self.doc = doc
        self.tags = Tags(tags)
        self.source = source
        self.lineno = lineno
        self.parent = None

    @property
    def shortdoc(self):
        if self.parent.doc_format == 'HTML':
            return self._get_shortdoc_from_html(self.doc)
        return getshortdoc(self.doc)

    @staticmethod
    def _get_shortdoc_from_html(doc):
        match = re.search('<p>(.*?)</p>', doc)
        if match:
            doc = match.group(1)
        doc = re.sub('(<b>)(.*?)(</b>)',
                     lambda m: '*' + m.group(2) + '*', doc)
        doc = re.sub('(<i>)(.*?)(</i>)',
                     lambda m: '_' + m.group(2) + '_', doc)
        doc = re.sub('(<code>)(.*?)(</code>)',
                     lambda m: '``' + m.group(2) + '``', doc)
        return doc

    @property
    def deprecated(self):
        return self.doc.startswith('*DEPRECATED') and '*' in self.doc[1:]

    @property
    def _sort_key(self):
        return self.name.lower()
