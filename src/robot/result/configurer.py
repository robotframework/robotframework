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

from robot import utils
from robot.errors import DataError


class SuiteConfigurer(object):

    def __init__(self, name=None, doc=None, metadata=None, set_tags=None,
                 include_tags=None, exclude_tags=None, include_suites=None,
                 include_tests=None, process_empty_suite=False,
                 remove_keywords=None, log_level=None, critical=None,
                 noncritical=None, starttime=None, endtime=None):
        self.name = name
        self.doc = doc
        self.metadata = metadata
        self.set_tags = set_tags or []
        self.critical_tags = critical
        self.non_critical_tags = noncritical
        self.include_tags = include_tags
        self.exclude_tags = exclude_tags
        self.include_suites = include_suites
        self.include_tests = include_tests
        self.process_empty_suite = process_empty_suite
        self.remove_keywords = self._get_remove_keywords(remove_keywords)
        self.log_level = log_level
        self.starttime = self._get_time(starttime)
        self.endtime = self._get_time(endtime)

    def _get_remove_keywords(self, value):
        if value is None:
            return []
        if isinstance(value, basestring):
            return [value]
        return value

    @property
    def add_tags(self):
        return [t for t in self.set_tags if not t.startswith('-')]

    @property
    def remove_tags(self):
        return [t[1:] for t in self.set_tags if t.startswith('-')]

    def configure(self, suite):
        self._set_suite_attributes(suite)
        suite.filter(self.include_suites, self.include_tests,
                     self.include_tags, self.exclude_tags)
        if not (suite.test_count or self.process_empty_suite):
            self._raise_no_tests_error(suite.name)
        suite.set_tags(self.add_tags, self.remove_tags)
        for how in self.remove_keywords:
            suite.remove_keywords(how)
        suite.filter_messages(self.log_level)
        suite.set_criticality(self.critical_tags, self.non_critical_tags)

    def _set_suite_attributes(self, suite):
        if self.name:
            suite.name = self.name
        if self.doc:
            suite.doc = self.doc
        if self.metadata:
            suite.metadata.update(self.metadata)
        if self.starttime:
            suite.starttime = self.starttime
        if self.endtime:
            suite.endtime = self.endtime

    def _get_time(self, timestamp):
        if not timestamp:
            return None
        try:
            secs = utils.timestamp_to_secs(timestamp, seps=' :.-_')
        except ValueError:
            return None
        return utils.secs_to_timestamp(secs, millis=True)

    def _raise_no_tests_error(self, suite):
        selectors = '%s %s' % (self._get_test_selector_msgs(),
                               self._get_suite_selector_msg())
        msg = "Suite '%s' contains no tests %s" % (suite, selectors.strip())
        raise DataError(msg.strip() + '.')

    def _get_test_selector_msgs(self):
        parts = []
        for explanation, selector in [('with tags', self.include_tags),
                                      ('without tags', self.exclude_tags),
                                      ('named', self.include_tests)]:
            if selector:
               parts.append(self._format_selector_msg(explanation, selector))
        return utils.seq2str(parts, quote='')

    def _format_selector_msg(self, explanation, selector):
        if isinstance(selector, basestring):
            selector = [selector]
        if len(selector) == 1 and explanation[-1] == 's':
            explanation = explanation[:-1]
        return '%s %s' % (explanation, utils.seq2str(selector, lastsep=' or '))

    def _get_suite_selector_msg(self):
        if not self.include_suites:
            return ''
        return self._format_selector_msg('in suites', self.include_suites)
