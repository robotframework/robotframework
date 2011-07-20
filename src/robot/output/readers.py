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
        return process_output(paths[0], log_level=settings['LogLevel'],
                              settings=settings)
    suite = CombinedTestSuite(settings)
    exec_errors = CombinedExecutionErrors()
    for path in paths:
        subsuite, suberrors = process_output(path, log_level=settings['LogLevel'])
        suite.add_suite(subsuite)
        exec_errors.add(suberrors)
    return suite, exec_errors


def process_output(path, log_level=None, settings=None):
    """Process one output file and return TestSuite and ExecutionErrors"""
    if not os.path.isfile(path):
        raise DataError("Output file '%s' does not exist." % path)
    LOGGER.info("Processing output file '%s'." % path)
    try:
        root = utils.etreewrapper.get_root(path)
    except:
        raise DataError("Opening XML file '%s' failed: %s"
                        % (path, utils.get_error_message()))
    suite = TestSuite(_get_suite_node(root, path), log_level=log_level,
                      settings=settings)
    errors = ExecutionErrors(_get_errors_node(root))
    return suite, errors


def _get_suite_node(root, path):
    if root.tag != 'robot':
        raise DataError("File '%s' is not Robot Framework output file." % path)
    node = root.find('suite')
    node.set('generator', root.get('generator', 'notset').split()[0].lower())
    node.set('path', path)
    return node

def _get_errors_node(root):
    return root.find('errors')


class _MissingStatus:
    """If XML was fixed for example by fixml.py, status tag may be missing"""
    text = 'Could not find status.'
    get = lambda self, name, default: 'FAIL' if name == 'status' else 'N/A'


class _BaseReader:

    def __init__(self, node):
        self.doc = self._get_doc(node)
        stnode = node.find('status')
        if stnode is None:
            stnode = _MissingStatus()
        self.status = stnode.get('status','').upper()
        if self.status not in ['PASS','FAIL', 'NOT_RUN']:
            raise DataError("Item '%s' has invalid status '%s'"
                            % (self.name, self.status))
        self.message = stnode.text or ''
        self.starttime = stnode.get('starttime', 'N/A')
        self.endtime = stnode.get('endtime', 'N/A')
        self.elapsedtime = utils.get_elapsed_time(self.starttime, self.endtime)

    def _get_doc(self, node):
        docnode = node.find('doc')
        if docnode is not None:
            return docnode.text or ''
        return ''


class _TestAndSuiteReader(_BaseReader):

    def __init__(self, node, log_level=None):
        _BaseReader.__init__(self, node)
        self.keywords = [Keyword(kw, log_level) for kw in node.findall('kw')]
        if self.keywords and self.keywords[0].type == 'setup':
            self.setup = self.keywords.pop(0)
        if self.keywords and self.keywords[-1].type == 'teardown':
            self.teardown = self.keywords.pop(-1)


class _SuiteReader(_TestAndSuiteReader):

    def __init__(self, node, log_level=None):
        _TestAndSuiteReader.__init__(self, node, log_level)
        del(self.keywords)
        for metanode in node.findall('metadata/item'):
            self.metadata[metanode.get('name')] = metanode.text

    def _get_texts(self, node, path):
        return [item.text for item in node.findall(path)]


class _TestReader(_TestAndSuiteReader):

    def __init__(self, node, log_level=None):
        _TestAndSuiteReader.__init__(self, node, log_level)
        self.tags = [tag.text for tag in node.findall('tags/tag')]
        self.timeout = node.get('timeout', '')


class _KeywordReader(_BaseReader):

    def __init__(self, node, log_level=None):
        _BaseReader.__init__(self, node)
        del(self.message)
        self.args = [(arg.text or '') for arg in node.findall('arguments/arg')]
        self.type = node.get('type', 'kw')
        self.timeout = node.get('timeout', '')
        self.keywords = []
        self.messages = []
        self.children = []
        log_filter = IsLogged(log_level or 'TRACE')
        for child in node:
            if child.tag == 'kw':
                kw = Keyword(child, log_level)
                self.keywords.append(kw)
                self.children.append(kw)
            elif child.tag == 'msg' and log_filter(child.get('level', 'INFO')):
                msg = MessageFromXml(child)
                self.messages.append(msg)
                self.children.append(msg)


class TestSuite(BaseTestSuite, _SuiteReader):

    def __init__(self, node, parent=None, log_level=None, settings=None):
        node = self._get_possibly_split_node(node)
        BaseTestSuite.__init__(self, node.get('name'),
                               node.get('source', None), parent)
        _SuiteReader.__init__(self, node, log_level=log_level)
        self._set_times_from_settings(settings)
        for snode in node.findall('suite'):
            self._set_attrs_from_parent(snode, node)
            TestSuite(snode, parent=self, log_level=log_level)
        for tnode in node.findall('test'):
            TestCase(tnode, parent=self, log_level=log_level)
        self.set_status()
        if node.get('generator') == 'robot' and \
                self.teardown and self.teardown.status == 'FAIL':
            self.suite_teardown_failed()

    def _get_possibly_split_node(self, orig):
        src = orig.get('src')
        if not src:
            return orig
        # Support for split outputs generated with 2.5.x.
        path = os.path.join(os.path.dirname(orig.get('path')), src)
        try:
            node = utils.etreewrapper.get_root(path).find('suite')
        except:
            LOGGER.error("Opening split output '%s' failed: %s"
                         % (path, utils.get_error_message()))
            return orig
        self._set_attrs_from_parent(node, orig)
        return node

    def _set_attrs_from_parent(self, child, parent):
        child.set('generator', parent.get('generator'))
        child.set('path', parent.get('path'))

    def _set_times_from_settings(self, settings):
        starttime, endtime = self._times_from_settings(settings)
        if not self.starttime or starttime != 'N/A':
            self.starttime = starttime
        if not self.endtime or endtime != 'N/A':
            self.endtime = endtime
        self.elapsedtime = utils.get_elapsed_time(self.starttime, self.endtime)

    def _times_from_settings(self, settings):
        if not settings:
            return 'N/A', 'N/A'
        return (self._get_time(settings['StartTime']),
                self._get_time(settings['EndTime']))

    def _get_time(self, timestamp):
        if not timestamp or utils.eq(timestamp, 'N/A'):
            return 'N/A'
        try:
            secs = utils.timestamp_to_secs(timestamp, seps=list(' :.-_'),
                                           millis=True)
        except ValueError:
            return 'N/A'
        return utils.secs_to_timestamp(secs, millis=True)

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
        should_remove = ShouldRemoveCallable(how)
        if not should_remove:
            return
        self._remove_fixture_keywords(should_remove)
        for suite in self.suites:
            suite.remove_keywords(how)
        for test in self.tests:
            test.remove_keywords(should_remove)

    def _remove_fixture_keywords(self, should_remove):
        critical_failures = self.critical_stats.failed != 0
        for kw in self.setup, self.teardown:
            if should_remove(kw, critical_failures):
                kw.remove_data()


class CombinedTestSuite(TestSuite):

    def __init__(self, settings):
        BaseTestSuite.__init__(self, name='')
        self.starttime = self.endtime = None
        self._set_times_from_settings(settings)

    def add_suite(self, suite):
        self.suites.append(suite)
        suite.parent = self
        self._add_suite_to_stats(suite)
        self.status = self.critical_stats.failed == 0 and 'PASS' or 'FAIL'
        if self.starttime == 'N/A' or self.endtime == 'N/A':
            self.elapsedtime += suite.elapsedtime


class TestCase(BaseTestCase, _TestReader):

    def __init__(self, node, parent, log_level=None):
        BaseTestCase.__init__(self, node.get('name'), parent)
        _TestReader.__init__(self, node, log_level=log_level)
        self.set_criticality(parent.critical)

    def remove_keywords(self, should_remove):
        if should_remove(self, (self.status != 'PASS')):
            for kw in self.keywords + [self.setup, self.teardown]:
                if kw is not None:
                    kw.remove_data()

    def contains_warnings(self):
        return any(kw.contains_warnings() for kw in self.keywords)


class Keyword(BaseKeyword, _KeywordReader):

    def __init__(self, node, log_level=None):
        self._init_data()
        BaseKeyword.__init__(self, node.get('name'))
        _KeywordReader.__init__(self, node, log_level)

    def _init_data(self):
        self.messages = []
        self.keywords = []
        self.children = []

    def remove_data(self):
        self._init_data()

    def contains_warnings(self):
        return any(msg.level == 'WARN' for msg in self.messages) or \
                    any(kw.contains_warnings() for kw in self.keywords)

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
                         level=node.get('level', 'INFO'),
                         html=node.get('html', 'no') == 'yes',
                         timestamp=node.get('timestamp', 'N/A'),
                         linkable=node.get('linkable', 'no') == 'yes')

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
            self.messages = [MessageFromXml(msg) for msg in node.findall('msg')]

    def serialize(self, serializer):
        serializer.start_errors()
        for msg in self.messages:
            msg.serialize(serializer)
        serializer.end_errors()


class CombinedExecutionErrors(ExecutionErrors):

    def __init__(self):
        self.messages = []

    def add(self, other):
        self.messages += other.messages


def ShouldRemoveCallable(how):
    def _removes_all(item, critical_failures):
        return item is not None
    def _removes_passed_not_containing_warnings(item, critical_failures):
        if item is None:
            return False
        if critical_failures:
            return False
        return not item.contains_warnings()
    how = how.upper()
    if how == 'ALL':
        return _removes_all
    return _removes_passed_not_containing_warnings if how == 'PASSED' else None
