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

import zlib
import base64
from operator import itemgetter

from robot import utils


class Context(object):

    def __init__(self, split_tests=False):
        self._main_text_cache = TextCache()
        self._current_texts = self._main_text_cache
        self._split_text_caches = []
        self._basemillis = 0
        self._stats = Stats()
        self._location = Location()
        self._links = {}
        self._split_tests = split_tests
        self._split_results = []

    @property
    def basemillis(self):
        return self._basemillis

    @property
    def split_results(self):
        return self._split_results

    def collect_stats(self):
        self._stats = self._stats.new_child()
        return self

    def dump_stats(self):
        stats = self._stats
        self._stats = self._stats.parent
        return stats

    def get_id(self, value):
        if value is None:
            return None
        if isinstance(value, basestring):
            return self._get_text_id(value)
        if isinstance(value, (int, long)):
            return value
        raise TypeError('Unsupported type %s' % type(value))

    def _get_text_id(self, text):
        return self._current_texts.add(text)

    def dump_texts(self):
        return self._current_texts.dump()

    def timestamp(self, time):
        if time == 'N/A':
            return None
        millis = int(utils.timestamp_to_secs(time, millis=True) * 1000)
        if not self._basemillis:
            self._basemillis = millis
        return millis - self.basemillis

    def start_suite(self, name):
        self._location.start_suite()

    def end_suite(self):
        self._location.end_suite()

    def start_test(self, name):
        if self._split_tests:
            self._split_text_caches.append(TextCache())
        self._location.start_test()

    def end_test(self, kw_data=None):
        self._location.end_test()
        if self._split_tests:
            self._split_results.append((kw_data, self._split_text_caches[-1].dump()))
            return len(self._split_results)
        return kw_data

    def start_keyword(self):
        if self._split_tests and self._location.on_test_level:
            self._current_texts = self._split_text_caches[-1]
        self._location.start_keyword()

    def end_keyword(self):
        self._location.end_keyword()
        if self._split_tests and self._location.on_test_level:
            self._current_texts = self._main_text_cache

    def create_link_to_current_location(self, key):
        self._links[tuple(key)] = self._location.current_id

    def link_to(self, key):
        return self._links[tuple(key)]

    def add_test(self, critical, passed):
        self._stats.add_test(critical, passed)

    def teardown_failed(self):
        self._stats.fail_all()


class Stats(object):

    def __init__(self, parent=None):
        self.parent = parent
        self.all = 0
        self.all_passed = 0
        self.critical = 0
        self.critical_passed = 0
        self._children = []

    def new_child(self):
        self._children.append(Stats(self))
        return self._children[-1]

    def add_test(self, critical, passed):
        self._update_stats(critical, passed)
        if self.parent:
            self.parent.add_test(critical, passed)

    def _update_stats(self, critical, passed):
        self.all += 1
        if passed:
            self.all_passed += 1
        if critical:
            self.critical += 1
        if critical and passed:
            self.critical_passed += 1

    def fail_all(self):
        # FIXME: Parent stats must be updated recursively!!!!!!!!
        # TODO: See above FIXME!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        self.all_passed = 0
        self.critical_passed = 0
        for child in self._children:
            child.fail_all()

    def __iter__(self):
        return iter([self.all, self.all_passed,
                     self.critical, self.critical_passed])

    def __len__(self):
        return 4


class Location(object):

    def __init__(self):
        self._ids = []
        self._suite_indices = [1]
        self._test_indices = []
        self._kw_indices = []

    def start_suite(self):
        self._start('s', self._suite_indices, self._test_indices,
                    self._kw_indices)

    def start_test(self):
        self._start('t', self._test_indices, self._kw_indices)

    def start_keyword(self):
        self._start('k', self._kw_indices)

    def _start(self, type, *indices):
        started = indices[0]
        self._ids.append('%s%d' % (type, started[-1]))
        started[-1] += 1
        for ind in indices:
            ind.append(1)

    def end_suite(self):
        self._end(self._suite_indices, self._test_indices, self._kw_indices)

    def end_test(self):
        self._end(self._test_indices, self._kw_indices)

    def end_keyword(self):
        self._end(self._kw_indices)

    def _end(self, *indices):
        self._ids.pop()
        for ind in indices:
            ind.pop()

    @property
    def on_test_level(self):
        return self._ids[-1][0] == 't'

    @property
    def current_id(self):
        return '-'.join(self._ids)


class TextIndex(long):
    pass


class TextCache(object):
    # TODO: Tune compressing thresholds
    _compress_threshold = 20
    _use_compressed_threshold = 1.1

    def __init__(self):
        self.texts = {'*': TextIndex(0)}
        self.index = 1

    def add(self, text):
        if not text:
            return TextIndex(0)
        text = self._encode(text)
        if text not in self.texts:
            self.texts[text] = TextIndex(self.index)
            self.index += 1
        return self.texts[text]

    def _encode(self, text):
        raw = self._raw(text)
        if raw in self.texts or len(raw) < self._compress_threshold:
            return raw
        compressed = self._compress(text)
        if len(compressed) * self._use_compressed_threshold < len(raw):
            return compressed
        return raw

    def _compress(self, text):
        return base64.b64encode(zlib.compress(text.encode('UTF-8'), 9))

    def _raw(self, text):
        return '*'+text

    def dump(self):
        # TODO: Could we yield or return an iterator?
        return [item[0] for item in sorted(self.texts.iteritems(),
                                           key=itemgetter(1))]

