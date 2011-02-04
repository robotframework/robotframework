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


import sys

from robot import utils


class PlainStatusText:

    def __init__(self, msg):
        self._msg = msg

    def __str__(self):
        return self._msg

    def write_status(self, stream=sys.__stdout__):
        self.write(' | %s |' % self._msg, stream)

    def write_message(self, message):
        self.write('[ %s ] %s' % (self._msg, message), stream=sys.__stderr__)

    def write(self, message, newline=True, stream=sys.__stdout__):
        if newline:
            message += '\n'
        stream.write(utils.encode_output(message).replace('\t', ' '*8))
        stream.flush()


class HiglightedStatusText(PlainStatusText):
    ANSI_RED    = '\033[31m'
    ANSI_GREEN  = '\033[32m'
    ANSI_YELLOW = '\033[33m'
    ANSI_RESET  = '\033[0m'

    _highlight_colors = {'FAIL': ANSI_RED,
                         'ERROR': ANSI_RED,
                         'WARN': ANSI_YELLOW,
                         'PASS': ANSI_GREEN}

    def __init__(self, msg):
        PlainStatusText.__init__(self, msg)
        color = self._highlight_colors[self._msg]
        reset = color != '' and self.ANSI_RESET or ''
        self._msg = color + self._msg + reset
