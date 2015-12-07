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

from itertools import chain

from robot.model import Tags
from robot.utils import Sortable, setter

from .writer import LibdocWriter
from .output import LibdocOutput


class LibraryDoc(object):

    def __init__(self, name='', doc='', version='', type='library',
                 scope='', named_args=True, doc_format=''):
        self.name = name
        self.doc = doc
        self.version = version
        self.type = type
        self.scope = scope
        self.named_args = named_args
        self.doc_format = doc_format
        self.inits = []
        self.keywords = []

    @setter
    def doc_format(self, format):
        return format or 'ROBOT'

    @setter
    def keywords(self, kws):
        return sorted(kws)

    @property
    def all_tags(self):
        return Tags(chain.from_iterable(kw.tags for kw in self.keywords))

    def save(self, output=None, format='HTML'):
        with LibdocOutput(output, format) as outfile:
            LibdocWriter(format).write(self, outfile)


class KeywordDoc(Sortable):

    def __init__(self, name='', args=(), doc='', tags=()):
        self.name = name
        self.args = args
        self.doc = doc
        self.tags = Tags(tags)

    @property
    def shortdoc(self):
        return self.doc.splitlines()[0] if self.doc else ''

    @property
    def _sort_key(self):
        return self.name.lower()
