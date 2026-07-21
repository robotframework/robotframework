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

from robot.utils import plural_or_not as s, secs_to_timestr

from .base import BaseConsole
from .types import ConsoleColors, ConsoleLinks

if TYPE_CHECKING:
    from robot import result, running


class DottedConsole(BaseConsole):
    """Dotted console logger.

    Reports each test with "." (PASS), "F" (FAIL) or "s" (SKIP).
    """

    def __init__(
        self,
        width: int = 78,
        colors: ConsoleColors = "AUTO",
        links: ConsoleLinks = "AUTO",
        stdout: "TextIOBase | None" = None,
        stderr: "TextIOBase | None" = None,
    ):
        super().__init__(width, colors, links, stdout, stderr)
        self.markers_on_row = 0

    def start_suite(self, data: "running.TestSuite", result: "result.TestSuite"):
        if not data.parent:
            count = data.test_count
            ts = ("test" if not data.rpa else "task") + s(count)
            self.write(f"Running suite '{result.name}' with {count} {ts}.\n")
            self.write("=" * self.width + "\n")

    def end_test(self, data: "running.TestCase", result: "result.TestCase"):
        if self.markers_on_row == self.width:
            self.write("\n")
            self.markers_on_row = 0
        self.markers_on_row += 1
        if result.passed:
            self.write(".")
        elif result.skipped:
            self.highlight("SKIP", "s")
        elif result.tags.robot("exit"):
            self.write("x")
        else:
            self.highlight("FAIL", "F")

    def end_suite(self, data: "running.TestSuite", result: "result.TestSuite"):
        if not data.parent:
            self.write("\n")
            self.report_failures(result)
            self.report_status(result)
            self.write("\n")

    def report_failures(self, suite: "result.TestSuite"):
        """Reports failed tests."""
        for test in suite.all_tests:
            if test.failed and not test.tags.robot("exit"):
                self.write(f"{'-' * self.width}\n")
                self.highlight("FAIL")
                self.write(f": {test.full_name}\n{test.message.strip()}\n")

    def report_status(self, suite: "result.TestSuite"):
        """Reports overall status."""
        stats = suite.statistics
        ts = ("test" if not suite.rpa else "task") + s(stats.total)
        elapsed = secs_to_timestr(suite.elapsed_time)
        self.write(
            f"{'=' * self.width}\n"
            f"Run suite '{suite.name}' with {stats.total} {ts} in {elapsed}.\n\n"
        )
        ed = "ED" if suite.status != "SKIP" else "PED"
        self.highlight(suite.status, suite.status + ed)
        self.write(f"\n{stats.message}\n")
