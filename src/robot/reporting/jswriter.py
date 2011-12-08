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

from .jsonwriter import JsonWriter


class ScriptBlockWriter(object):
    _output = 'window.output'
    _settings = 'window.settings'
    _suite_key = 'suite'
    _strings_key = 'strings'

    def __init__(self, output, separator, split_threshold=9500):
        self._writer = JsonWriter(output, separator)
        self._split_threshold = split_threshold

    def write(self, model, config):
        self._start_output_block()
        self._write_suite(model.suite)
        self._write_strings(model.strings)
        self._write_data(model.data)
        self._write_config(config)

    def _start_output_block(self):
        self._writer.write('%s = {};\n' % self._output, separator=True)

    def _write_suite(self, suite):
        split_writer = SplittingSuiteWriter(self._writer, self._split_threshold)
        mapping = split_writer.write(suite)
        self._writer.write_json('%s = ' % self._output_var(self._suite_key),
                                suite, mapping=mapping, separator=True)

    def _write_strings(self, strings):
        variable = self._output_var(self._strings_key)
        self._writer.write('%s = [];\n' % variable, separator=True)
        prefix = '%s = %s.concat(' % (variable, variable)
        postfix = ');\n'
        for chunk in self._chunks(strings, self._split_threshold):
            self._writer.write_json(prefix, chunk, postfix, separator=True)

    def _write_data(self, data):
        for key in data:
            self._writer.write_json('%s = ' % self._output_var(key), data[key],
                                    separator=True)

    def _write_config(self, config):
        self._writer.write_json('%s = ' % self._settings, config)

    def _output_var(self, key):
        return '%s["%s"]' % (self._output, key)

    def _chunks(self, iterable, chunk_size):
        for index in xrange(0, len(iterable), chunk_size):
            yield iterable[index:index+chunk_size]



#TODO: Naming
class SplittingSuiteWriter(object):

    def __init__(self, writer, split_threshold):
        self._index = 0
        self._writer = writer
        self._split_threshold = split_threshold

    def write(self, data_block):
        mapping = {}
        self._write(data_block, mapping)
        return mapping

    def _write(self, data, mapping, size=1):
        if not isinstance(data, tuple):
            return size
        for item in data:
            size += self._write(item, mapping)
        if size > self._split_threshold:
            self._dump_suite_part(mapping, data)
            return 1
        return size

    @property
    def _list_name(self):
        return 'window.sPart%d' % self._index

    def _dump_suite_part(self, mapping, data_block):
        self._writer.write_json(self._list_name+' = ', data_block,
                               mapping=mapping)
        self._writer.separator()
        mapping[data_block] = self._list_name
        self._index += 1
