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
from contextlib import contextmanager

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
from robot.utils import console_encode, isatty, WINDOWS


class HighlightingStream:

    def __init__(self, stream, colors="AUTO", links="AUTO"):
        self.stream = stream or NullStream()
        self._highlighter = self._get_highlighter(stream, colors, links)

    def _get_highlighter(self, stream, colors, links):
        if not stream:
            return NoHighlighting()
        options = {
            "AUTO": Highlighter if isatty(stream) else NoHighlighting,
            "ON": Highlighter,
            "OFF": NoHighlighting,
            "ANSI": AnsiHighlighter,
        }
        try:
            highlighter = options[colors.upper()]
        except KeyError:
            raise DataError(
                f"Invalid console color value '{colors}'. "
                f"Available 'AUTO', 'ON', 'OFF' and 'ANSI'."
            )
        if links.upper() not in ("AUTO", "OFF"):
            raise DataError(
                f"Invalid console link value '{links}. Available 'AUTO' and 'OFF'."
            )
        return highlighter(stream, links.upper() == "AUTO")

    def write(self, text, flush=True):
        self._write(console_encode(text, stream=self.stream))
        if flush:
            self.flush()

    def _write(self, text, retry=5):
        # Workaround for Windows 10 console bug:
        # https://github.com/robotframework/robotframework/issues/2709
        try:
            with self._suppress_broken_pipe_error:
                self.stream.write(text)
        except IOError as err:
            if not (WINDOWS and err.errno == 0 and retry > 0):
                raise
            self._write(text, retry - 1)

    @property
    @contextmanager
    def _suppress_broken_pipe_error(self):
        try:
            yield
        except IOError as err:
            if err.errno not in (errno.EPIPE, errno.EINVAL, errno.EBADF):
                raise

    def flush(self):
        with self._suppress_broken_pipe_error:
            self.stream.flush()

    def highlight(self, text, status=None, flush=True):
        # Must flush before and after highlighting when using Windows APIs to make
        # sure colors only affects the actual highlighted text.
        if isinstance(self._highlighter, DosHighlighter):
            self.flush()
            flush = True
        with self._highlighting(status or text):
            self.write(text, flush)

    def error(self, message, level):
        self.write("[ ", flush=False)
        self.highlight(level, flush=False)
        self.write(f" ] {message}\n")

    @contextmanager
    def _highlighting(self, status):
        highlighter = self._highlighter
        start = {
            "PASS": highlighter.green,
            "FAIL": highlighter.red,
            "ERROR": highlighter.red,
            "WARN": highlighter.yellow,
            "SKIP": highlighter.yellow,
        }[status]
        start()
        try:
            yield
        finally:
            highlighter.reset()

    def result_file(self, kind, path):
        path = self._highlighter.link(path) if path else "NONE"
        self.write(f"{kind + ':':8} {path}\n")


class NullStream:

    def write(self, text):
        pass

    def flush(self):
        pass


def Highlighter(stream, links=True):
    if os.sep == "/":
        return AnsiHighlighter(stream, links)
    if not windll:
        return NoHighlighting(stream)
    if virtual_terminal_enabled(stream):
        return AnsiHighlighter(stream, links)
    return DosHighlighter(stream)


class AnsiHighlighter:
    GREEN = "\033[32m"
    RED = "\033[31m"
    YELLOW = "\033[33m"
    RESET = "\033[0m"

    def __init__(self, stream, links=True):
        self._stream = stream
        self._links = links

    def green(self):
        self._set_color(self.GREEN)

    def red(self):
        self._set_color(self.RED)

    def yellow(self):
        self._set_color(self.YELLOW)

    def reset(self):
        self._set_color(self.RESET)

    def link(self, path):
        if not self._links:
            return path
        try:
            uri = path.as_uri()
        except ValueError:
            return path
        # Terminal hyperlink syntax is documented here:
        # https://gist.github.com/egmontkob/eb114294efbcd5adb1944c9f3cb5feda
        return f"\033]8;;{uri}\033\\{path}\033]8;;\033\\"

    def _set_color(self, color):
        self._stream.write(color)


class NoHighlighting(AnsiHighlighter):

    def __init__(self, stream=None, links=True):
        super().__init__(stream, links)

    def link(self, path):
        return path

    def _set_color(self, color):
        pass


class DosHighlighter:
    FOREGROUND_GREEN = 0x2
    FOREGROUND_RED = 0x4
    FOREGROUND_YELLOW = 0x6
    FOREGROUND_GREY = 0x7
    FOREGROUND_INTENSITY = 0x8
    BACKGROUND_MASK = 0xF0

    def __init__(self, stream):
        self._handle = get_std_handle(stream)
        self._orig_colors = self._get_colors()
        self._background = self._orig_colors & self.BACKGROUND_MASK

    def green(self):
        self._set_foreground_colors(self.FOREGROUND_GREEN)

    def red(self):
        self._set_foreground_colors(self.FOREGROUND_RED)

    def yellow(self):
        self._set_foreground_colors(self.FOREGROUND_YELLOW)

    def reset(self):
        self._set_colors(self._orig_colors)

    def link(self, path):
        return path

    def _get_colors(self):
        info = ConsoleScreenBufferInfo()
        ok = windll.kernel32.GetConsoleScreenBufferInfo(self._handle, byref(info))
        if not ok:  # Call failed, return default console colors (gray on black)
            return self.FOREGROUND_GREY
        return info.wAttributes

    def _set_foreground_colors(self, colors):
        self._set_colors(colors | self.FOREGROUND_INTENSITY | self._background)

    def _set_colors(self, colors):
        windll.kernel32.SetConsoleTextAttribute(self._handle, colors)


def get_std_handle(stream):
    handle = -11 if stream is sys.__stdout__ else -12
    return windll.kernel32.GetStdHandle(handle)


def virtual_terminal_enabled(stream):
    handle = get_std_handle(stream)
    enable_vt = 0x0004
    mode = DWORD()
    if not windll.kernel32.GetConsoleMode(handle, byref(mode)):
        return False  # Calling GetConsoleMode failed.
    if mode.value & enable_vt:
        return True  # VT already enabled.
    # Try to enable VT.
    return windll.kernel32.SetConsoleMode(handle, mode.value | enable_vt) != 0
