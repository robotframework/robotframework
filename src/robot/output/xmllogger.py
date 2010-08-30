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
from robot.version import get_full_version

from loggerhelper import IsLogged


class XmlLogger:

    def __init__(self, path, log_level='TRACE', split_level=-1, generator='Robot'):
        self._namegen = utils.FileNameGenerator(path)
        self._log_message_is_logged = IsLogged(log_level)
        self._error_is_logged = IsLogged('WARN')
        self._writer = None
        self._writer_args = (path, {'generator': get_full_version(generator),
                                    'generated': utils.get_timestamp()})
        self._index_writer = None
        self._split_level = split_level
        self._suite_level = 0
        self._errors = []

    def _get_writer(self, path, attrs={}):
        try:
            writer = utils.XmlWriter(path)
        except:
            raise DataError("Opening output file '%s' for writing failed: %s"
                            % (path, utils.get_error_message()))
        writer.start('robot', attrs)
        return writer

    def _close_writer(self, writer):
        if not writer.closed:
            writer.end('robot')
            writer.close()

    def close(self, serialize_errors=False):
        if serialize_errors:
            self.start_errors()
            for msg in self._errors:
                self._message(msg)
            self.end_errors()
        self._close_writer(self._writer)

    def message(self, msg):
        if self._error_is_logged(msg.level):
            self._errors.append(msg)

    def log_message(self, msg):
        if self._log_message_is_logged(msg.level):
            self._message(msg)

    def set_log_level(self, level):
        return self._log_message_is_logged.set_level(level)

    def _message(self, msg):
        attrs = {'timestamp': msg.timestamp, 'level': msg.level}
        if msg.html:
            attrs['html'] = 'yes'
        if msg.linkable:
            attrs['linkable'] = 'yes'
        self._writer.element('msg', msg.message, attrs)

    def start_keyword(self, kw):
        attrs = {'name': kw.name, 'type': kw.type, 'timeout': kw.timeout}
        self._writer.start('kw', attrs)
        self._writer.element('doc', kw.doc)
        self._write_list('arg', [utils.unic(a) for a in kw.args], 'arguments')

    def end_keyword(self, kw):
        self._write_status(kw)
        self._writer.end('kw')

    def start_test(self, test):
        attrs = {'name': test.name, 'critical': test.critical,
                 'timeout': str(test.timeout)}
        self._writer.start('test', attrs)
        self._writer.element('doc', test.doc)

    def end_test(self, test):
        self._write_list('tag', test.tags, 'tags')
        self._write_status(test, test.message)
        self._writer.end('test')

    def start_suite(self, suite):
        if not self._writer:
            self._writer = self._get_writer(*self._writer_args)
            del self._writer_args
        if self._suite_level == self._split_level:
            self._start_split_output(suite)
            self.started_output = self._writer.path
        else:
            self.started_output = None
        self._start_suite(suite)
        self._suite_level += 1

    def _start_split_output(self, suite):
        path =  self._namegen.get_name()
        self._start_suite(suite, {'src': os.path.basename(path)})
        self._index_writer = self._writer
        self._writer = self._get_writer(path)

    def _start_suite(self, suite, extra_attrs=None):
        attrs = extra_attrs is not None and extra_attrs or {}
        attrs['name'] = suite.name
        if suite.source:
            attrs['source'] = suite.source
        self._writer.start('suite', attrs)
        self._writer.element('doc', suite.doc)
        self._writer.start('metadata')
        for name, value in suite.get_metadata():
            self._writer.element('item', value, {'name': name})
        self._writer.end('metadata')

    def end_suite(self, suite):
        self._suite_level -= 1
        self._end_suite(suite)
        if self._suite_level == self._split_level:
            self.ended_output = self._end_split_output(suite)
        else:
            self.ended_output = None

    def _end_split_output(self, suite):
        outpath = self._writer.path
        self._close_writer(self._writer)
        self._writer = self._index_writer
        self._end_suite(suite)
        return outpath

    def _end_suite(self, suite):
        # Note that suites statistics message is _not_ written into xml
        self._write_status(suite, suite.message)
        self._writer.end('suite')

    def start_statistics(self, stats):
        self._writer.start('statistics')

    def end_statistics(self, stats):
        self._writer.end('statistics')

    def start_total_stats(self, total_stats):
        self._writer.start('total')

    def end_total_stats(self, total_stats):
        self._writer.end('total')

    def start_tag_stats(self, tag_stats):
        self._writer.start('tag')

    def end_tag_stats(self, tag_stats):
        self._writer.end('tag')

    def start_suite_stats(self, tag_stats):
        self._writer.start('suite')

    def end_suite_stats(self, tag_stats):
        self._writer.end('suite')

    def total_stat(self, stat):
        self._stat(stat)

    def suite_stat(self, stat):
        self._stat(stat, stat.get_long_name(self._split_level))

    def tag_stat(self, stat):
        self._stat(stat, attrs={'info': self._get_tag_stat_info(stat)})

    def _stat(self, stat, name=None, attrs=None):
        name = name or stat.name
        attrs = attrs or {}
        attrs['pass'] = str(stat.passed)
        attrs['fail'] = str(stat.failed)
        doc = stat.get_doc(self._split_level)
        if doc:
            attrs['doc'] = doc
        self._writer.element('stat', name, attrs)

    def _get_tag_stat_info(self, stat):
        if stat.critical is True:
            return 'critical'
        if stat.non_critical is True:
            return 'non-critical'
        if stat.combined is True:
            return 'combined'
        return ''

    def start_errors(self):
        self._writer.start('errors')

    def end_errors(self):
        self._writer.end('errors')

    def _write_list(self, tag, items, container=None):
        if container is not None:
            self._writer.start(container)
        for item in items:
            self._writer.element(tag, item)
        if container is not None:
            self._writer.end(container)

    def _write_status(self, item, message=None):
        self._writer.element('status', message, {'status': item.status,
                                                 'starttime': item.starttime,
                                                 'endtime': item.endtime})
