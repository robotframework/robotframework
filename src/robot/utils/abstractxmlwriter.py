#  Copyright 2008-2010 Nokia Siemens Networks Oyj
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


from unic import unic


# See http://www.spamagogo.com/wiki/index.php/Illegal_XML_characters
_ILLEGAL_CHARS_IN_XML = u'\x00\x01\x02\x03\x04\x05\x06\x07\x08\x0b\x0c\x0e' \
    + u'\x0f\x10\x11\x12\x13\x14\x15\x16\x17\x18\x19\x1a\x1b\x1c\x1d\x1e\x1f\ufffe'


class AbstractXmlWriter:

    def start(self, name, attributes={}, newline=True):
        raise NotImplementedError

    def content(self, content):
        raise NotImplementedError

    def end(self, name, newline=True):
        raise NotImplementedError

    def element(self, name, content=None, attributes={}, newline=True):
        self.start(name, attributes, newline=False)
        self.content(content)
        self.end(name, newline)

    def close(self):
        raise NotImplementedError

    def _encode(self, message):
        message = unic(message)
        for char in _ILLEGAL_CHARS_IN_XML:
            message = message.replace(char, '')
        return message
