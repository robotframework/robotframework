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


class NoHiglighting:
    start = end = lambda self: ''


class Higlighting:
    ANSI_RED    = '\033[31m'
    ANSI_GREEN  = '\033[32m'
    ANSI_YELLOW = '\033[33m'
    ANSI_RESET  = '\033[0m'

    _highlight_colors = {'FAIL': ANSI_RED,
                         'ERROR': ANSI_RED,
                         'WARN': ANSI_YELLOW,
                         'PASS': ANSI_GREEN}

    def __init__(self, msg):
        self._msg = msg

    def start(self):
        return self._highlight_colors[self._msg]

    def end(self):
        return self.ANSI_RESET
