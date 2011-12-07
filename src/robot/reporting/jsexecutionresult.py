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
from robot.reporting.parsingcontext import StringIndex


class JsExecutionResult(object):

    def __init__(self, suite, statistics, errors, strings, basemillis,
                 split_results=None):
        self.suite = suite
        self.strings = strings
        self.data = self._get_data(statistics, errors, basemillis)
        self.split_results = split_results or []

    def _get_data(self, statistics, errors, basemillis):
        gentime = time.localtime()
        return {
            'stats': statistics,
            'errors': errors,
            'baseMillis': basemillis,
            'generatedMillis': long(time.mktime(gentime) * 1000) - basemillis,
            'generatedTimestamp': utils.format_time(gentime, gmtsep=' ')
        }

    def remove_data_not_needed_in_report(self):
        self.data.pop('errors')

        # TODO: All code below needs to be moved into separate object and unit tested
        self.suite = tuple(self._remove_keywords_from_suite(self.suite))
        self._remove_unused_strings()

    def _remove_keywords_from_suite(self, suite):
        for index, item in enumerate(suite):
            if index == 6:
                yield tuple(tuple(self._remove_keywords_from_suite(s)) for s in item)
            elif index == 7:
                yield tuple(tuple(self._remove_keywords_from_test(t)) for t in item)
            elif index == 8:
                yield ()
            else:
                yield item

    def _remove_keywords_from_test(self, test):
        for index, item in enumerate(test):
            yield item if index != 6 else ()

    def _remove_unused_strings(self):
        used = self._collect_used_indices(self.suite, set())
        remap = {}
        self.strings = tuple(self._get_used_strings(self.strings, used, remap))
        self.suite = tuple(self._remap_string_indices(self.suite, remap))

    def _collect_used_indices(self, data, result):
        for item in data:
            if isinstance(item, StringIndex):
                result.add(item)
            elif isinstance(item, tuple):
                self._collect_used_indices(item, result)
        return result

    def _get_used_strings(self, data, used, index_remap):
        offset = 0
        for index, text in enumerate(data):
            if index in used:
                index_remap[index] = index - offset
                yield text
            else:
                offset += 1

    def _remap_string_indices(self, data, remap):
        for item in data:
            if isinstance(item, StringIndex):
                yield remap[item]
            elif isinstance(item, tuple):
                yield tuple(self._remap_string_indices(item, remap))
            else:
                yield item
