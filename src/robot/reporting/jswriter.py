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

from robot.htmldata import JsonWriter


class JsResultWriter:
    _output_attr = "window.output"
    _settings_attr = "window.settings"
    _suite_key = "suite"
    _strings_key = "strings"

    def __init__(
        self,
        output,
        start_block='<script type="text/javascript">\n',
        end_block="</script>\n",
        split_threshold=9500,
    ):
        writer = JsonWriter(output, separator=end_block + start_block)
        self._write = writer.write
        self._write_json = writer.write_json
        self._start_block = start_block
        self._end_block = end_block
        self._split_threshold = split_threshold

    def write(self, result, settings):
        self._start_output_block()
        self._write_suite(result.suite)
        self._write_strings(result.strings)
        self._write_data(result.data)
        self._write_settings_and_end_output_block(settings)

    def _start_output_block(self):
        self._write(self._start_block, postfix="", separator=False)
        self._write(f"{self._output_attr} = {{}}")

    def _write_suite(self, suite):
        writer = SuiteWriter(self._write_json, self._split_threshold)
        writer.write(suite, self._output_var(self._suite_key))

    def _write_strings(self, strings):
        variable = self._output_var(self._strings_key)
        self._write(f"{variable} = []")
        prefix = f"{variable} = {variable}.concat("
        postfix = ");\n"
        threshold = self._split_threshold
        for index in range(0, len(strings), threshold):
            self._write_json(prefix, strings[index : index + threshold], postfix)

    def _write_data(self, data):
        for key in data:
            self._write_json(f"{self._output_var(key)} = ", data[key])

    def _write_settings_and_end_output_block(self, settings):
        self._write_json(f"{self._settings_attr} = ", settings, separator=False)
        self._write(self._end_block, postfix="", separator=False)

    def _output_var(self, key):
        return f'{self._output_attr}["{key}"]'


class SuiteWriter:

    def __init__(self, write_json, split_threshold):
        self._write_json = write_json
        self._split_threshold = split_threshold

    def write(self, suite, variable):
        mapping = {}
        self._write_parts_over_threshold(suite, mapping)
        self._write_json(f"{variable} = ", suite, mapping=mapping)

    def _write_parts_over_threshold(self, data, mapping):
        if not isinstance(data, tuple):
            return 1
        not_written = 1
        for item in data:
            not_written += self._write_parts_over_threshold(item, mapping)
        if not_written > self._split_threshold:
            self._write_part(data, mapping)
            return 1
        return not_written

    def _write_part(self, data, mapping):
        part_name = f"window.sPart{len(mapping)}"
        self._write_json(f"{part_name} = ", data, mapping=mapping)
        mapping[data] = part_name


class SplitLogWriter:

    def __init__(self, output):
        self._writer = JsonWriter(output)

    def write(self, keywords, strings, index, notify):
        self._writer.write_json(f"window.keywords{index} = ", keywords)
        self._writer.write_json(f"window.strings{index} = ", strings)
        self._writer.write(f'window.fileLoading.notify("{notify}")')
