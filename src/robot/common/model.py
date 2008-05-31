#  Copyright 2008 Nokia Siemens Networks Oyj
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
    
    def __getattr__(self, name):
        if name == 'htmldoc':
            return utils.html_escape(self.doc, formatting=True)
        raise AttributeError("%s does not have attribute '%s'" 
                             % (self.__class__.__name__, name))

    def set_names(self, name=None, parent=None):
        if name is not None:
            self.name = name
        if parent is None:
            self.mediumname = self.longname = self.name
        else:
            self.longname = parent.longname + '.' + self.name
            mediumname_parts = parent.mediumname.split('.')
            mediumname_parts[-1] = mediumname_parts[-1][0].lower()
            mediumname_parts.append(self.name)
            self.mediumname = '.'.join(mediumname_parts)
            
    def _set_teardown_fail_msg(self, message):
        if self.message == '':
            self.message = message
        else:
            self.message += '\n\nAlso ' + message[0].lower() + message[1:]
            
    def __str__(self):
        return self.name
    
    def __repr__(self):
        return "'%s'" % self.name


class BaseTestSuite(_TestAndSuiteHelper):
    """Base class for TestSuite used in runtime and by rebot."""

    def __init__(self, name='', source=None):
        self.name = name
        self.source = source is not None and utils.normpath(source) or None
        self.metadata = {}
        self.suites = []
        self.tests = []
        self.critical = _Critical()
        self.filtered = _FilteredBy()
        self.critical_stats = Stat()
        self.all_stats = Stat()
        self.setup = self.teardown = None
        
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
    
    def set_names(self, name=None, parent=None):
        _TestAndSuiteHelper.set_names(self, name, parent)
        for suite in self.suites:
            suite.set_names(parent=self)
        for test in self.tests:
            test.set_names(parent=self)
        return self.name
    
    def set_doc(self, doc):
        if doc is not None:
            self.doc = doc
    
    def set_metadata(self, metalist):
        for metastr in metalist:
            try:
                name, value = metastr.split(':', 1)
            except ValueError:
                name, value = metastr, ''
            self.metadata[utils.printable_name(name.replace('_',' '))] = value
            
    def get_metadata(self, html=False):
        names = self.metadata.keys()
        names.sort()
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
                test.tags = utils.normalize_list(test.tags + tags)
            for suite in self.suites:
                suite.set_tags(tags)
    
    def filter(self, suites=None, tests=None, includes=None, excludes=None):
        self.filter_by_names(suites, tests)
        self.filter_by_tags(includes, excludes)

    def filter_by_names(self, suites=None, tests=None):
        suites = utils.to_list(suites)
        tests = utils.to_list(tests)
        if suites == [] and tests == []:
            return
        if not self._filter_by_names(suites, tests):
            self._raise_no_tests_filtered_by_names(suites, tests)
        
    def _filter_by_names(self, suites, tests):
        self.filtered.add_suites(suites)
        self.filtered.add_tests(tests)
        suites = self._filter_suite_names(suites)
        self.suites = [ suite for suite in self.suites 
                        if suite._filter_by_names(suites, tests) ]
        if suites == []:
            self.tests = [ test for test in self.tests if tests == [] or
                           utils.matches_any(test.name, tests, ignore=['_']) ]
        else:
            self.tests = []
        return len(self.suites) + len(self.tests) > 0
    
    def _filter_suite_names(self, names):
        names = [ self._filter_suite_name(name) for name in names ]
        if names.count(True) > 0:
            return []
        return names
    
    def _filter_suite_name(self, name):
        tokens = name.split('.')
        if utils.matches(self.name, tokens[0], ignore=['_']):
            if len(tokens) == 1:
                return True   # match
            return '.'.join(tokens[1:])
        return name
    
    def _raise_no_tests_filtered_by_names(self, suites, tests):
        err = "Suite '%s' contains no " % self.name
        if suites == []:
            err += 'test cases named %s.' % utils.seq2str(tests, lastsep=' or ')
        elif tests == []:
            err += 'test suites named %s.' % utils.seq2str(suites, lastsep=' or ')
        else:
            err += 'test cases %s in suites %s.' \
                    % (utils.seq2str(tests, lastsep=' or '),
                       utils.seq2str(suites, lastsep=' or '))
        raise DataError(err)

    def filter_by_tags(self, includes=None, excludes=None):
        if includes is None: includes = []
        if excludes is None: excludes = []
        if includes == [] and excludes == []:
            return
        if not self._filter_by_tags(includes, excludes):
            self._raise_no_tests_filtered_by_tags(includes, excludes)
        
    def _filter_by_tags(self, incls, excls):
        self.filtered.add_incls(incls)
        self.filtered.add_excls(excls)
        self.suites = [ suite for suite in self.suites 
                        if suite._filter_by_tags(incls, excls) ]
        self.tests = [ test for test in self.tests 
                       if test.is_included(incls, excls) ]
        return len(self.suites) + len(self.tests) > 0

    def _raise_no_tests_filtered_by_tags(self, incls, excls):
        incl = utils.seq2str(incls)
        excl = utils.seq2str(excls)
        msg = "Suite '%s' with "  % self.name
        if incl != '':
            msg += 'includes %s ' % incl
            if excl != '':
                msg += 'and '
        if excl != '':
            msg += 'excludes %s ' % excl
        raise DataError(msg + 'contains no test cases.')
    
    def set_runmode(self, runmode):
        runmode = runmode.upper()
        if runmode == 'EXITONFAILURE':
            self._exit_on_failure = True
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
        self.set_names(settings['Name'])
        settings['Name'] = self.name
        self.set_doc(settings['Doc'])
        self.set_metadata(settings['Metadata'])
        self.set_critical_tags(settings['Critical'], settings['NonCritical'])
        try:
            self.set_runmode(settings['RunMode'])
        except (KeyError, AttributeError) :
            pass
        if len(self.suites) == 0:
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

    def __init__(self, name=''):
        self.name = name
        self.state = 'NOTRUN'
        self.critical = 'yes'
        self.setup = self.teardown = None

    def suite_teardown_failed(self, message):
        self.status = 'FAIL'
        self._set_teardown_fail_msg(message)

    def set_criticality(self, critical):
        self.critical = critical.are_critical(self.tags) and 'yes' or 'no'

    def is_included(self, incl_tags, excl_tags):
        """Returns True if this test case is included but not excluded.
        
        If no 'incl_tags' are given all tests are considered to be included.
        """
        included = len(incl_tags) == 0 or self._contains_any_tag(incl_tags)
        excluded = self._contains_any_tag(excl_tags)
        return included and not excluded

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
        tag1&tag2) and then all of them must match some tag from selg.tags.
        """
        for item in tag.split('&'):
            if not utils.any_matches(self.tags, item):
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

        
class _Critical:
    
    def __init__(self, tags=None, nons=None):
        self.set(tags, nons)

    def set(self, tags, nons):
        self.tags = utils.normalize_list(utils.to_list(tags))
        self.nons = utils.normalize_list(utils.to_list(nons))
        
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


class _FilteredBy:
    
    def __init__(self):
        self.tests = []
        self.suites = []
        self.incls = []
        self.excls = []
        
    def add_tests(self, tests):
        self.tests = utils.normalize_list(self.tests + tests, ignore=['_'])
        
    def add_suites(self, suites):
        self.suites = utils.normalize_list(self.suites + suites, ignore=['_'])

    def add_incls(self, incls):
        self.incls = utils.normalize_list(self.incls + incls)

    def add_excls(self, excls):
        self.excls = utils.normalize_list(self.excls + excls)

    