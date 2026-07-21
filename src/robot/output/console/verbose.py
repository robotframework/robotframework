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
from typing import TYPE_CHECKING

from robot.errors import DataError
from robot.utils import (
    get_console_length, getshortdoc, isatty, pad_console_length, validate_literal
)

from .base import BaseConsole
from .types import ConsoleColors, ConsoleLinks, ConsoleMarkers, Status

if TYPE_CHECKING:
    from robot import output, result, running


class VerboseConsole(BaseConsole):
    """Verbose console logger.

    Reports started suites and tests separately.
    """

    status_length = len("| PASS |")

    def __init__(
        self,
        width: int = 78,
        colors: ConsoleColors = "AUTO",
        links: ConsoleLinks = "AUTO",
        markers: ConsoleMarkers = "AUTO",
        stdout: "TextIOBase | None" = None,
        stderr: "TextIOBase | None" = None,
    ):
        super().__init__(width, colors, links, stdout, stderr)
        self.test_started = False
        self.keywords_started = 0
        self.markers_enabled = self._markers_enabled(markers)
        self.marker_count = 0
        self.current_info = ""

    def _markers_enabled(self, markers: ConsoleMarkers) -> bool:
        try:
            markers = validate_literal(markers, ConsoleMarkers, "console marker")
        except ValueError as err:
            raise DataError(str(err))
        return markers == "AUTO" and isatty(self._stdout.stream) or markers == "ON"

    def start_suite(self, data: "running.TestSuite", result: "result.TestSuite"):
        if not result.parent:
            self.suite_separator()
        self.info(result.full_name, result.doc, start_suite=True)
        self.suite_separator()

    def end_suite(self, data: "running.TestSuite", result: "result.TestSuite"):
        self.info(result.full_name, result.doc)
        self.status(result.status, result.full_message)
        self.suite_separator()

    def start_test(self, data: "running.TestCase", result: "result.TestCase"):
        self.test_started = True
        self.info(result.name, result.doc)

    def end_test(self, data: "running.TestCase", result: "result.TestCase"):
        self.status(result.status, result.message)
        self.test_separator()
        self.test_started = False

    def start_body_item(self, data, result):
        self.keywords_started += 1

    def end_body_item(self, data, result):
        self.keywords_started -= 1
        if self.test_started and not self.keywords_started:
            self.marker(result.status)

    def message(self, msg: "output.Message"):
        if self.marker_count:
            self.clear()
            super().message(msg)
            self.write(self.current_info)
            self.marker_count = 0
        else:
            super().message(msg)

    def suite_separator(self):
        """Write suite separator."""
        self.write(f"{'=' * self.width}\n")

    def test_separator(self):
        """Write test separator."""
        self.write(f"{'-' * self.width}\n")

    def info(self, name: str, doc: str, start_suite: bool = False):
        """Write info about started or ended suite or test."""
        if start_suite:
            width = self.width
            separator = "\n"
        else:
            width = self.width - self.status_length - 1
            separator = " "
        if doc and get_console_length(name) < width:
            info = f"{name} :: {getshortdoc(doc, linesep=' ')}"
        else:
            info = name
        self.current_info = pad_console_length(info, width) + separator
        self.write(self.current_info)
        self.marker_count = 0

    def status(self, status: Status, message: str):
        """Write status information."""
        if self.marker_count:
            self._clear_markers()
        self.write("| ", flush=False)
        self.highlight(status, flush=False)
        self.write(" |\n")
        if message:
            self.write(message.strip() + "\n")

    def marker(self, status: str):
        """Write marker when a top level keyword is started."""
        if self.markers_enabled:
            if self.marker_count == self.status_length:
                self._clear_markers()
            marker, status = (".", "PASS") if status != "FAIL" else ("F", "FAIL")
            self.highlight(status, marker)
            self.marker_count += 1

    def _clear_markers(self):
        self.clear()
        self.write(self.current_info)
        self.marker_count = 0
