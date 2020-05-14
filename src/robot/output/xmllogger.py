#  Copyright 2008-2015 Nokia Networks
#  Copyright 2016-     Robot Framework Foundation
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

from robot.utils import XmlWriter, NullMarkupWriter, get_timestamp, unic
from robot.version import get_full_version
from robot.result.visitor import ResultVisitor

from .loggerhelper import IsLogged


class XmlLogger(ResultVisitor):

    def __init__(self, path, log_level='TRACE', rpa=False, generator='Robot'):
        self._log_message_is_logged = IsLogged(log_level)
        self._error_message_is_logged = IsLogged('WARN')
        self._writer = self._get_writer(path, rpa, generator)
        self._errors = []

    def _get_writer(self, path, rpa, generator):
        if not path:
            return NullMarkupWriter()
        writer = XmlWriter(path, write_empty=False, usage='output')
        writer.start('robot', {'generator': get_full_version(generator),
                               'generated': get_timestamp(),
                               'rpa': 'true' if rpa else 'false'})
        return writer

    def close(self):
        self.start_errors()
        for msg in self._errors:
            self._write_message(msg)
        self.end_errors()
        self._writer.end('robot')
        self._writer.close()

    def set_log_level(self, level):
        return self._log_message_is_logged.set_level(level)

    def message(self, msg):
        if self._error_message_is_logged(msg.level):
            self._errors.append(msg)

    def log_message(self, msg):
        if self._log_message_is_logged(msg.level):
            self._write_message(msg)

    def _write_message(self, msg):
        attrs = {'timestamp': msg.timestamp or 'N/A', 'level': msg.level}
        if msg.html:
            attrs['html'] = 'yes'
        self._writer.element('msg', msg.message, attrs)

    def start_keyword(self, kw):
        attrs = {'name': kw.kwname, 'library': kw.libname}
        if kw.type != 'kw':
            attrs['type'] = kw.type
        self._writer.start('kw', attrs)
        self._write_list('tags', 'tag', [unic(t) for t in kw.tags])
        self._writer.element('doc', kw.doc)
        self._write_list('arguments', 'arg', [unic(a) for a in kw.args])
        self._write_list('assign', 'var', kw.assign)

    def end_keyword(self, kw):
        if kw.timeout:
            self._writer.element('timeout', attrs={'value': unic(kw.timeout)})
        self._write_status(kw)
        self._writer.end('kw')

    def start_test(self, test):
        self._writer.start('test', {'id': test.id, 'name': test.name})

    def end_test(self, test):
        self._writer.element('doc', test.doc)
        self._write_list('tags', 'tag', test.tags)
        if test.timeout:
            self._writer.element('timeout', attrs={'value': unic(test.timeout)})
        self._write_status(test, {'critical': 'yes' if test.critical else 'no'})
        self._writer.end('test')

    def start_suite(self, suite):
        attrs = {'id': suite.id, 'name': suite.name, 'source': suite.source}
        self._writer.start('suite', attrs)

    def end_suite(self, suite):
        self._writer.element('doc', suite.doc)
        if suite.metadata:
            self._write_metadata(suite.metadata)
        self._write_status(suite)
        self._writer.end('suite')

    def _write_metadata(self, metadata):
        self._writer.start('metadata')
        for name, value in metadata.items():
            self._writer.element('item', value, {'name': name})
        self._writer.end('metadata')

    def start_statistics(self, stats):
        self._writer.start('statistics')

    def end_statistics(self, stats):
        self._writer.end('statistics')

    def start_total_statistics(self, total_stats):
        self._writer.start('total')

    def end_total_statistics(self, total_stats):
        self._writer.end('total')

    def start_tag_statistics(self, tag_stats):
        self._writer.start('tag')

    def end_tag_statistics(self, tag_stats):
        self._writer.end('tag')

    def start_suite_statistics(self, tag_stats):
        self._writer.start('suite')

    def end_suite_statistics(self, tag_stats):
        self._writer.end('suite')

    def visit_stat(self, stat):
        self._writer.element('stat', stat.name,
                             stat.get_attributes(values_as_strings=True))

    def start_errors(self, errors=None):
        self._writer.start('errors')

    def end_errors(self, errors=None):
        self._writer.end('errors')

    def _write_list(self, container_tag, item_tag, items):
        if items:
            self._writer.start(container_tag)
            for item in items:
                self._writer.element(item_tag, item)
            self._writer.end(container_tag)

    def _write_status(self, item, extra_attrs=None):
        attrs = {'status': item.status, 'starttime': item.starttime or 'N/A',
                 'endtime': item.endtime or 'N/A'}
        if not (item.starttime and item.endtime):
            attrs['elapsedtime'] = str(item.elapsedtime)
        if extra_attrs:
            attrs.update(extra_attrs)
        self._writer.element('status', item.message, attrs)
