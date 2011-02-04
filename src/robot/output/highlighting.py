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

import os
import sys

if os.sep == '\\':
    from doshighlighting import DosHiglighter


class Highlighter:

    def __init__(self, colors):
        self._current = None
        self._highlighters = {
            sys.__stdout__: self._get_highlighter(sys.__stdout__, colors),
            sys.__stderr__: self._get_highlighter(sys.__stderr__, colors)
        }

    def start(self, message, stream=sys.__stdout__):
        self._current = self._highlighters[stream]
        if not self._current:
            return
        {'PASS': self._current.green, 'FAIL': self._current.red,
         'ERROR': self._current.red, 'WARN': self._current.yellow}[message]()

    def end(self):
        if self._current:
            self._current.reset()

    def _get_highlighter(self, stream, colors):
        if not colors:
            return None
        HL = UnixHiglighter if os.sep == '/' else DosHiglighter
        return HL(stream)


class UnixHiglighter:
    _ANSI_GREEN  = '\033[32m'
    _ANSI_RED = '\033[31m'
    _ANSI_YELLOW = '\033[33m'
    _ANSI_RESET = '\033[0m'

    def __init__(self, stream):
        self._stream = stream

    def green(self):
        self._stream.write(self._ANSI_GREEN)

    def red(self):
        self._stream.write(self._ANSI_RED)

    def yellow(self):
        self._stream.write(self._ANSI_YELLOW)

    def reset(self):
        self._stream.write(self.ANSI_RESET)
