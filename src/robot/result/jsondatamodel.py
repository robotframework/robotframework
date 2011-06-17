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
import json


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

    def write_to(self, output):
        # TODO! Clean this method!
        # TODO! Should find a better solution to script too big problems
        # This has the initial solution to IE / Firefox script too big problems
        # It splits suite to smaller script parts
        strings = self._robot_data['strings']
        suite = self._robot_data['suite']
        del self._robot_data['strings']
        del self._robot_data['suite']
        self._dump_json('window.output = ', self._robot_data, output)
        if self._settings:
            self._dump_json('window.settings = ', self._settings, output)
        output.write('</script>\n<script type="text/javascript">\n')
        self._dump_json('window.output["strings"] = ', strings, output)
        output.write('window.output["suite"] = [];\n')
        for i, suite_elem in enumerate(suite):
            output.write('</script>\n<script type="text/javascript">\n')
            self._dump_json('window.output["suite"]['+str(i)+'] = ', suite_elem, output)
            output.write('</script>\n<script type="text/javascript">\n')
        self._robot_data['strings'] = strings
        self._robot_data['suite'] = suite

    def _dump_json(self, name, data, output):
        output.write(name)
        json.json_dump(data, output)
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
        return isinstance(item, list) and item and item[0] in ['kw', 'setup', 'forloop', 'foritem']

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


