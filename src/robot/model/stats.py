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

from robot.utils import (Sortable, elapsed_time_to_string, html_escape,
                         is_string, normalize, py2to3, unicode)

from .tags import TagPattern


@py2to3
class Stat(Sortable):
    """Generic statistic object used for storing all the statistic values."""

    def __init__(self, name):
        #: Human readable identifier of the object these statistics
        #: belong to. Either `All Tests` or `Critical Tests` for
        #: :class:`~robot.model.totalstatistics.TotalStatistics`,
        #: long name of the suite for
        #: :class:`~robot.model.suitestatistics.SuiteStatistics`
        #: or name of the tag for
        #: :class:`~robot.model.tagstatistics.TagStatistics`
        self.name = name
        #: Number of passed tests.
        self.passed = 0
        #: Number of failed tests.
        self.failed = 0
        #: Number of milliseconds it took to execute.
        self.elapsed = 0
        self._norm_name = normalize(name, ignore='_')

    def get_attributes(self, include_label=False, include_elapsed=False,
                       exclude_empty=True, values_as_strings=False,
                       html_escape=False):
        attrs = {'pass': self.passed, 'fail': self.failed}
        attrs.update(self._get_custom_attrs())
        if include_label:
            attrs['label'] = self.name
        if include_elapsed:
            attrs['elapsed'] = elapsed_time_to_string(self.elapsed,
                                                      include_millis=False)
        if exclude_empty:
            attrs = dict((k, v) for k, v in attrs.items() if v not in ('', None))
        if values_as_strings:
            attrs = dict((k, unicode(v if v is not None else ''))
                         for k, v in attrs.items())
        if html_escape:
            attrs = dict((k, self._html_escape(v)) for k, v in attrs.items())
        return attrs

    def _get_custom_attrs(self):
        return {}

    def _html_escape(self, item):
        return html_escape(item) if is_string(item) else item

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

    @property
    def _sort_key(self):
        return self._norm_name

    def __nonzero__(self):
        return not self.failed

    def visit(self, visitor):
        visitor.visit_stat(self)


class TotalStat(Stat):
    """Stores statistic values for a test run."""
    type = 'total'


class SuiteStat(Stat):
    """Stores statistics values for a single suite."""
    type = 'suite'

    def __init__(self, suite):
        Stat.__init__(self, suite.longname)
        #: Identifier of the suite, e.g. `s1-s2`.
        self.id = suite.id
        #: Number of milliseconds it took to execute this suite,
        #: including sub-suites.
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
    """Stores statistic values for a single tag."""
    type = 'tag'

    def __init__(self, name, doc='', links=None, critical=False,
                 non_critical=False, combined=None):
        Stat.__init__(self, name)
        #: Documentation of tag as a string.
        self.doc = doc
        #: List of tuples in which the first value is the link URL and
        #: the second is the link title. An empty list by default.
        self.links = links or []
        #: ``True`` if tag is considered critical, ``False`` otherwise.
        self.critical = critical
        #: ``True`` if tag is considered non-critical, ``False`` otherwise.
        self.non_critical = non_critical
        #: Pattern as a string if the tag is combined, ``None`` otherwise.
        self.combined = combined

    @property
    def info(self):
        """Returns additional information of the tag statistics
           are about. Either `critical`, `non-critical`, `combined` or an
           empty string.
        """
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

    @property
    def _sort_key(self):
        return (not self.critical,
                not self.non_critical,
                not self.combined,
                self._norm_name)


class CombinedTagStat(TagStat):

    def __init__(self, pattern, name=None, doc='', links=None):
        TagStat.__init__(self, name or pattern, doc, links, combined=pattern)
        self.pattern = TagPattern(pattern)

    def match(self, tags):
        return self.pattern.match(tags)


class CriticalTagStat(TagStat):

    def __init__(self, tag_pattern, name=None, critical=True, doc='',
                 links=None):
        TagStat.__init__(self, name or unicode(tag_pattern), doc, links,
                         critical=critical, non_critical=not critical)
        self.pattern = tag_pattern

    def match(self, tags):
        return self.pattern.match(tags)
