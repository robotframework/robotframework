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

from robot.utils import get_timestamp, NullMarkupWriter, safe_str, XmlWriter
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
                               'rpa': 'true' if rpa else 'false',
                               'schemaversion': '3'})
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
            attrs['html'] = 'true'
        self._writer.element('msg', msg.message, attrs)

    def start_keyword(self, kw):
        attrs = {'name': kw.kwname, 'library': kw.libname}
        if kw.type != 'KEYWORD':
            attrs['type'] = kw.type
        if kw.sourcename:
            attrs['sourcename'] = kw.sourcename
        self._writer.start('kw', attrs)
        self._write_list('var', kw.assign)
        self._write_list('arg', [safe_str(a) for a in kw.args])
        self._write_list('tag', kw.tags)
        # Must be after tags to allow adding message when using --flattenkeywords.
        self._writer.element('doc', kw.doc)

    def end_keyword(self, kw):
        if kw.timeout:
            self._writer.element('timeout', attrs={'value': str(kw.timeout)})
        self._write_status(kw)
        self._writer.end('kw')

    def start_if(self, if_):
        self._writer.start('if')
        self._writer.element('doc', if_.doc)

    def end_if(self, if_):
        self._write_status(if_)
        self._writer.end('if')

    def start_if_branch(self, branch):
        self._writer.start('branch', {'type': branch.type,
                                      'condition': branch.condition})
        self._writer.element('doc', branch.doc)

    def end_if_branch(self, branch):
        self._write_status(branch)
        self._writer.end('branch')

    def start_for(self, for_):
        self._writer.start('for', {'flavor': for_.flavor})
        for name in for_.variables:
            self._writer.element('var', name)
        for value in for_.values:
            self._writer.element('value', value)
        self._writer.element('doc', for_.doc)

    def end_for(self, for_):
        self._write_status(for_)
        self._writer.end('for')

    def start_for_iteration(self, iteration):
        self._writer.start('iter')
        for name, value in iteration.variables.items():
            self._writer.element('var', value, {'name': name})
        self._writer.element('doc', iteration.doc)

    def end_for_iteration(self, iteration):
        self._write_status(iteration)
        self._writer.end('iter')

    def start_try(self, root):
        self._writer.start('try')

    def end_try(self, root):
        self._write_status(root)
        self._writer.end('try')

    def start_try_branch(self, branch):
        if branch.type == branch.EXCEPT:
            self._writer.start('branch', attrs={
                'type': 'EXCEPT', 'variable': branch.variable,
                'pattern_type': branch.pattern_type
            })
            self._write_list('pattern', branch.patterns)
        else:
            self._writer.start('branch', attrs={'type': branch.type})

    def end_try_branch(self, branch):
        self._write_status(branch)
        self._writer.end('branch')

    def start_while(self, while_):
        self._writer.start('while', attrs={
            'condition': while_.condition,
            'limit': while_.limit
        })
        self._writer.element('doc', while_.doc)

    def end_while(self, while_):
        self._write_status(while_)
        self._writer.end('while')

    def start_while_iteration(self, iteration):
        self._writer.start('iter')
        self._writer.element('doc', iteration.doc)

    def end_while_iteration(self, iteration):
        self._write_status(iteration)
        self._writer.end('iter')

    def start_return(self, return_):
        self._writer.start('return')
        for value in return_.values:
            self._writer.element('value', value)

    def end_return(self, return_):
        self._write_status(return_)
        self._writer.end('return')

    def start_continue(self, continue_):
        self._writer.start('continue')

    def end_continue(self, continue_):
        self._write_status(continue_)
        self._writer.end('continue')

    def start_break(self, break_):
        self._writer.start('break')

    def end_break(self, break_):
        self._write_status(break_)
        self._writer.end('break')

    def start_test(self, test):
        self._writer.start('test', {'id': test.id, 'name': test.name,
                                    'line': str(test.lineno or '')})

    def end_test(self, test):
        self._writer.element('doc', test.doc)
        self._write_list('tag', test.tags)
        if test.timeout:
            self._writer.element('timeout', attrs={'value': str(test.timeout)})
        self._write_status(test)
        self._writer.end('test')

    def start_suite(self, suite):
        attrs = {'id': suite.id, 'name': suite.name, 'source': suite.source}
        self._writer.start('suite', attrs)

    def end_suite(self, suite):
        self._writer.element('doc', suite.doc)
        for name, value in suite.metadata.items():
            self._writer.element('meta', value, {'name': name})
        self._write_status(suite)
        self._writer.end('suite')

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

    def _write_list(self, tag, items):
        for item in items:
            self._writer.element(tag, item)

    def _write_status(self, item):
        attrs = {'status': item.status, 'starttime': item.starttime or 'N/A',
                 'endtime': item.endtime or 'N/A'}
        if not (item.starttime and item.endtime):
            attrs['elapsedtime'] = str(item.elapsedtime)
        self._writer.element('status', item.message, attrs)
