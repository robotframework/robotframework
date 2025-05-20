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

from robot.utils import compress_text, html_format


class StringIndex(int):
    pass


class StringCache:
    empty = StringIndex(0)
    _compress_threshold = 80
    _use_compressed_threshold = 1.1

    def __init__(self):
        self._cache = {("", False): self.empty}

    def add(self, text, html=False):
        if not text:
            return self.empty
        key = (text, html)
        if key not in self._cache:
            self._cache[key] = StringIndex(len(self._cache))
        return self._cache[key]

    def dump(self):
        return tuple(self._encode(text, html) for text, html in self._cache)

    def _encode(self, text, html=False):
        if html:
            text = html_format(text)
        if len(text) > self._compress_threshold:
            compressed = compress_text(text)
            if len(compressed) * self._use_compressed_threshold < len(text):
                return compressed
        # Strings starting with '*' are raw, others are compressed.
        return "*" + text
