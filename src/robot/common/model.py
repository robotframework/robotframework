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

import random

from robot import utils
from robot.errors import DataError

from .statistics import Stat


class _TestAndSuiteHelper:
    _longname = None

    def __init__(self, name, parent=None):
        self.name = name
        self.doc = ''
        self.parent = parent
        self.setup = None
        self.teardown = None
        self.status = 'NOT_RUN'
        self.message = ''

    def _get_longname(self, sep='.'):
        if self._longname:
            return self._longname
        names = self.parent._get_longname(sep=None) if self.parent else []
        names.append(self.name)
        return sep.join(names) if sep else names

    def _set_longname(self, name):
        self._longname = name

    # Mabot requires longname to be assignable
    longname = property(_get_longname, _set_longname)

    def _set_teardown_fail_msg(self, message):
        if self.message == '':
            self.message = message
        else:
            self.message += '\n\nAlso ' + message[0].lower() + message[1:]

    def __str__(self):
        return self.name

    def __repr__(self):
        return repr(self.name)


class BaseTestSuite(_TestAndSuiteHelper):
    """Base class for TestSuite used in runtime and by rebot."""

    def __init__(self, name, source=None, parent=None):
        _TestAndSuiteHelper.__init__(self, name, parent)
        self.source = utils.abspath(source) if source else None
        self._id = None
        self.metadata = utils.NormalizedDict()
        self.suites = []
        self.tests = []
        self.critical = _Critical()
        self.critical_stats = Stat()
        self.all_stats = Stat()
        if parent:
            parent.suites.append(self)

    def set_name(self, name):
        if name:
            self.name = name
        elif self._is_multi_source_suite():
            self.name = ' & '.join(suite.name for suite in self.suites)

    def _is_multi_source_suite(self):
        return self.parent is None and self.name == ''

    @property
    def id(self):
        if not self._id:
            self._find_root()._set_id()
        return self._id

    def _find_root(self):
        if self.parent:
            return self.parent._find_root()
        return self

    def _set_id(self):
        if not self._id:
            self._id = 's1'
        for index, suite in enumerate(self.suites):
            suite._id = '%s-s%s' % (self._id, index+1)
            suite._set_id()

    def set_critical_tags(self, critical, non_critical):
        if critical is not None or non_critical is not None:
            self.critical.set(critical, non_critical)
            self._set_critical_tags(self.critical)

    def _set_critical_tags(self, critical):
        self.critical = critical
        for suite in self.suites:
            suite._set_critical_tags(critical)
        for test in self.tests:
            test.set_criticality(critical)

    def set_doc(self, doc):
        if doc:
            self.doc = doc

    def set_metadata(self, metalist):
        for name, value in metalist:
            self.metadata[name] = value

    def get_test_count(self):
        count = len(self.tests)
        for suite in self.suites:
            count += suite.get_test_count()
        return count

    def get_full_message(self):
        """Returns suite's message including statistics message"""
        stat_msg = self.get_stat_message()
        if not self.message:
            return stat_msg
        return '%s\n\n%s' % (self.message, stat_msg)

    def get_stat_message(self):
        ctotal, cend, cpass, cfail = self._get_counts(self.critical_stats)
        atotal, aend, apass, afail = self._get_counts(self.all_stats)
        return ('%d critical test%s, %d passed, %d failed\n'
                '%d test%s total, %d passed, %d failed'
                % (ctotal, cend, cpass, cfail, atotal, aend, apass, afail))

    def _get_counts(self, stat):
        ending = utils.plural_or_not(stat.total)
        return stat.total, ending, stat.passed, stat.failed

    def set_status(self):
        """Sets status and statistics based on subsuite and test statuses.

        Can/should be used when statuses have been changed somehow.
        """
        self.status = self._set_stats()

    def _set_stats(self):
        self.critical_stats = Stat()
        self.all_stats = Stat()
        for suite in self.suites:
            suite.set_status()
            self._add_suite_to_stats(suite)
        for test in self.tests:
            self._add_test_to_stats(test)
        return self._get_status()

    def _get_status(self):
        return 'PASS' if not self.critical_stats.failed else 'FAIL'

    def _add_test_to_stats(self, test):
        self.all_stats.add_test(test)
        if test.critical:
            self.critical_stats.add_test(test)

    def _add_suite_to_stats(self, suite):
        self.critical_stats.add_stat(suite.critical_stats)
        self.all_stats.add_stat(suite.all_stats)

    def suite_teardown_failed(self, message=None):
        if message:
            self._set_teardown_fail_msg(message)
        self.critical_stats.fail_all()
        self.all_stats.fail_all()
        self.status = self._get_status()
        sub_message = 'Teardown of the parent suite failed.'
        for suite in self.suites:
            suite.suite_teardown_failed(sub_message)
        for test in self.tests:
            test.suite_teardown_failed(sub_message)

    def set_tags(self, tags):
        if tags:
            for test in self.tests:
                test.tags = utils.normalize_tags(test.tags + tags)
            for suite in self.suites:
                suite.set_tags(tags)

    def filter(self, suites=None, tests=None, includes=None, excludes=None,
               zero_tests_ok=False):
        if suites or tests:
            self.filter_by_names(suites, tests, zero_tests_ok)
        if includes or excludes:
            self.filter_by_tags(includes, excludes, zero_tests_ok)

    def filter_by_names(self, suites=None, tests=None, zero_tests_ok=False):
        suites = [([], name.split('.')) for name in suites or []]
        tests = utils.MultiMatcher(tests, ignore=['_'], match_if_no_patterns=True)
        if not self._filter_by_names(suites, tests) and not zero_tests_ok:
            self._raise_no_tests_filtered_by_names(suites, tests)

    def _filter_by_names(self, suites, tests):
        suites = self._filter_suite_names(suites)
        self.suites = [suite for suite in self.suites
                       if suite._filter_by_names(suites, tests)]
        if not suites:
            self.tests = [test for test in self.tests
                          if tests.match(test.name) or tests.match(test.longname)]
        else:
            self.tests = []
        return bool(self.suites or self.tests)

    def _filter_suite_names(self, suites):
        try:
            return [self._filter_suite_name(p, s) for p, s in suites]
        except StopIteration:
            return []

    def _filter_suite_name(self, parent, suite):
        if utils.matches(self.name, suite[0], ignore=['_']):
            if len(suite) == 1:
                raise StopIteration('Match found')
            return (parent + [suite[0]], suite[1:])
        return ([], parent + suite)

    def _raise_no_tests_filtered_by_names(self, suites, tests):
        tests = utils.seq2str(list(tests), lastsep=' or ')
        suites = utils.seq2str(['.'.join(p + s) for p, s in suites],
                               lastsep=' or ')
        if not suites:
            msg = 'test cases named %s.' % tests
        elif not tests:
            msg = 'test suites named %s.' % suites
        else:
            msg = 'test cases %s in suites %s.' % (tests, suites)
        raise DataError("Suite '%s' contains no %s" % (self.name, msg))

    def filter_by_tags(self, includes=None, excludes=None, zero_tests_ok=False):
        includes = includes or []
        excludes = excludes or []
        if not self._filter_by_tags(includes, excludes) and not zero_tests_ok:
            self._raise_no_tests_filtered_by_tags(includes, excludes)

    def _filter_by_tags(self, incls, excls):
        self.suites = [suite for suite in self.suites
                       if suite._filter_by_tags(incls, excls)]
        self.tests = [test for test in self.tests
                      if test.is_included(incls, excls)]
        return bool(self.suites or self.tests)

    def _raise_no_tests_filtered_by_tags(self, incls, excls):
        incl = utils.seq2str(incls)
        excl = utils.seq2str(excls)
        msg = "Suite '%s' with "  % self.name
        if incl:
            msg += 'includes %s ' % incl
            if excl:
                msg += 'and '
        if excl:
            msg += 'excludes %s ' % excl
        raise DataError(msg + 'contains no test cases.')

    def set_runmode(self, runmode):
        runmode = runmode.upper()
        if runmode == 'EXITONFAILURE':
            self._run_mode_exit_on_failure = True
        elif runmode == 'SKIPTEARDOWNONEXIT':
            self._run_mode_skip_teardowns_on_exit = True
        elif runmode == 'DRYRUN':
            self._run_mode_dry_run = True
        elif runmode == 'RANDOM:TEST':
            random.shuffle(self.tests)
        elif runmode == 'RANDOM:SUITE':
            random.shuffle(self.suites)
        elif runmode == 'RANDOM:ALL':
            random.shuffle(self.suites)
            random.shuffle(self.tests)
        else:
            return
        for suite in self.suites:
            suite.set_runmode(runmode)

    def set_options(self, settings):
        self.set_tags(settings['SetTag'])
        self.filter(settings['SuiteNames'], settings['TestNames'],
                    settings['Include'], settings['Exclude'],
                    settings['RunEmptySuite'])
        self.set_name(settings['Name'])
        self.set_doc(settings['Doc'])
        self.set_metadata(settings['Metadata'])
        self.set_critical_tags(settings['Critical'], settings['NonCritical'])
        self._return_status_rc = not settings['NoStatusRC']
        if 'RunMode' in settings:
            map(self.set_runmode, settings['RunMode'])

    def serialize(self, serializer):
        serializer.start_suite(self)
        if self.setup is not None:
            self.setup.serialize(serializer)
        if self.teardown is not None:
            self.teardown.serialize(serializer)
        for suite in self.suites:
            suite.serialize(serializer)
        for test in self.tests:
            test.serialize(serializer)
        serializer.end_suite(self)

    @property
    def return_code(self):
        rc = min(self.critical_stats.failed, 250)
        return rc if self._return_status_rc else 0


class BaseTestCase(_TestAndSuiteHelper):

    def __init__(self, name, parent):
        _TestAndSuiteHelper.__init__(self, name, parent)
        self.critical = True
        if parent:
            parent.tests.append(self)

    @property
    def id(self):
        if not self.parent:
            return 't1'
        return '%s-t%d' % (self.parent.id, self.parent.tests.index(self)+1)

    @property
    def passed(self):
        return self.status == 'PASS'

    def suite_teardown_failed(self, message):
        self.status = 'FAIL'
        self._set_teardown_fail_msg(message)

    def set_criticality(self, critical):
        self.critical = critical.are_critical(self.tags)

    def is_included(self, incl_tags, excl_tags):
        """Returns True if this test case is included but not excluded.

        If no 'incl_tags' are given all tests are considered to be included.
        """
        included = not incl_tags or self._matches_any_tag_rule(incl_tags)
        excluded = self._matches_any_tag_rule(excl_tags)
        return included and not excluded

    def _matches_any_tag_rule(self, tag_rules):
        """Returns True if any of tag_rules matches self.tags

        Matching equals supporting AND, & and NOT boolean operators and simple
        pattern matching. NOT is 'or' operation meaning if any of the NOTs is
        matching, False is returned.
        """
        return any(self._matches_tag_rule(rule) for rule in tag_rules)

    def _matches_tag_rule(self, tag_rule):
        if 'NOT' not in tag_rule:
            return self._matches_tag(tag_rule)
        nots = tag_rule.split('NOT')
        should_match = nots.pop(0)
        return self._matches_tag(should_match) \
            and not any(self._matches_tag(n) for n in nots)

    def _matches_tag(self, tag):
        """Returns True if given tag matches any tag from self.tags.

        Note that given tag may be ANDed combination of multiple tags (e.g.
        tag1&tag2) and then all of them must match some tag from self.tags.
        """
        for item in tag.split('&'):
            if not any(utils.matches(t, item, ignore=['_']) for t in self.tags):
                return False
        return True

    def __cmp__(self, other):
        if self.status != other.status:
            return -1 if not self.passed else 1
        if self.critical != other.critical:
            return -1 if self.critical else 1
        try:
            return cmp(self.longname, other.longname)
        except AttributeError:
            return cmp(self.name, other.name)

    def serialize(self, serializer):
        serializer.start_test(self)
        if self.setup is not None:
            self.setup.serialize(serializer)
        for kw in self.keywords:
            kw.serialize(serializer)
        if self.teardown is not None:
            self.teardown.serialize(serializer)
        serializer.end_test(self)


class _Critical:

    def __init__(self, tags=None, nons=None):
        self.set(tags, nons)

    def set(self, tags, nons):
        self.tags = self._get_tags(tags)
        self.nons = self._get_tags(nons)

    def _get_tags(self, tags):
        if isinstance(tags, utils.MultiMatcher):
            return tags
        return utils.MultiMatcher(utils.normalize_tags(tags or []), ignore=['_'])

    def is_critical(self, tag):
        return self.tags.match(tag)

    def is_non_critical(self, tag):
        return self.nons.match(tag)

    def are_critical(self, tags):
        for tag in tags:
            if self.is_non_critical(tag):
                return False
        for tag in tags:
            if self.is_critical(tag):
                return True
        return not self.tags

    def __nonzero__(self):
        return bool(self.tags or self.nons)
