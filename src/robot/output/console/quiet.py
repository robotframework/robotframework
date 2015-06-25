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

import sys

from .highlighting import HighlightingStream


class QuietOutput(object):

    def __init__(self, colors='AUTO', stderr=None):
        self._stderr = HighlightingStream(stderr or sys.__stderr__, colors)

    def message(self, msg):
        if msg.level in ('WARN', 'ERROR'):
            self._stderr.error(msg.message, msg.level)


class NoOutput(object):
    pass
