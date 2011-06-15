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

from elementhandlers import TextIndex

class DataModel(object):

    def __init__(self, robot_data):
        self._robot_data = robot_data

    def set_generated(self, timetuple):
        self._robot_data['generatedMillis'] = long(time.mktime(timetuple))*1000-self._robot_data['baseMillis']
        self._robot_data['generatedTimestamp'] = utils.format_time(timetuple, daytimesep='&nbsp;', gmtsep='&nbsp;')

    def write_to(self, output):
        output.write('window.output = ')
        json_dump(self._robot_data, output)
        output.write(';\n')

    def remove_keywords(self):
        self._robot_data['suite'] = self._remove_keywords_from(self._robot_data['suite'])
        self._prune_unused_texts()

    def _remove_keywords_from(self, data):
        if not isinstance(data, list):
            return data
        return [self._remove_keywords_from(item) for item in data
                if not self._is_ignorable_keyword(item)]

    def _is_ignorable_keyword(self, item):
        # Top level teardown is kept to make tests fail if suite teardown failed
        # TODO: Could we store information about failed suite teardown otherwise?
        return isinstance(item, list) and item and item[0] in ['kw', 'setup']

    def _prune_unused_texts(self):
        used = self._collect_used_text_indices(self._robot_data['suite'], set())
        self._robot_data['strings'] = [text if index in used else '' for index, text in enumerate(self._robot_data['strings'])]

    def _collect_used_text_indices(self, data, result):
        for item in data:
            if isinstance(item, TextIndex):
                result.add(item)
            elif isinstance(item, list):
                self._collect_used_text_indices(item, result)
            elif isinstance(item, dict):
                self._collect_used_text_indices(item.values(), result)
        return result

def encode_basestring(string):
    def get_matching_char(c):
        val = ord(c)
        if val < 127 and val > 31:
            return c
        return '\\u' + hex(val)[2:].rjust(4,'0')
    string = string.replace('\\', '\\\\')
    string = string.replace('"', '\\"')
    string = string.replace('\b', '\\b')
    string = string.replace('\f', '\\f')
    string = string.replace('\n', '\\n')
    string = string.replace('\r', '\\r')
    string = string.replace('\t', '\\t')
    result = []
    for c in string:
        result += [get_matching_char(c)]
    return '"'+''.join(result)+'"'

def json_dump(data, output):
    if data is None:
        output.write('null')
    elif isinstance(data, int):
        output.write(str(data))
    elif isinstance(data, long):
        output.write(str(data))
    elif isinstance(data, basestring):
        output.write(encode_basestring(data))
    elif isinstance(data, list):
        output.write('[')
        for index, item in enumerate(data):
            json_dump(item, output)
            if index < len(data)-1:
                output.write(',')
        output.write(']')
    elif type(data) == dict:
        output.write('{')
        for index, item in enumerate(data.items()):
            json_dump(item[0], output)
            output.write(':')
            json_dump(item[1], output)
            if index < len(data)-1:
                output.write(',')
        output.write('}')
    else:
        raise Exception('Data type (%s) serialization not supported' % type(data))
