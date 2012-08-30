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

from robot.errors import DataError
from robot.utils import XmlWriter, NullMarkupWriter, get_timestamp, unic
from robot.version import get_full_version

from .loggerhelper import IsLogged


class XmlLogger(object):

    def __init__(self, path, log_level='TRACE', generator='Robot'):
        self._log_message_is_logged = IsLogged(log_level)
        self._error_message_is_logged = IsLogged('WARN')
        self._writer = self._get_writer(path, generator)
        self._errors = []

    def _get_writer(self, path, generator):
        if path == 'NONE':
            return NullMarkupWriter()
        try:
            writer = XmlWriter(path, encoding='UTF-8')
        except EnvironmentError, err:
            raise DataError("Opening output file '%s' failed: %s" %
                            (path, err.strerror))
        writer.start('robot', {'generator': get_full_version(generator),
                               'generated': get_timestamp()})
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
        self._writer.start('kw', {'name': kw.name, 'type': kw.type,
                                  'timeout': str(kw.timeout)})
        self._writer.element('doc', kw.doc)
        self._write_list('arguments', 'arg', (unic(a) for a in kw.args))

    def end_keyword(self, kw):
        self._write_status(kw)
        self._writer.end('kw')

    def start_test(self, test):
        self._writer.start('test', {'id': test.id, 'name': test.name,
                                    'timeout': str(test.timeout)})

    def end_test(self, test):
        self._writer.element('doc', test.doc)
        self._write_list('tags', 'tag', test.tags)
        self._write_status(test, test.message,
                           {'critical': 'yes' if test.critical else 'no'})
        self._writer.end('test')

    def start_suite(self, suite):
        attrs = {'id': suite.id, 'name': suite.name}
        if suite.source:
            attrs['source'] = suite.source
        self._writer.start('suite', attrs)

    def end_suite(self, suite):
        self._writer.element('doc', suite.doc)
        self._writer.start('metadata')
        for name, value in suite.metadata.items():
            self._writer.element('item', value, {'name': name})
        self._writer.end('metadata')
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
        self._stat(stat, stat.longname,
                   attrs={'id': stat.id, 'name': stat.name})

    def tag_stat(self, stat):
        self._stat(stat, attrs={'info': self._get_tag_stat_info(stat),
                                'links': self._get_tag_links(stat),
                                'doc': stat.doc,
                                'combined': stat.combined})

    def _get_tag_links(self, stat):
        return ':::'.join(':'.join([title, url]) for url, title in stat.links)

    def _stat(self, stat, name=None, attrs=None):
        attrs = attrs or {}
        attrs['pass'] = str(stat.passed)
        attrs['fail'] = str(stat.failed)
        self._writer.element('stat', name or stat.name, attrs)

    def _get_tag_stat_info(self, stat):
        if stat.critical:
            return 'critical'
        if stat.non_critical:
            return 'non-critical'
        if stat.combined:
            return 'combined'
        return ''

    def start_errors(self):
        self._writer.start('errors')

    def end_errors(self):
        self._writer.end('errors')

    def _write_list(self, container_tag, item_tag, items):
        self._writer.start(container_tag)
        for item in items:
            self._writer.element(item_tag, item)
        self._writer.end(container_tag)

    def _write_status(self, item, message=None, extra_attrs=None):
        attrs = {'status': item.status, 'starttime': item.starttime or 'N/A',
                 'endtime': item.endtime or 'N/A'}
        if not (item.starttime and item.endtime):
            attrs['elapsedtime'] = str(item.elapsedtime)
        if extra_attrs:
            attrs.update(extra_attrs)
        self._writer.element('status', message, attrs)
