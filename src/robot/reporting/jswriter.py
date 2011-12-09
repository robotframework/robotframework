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


class JsResultWriter(object):
    start_block = '<script type="text/javascript">\n'
    end_block = '</script>\n'
    split_threshold = 9500
    _output_attr = 'window.output'
    _settings_attr = 'window.settings'
    _suite_key = 'suite'
    _strings_key = 'strings'

    def __init__(self, output):
        block_separator = self.end_block + self.start_block
        self._writer = JsonWriter(output, separator=block_separator)

    def write(self, result, settings):
        self._start_output_block()
        self._write_suite(result.suite)
        self._write_strings(result.strings)
        self._write_data(result.data)
        self._write_settings(settings)
        self._end_output_block()

    def _start_output_block(self):
        self._writer.write(self.start_block)
        self._writer.write('%s = {};\n' % self._output_attr, separator=True)

    def _write_suite(self, suite):
        split_writer = SplittingSuiteWriter(self._writer, self.split_threshold)
        mapping = split_writer.write(suite)
        self._writer.write_json('%s = ' % self._output_var(self._suite_key),
                                suite, mapping=mapping, separator=True)

    def _write_strings(self, strings):
        variable = self._output_var(self._strings_key)
        self._writer.write('%s = [];\n' % variable, separator=True)
        prefix = '%s = %s.concat(' % (variable, variable)
        postfix = ');\n'
        for chunk in self._chunks(strings, self.split_threshold):
            self._writer.write_json(prefix, chunk, postfix, separator=True)

    def _write_data(self, data):
        for key in data:
            self._writer.write_json('%s = ' % self._output_var(key), data[key],
                                    separator=True)

    def _write_settings(self, settings):
        self._writer.write_json('%s = ' % self._settings_attr, settings)

    def _end_output_block(self):
        self._writer.write(self.end_block)

    def _output_var(self, key):
        return '%s["%s"]' % (self._output_attr, key)

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
