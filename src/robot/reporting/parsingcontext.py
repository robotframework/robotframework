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

from operator import itemgetter

from robot.utils import compress_text


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
        compressed = compress_text(text)
        if len(compressed) * self._use_compressed_threshold < len(raw):
            return compressed
        return raw

    def _raw(self, text):
        return '*'+text

    def dump(self):
        return tuple(item[0] for item in sorted(self.texts.iteritems(),
                                                key=itemgetter(1)))
