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


import os.path

from robot import utils
from robot.errors import DataError
from robot.common import BaseTestSuite, BaseTestCase, BaseKeyword
from robot.output import LOGGER
from robot.output.loggerhelper import IsLogged, Message


def process_outputs(paths, settings):
    if not paths:
        raise DataError('No output files given.')
    if len(paths) == 1:
        return process_output(paths[0], log_level=settings['LogLevel'])
    suite = CombinedTestSuite(settings['StartTime'], settings['EndTime'])
    exec_errors = CombinedExecutionErrors()
    for path in paths:
        subsuite, suberrors = process_output(path, log_level=settings['LogLevel'])
        suite.add_suite(subsuite)
        exec_errors.add(suberrors)
    return suite, exec_errors


def process_output(path, read_level=-1, log_level=None):
    """Process one output file and return TestSuite and ExecutionErrors

    'read_level' can be used to limit how many suite levels are read. This is
    mainly useful when Robot has split outputs and only want to read index.
    """
    if not os.path.isfile(path):
        raise DataError("Output file '%s' does not exist." % path)
    LOGGER.info("Processing output file '%s'." % path)
    try:
        root = utils.DomWrapper(path)
    except:
        err = utils.get_error_message()
        raise DataError("Opening XML file '%s' failed: %s" % (path, err))
    suite = _get_suite_node(root, path)
    errors = _get_errors_node(root)
    return TestSuite(suite, read_level, log_level=log_level), ExecutionErrors(errors)

def _get_suite_node(root, path):
    if root.name != 'robot':
        raise DataError("File '%s' is not Robot Framework output file." % path)
    node = root.get_node('suite')
    node.generator = root.get_attr('generator', 'notset').split()[0].lower()
    return node

def _get_errors_node(root):
    try:
        try:
            return root.get_node('errors')
        except AttributeError:
            return root.get_node('syslog') # Compatibility for RF 2.0.x outputs
    except AttributeError:
        return None


class _MissingStatus:
    """If XML was fixed for example by fixml.py, status tag may be missing"""
    text = 'Could not find status.'
    get_attr = lambda self, name, default: name == 'status' and 'FAIL' or 'N/A'


class _BaseReader:

    def __init__(self, node):
        try:
            self.doc = node.get_node('doc').text
        except AttributeError:
            self.doc = ''
        try:
            status = node.get_node('status')
        except AttributeError:
            status = _MissingStatus()
        self.status = status.get_attr('status','').upper()
        if self.status not in ['PASS','FAIL', 'NOT_RUN']:
            raise DataError("Item '%s' has invalid status '%s'"
                            % (self.name, status))
        self.message = status.text
        self.starttime = status.get_attr('starttime', 'N/A')
        self.endtime = status.get_attr('endtime', 'N/A')
        self.elapsedtime = utils.get_elapsed_time(self.starttime, self.endtime)


class _TestAndSuiteReader(_BaseReader):

    def __init__(self, node, log_level=None):
        _BaseReader.__init__(self, node)
        self.keywords = [Keyword(kw, log_level) for kw in node.get_nodes('kw')]
        if self.keywords and self.keywords[0].type == 'setup':
            self.setup = self.keywords.pop(0)
        if self.keywords and self.keywords[-1].type == 'teardown':
            self.teardown = self.keywords.pop(-1)


class _SuiteReader(_TestAndSuiteReader):

    def __init__(self, node, log_level=None):
        _TestAndSuiteReader.__init__(self, node, log_level)
        del(self.keywords)
        for metanode in node.get_nodes('metadata/item'):
            self.metadata[metanode.get_attr('name')] = metanode.text

    def _get_texts(self, node, path):
        return [item.text for item in node.get_nodes(path)]


class _TestReader(_TestAndSuiteReader):

    def __init__(self, node, log_level=None):
        _TestAndSuiteReader.__init__(self, node, log_level)
        self.tags = [tag.text for tag in node.get_nodes('tags/tag')]
        self.timeout = node.get_attr('timeout', '')


class _KeywordReader(_BaseReader):

    def __init__(self, node, log_level=None):
        _BaseReader.__init__(self, node)
        del(self.message)
        self.args = [arg.text for arg in node.get_nodes('arguments/arg')]
        self.type = node.get_attr('type', 'kw')
        self.timeout = node.get_attr('timeout', '')
        self.keywords = []
        self.messages = []
        self.children = []
        log_filter = IsLogged(log_level or 'TRACE')
        for child in node.children:
            if child.name == 'kw':
                kw = Keyword(child)
                self.keywords.append(kw)
                self.children.append(kw)
            elif child.name == 'msg' and log_filter(child.get_attr('level', 'INFO')):
                msg = MessageFromXml(child)
                self.messages.append(msg)
                self.children.append(msg)


class TestSuite(BaseTestSuite, _SuiteReader):

    def __init__(self, node, read_level=-1, level=1, parent=None, log_level=None):
        node = self._get_node(node, read_level, level)
        BaseTestSuite.__init__(self, node.attrs.get('name'),
                               node.attrs.get('source', None), parent)
        _SuiteReader.__init__(self, node, log_level=log_level)
        for snode in node.get_nodes('suite'):
            snode.generator = node.generator
            TestSuite(snode, read_level, level+1, parent=self, log_level=log_level)
        for tnode in node.get_nodes('test'):
            TestCase(tnode, parent=self, log_level=log_level)
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
            subitems = self.suites + self.tests + [self.setup, self.teardown]
            self.elapsedtime = sum(item.elapsedtime for item in subitems
                                   if item is not None )

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
        BaseTestSuite.__init__(self, name='')
        self.starttime = self._get_time(starttime)
        self.endtime = self._get_time(endtime)
        self.elapsedtime = utils.get_elapsed_time(self.starttime, self.endtime)

    def _get_time(self, timestamp):
        if utils.eq(timestamp, 'N/A'):
            return 'N/A'
        try:
            seps = (' ', ':', '.', '-', '_')
            secs = utils.timestamp_to_secs(timestamp, seps, millis=True)
        except DataError:
            return 'N/A'
        return utils.secs_to_timestamp(secs, millis=True)

    def add_suite(self, suite):
        self.suites.append(suite)
        suite.parent = self
        self._add_suite_to_stats(suite)
        self.status = self.critical_stats.failed == 0 and 'PASS' or 'FAIL'
        if self.starttime == 'N/A' or self.endtime == 'N/A':
            self.elapsedtime += suite.elapsedtime


class TestCase(BaseTestCase, _TestReader):

    def __init__(self, node, parent, log_level=None):
        BaseTestCase.__init__(self, node.get_attr('name'), parent)
        _TestReader.__init__(self, node, log_level=log_level)
        self.set_criticality(parent.critical)

    def remove_keywords(self, how):
        if how == 'ALL' or (how == 'PASSED' and self.status == 'PASS'):
            for kw in self.keywords + [self.setup, self.teardown]:
                if kw is not None:
                    kw.remove_data()


class Keyword(BaseKeyword, _KeywordReader):

    def __init__(self, node, log_level=None):
        self._init_data()
        BaseKeyword.__init__(self, node.get_attr('name'))
        _KeywordReader.__init__(self, node, log_level)

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


class MessageFromXml(Message):

    def __init__(self, node):
        Message.__init__(self, node.text,
                         level=node.get_attr('level', 'INFO'),
                         html=node.get_attr('html', 'no') == 'yes',
                         timestamp=node.get_attr('timestamp', 'N/A'),
                         linkable=node.get_attr('linkable', 'no') == 'yes')

    def serialize(self, serializer):
        serializer.message(self)

    def __str__(self):
        return '%s %s %s' % (self.timestamp, self.level, self.message)

    def __repr__(self):
        lines = self.message.split('\n')
        msg = len(lines) > 1 and lines[0] + '...' or lines[0]
        return "'%s %s'" % (self.level, msg.replace("'",'"'))


class ExecutionErrors:

    def __init__(self, node):
        if node is None:
            self.messages = []
        else:
            self.messages = [MessageFromXml(msg) for msg in node.get_nodes('msg')]

    def serialize(self, serializer):
        serializer.start_errors(self)
        for msg in self.messages:
            msg.serialize(serializer)
        serializer.end_errors(self)


class CombinedExecutionErrors(ExecutionErrors):

    def __init__(self):
        self.messages = []

    def add(self, other):
        self.messages += other.messages
