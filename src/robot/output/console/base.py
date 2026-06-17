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

import sys
from io import TextIOBase
from pathlib import Path
from typing import TYPE_CHECKING

from .highlighting import HighlightingStream
from .types import ConsoleColors, ConsoleLinks, Status

if TYPE_CHECKING:
    from robot.output import Message, ResultFile


class BaseConsole:
    """Base class for built-in console loggers that also external loggers can use.

    Writes warnings and errors to the stderr and result file paths to the stdout
    by default. That can be changed by overriding relevant methods. More
    functionality can be added by implementing needed listener interface methods.

    Public methods and attributes are part of the stable API and can be used
    by extending classes. Anything private (i.e. starting with an underscore)
    may change between releases.

    New in Robot Framework 7.5.
    """

    def __init__(
        self,
        width: int = 78,
        colors: ConsoleColors = "AUTO",
        links: ConsoleLinks = "AUTO",
        stdout: "TextIOBase | None" = None,
        stderr: "TextIOBase | None" = None,
    ):
        self.width = width
        self._stdout = HighlightingStream(stdout or sys.__stdout__, colors, links)
        self._stderr = HighlightingStream(stderr or sys.__stderr__, colors, links)

    def message(self, msg: "Message"):
        """Hook method to handle warnings and errors."""
        if msg.level in ("WARN", "ERROR") and msg.console and msg.message is not None:
            self._stderr.error(msg.message, msg.level)

    def output_file(self, path: "Path | None"):
        """Hook method to handle output files.

        Called when the output file is finished, even if the output file would
        be disabled. Calls :meth:`result_file` by default.
        """
        self.result_file("OUTPUT", path)

    def result_file(self, kind: "ResultFile", path: "Path | None"):
        """Hook method to handle other result files than the output file.

        Called when result files are finished unless they are disabled.
        """
        kind = kind.title() if kind != "XUNIT" else "XUnit"
        self.write(f"{kind + ':':9}")
        self.link(path)
        self.write("\n")

    def write(self, text: str, stderr: bool = False, flush: bool = True):
        """Write given text to stdout or stderr.

        :param text: Text to write to stdout/stderr.
        :param stderr: When true, write to stderr instead of stdout.
        :param flush: When true, stream is flushed after writing to it.
        """
        stream = self._stderr if stderr else self._stdout
        stream.write(text, flush)

    def highlight(
        self,
        status: Status,
        text: "str | None" = None,
        stderr: bool = False,
        flush: bool = True,
    ):
        """Highlight given status or text.

        :param status: Status marker.
        :param text: Text to highlight. If not given, highlights the status text.
        :param stderr: When true, write to stderr instead of stdout.
        :param flush: When true, stream is flushed after writing to it.
        """
        stream = self._stderr if stderr else self._stdout
        stream.highlight(status, text, flush)

    def link(self, path: "Path | None"):
        """Console link given path.

        If console does not support linking, write path as-is. Write "NONE"
        if path is `None`.
        """
        self._stdout.link(path)

    def clear(self):
        """Clear the current line in stdout."""
        self.write(f"\r{' ' * self.width}\r")
