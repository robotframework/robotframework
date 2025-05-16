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

import re
from datetime import datetime

from .loggerhelper import Message, write_to_console


class StdoutLogSplitter:
    """Splits messages logged through stdout (or stderr) into Message objects"""

    _split_from_levels = re.compile(
        r"^(?:\*"
        r"(TRACE|DEBUG|INFO|CONSOLE|HTML|WARN|ERROR)"
        r"(:\d+(?:\.\d+)?)?"  # Optional timestamp
        r"\*)",
        re.MULTILINE,
    )

    def __init__(self, output):
        self._messages = list(self._get_messages(output.strip()))

    def _get_messages(self, output):
        for level, timestamp, msg in self._split_output(output):
            if level == "CONSOLE":
                write_to_console(msg.lstrip())
                level = "INFO"
            if timestamp:
                timestamp = datetime.fromtimestamp(float(timestamp[1:]) / 1000)
            yield Message(msg.strip(), level, timestamp=timestamp)

    def _split_output(self, output):
        tokens = self._split_from_levels.split(output)
        tokens = self._add_initial_level_and_time_if_needed(tokens)
        for i in range(0, len(tokens), 3):
            yield tokens[i : i + 3]

    def _add_initial_level_and_time_if_needed(self, tokens):
        if self._output_started_with_level(tokens):
            return tokens[1:]
        return ["INFO", None, *tokens]

    def _output_started_with_level(self, tokens):
        return tokens[0] == ""

    def __iter__(self):
        return iter(self._messages)

    def __len__(self):
        return len(self._messages)

    def __getitem__(self, item):
        return self._messages[item]
