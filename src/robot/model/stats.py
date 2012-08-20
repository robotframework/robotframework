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

from robot.utils import elapsed_time_to_string, html_escape

from .tags import TagPatterns


class Stat(object):

    def __init__(self, name):
        self.name = name
        self.passed = 0
        self.failed = 0
        self.elapsed = 0

    def get_attributes(self, include_label=False, include_elapsed=False,
                       exclude_empty=False, values_as_strings=False,
                       html_escape=False):
        attrs =  {'pass': self.passed, 'fail': self.failed}
        attrs.update(self._get_custom_attrs())
        if include_label:
            attrs['label'] = self.name
        if include_elapsed:
            attrs['elapsed'] = elapsed_time_to_string(self.elapsed,
                                                      include_millis=False)
        if exclude_empty:
            attrs = dict((k, v) for k, v in attrs.items() if v != '')
        if values_as_strings:
            attrs = dict((k, unicode(v)) for k, v in attrs.items())
        if html_escape:
            attrs = dict((k, self._html_escape(v)) for k, v in attrs.items())
        return attrs

    def _get_custom_attrs(self):
        return {}

    def _html_escape(self, item):
        return html_escape(item) if isinstance(item, basestring) else item

    @property
    def total(self):
        return self.passed + self.failed

    def add_test(self, test):
        self._update_stats(test)
        self._update_elapsed(test)

    def _update_stats(self, test):
        if test.passed:
            self.passed += 1
        else:
            self.failed += 1

    def _update_elapsed(self, test):
        self.elapsed += test.elapsedtime

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
        self.elapsed = suite.elapsedtime
        self._name = suite.name

    def _get_custom_attrs(self):
        return {'id': self.id, 'name': self._name}

    def _update_elapsed(self, test):
        pass

    def add_stat(self, other):
        self.passed += other.passed
        self.failed += other.failed


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
