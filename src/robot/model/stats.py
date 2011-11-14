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


class Stat(object):

    def __init__(self, name=''):
        self.name = name
        self.passed = 0
        self.failed = 0

    @property
    def _default_attrs(self):
        return {'pass': str(self.passed),
                'fail': str(self.failed)}

    @property
    def total(self):
        return self.passed + self.failed

    def add_stat(self, other):
        self.passed += other.passed
        self.failed += other.failed

    def add_test(self, test):
        if test.status == 'PASS':
            self.passed += 1
        else:
            self.failed += 1

    def fail_all(self):
        self.failed += self.passed
        self.passed = 0

    def add_suite(self, suite):
        for test in suite.tests:
            if self._is_included(test):
                self.add_test(test)
        for suite in suite.suites:
            self.add_stat(self._subsuite_stats(suite))

    def _is_included(self, test):
        return True

    def _subsuite_stats(self, suite):
        return suite.all_stats

    def __cmp__(self, other):
        return cmp(self.name, other.name)

    def __nonzero__(self):
        return self.failed == 0

    def visit(self, visitor):
        visitor.visit_stat(self)


class SuiteStat(Stat):
    type = 'suite'

    def __init__(self, suite):
        Stat.__init__(self, suite.longname)
        self.id = suite.id
        self._attrs = {'name': suite.name, 'idx': suite.id}

    @property
    def attrs(self):
        return dict(self._default_attrs, **self._attrs) # TODO: idx -> id


class TagStat(Stat):
    type = 'tag'

    def __init__(self, name, doc='', links=[], critical=False,
                 non_critical=False, combined=''):
        Stat.__init__(self, name)
        self.doc = doc
        self.links = links
        self.critical = critical
        self.non_critical = non_critical
        self.combined = combined
        self.tests = []

    @property
    def attrs(self):
        return dict(self._default_attrs, info=self._info, links=self._links,
                    doc=self.doc, combined=self.combined)

    @property
    def _info(self):
        if self.critical:
            return 'critical'
        if self.non_critical:
            return 'non-critical'
        if self.combined:
            return 'combined'
        return ''

    @property
    def _links(self):
        return  ':::'.join(':'.join([title, url]) for url, title in self.links)

    def add_test(self, test):
        Stat.add_test(self, test)
        self.tests.append(test)

    def __cmp__(self, other):
        if self.critical != other.critical:
            return cmp(other.critical, self.critical)
        if self.non_critical != other.non_critical:
            return cmp(other.non_critical, self.non_critical)
        if bool(self.combined) != bool(other.combined):
            return cmp(bool(other.combined), bool(self.combined))
        return cmp(self.name, other.name)


class TotalStat(Stat):
    type = 'total'

    def __init__(self, name, suite_stat):
        Stat.__init__(self, name)
        self.passed = suite_stat.passed
        self.failed = suite_stat.failed

    @property
    def attrs(self):
        return self._default_attrs
