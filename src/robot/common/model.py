#  Copyright 2008-2010 Nokia Siemens Networks Oyj
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

from statistics import Stat
from robot import utils
from robot.errors import DataError


class _TestAndSuiteHelper:

    def __init__(self, name, parent=None):
        self.name = name
        self.doc = ''
        self.parent = parent
        self.setup = None
        self.teardown = None
        self.status = 'NOT_RUN'
        self.message = ''

    def __getattr__(self, name):
        if name == 'htmldoc':
            return utils.html_escape(self.doc, formatting=True)
        if name == 'longname':
            return self.get_long_name()
        raise AttributeError("%s does not have attribute '%s'"
                             % (self.__class__.__name__, name))

    def get_long_name(self, split_level=-1, separator='.'):
        """Returns long name. If separator is None, list of names is returned."""
        names = self.parent and self.parent.get_long_name(separator=None) or []
        names.append(self.name)
        slice_level = self._get_name_slice_index(len(names), split_level)
        if split_level >= 0 and len(names) > slice_level:
            names = names[slice_level:]
        if separator:
            return separator.join(names)
        return names

    def _get_name_slice_index(self, name_parts_count, split_level):
        return split_level

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
        self.source = source is not None and utils.normpath(source) or None
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
        elif not self.parent and self.name == '':  # MultiSourceSuite
            self.name = ' & '.join([suite.name for suite in self.suites])

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
        if doc is not None:
            self.doc = doc

    def set_metadata(self, metalist):
        for metastr in metalist:
            try:
                name, value = metastr.split(':', 1)
            except ValueError:
                name, value = metastr, ''
            self.metadata[name] = value

    def get_metadata(self, html=False):
        names = sorted(self.metadata.keys())
        values = [ self.metadata[n] for n in names ]
        if html:
            values = [ utils.html_escape(v, formatting=True) for v in values ]
        return zip(names, values)

    def get_test_count(self):
        count = len(self.tests)
        for suite in self.suites:
            count += suite.get_test_count()
        return count

    def get_full_message(self, html=False):
        """Returns suite's message including statistics message"""
        stat_msg = self.get_stat_message(html)
        if self.message == '':
            return stat_msg
        if not html:
            return '%s\n\n%s' % (self.message, stat_msg)
        return '%s<br /><br />%s' % (utils.html_escape(self.message), stat_msg)

    def get_stat_message(self, html=False):
        ctotal, cend, cpass, cfail = self._get_counts(self.critical_stats)
        atotal, aend, apass, afail = self._get_counts(self.all_stats)
        msg = ('%%d critical test%%s, %%d passed, %(cfail)s%%d failed%(end)s\n'
               '%%d test%%s total, %%d passed, %(afail)s%%d failed%(end)s')
        if html:
            msg = msg.replace(' ', '&nbsp;').replace('\n', '<br />')
            msg = msg % {'cfail': '<span%s>' % (cfail and ' class="fail"' or ''),
                         'afail': '<span%s>' % (afail and ' class="fail"' or ''),
                         'end': '</span>'}
        else:
            msg = msg % {'cfail': '', 'afail': '', 'end': ''}
        return msg % (ctotal, cend, cpass, cfail, atotal, aend, apass, afail)

    def _get_counts(self, stat):
        total = stat.passed + stat.failed
        ending = utils.plural_or_not(total)
        return total, ending, stat.passed, stat.failed

    def set_status(self):
        """Sets status and statistics based on subsuite and test statuses.

        Can/should be used when statuses have been changed somehow.
        """
        self._set_stats()
        self.status = self.critical_stats.failed == 0 and 'PASS' or 'FAIL'

    def _set_stats(self):
        self.critical_stats = Stat()
        self.all_stats = Stat()
        for suite in self.suites:
            suite.set_status()
            self._add_suite_to_stats(suite)
        for test in self.tests:
            self._add_test_to_stats(test)

    def _add_test_to_stats(self, test):
        self.all_stats.add_test(test)
        if test.critical == 'yes':
            self.critical_stats.add_test(test)

    def _add_suite_to_stats(self, suite):
        self.critical_stats.add_stat(suite.critical_stats)
        self.all_stats.add_stat(suite.all_stats)

    def suite_teardown_failed(self, message=None):
        if message is not None:
            self._set_teardown_fail_msg(message)
        self.critical_stats.fail_all()
        self.all_stats.fail_all()
        self.status = self.critical_stats.failed == 0 and 'PASS' or 'FAIL'
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

    def filter(self, suites=None, tests=None, includes=None, excludes=None):
        self.filter_by_names(suites, tests)
        self.filter_by_tags(includes, excludes)

    def filter_by_names(self, suites=None, tests=None):
        suites = [ ([], name.split('.')) for name in suites or [] ]
        tests = tests or []
        if (suites or tests) and not self._filter_by_names(suites, tests):
            self._raise_no_tests_filtered_by_names(suites, tests)

    def _filter_by_names(self, suites, tests):
        suites = self._filter_suite_names(suites)
        self.suites = [ suite for suite in self.suites
                        if suite._filter_by_names(suites, tests) ]
        if not suites:
            self.tests = [ test for test in self.tests if tests == [] or
                           utils.matches_any(test.name, tests, ignore=['_']) ]
        else:
            self.tests = []
        return self.suites or self.tests

    def _filter_suite_names(self, suites):
        try:
            return [ self._filter_suite_name(p, s) for p, s in suites ]
        except StopIteration:
            return []

    def _filter_suite_name(self, parent, suite):
        if utils.matches(self.name, suite[0], ignore=['_']):
            if len(suite) == 1:
                raise StopIteration('Match found')
            return (parent + [suite[0]], suite[1:])
        return ([], parent + suite)

    def _raise_no_tests_filtered_by_names(self, suites, tests):
        tests = utils.seq2str(tests, lastsep=' or ')
        suites = utils.seq2str([ '.'.join(p + s) for p, s in suites ],
                               lastsep=' or ')
        if not suites:
            msg = 'test cases named %s.' % tests
        elif not tests:
            msg = 'test suites named %s.' % suites
        else:
            msg = 'test cases %s in suites %s.' % (tests, suites)
        raise DataError("Suite '%s' contains no %s" % (self.name, msg))

    def filter_by_tags(self, includes=None, excludes=None):
        if not (includes or excludes):
            return
        if not includes: includes = []
        if not excludes: excludes = []
        if not self._filter_by_tags(includes, excludes):
            self._raise_no_tests_filtered_by_tags(includes, excludes)

    def _filter_by_tags(self, incls, excls):
        self.suites = [ suite for suite in self.suites
                        if suite._filter_by_tags(incls, excls) ]
        self.tests = [ test for test in self.tests
                       if test.is_included(incls, excls) ]
        return len(self.suites) + len(self.tests) > 0

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
                    settings['Include'], settings['Exclude'])
        self.set_name(settings['Name'])
        self.set_doc(settings['Doc'])
        self.set_metadata(settings['Metadata'])
        self.set_critical_tags(settings['Critical'], settings['NonCritical'])
        try:
            for runmode in settings['RunMode']:
                self.set_runmode(runmode)
        except (KeyError, AttributeError) : # Only applicable when running tcs
            pass
        if not self.suites:
            settings['SplitOutputs'] = -2
        try:
            self.remove_keywords(settings['RemoveKeywords'])
        except (KeyError, AttributeError):  # Only applicable with Rebot
            pass

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


class BaseTestCase(_TestAndSuiteHelper):

    def __init__(self, name, parent):
        _TestAndSuiteHelper.__init__(self, name, parent)
        self.critical = 'yes'
        if parent:
            parent.tests.append(self)

    def suite_teardown_failed(self, message):
        self.status = 'FAIL'
        self._set_teardown_fail_msg(message)

    def set_criticality(self, critical):
        self.critical = critical.are_critical(self.tags) and 'yes' or 'no'

    def is_included(self, incl_tags, excl_tags):
        """Returns True if this test case is included but not excluded.

        If no 'incl_tags' are given all tests are considered to be included.
        """
        included = not incl_tags or self._matches_any_of_the(incl_tags)
        excluded = self._matches_any_of_the(excl_tags)
        return included and not excluded

    def _matches_any_of_the(self, tag_rules):
        """Returns True if any of tag_rules matches self.tags

        Matching equals supporting AND, & and NOT boolean operators and simple
        pattern matching. NOT is 'or' operation meaning if any of the NOTs is
        matching, False is returned.
        """
        for rule in tag_rules:
            if self._matches_tag_rule(rule):
                return True
        return False

    def _matches_tag_rule(self, tag_rule):
        that_should_be, that_should_not_be = self._split_boolean_operators(tag_rule)
        if self._contains_any_tag(that_should_not_be):
            return False
        if self._contains_tag(that_should_be):
            return True
        return False

    def _split_boolean_operators(self, tag_rule):
        if not tag_rule:
            return self._empty_split()
        if 'NOT' in tag_rule:
            return self._split_nots(tag_rule)
        return tag_rule, []

    def _empty_split(self):
        return '', []

    def _split_nots(self, tag_rule):
        parts = tag_rule.split('NOT')
        if '' not in parts:
            return parts[0], parts[1:]
        return self._empty_split()

    def _contains_any_tag(self, tags):
        """Returns True if any of the given tags matches a tag from self.tags.

        Note that one tag may be ANDed combination of multiple tags (e.g.
        tag1&tag2) and then all of them must match some tag from selg.tags.
        """
        for tag in tags:
            if self._contains_tag(tag):
                return True
        return False

    def _contains_tag(self, tag):
        """Returns True if given tag matches any tag from self.tags.

        Note that given tag may be ANDed combination of multiple tags (e.g.
        tag1&tag2) and then all of them must match some tag from self.tags.
        """
        for item in tag.split('&'):
            if not any(utils.matches(tag, item) for tag in self.tags):
                return False
        return True

    def __cmp__(self, other):
        if self.status != other.status:
            return self.status == 'FAIL' and -1 or 1
        if self.critical != other.critical:
            return self.critical == 'yes' and -1 or 1
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

    def _get_name_slice_index(self, name_parts_count, split_level):
        if name_parts_count == split_level + 1:
            return split_level + 1
        return split_level


class _Critical:

    def __init__(self, tags=None, nons=None):
        self.set(tags, nons)

    def set(self, tags, nons):
        self.tags = utils.normalize_tags(tags or [])
        self.nons = utils.normalize_tags(nons or [])

    def is_critical(self, tag):
        return utils.matches_any(tag, self.tags)

    def is_non_critical(self, tag):
        return utils.matches_any(tag, self.nons)

    def are_critical(self, tags):
        for tag in tags:
            if self.is_non_critical(tag):
                return False
        for tag in tags:
            if self.is_critical(tag):
                return True
        return len(self.tags) == 0
