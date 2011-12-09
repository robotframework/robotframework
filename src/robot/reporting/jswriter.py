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
        writer = SuiteWriter(self._writer, self.split_threshold)
        writer.write(suite, self._output_var(self._suite_key))

    def _write_strings(self, strings):
        variable = self._output_var(self._strings_key)
        self._writer.write('%s = [];\n' % variable, separator=True)
        prefix = '%s = %s.concat(' % (variable, variable)
        self._write_string_chunks(prefix, strings, postfix=');\n')

    def _write_string_chunks(self, prefix, strings, postfix):
        # Optimize attribute access inside for loop
        threshold = self.split_threshold
        write_json = self._writer.write_json
        for index in xrange(0, len(strings), threshold):
            write_json(prefix, strings[index:index+threshold], postfix,
                       separator=True)

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


class SuiteWriter(object):

    def __init__(self, writer, split_threshold):
        self._writer = writer
        self._split_threshold = split_threshold

    def write(self, suite, variable):
        mapping = {}
        self._write_parts_over_threshold(suite, mapping)
        self._writer.write_json('%s = ' % variable, suite, mapping=mapping,
                                separator=True)

    def _write_parts_over_threshold(self, data, mapping):
        if not isinstance(data, tuple):
            return 1
        not_written = sum(self._write_parts_over_threshold(item, mapping)
                          for item in data)
        if not_written < self._split_threshold:
            return not_written
        self._write_part(data, mapping)
        return 1

    def _write_part(self, data, mapping):
        part_name = 'window.sPart%d' % len(mapping)
        self._writer.write_json('%s = ' % part_name, data, mapping=mapping,
                                separator=True)
        mapping[data] = part_name


class SplitLogWriter(object):

    def __init__(self, output):
        self._writer = JsonWriter(output)

    def write(self, keywords, strings, index, notify):
        self._writer.write_json('window.keywords%d = ' % index, keywords)
        self._writer.write_json('window.strings%d = ' % index, strings)
        self._writer.write('window.fileLoading.notify("%s");\n' % notify)
