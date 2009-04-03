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


import re

from robot import utils


class Statistics:
    
    def __init__(self, suite, suite_stat_level=-1, tag_stat_include=None, 
                 tag_stat_exclude=None, tag_stat_combine=None, tag_doc=None,
                 tag_stat_link=None):
        self.tags = TagStatistics(tag_stat_include, tag_stat_exclude, 
                                  tag_stat_combine, tag_doc, tag_stat_link)
        self.suite = SuiteStatistics(suite, self.tags, suite_stat_level)
        self.total = TotalStatistics(self.suite)
        self.tags.sort()
        
    def serialize(self, serializer):
        serializer.start_statistics(self)
        self.total.serialize(serializer)
        self.tags.serialize(serializer)
        self.suite.serialize(serializer)
        serializer.end_statistics(self)


class Stat:
    
    def __init__(self, name=None, doc=None, link=None):
        self.name = name
        self.doc = doc
        self.link = link
        self.passed = 0
        self.failed = 0
        
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
                        
    def serialize(self, serializer):
        serializer.stat(self)
        
    def __cmp__(self, other):
        return cmp(self.name, other.name)

    def get_name(self, split_level=-1):
        return self.name

    def get_doc(self, split_level=-1):
        return self.doc
    
    def get_link(self, split_level=-1):
        return self.link
    
    def should_link_to_sub_log(self, split_level=-1):
        return False


class SuiteStat(Stat):

    type = 'suite'

    def __init__(self, suite):
        Stat.__init__(self, suite.name)
        self._suite = suite

    def get_name(self, split_level=-1):
        return self._suite.get_medium_name(split_level=split_level)

    def get_doc(self, split_level=-1):
        return self._suite.get_long_name(split_level=split_level)

    def get_link(self, split_level=-1):
        return self._suite.get_long_name(split_level=split_level)
        
    def should_link_to_sub_log(self, split_level=-1):
        return len(self._suite.get_long_name(separator=None)) == split_level+1


class TagStat(Stat):

    type = 'tag'
    
    def __init__(self, name, critical=False, non_critical=False, info=None):
        doc = info and info.get_doc(name) or None 
        Stat.__init__(self, name, doc, link=name)
        self.critical = critical
        self.non_critical = non_critical
        self.combined = False
        self.tests = []
        self.links = info and info.get_links(name) or []
        
    def add_test(self, test):
        Stat.add_test(self, test)
        self.tests.append(test)

    def __cmp__(self, other):
        if self.critical != other.critical:
            return self.critical is True and -1 or 1
        if self.non_critical != other.non_critical:
            return self.non_critical is True and -1 or 1
        if self.combined != other.combined:
            return self.combined is True and -1 or 1
        return cmp(self.name, other.name)


class CombinedTagStat(TagStat):
    
    def __init__(self, name):
        TagStat.__init__(self, name)
        self.combined = True

        
class TotalStat(Stat):
    
    type = 'total'

        
class SuiteStatistics:
    
    def __init__(self, suite, tag_stats, suite_stat_level=-1):
        self.name = suite.mediumname
        self.all = SuiteStat(suite)
        self.critical = SuiteStat(suite)
        self.suites = []
        self._process_suites(suite, tag_stats)
        self._process_tests(suite, tag_stats)
        self._suite_stat_level = suite_stat_level
        
    def _process_suites(self, suite, tag_stats):
        for subsuite in suite.suites:
            substat = SuiteStatistics(subsuite, tag_stats)
            self.suites.append(substat)
            self.all.add_stat(substat.all)
            self.critical.add_stat(substat.critical)
        
    def _process_tests(self, suite, tag_stats):
        for test in suite.tests:
            self.all.add_test(test)
            if test.critical == 'yes':
                self.critical.add_test(test)
            tag_stats.add_test(test, suite.critical)
        
    def serialize(self, serializer):
        if self._suite_stat_level == 0:
            return
        serializer.start_suite_stats(self)
        self._serialize(serializer, self._suite_stat_level)
        serializer.end_suite_stats(self)
        
    def _serialize(self, serializer, max_suite_level, suite_level=1):
        self.all.serialize(serializer)
        if max_suite_level < 0 or max_suite_level > suite_level:
            for suite in self.suites:
                suite._serialize(serializer, max_suite_level, suite_level+1)


class TagStatistics:
    
    def __init__(self, include=None, exclude=None, combine=None, docs=None, 
                 links=None):
        self.stats = utils.NormalizedDict()
        self._include = utils.to_list(include)
        self._exclude = utils.to_list(exclude)
        self._combine_and, self._combine_not = self._get_combine(combine)
        self._taginfo = TagStatInfo(utils.to_list(docs), utils.to_list(links))

    def _get_combine(self, combine):
        ands = []
        nots = []
        if combine is None or combine == []:
            return ands, nots
        for tags in combine:
            tags, name = self._split_tag_stat_combine_option(tags)
            if 'NOT' in tags:
                parts = [ utils.normalize(t) for t in tags.split('NOT') ]
                if '' not in parts:
                    nots.append((parts, name))
            else:
                parts = [ tag for tag in utils.normalize(tags).split('&') 
                          if tag != '' ]
                if parts != []:
                    ands.append((parts, name))
        return ands, nots

    def _split_tag_stat_combine_option(self, tags):
        if ':' in tags:
            index = tags.rfind(':')
            return tags[:index], utils.printable_name(tags[index+1:], True)
        return tags, None

    def add_test(self, test, critical):
        for tag in test.tags:
            if not self._is_included(tag):
                continue
            if not self.stats.has_key(tag):
                self.stats[tag] = TagStat(tag, critical.is_critical(tag),
                                          critical.is_non_critical(tag),
                                          self._taginfo)
            self.stats[tag].add_test(test)
        self._add_test_to_combined(test, self._combine_and, ' & ',
                                   self._is_combined_with_and)
        self._add_test_to_combined(test, self._combine_not, ' NOT ',
                                   self._is_combined_with_not)
    
    def _add_test_to_combined(self, test, combined_tags, joiner, is_combined):
        for tags, name in combined_tags:
            if name is None:
                name = joiner.join(tags)
            if not self.stats.has_key(name):
                self.stats[name] = CombinedTagStat(name)
            if is_combined(tags, test.tags):
                self.stats[name].add_test(test)
            
    def _is_combined_with_and(self, comb_tags, test_tags):
        for c_tag in comb_tags:
            if not utils.any_matches(test_tags, c_tag):
                return False
        return True

    def _is_combined_with_not(self, comb_tags, test_tags):
        if not utils.any_matches(test_tags, comb_tags[0]):
            return False
        for not_tag in comb_tags[1:]:
            if utils.any_matches(test_tags, not_tag):
                return False
        return True
            
    def _is_included(self, tag):
        if self._include != [] and not utils.matches_any(tag, self._include):
            return False
        return not utils.matches_any(tag, self._exclude)
    
    def serialize(self, serializer):
        if self.stats and (self._include or self._exclude):
            return
        serializer.start_tag_stats(self)
        stats = self.stats.values()
        stats.sort()
        for stat in stats:
            stat.serialize(serializer)
        serializer.end_tag_stats(self)

    def sort(self):
        for stat in self.stats.values():
            stat.tests.sort()


class TotalStatistics:
    
    def __init__(self, suite): 
        self.critical = self._get_stat('Critical Tests', suite.critical)
        self.all = self._get_stat('All Tests', suite.all)
                             
    def _get_stat(self, name, suite_stat):
        stat = TotalStat(name)
        stat.passed = suite_stat.passed
        stat.failed = suite_stat.failed
        return stat
        
    def serialize(self, serializer):
        serializer.start_total_stats(self)
        self.critical.serialize(serializer)
        self.all.serialize(serializer)
        serializer.end_total_stats(self)
        
        
class TagStatInfo:
    
    def __init__(self, docs, links):
        self._docs = dict([ self._parse_doc(doc) for doc in docs ])
        self._links = [ TagStatLink(*link) for link in links ]

    def _parse_doc(self, cli_item):
        try:
            tag, doc = cli_item.split(':', 1)
        except ValueError:
            tag, doc = cli_item, ''
        return tag, doc

    def get_doc(self, tag):
        docs = []
        for key, value in self._docs.items():
            if utils.matches(tag, key):
                docs.append(value)
        return docs and ' '.join(docs) or None

    def get_links(self, tag):
        links = [ link.get_link(tag) for link in self._links ]
        return [ link for link in links if link is not None ] 
        
        
class TagStatLink:
    _match_pattern_tokenizer = re.compile('(\*|\?)')
    
    def __init__(self, pattern, link, title):
        self._regexp = self._get_match_regexp(pattern) 
        self._link = link
        self._title = title.replace('_', ' ')
    
    def get_link(self, tag):
        match = self._regexp.match(tag)
        if match is not None: 
            link = self._replace_matches(self._link, match)
            return link, self._title
        return None
    
    def _replace_matches(self, url, match):
        groups = match.groups()
        for i, group in enumerate(groups):
            url = url.replace('%%%d' % (i+1), group)
        return url

    def _get_match_regexp(self, pattern):
        pattern = utils.normalize(pattern)
        regexp = []
        open_parenthesis = False
        for token in self._match_pattern_tokenizer.split(pattern):
            if token == '':
                continue
            if token == '?':
                if not open_parenthesis:
                    regexp.append('(')
                    open_parenthesis = True
                regexp.append('.')
                continue
            if open_parenthesis:
                regexp.append(')')
                open_parenthesis = False
            if token == '*':
                regexp.append('(.*)')
                continue
            regexp.append(re.escape(token))
        if open_parenthesis:
            regexp.append(')')
        return re.compile('^%s$' % ''.join(regexp))
