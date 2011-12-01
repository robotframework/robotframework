#  Copyright 2008-2011 Nokia Siemens Networks Oyj
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

from .tags import TagPatterns


class Stat(object):

    def __init__(self, name):
        self.name = name
        self.passed = 0
        self.failed = 0

    # TODO: Combine attrs and js_attrs propertys into get_attrs method

    @property
    def attrs(self):
        attrs = {'pass': str(self.passed), 'fail': str(self.failed)}
        attrs.update(self._get_custom_attrs())
        return attrs

    @property
    def js_attrs(self):
        attrs =  {'label': self.name, 'pass': self.passed, 'fail': self.failed}
        attrs.update(self._get_custom_attrs())
        return dict((key, value) for key, value in attrs.items() if value != '')

    def _get_custom_attrs(self):
        return {}

    @property
    def total(self):
        return self.passed + self.failed

    def add_test(self, test):
        if test.status == 'PASS':
            self.passed += 1
        else:
            self.failed += 1

    def add_stat(self, other):
        self.passed += other.passed
        self.failed += other.failed

    def __cmp__(self, other):
        return cmp(self.name, other.name)

    def __nonzero__(self):
        return not self.failed

    def visit(self, visitor):
        visitor.visit_stat(self)


class TotalStat(Stat):
    type = 'total'


class SuiteStat(Stat):
    type = 'suite'

    def __init__(self, suite):
        Stat.__init__(self, suite.longname)
        self.id = suite.id
        self._name = suite.name

    def _get_custom_attrs(self):
        return {'id': self.id, 'name': self._name}


class TagStat(Stat):
    type = 'tag'

    def __init__(self, name, doc='', links=None, critical=False,
                 non_critical=False, combined=''):
        Stat.__init__(self, name)
        self.doc = doc
        self.links = links or []
        self.critical = critical
        self.non_critical = non_critical
        self.combined = combined

    @property
    def info(self):
        if self.critical:
            return 'critical'
        if self.non_critical:
            return 'non-critical'
        if self.combined:
            return 'combined'
        return ''

    def _get_custom_attrs(self):
        return {'doc': self.doc, 'links': self._get_links_as_string(),
                'info': self.info, 'combined': self.combined}

    def _get_links_as_string(self):
        return ':::'.join('%s:%s' % (title, url) for url, title in self.links)

    def __cmp__(self, other):
        return cmp(other.critical, self.critical) \
            or cmp(other.non_critical, self.non_critical) \
            or cmp(bool(other.combined), bool(self.combined)) \
            or cmp(self.name, other.name)


class CombinedTagStat(TagStat):

    def __init__(self, pattern, name=None, doc='', links=None):
        TagStat.__init__(self, name or pattern, doc, links, combined=pattern)
        self._matcher = TagPatterns(pattern)

    def match(self, tags):
        return self._matcher.match(tags)
