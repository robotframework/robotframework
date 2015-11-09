#  Copyright 2008-2015 Nokia Solutions and Networks
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

from robot.utils import OrderedDict, compress_text


class StringIndex(int):
    pass


class StringCache(object):
    _compress_threshold = 80
    _use_compressed_threshold = 1.1
    _zero_index = StringIndex(0)

    def __init__(self):
        self._cache = OrderedDict({'*': self._zero_index})

    def add(self, text):
        if not text:
            return self._zero_index
        text = self._encode(text)
        if text not in self._cache:
            self._cache[text] = StringIndex(len(self._cache))
        return self._cache[text]

    def _encode(self, text):
        raw = self._raw(text)
        if raw in self._cache or len(raw) < self._compress_threshold:
            return raw
        compressed = compress_text(text)
        if len(compressed) * self._use_compressed_threshold < len(raw):
            return compressed
        return raw

    def _raw(self, text):
        return '*'+text

    def dump(self):
        return tuple(self._cache)
