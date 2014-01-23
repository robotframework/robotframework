#  Copyright 2008-2014 Nokia Solutions and Networks
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

from robot.utils import setter

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
    def scope(self, scope):
        return {'TESTCASE': 'test case',
                'TESTSUITE': 'test suite',
                'GLOBAL': 'global'}.get(scope, scope)

    @setter
    def doc_format(self, format):
        return format or 'ROBOT'

    @setter
    def keywords(self, kws):
        return sorted(kws)

    def save(self, output=None, format='HTML'):
        with LibdocOutput(output, format) as outfile:
            LibdocWriter(format).write(self, outfile)


class KeywordDoc(object):

    def __init__(self, name='', args=None, doc=''):
        self.name = name
        self.args = args or []
        self.doc = doc

    @property
    def shortdoc(self):
        return self.doc.splitlines()[0] if self.doc else ''

    def __cmp__(self, other):
        return cmp(self.name.lower(), other.name.lower())
