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

# Windows highlighting code adapted from color_console.py. It is copyright
# Andre Burgaud, licensed under the MIT License, and available here:
# http://www.burgaud.com/bring-colors-to-the-windows-console-with-python/

import errno
import os
import sys
from abc import ABC
from contextlib import contextmanager
from io import TextIOBase
from pathlib import Path
from typing import Literal

try:
    from ctypes import windll
except ImportError:  # Not on Windows
    windll = None
else:
    from ctypes import byref, c_ushort, Structure
    from ctypes.wintypes import _COORD, DWORD, SMALL_RECT

    class ConsoleScreenBufferInfo(Structure):
        _fields_ = [
            ("dwSize", _COORD),
            ("dwCursorPosition", _COORD),
            ("wAttributes", c_ushort),
            ("srWindow", SMALL_RECT),
            ("dwMaximumWindowSize", _COORD),
        ]


from robot.errors import DataError
from robot.utils import console_encode, isatty, validate_literal, WINDOWS

from .types import ConsoleColors, ConsoleLinks, Status


class HighlightingStream:

    def __init__(
        self,
        stream: "TextIOBase | None",
        colors: ConsoleColors = "AUTO",
        links: ConsoleLinks = "AUTO",
    ):
        self.stream = stream or NullStream()
        self.highlighter = Highlighter.from_config(stream, colors, links)

    def write(self, text: str, flush: bool = True):
        self._write(console_encode(text, stream=self.stream))
        if flush:
            self.flush()

    def _write(self, text: str, retry: int = 5):
        try:
            with self._suppress_broken_pipe_error():
                self.stream.write(text)
        except IOError as err:
            # Workaround for Windows 10 console bug:
            # https://github.com/robotframework/robotframework/issues/2709
            if WINDOWS and err.errno == 0 and retry > 0:
                self._write(text, retry - 1)
            else:
                raise

    @contextmanager
    def _suppress_broken_pipe_error(self):
        try:
            yield
        except IOError as err:
            if err.errno not in (errno.EPIPE, errno.EINVAL, errno.EBADF):
                raise

    def flush(self):
        with self._suppress_broken_pipe_error():
            self.stream.flush()

    def highlight(self, status: Status, text: "str | None" = None, flush: bool = True):
        highlighter = self.highlighter
        # Must flush before and after highlighting when using Windows APIs to make
        # sure colors only affects the actual highlighted text.
        if isinstance(highlighter, DosHighlighter):
            self.flush()
            flush = True
        {
            "PASS": highlighter.green,
            "FAIL": highlighter.red,
            "SKIP": highlighter.yellow,
            "ERROR": highlighter.red,
            "WARN": highlighter.yellow,
        }[status]()
        try:
            self.write(text or status, flush)
        finally:
            highlighter.reset()

    def error(self, message: str, level: Literal["ERROR", "WARN"]):
        self.write("[ ", flush=False)
        self.highlight(level, flush=False)
        self.write(f" ] {message}\n")

    def link(self, path: "Path | None"):
        self.write(self.highlighter.link(path) if path else "NONE")


class NullStream(TextIOBase):

    def write(self, text):
        pass

    def flush(self):
        pass


class Highlighter(ABC):

    @classmethod
    def from_config(
        cls,
        stream: "TextIOBase | None",
        colors: ConsoleColors = "AUTO",
        links: ConsoleLinks = "AUTO",
    ) -> "Highlighter":
        try:
            colors = validate_literal(colors, ConsoleColors, "console color")
            links = validate_literal(links, ConsoleLinks, "console link")
        except ValueError as err:
            raise DataError(str(err))
        if colors == "AUTO":
            colors = "ON" if isatty(stream) else "OFF"
        if colors == "OFF" or not stream:
            return NoHighlighting()
        if os.sep == "/" or colors == "ANSI" or virtual_terminal_enabled(stream):
            return AnsiHighlighter(stream, links == "AUTO")
        return DosHighlighter(stream)

    def green(self):
        pass

    def red(self):
        pass

    def yellow(self):
        pass

    def reset(self):
        pass

    def link(self, path: Path) -> str:
        return str(path)


class NoHighlighting(Highlighter):
    pass


class AnsiHighlighter(Highlighter):
    GREEN = "\033[32m"
    RED = "\033[31m"
    YELLOW = "\033[33m"
    RESET = "\033[0m"

    def __init__(self, stream: TextIOBase, links: bool = True):
        self.stream = stream
        self.links = links

    def green(self):
        self._set_color(self.GREEN)

    def red(self):
        self._set_color(self.RED)

    def yellow(self):
        self._set_color(self.YELLOW)

    def reset(self):
        self._set_color(self.RESET)

    def link(self, path: Path) -> str:
        if not self.links:
            return str(path)
        try:
            uri = path.as_uri()
        except ValueError:
            return str(path)
        # Terminal hyperlink syntax is documented here:
        # https://gist.github.com/egmontkob/eb114294efbcd5adb1944c9f3cb5feda
        return f"\033]8;;{uri}\033\\{path}\033]8;;\033\\"

    def _set_color(self, color):
        self.stream.write(color)


class DosHighlighter(Highlighter):
    FOREGROUND_GREEN = 0x2
    FOREGROUND_RED = 0x4
    FOREGROUND_YELLOW = 0x6
    FOREGROUND_GREY = 0x7
    FOREGROUND_INTENSITY = 0x8
    BACKGROUND_MASK = 0xF0

    def __init__(self, stream: TextIOBase):
        self.handle = get_std_handle(stream)
        self.orig_colors = self._get_colors()
        self.background = self.orig_colors & self.BACKGROUND_MASK

    def green(self):
        self._set_foreground_colors(self.FOREGROUND_GREEN)

    def red(self):
        self._set_foreground_colors(self.FOREGROUND_RED)

    def yellow(self):
        self._set_foreground_colors(self.FOREGROUND_YELLOW)

    def reset(self):
        self._set_colors(self.orig_colors)

    def _get_colors(self):
        info = ConsoleScreenBufferInfo()
        ok = windll.kernel32.GetConsoleScreenBufferInfo(self.handle, byref(info))
        if not ok:  # Call failed, return default console colors (gray on black)
            return self.FOREGROUND_GREY
        return info.wAttributes

    def _set_foreground_colors(self, colors):
        self._set_colors(colors | self.FOREGROUND_INTENSITY | self.background)

    def _set_colors(self, colors):
        windll.kernel32.SetConsoleTextAttribute(self.handle, colors)


def get_std_handle(stream: TextIOBase):
    handle = -11 if stream is sys.__stdout__ else -12
    return windll.kernel32.GetStdHandle(handle)


def virtual_terminal_enabled(stream):
    if not windll:
        return False
    handle = get_std_handle(stream)
    enable_vt = 0x0004
    mode = DWORD()
    if not windll.kernel32.GetConsoleMode(handle, byref(mode)):
        return False  # Calling GetConsoleMode failed.
    if mode.value & enable_vt:
        return True  # VT already enabled.
    # Try to enable VT.
    return windll.kernel32.SetConsoleMode(handle, mode.value | enable_vt) != 0
