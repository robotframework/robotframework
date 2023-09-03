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

import time

from .stringcache import StringIndex


class JsExecutionResult:

    def __init__(self, suite, statistics, errors, strings, basemillis=None,
                 split_results=None, min_level=None, expand_keywords=None):
        self.suite = suite
        self.strings = strings
        self.min_level = min_level
        self.data = self._get_data(statistics, errors, basemillis or 0, expand_keywords)
        self.split_results = split_results or []

    def _get_data(self, statistics, errors, basemillis, expand_keywords):
        return {'stats': statistics,
                'errors': errors,
                'baseMillis': basemillis,
                'generated': int(time.time() * 1000) - basemillis,
                'expand_keywords': expand_keywords}

    def remove_data_not_needed_in_report(self):
        self.data.pop('errors')
        remover = _KeywordRemover()
        self.suite = remover.remove_keywords(self.suite)
        self.suite, self.strings = remover.remove_unused_strings(self.suite, self.strings)


class _KeywordRemover:

    def remove_keywords(self, suite):
        return self._remove_keywords_from_suite(suite)

    def _remove_keywords_from_suite(self, suite):
        return suite[:6] + (self._remove_keywords_from_suites(suite[6]),
                            self._remove_keywords_from_tests(suite[7]),
                            (), suite[9])

    def _remove_keywords_from_suites(self, suites):
        return tuple(self._remove_keywords_from_suite(s) for s in suites)

    def _remove_keywords_from_tests(self, tests):
        return tuple(self._remove_keywords_from_test(t) for t in tests)

    def _remove_keywords_from_test(self, test):
        return test[:-1] + ((),)

    def remove_unused_strings(self, model, strings):
        used = set(self._get_used_indices(model))
        remap = {}
        strings = tuple(self._get_used_strings(strings, used, remap))
        model = tuple(self._remap_string_indices(model, remap))
        return model, strings

    def _get_used_indices(self, model):
        for item in model:
            if isinstance(item, StringIndex):
                yield item
            elif isinstance(item, tuple):
                for i in self._get_used_indices(item):
                    yield i

    def _get_used_strings(self, strings, used_indices, remap):
        offset = 0
        for index, string in enumerate(strings):
            if index in used_indices:
                remap[index] = index - offset
                yield string
            else:
                offset += 1

    def _remap_string_indices(self, model, remap):
        for item in model:
            if isinstance(item, StringIndex):
                yield remap[item]
            elif isinstance(item, tuple):
                yield tuple(self._remap_string_indices(item, remap))
            else:
                yield item
