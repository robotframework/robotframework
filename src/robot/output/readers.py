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


import os.path

from robot import utils
from robot.errors import DataError
from robot.common import BaseTestSuite, BaseTestCase, BaseKeyword


def process_outputs(paths, settings, syslog=None):
    if not paths:
        raise DataError('No output files given.')
    if len(paths) == 1:
        return process_output(paths[0], syslog)
    testsuite = CombinedTestSuite(settings['StartTime'], settings['EndTime'])
    testsyslog = CombinedSyslog()
    for path in paths:
        subsuite, subsyslog = process_output(path, syslog)
        testsuite.add_suite(subsuite)
        testsyslog.add(subsyslog)
    return testsuite, testsyslog


def process_output(path, read_level=-1, syslog=None):
    """Process one Robot output xml file and return TestSuite and Syslog
    
    'read_level' can be used to limit how many suite levels are read. This is
    mainly useful when Robot has split outputs and only want to read index.
    """
    if not os.path.isfile(path):
        raise DataError("Output file '%s' does not exist." % path)
    if syslog is not None:
        syslog.info("Processing output file '%s'." % path)
    try:
        root = utils.DomWrapper(path)
    except:
        raise DataError("File '%s' is not a valid XML file." % path)
    try:
        suite = _get_suite_node(root)
    except AttributeError:
        raise DataError("File '%s' is not a Robot output file." % path)
    try:
        syslognode = root.get_node('syslog')
    except AttributeError:
        syslognode = None
    return TestSuite(suite, read_level), Syslog(syslognode)

    
def _get_suite_node(root):
    if root.name != 'robot': 
        raise AttributeError
    node = root.get_node('suite')
    node.generator = root.get_attr('generator', 'notset').split(' ')[0].lower()
    return node


class _BaseReader:
    
    def __init__(self, node):
        self.name = node.get_attr('name')
        try:
            self.doc = node.get_node('doc').text
        except AttributeError:
            self.doc = ''
        status = node.get_node('status')
        self.status = status.get_attr('status','').upper()
        if self.status not in ['PASS','FAIL']:
            raise DataError("Item '%s' has invalid status '%s'" % (self.name, status))
        self.message = status.text
        self.starttime = status.get_attr('starttime', 'N/A')
        self.endtime = status.get_attr('endtime', 'N/A')
        self._set_elapsed_time()
        
    def _set_elapsed_time(self):
        if self.starttime != 'N/A' and self.endtime != 'N/A':
            self.elapsedmillis = utils.get_elapsed_millis(self.starttime, self.endtime)
            self.elapsedtime = utils.elapsed_millis_to_string(self.elapsedmillis)
        else:
            self.elapsedmillis = 0
            self.elapsedtime = '00:00:00.000'
            

class _TestAndSuiteReader(_BaseReader):
    
    def __init__(self, node):
        _BaseReader.__init__(self, node)
        self.keywords = [ Keyword(kw) for kw in node.get_nodes('kw') ]
        if len(self.keywords) > 0 and self.keywords[0].type == 'setup':
            self.setup = self.keywords.pop(0)
        if len(self.keywords) > 0 and self.keywords[-1].type == 'teardown':
            self.teardown = self.keywords.pop(-1)

        
class _SuiteReader(_TestAndSuiteReader):
    
    def __init__(self, node):
        _TestAndSuiteReader.__init__(self, node)
        del(self.keywords)
        for metanode in node.get_nodes('metadata/item'):
            self.metadata[metanode.get_attr('name')] = metanode.text
        self.critical.tags = self._get_texts(node, 'critical/tag')
        self.critical.nons = self._get_texts(node, 'critical/non')
        self.filtered.suites = self._get_texts(node, 'filtered/suite')
        self.filtered.tests = self._get_texts(node, 'filtered/test')
        self.filtered.incls = self._get_texts(node, 'filtered/incl')
        self.filtered.excls = self._get_texts(node, 'filtered/excl')
            
    def _get_texts(self, node, path):
        return [ item.text for item in node.get_nodes(path) ]
            

class _TestReader(_TestAndSuiteReader):

    def __init__(self, node):
        _TestAndSuiteReader.__init__(self, node)
        self.tags = [ tag.text for tag in node.get_nodes('tags/tag') ]
        self.timeout = node.get_attr('timeout', '')


class _KeywordReader(_BaseReader): 

    def __init__(self, node):
        _BaseReader.__init__(self, node)
        del(self.message)
        self.args = [ arg.text for arg in node.get_nodes('arguments/arg') ]
        self.type = node.get_attr('type', 'kw')
        self.timeout = node.get_attr('timeout', '')
        self.keywords = []
        self.messages = []
        self.children = []
        for child in node.children:
            if child.name == 'kw':
                kw = Keyword(child)
                self.keywords.append(kw) 
                self.children.append(kw) 
            elif child.name == 'msg':
                msg = Message(child)
                self.messages.append(msg) 
                self.children.append(msg) 

    
class TestSuite(BaseTestSuite, _SuiteReader):

    def __init__(self, node, read_level=-1, level=1):
        node = self._get_node(node, read_level, level)
        BaseTestSuite.__init__(self)
        _SuiteReader.__init__(self, node)
        for snode in node.get_nodes('suite'):
            snode.generator = node.generator
            suite = TestSuite(snode, read_level, level+1)
            self.suites.append(suite)
        for tnode in node.get_nodes('test'):
            test = TestCase(tnode, self)
            self.tests.append(test)
        self.set_status()
        if node.generator == 'robot' and \
                self.teardown is not None and self.teardown.status == 'FAIL':
            self.suite_teardown_failed()

    def _get_node(self, orignode, read_level, level):
        if read_level > 0 and level > read_level:
            return orignode
        try:
            src = orignode.get_attr('src')
        except AttributeError:
            return orignode
        path = os.path.join(os.path.dirname(orignode.source), src)
        node = utils.DomWrapper(path).get_node('suite')
        node.generator = orignode.generator
        return node

    def set_status(self):
        BaseTestSuite.set_status(self)
        if self.starttime == 'N/A' or self.endtime == 'N/A':
            self._set_elapsed()

    def _set_elapsed(self):
        subitems = self.suites + self.tests + [self.setup, self.teardown]
        self.elapsedmillis = sum([ item.elapsedmillis for item in subitems 
                                   if item is not None ])
        self.elapsedtime = utils.elapsed_millis_to_string(self.elapsedmillis)

    def _set_critical_tags(self, critical):
        BaseTestSuite._set_critical_tags(self, critical)
        self.set_status()
        
    def _filter_by_tags(self, incls, excls):
        ret = BaseTestSuite._filter_by_tags(self, incls, excls)
        self.starttime = self.endtime = 'N/A'
        self.set_status()
        return ret

    def _filter_by_names(self, suites, tests):
        ret = BaseTestSuite._filter_by_names(self, suites, tests)
        self.starttime = self.endtime = 'N/A'
        self.set_status()
        return ret
    
    def remove_keywords(self, how):
        how = how.upper() 
        if how not in ['ALL','PASSED']:
            return
        if how == 'ALL' or (how == 'PASSED' and self.critical_stats.failed == 0):
            for kw in self.setup, self.teardown:
                if kw is not None:
                    kw.remove_data()
        for suite in self.suites:
            suite.remove_keywords(how)
        for test in self.tests:
            test.remove_keywords(how)


class CombinedTestSuite(TestSuite):
    
    def __init__(self, starttime, endtime):
        BaseTestSuite.__init__(self)
        self.doc = ''
        self.message = ''
        self.starttime = self._get_time(starttime)
        self.endtime = self._get_time(endtime)
        self._set_elapsed_time()
        
    def _get_time(self, timestamp):
        if utils.eq(timestamp, 'N/A'):
            return 'N/A'
        try:
            seps = (' ', ':', '.', '-', '_')
            secs = utils.timestamp_to_secs(timestamp, seps, millis=True)
        except:
            return 'N/A'
        return utils.secs_to_timestamp(secs, millis=True)

    def set_names(self, name=None):
        if name is None:
            name = ' & '.join([suite.name for suite in self.suites])
        return BaseTestSuite.set_names(self, name)

    def add_suite(self, suite):
        self.suites.append(suite)
        self._add_suite_to_stats(suite)
        self.status = self.critical_stats.failed == 0 and 'PASS' or 'FAIL'
        if self.starttime == self.endtime == 'N/A':
            self.elapsedmillis += suite.elapsedmillis
            self.elapsedtime = utils.elapsed_millis_to_string(self.elapsedmillis)
        

class TestCase(BaseTestCase, _TestReader):

    def __init__(self, node, parent):
        BaseTestCase.__init__(self)
        _TestReader.__init__(self, node)
        self.set_criticality(parent.critical)
  
    def remove_keywords(self, how):
        if how == 'ALL' or (how == 'PASSED' and self.status == 'PASS'):
            for kw in self.keywords + [self.setup, self.teardown]:
                if kw is not None:
                    kw.remove_data()

        
class Keyword(BaseKeyword, _KeywordReader):

    def __init__(self, node):
        self._init_data()
        BaseKeyword.__init__(self)
        _KeywordReader.__init__(self, node)
        
    def _init_data(self):
        self.messages = []
        self.keywords = []
        self.children = []
            
    def remove_data(self):
        self._init_data()
            
    def __str__(self):
        return self.name

    def __repr__(self):
        return "'%s'" % self.name
    
    def serialize(self, serializer):
        serializer.start_keyword(self)
        for child in self.children:
            child.serialize(serializer)
        serializer.end_keyword(self)


class Message:

    def __init__(self, node):
        self.timestamp = node.get_attr('timestamp', 'N/A')
        self.level = node.get_attr('level', 'INFO')
        self.message = node.text
        self.html = node.get_attr('html', 'no') == 'yes'

    def serialize(self, serializer):
        serializer.message(self)

    def __str__(self):
        return '%s %s %s' % (self.timestamp, self.level, self.message)
    
    def __repr__(self):
        lines = self.message.split('\n')
        msg = len(lines) > 1 and lines[0] + '...' or lines[0]
        return "'%s %s'" % (self.level, msg.replace("'",'"'))


class Syslog:
    
    def __init__(self, node):
        if node is None:
            self.messages = []
        else:
            self.messages = [ Message(msg) for msg in node.get_nodes('msg') ]

    def serialize(self, serializer):
        serializer.start_syslog(self)
        for msg in self.messages:
            msg.serialize(serializer)
        serializer.end_syslog(self)


class CombinedSyslog(Syslog):
    
    def __init__(self):
        self.messages = []
        
    def add(self, other):
        self.messages += other.messages
