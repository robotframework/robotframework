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

import os.path
from operator import itemgetter

from robot import utils


class Context(object):

    def __init__(self, log_path=None, split_log=False):
        self._main_text_cache = TextCache()
        self._current_texts = self._main_text_cache
        self._split_text_caches = []
        self.basemillis = 0
        self._links = {}
        self._split_log = split_log
        self.split_results = []
        self._log_path = log_path

    def get_rel_log_path(self, path):
        if path and os.path.exists(path) and self._log_path:
            return utils.get_link_path(path, os.path.dirname(self._log_path))
        return ''

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
        # Must use `long` and not `int` below due to this IronPython bug:
        # http://ironpython.codeplex.com/workitem/31549
        millis = long(round(utils.timestamp_to_secs(time, millis=True) * 1000))
        if not self.basemillis:
            self.basemillis = millis
        return millis - self.basemillis

    def start_test(self):
        if self._split_log:
            self._split_text_caches.append(TextCache())

    def end_test(self, kw_data=None):
        if self._split_log and kw_data:
            self.split_results.append((kw_data, self._split_text_caches[-1].dump()))
            return len(self.split_results)
        return kw_data

    def start_keyword(self):
        if self._split_log:
            self._current_texts = self._split_text_caches[-1]

    def end_keyword(self, split_level=False):
        if self._split_log and split_level:
            self._current_texts = self._main_text_cache

    def start_suite_setup_or_teardown(self):
        return self.start_test()

    def end_suite_setup_or_teardown(self, kw_data=None):
        return self.end_test(kw_data)

    def create_link_to_current_location(self, msg):
        self._links[self._link_key(msg)] = msg.parent.id

    def link_to(self, msg):
        return self._links[self._link_key(msg)]

    def _link_key(self, msg):
        return (msg.message, msg.level, msg.timestamp)


class TextIndex(long):

    def __str__(self):
        return long.__str__(self).rstrip('L')  # Jython adds L at the end


class TextCache(object):
    _compress_threshold = 80
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
        return utils.compress_text(text)

    def _raw(self, text):
        return '*'+text

    def dump(self):
        return [item[0] for item in sorted(self.texts.iteritems(),
                                           key=itemgetter(1))]
