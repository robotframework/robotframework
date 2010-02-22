#  Copyright 2008-2009 Nokia Siemens Networks Oyj
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


from robottypes import unic


# See http://www.spamagogo.com/wiki/index.php/Illegal_XML_characters
_ILLEGAL_CHARS_IN_XML = [ u'\x00', u'\x01', u'\x02', u'\x03', u'\x04', u'\x05',
                          u'\x06', u'\x07', u'\x08', u'\x0b', u'\x0c', u'\x0e',
                          u'\x0f', u'\x10', u'\x11', u'\x12', u'\x13', u'\x14',
                          u'\x15', u'\x16', u'\x17', u'\x18', u'\x19', u'\x1a',
                          u'\x1b', u'\x1c', u'\x1d', u'\x1e', u'\x1f' ]


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
