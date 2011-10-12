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

import time

from robot import utils
from robot.result.jsondump import JsonDumper
from robot.result.parsingcontext import TextIndex


class DataModelWriter(object):

    _OUTPUT = 'window.output'
    _SETTINGS = 'window.settings'
    _SUITE_KEY = 'suite'
    _STRINGS_KEY = 'strings'

    def __init__(self, robot_data, split_results=None):
        self._robot_data = robot_data
        self._split_results = split_results
        self._settings = None
        self._set_generated(time.localtime())

    def _set_generated(self, timetuple):
        genMillis = long(time.mktime(timetuple) * 1000) -\
                        self._robot_data['baseMillis']
        self._set_attr('generatedMillis', genMillis)
        self._set_attr('generatedTimestamp',
                       utils.format_time(timetuple, gmtsep=' '))

    def _set_attr(self, name, value):
        self._robot_data[name] = value

    def set_settings(self, settings):
        self._settings = settings

    def write_to(self, output, separator='', split_threshold=9500):
        writer = SeparatingWriter(output, separator)
        writer.write(self._OUTPUT+' = {};\n')
        writer.separator()
        for key, value in self._robot_data.items():
            self._write_output_element(key, split_threshold, value, writer)
            writer.separator()
        writer.dump_json(self._SETTINGS+' = ', self._settings)

    def _write_output_element(self, key, split_threshold, value, writer):
        if key == self._SUITE_KEY:
            splitWriter = SplittingSuiteWriter(writer, split_threshold)
            data, mapping = splitWriter.write(self._robot_data[self._SUITE_KEY])
            writer.dump_json(self._str_out(self._SUITE_KEY)+' = ', data, mapping=mapping)
        elif key == self._STRINGS_KEY:
            self._dump_and_split_strings(split_threshold, writer)
        else:
            writer.dump_json(self._str_out(key)+' = ', value)

    def _str_out(self, key):
        return self._OUTPUT+'["%s"]' % key

    def _dump_and_split_strings(self, split_threshold, writer):
        strings = self._robot_data[self._STRINGS_KEY]
        writer.write(self._OUTPUT+'["'+self._STRINGS_KEY+'"] = [];\n')
        while strings:
            writer.separator()
            writer.dump_json(self._str_out(self._STRINGS_KEY)+' = '+self._str_out(self._STRINGS_KEY)+'.concat(', strings[:split_threshold], ');\n')
            strings = strings[split_threshold:]

    def remove_keywords(self):
        self._remove_keywords_from_suite(self._robot_data[self._SUITE_KEY])
        self._prune_unused_indices()

    # TODO: this and remove_keywords should be removed
    # instead there should be a reportify or write_for_report_to method
    def remove_errors(self):
        self._robot_data.pop('errors')

    def _remove_keywords_from_suite(self, suite):
        suite[8] = []
        for subsuite in suite[6]:
            self._remove_keywords_from_suite(subsuite)
        for test in suite[7]:
            test[-1] = []

    def _prune_unused_indices(self):
        used = self._collect_used_indices(self._robot_data[self._SUITE_KEY], set())
        remap = {}
        self._robot_data[self._STRINGS_KEY] = \
            list(self._prune(self._robot_data[self._STRINGS_KEY], used, remap))
        self._remap_indices(self._robot_data[self._SUITE_KEY], remap)

    def _prune(self, data, used, index_remap, map_index=None, offset_increment=1):
        offset = 0
        for index, text in enumerate(data):
            index = map_index(index) if map_index else index
            if index in used:
                index_remap[index] = index - offset
                yield text
            else:
                offset += offset_increment

    def _remap_indices(self, data, remap):
        for i, item in enumerate(data):
            if isinstance(item, TextIndex):
                data[i] = remap[item]
            elif isinstance(item, list):
                self._remap_indices(item, remap)

    def _collect_used_indices(self, data, result):
        for item in data:
            if isinstance(item, TextIndex):
                result.add(item)
            elif isinstance(item, list):
                self._collect_used_indices(item, result)
            elif isinstance(item, dict):
                self._collect_used_indices(item.values(), result)
                self._collect_used_indices(item.keys(), result)
        return result


class SeparatingWriter(object):

    def __init__(self, output, separator):
        self._dumper = JsonDumper(output)
        self._separator = separator

    def separator(self):
        self._dumper.write(self._separator)

    def dump_json(self, prefix, data, postfix = ';\n', mapping=None):
        if prefix:
            self.write(prefix)
        self._dumper.dump(data, mapping)
        self.write(postfix)

    def write(self, string):
        self._dumper.write(string)


class _SubResult(object):

    def __init__(self, data_block, size, mapping):
        self.data_block = data_block
        self.size = size
        self.mapping = mapping

    def update(self, subresult):
        self.data_block += [subresult.data_block]
        self.size += subresult.size
        if subresult.mapping:
            self.mapping.update(subresult.mapping)

    def link(self, name):
        key = object()
        return _SubResult(key, 1, {key:name})


class SplittingSuiteWriter(object):

    def __init__(self, writer, split_threshold):
        self._index = 0
        self._writer = writer
        self._split_threshold = split_threshold

    def write(self, data_block):
        result = self._write(data_block)
        return result.data_block, result.mapping

    def _write(self, data_block):
        if not isinstance(data_block, list):
            return _SubResult(data_block, 1, None)
        result = _SubResult([], 1, {})
        for item in data_block:
            result.update(self._write(item))
        if result.size > self._split_threshold:
            result = self._dump_suite_part(result)
        return result

    def _list_name(self):
        return 'window.sPart%s' % self._index

    def _dump_suite_part(self, result):
        self._writer.dump_json(self._list_name()+' = ', result.data_block, mapping=result.mapping)
        self._writer.separator()
        new_result = result.link(self._list_name())
        self._index += 1
        return new_result
