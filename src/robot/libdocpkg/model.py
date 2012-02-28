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

from __future__ import with_statement
import re

from robot.utils import setter

from .writer import LibdocWriter
from .output import LibdocOutput


class LibraryDoc(object):

    def __init__(self, name='', doc='', version='', type='library',
                 scope='', named_args=False):
        self._doc_formatter = DocFormatter()
        self.name = name
        self.doc = doc
        self.version = version
        self.type = type
        self.scope = scope
        self.named_args = named_args
        self.inits = []
        self.keywords = []

    @setter
    def doc(self, doc):
        return self._doc_formatter.format(doc)

    @setter
    def keywords(self, kws):
        return sorted(kws)

    def save(self, output=None, format='HTML'):
        with LibdocOutput(output, format) as outfile:
            LibdocWriter(format).write(self, outfile)


class KeywordDoc(object):

    def __init__(self, name='', args=None, doc=''):
        self._doc_formatter = DocFormatter()
        self.name = name
        self.args = args or []
        self.doc = doc

    @setter
    def doc(self, doc):
        return self._doc_formatter.format(doc)

    @property
    def shortdoc(self):
        return self.doc.splitlines()[0] if self.doc else ''

    def __cmp__(self, other):
        return cmp(self.name.lower(), other.name.lower())


class DocFormatter(object):
    _list_or_table_regexp = re.compile('^(\d+\.|[-*|]|\[\d+\]) .')

    def format(self, doc):
        ret = ['']
        for line in doc.splitlines():
            line = line.strip()
            ret.append(self._get_line_joiner(line, ret[-1]))
            ret.append(line)
        return ''.join(ret)

    def _get_line_joiner(self, line, prev):
        if prev == '':
            return ''
        if line == '':
            return '\n\n'
        if self._list_or_table_regexp.search(line) or line == '|':
            return '\n'
        if prev.startswith('| ') and prev.endswith(' |'):
            return '\n'
        return ' '
