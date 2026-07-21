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

from io import TextIOBase
from pathlib import Path
from typing import TYPE_CHECKING

from .base import BaseConsole
from .types import ConsoleColors, ResultFile

if TYPE_CHECKING:
    from robot.output import Message


class QuietConsole(BaseConsole):
    """Quiet console logger.

    Only reports warnings and errors.
    """

    def __init__(
        self,
        colors: ConsoleColors = "AUTO",
        stderr: "TextIOBase | None" = None,
    ):
        super().__init__(colors=colors, stderr=stderr)

    def result_file(self, kind: ResultFile, path: Path):
        pass


class NoneConsole(BaseConsole):
    """Totally quiet console logger.

    Does not report anything, not even warnings or errors.
    """

    def __init__(self):
        super().__init__()

    def message(self, msg: "Message"):
        pass

    def result_file(self, kind: ResultFile, path: Path):
        pass
