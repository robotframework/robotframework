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

    def __init__(self, separator, split_threshold=9500):
        self._separator = separator
        self._split_threshold = split_threshold

    def write_to(self, output, model, config):
        writer = JsonWriter(output, self._separator)
        writer.write('%s = {};\n' % self._output)
        writer.separator()
        self._write_suite(writer, model.suite)
        writer.separator()
        self._write_strings(model.strings, writer)
        writer.separator()
        for key, value in model.data.items():
            writer.write_json('%s = ' % self._output_var(key), value)
            writer.separator()
        writer.write_json('%s = ' % self._settings, config)

    def _write_suite(self, writer, suite):
        split_writer = SplittingSuiteWriter(writer, self._split_threshold)
        mapping = split_writer.write(suite)
        writer.write_json('%s = ' % self._output_var(self._suite_key),
                         suite, mapping=mapping)

    def _output_var(self, key):
        return '%s["%s"]' % (self._output, key)

    def _write_strings(self, strings, writer):
        variable = self._output_var(self._strings_key)
        writer.write('%s = [];\n' % variable)
        prefix = '%s = %s.concat(' % (variable, variable)
        postfix = ');\n'
        for chunk in self._chunks(strings, self._split_threshold):
            writer.separator()
            writer.write_json(prefix, chunk, postfix)

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
