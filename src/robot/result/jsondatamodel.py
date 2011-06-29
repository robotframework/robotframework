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

import json
from robot.result.elementhandlers import TextIndex


class DataModel(object):

    def __init__(self, robot_data):
        self._robot_data = robot_data
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
        output.write('window.output = {};\n')
        output.write(separator)
        for key, value in self._robot_data.items():
            self._write_output_element(key, output, separator, split_threshold, value)
            output.write(separator)
        self._dump_json('window.settings = ', self._settings, output)

    def _write_output_element(self, key, output, separator, split_threshold, value):
        if key == 'suite':
            splitWriter = SplittingSuiteWriter(self, output, separator,
                                               split_threshold)
            data, mapping = splitWriter.write(self._robot_data['suite'])
            self._dump_json('window.output["suite"] = ', data, output, mapping)
        elif key in ['integers', 'strings']:
            self._dump_and_split_list(key, output, separator, split_threshold)
        else:
            self._dump_json('window.output["%s"] = ' % key, value, output)

    def _dump_and_split_list(self, name, output, separator, split_threshold):
        lst = self._robot_data[name]
        output.write('window.output["%s"] = [];\n' % name)
        while lst:
            output.write(separator)
            output.write('window.output["%s"] = window.output["%s"].concat(' % (name, name))
            json.json_dump(lst[:split_threshold], output)
            output.write(');\n')
            lst = lst[split_threshold:]

    def _dump_json(self, name, data, output, mappings=None):
        output.write(name)
        json.json_dump(data, output, mappings=mappings)
        output.write(';\n')

    def remove_keywords(self):
        self._robot_data['suite'] = self._remove_keywords_from(self._robot_data['suite'])
        self._prune_unused_indices()

    # TODO: this and remove_keywords should be removed
    # instead there should be a reportify or write_for_report_to method
    def remove_errors(self):
        self._robot_data.pop('errors')

    def _remove_keywords_from(self, data):
        if not isinstance(data, list):
            return data
        return [self._remove_keywords_from(item) for item in data
                if not self._is_ignorable_keyword(item)]

    def _is_ignorable_keyword(self, item):
        # Top level teardown is kept to make tests fail if suite teardown failed
        # TODO: Could we store information about failed suite teardown otherwise?
        # TODO: Cleanup?
        return item and \
               isinstance(item, list) and \
               (isinstance(item[0], TextIndex)) and \
               self._robot_data['strings'][item[0]] in \
                        ['*kw', '*setup', '*forloop', '*foritem']

    def _prune_unused_indices(self):
        used = self._collect_used_indices(self._robot_data['suite'], set())
        remap = {}
        self._robot_data['strings'] = \
            list(self._prune(self._robot_data['strings'], used, remap))
        self._remap_indices(self._robot_data['suite'], remap)

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
            if isinstance(item, (int, long)):
                result.add(item)
            elif isinstance(item, list):
                self._collect_used_indices(item, result)
            elif isinstance(item, dict):
                self._collect_used_indices(item.values(), result)
                self._collect_used_indices(item.keys(), result)
        return result


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

    def __init__(self, writer, output, separator, split_threshold):
        self._index = 0
        self._output = output
        self._writer = writer
        self._separator = separator
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
        self._writer._dump_json(self._list_name()+' = ', result.data_block, self._output, result.mapping)
        self._write_separator()
        new_result = result.link(self._list_name())
        self._index += 1
        return new_result

    def _write_separator(self):
        self._output.write(self._separator)
