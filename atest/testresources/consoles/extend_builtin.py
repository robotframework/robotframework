from pathlib import Path

from robot import result, running
from robot.api.console import (
    BaseConsole, DottedConsole, NoneConsole, QuietConsole, ResultFile, VerboseConsole
)


class ExtendBase(BaseConsole):

    def start_suite(self, data: running.TestSuite, result: result.TestSuite):
        self.write(f"BASE: {result.name}\n")

    def result_file(self, kind: ResultFile, path: "Path | None"):
        self.write(f"{kind.title()}: {path.name if path else 'None'}\n")


class ExtendQuiet(QuietConsole):

    def start_suite(self, data: running.TestSuite, result: result.TestSuite):
        self.write(f"QUIET: {result.name}\n")


class ExtendNone(NoneConsole):

    def start_suite(self, data: running.TestSuite, result: result.TestSuite):
        self.write(f"NONE: {result.name}\n")


class ExtendDotted(DottedConsole):

    def start_suite(self, data: running.TestSuite, result: result.TestSuite):
        self.write(f"DOTTED: {result.name}\n")

    def end_suite(self, data: running.TestSuite, result: result.TestSuite):
        self.write("\n")

    def result_file(self, kind: ResultFile, path: "Path | None"):
        self.write(f"{kind.title()}: {path.name if path else 'None'}\n")


class ExtendVerbose(VerboseConsole):

    def start_suite(self, data: running.TestSuite, result: result.TestSuite):
        self.write(f"VERBOSE: {result.name}\n")

    def info(self, name: str, doc: str, start_suite: bool = False):
        super().info(name, "Overwrite!", start_suite)
