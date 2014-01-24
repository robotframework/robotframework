#  Copyright 2008-2014 Nokia Solutions and Networks
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

import os
import sys
try:
    from ctypes import windll, Structure, c_short, c_ushort, byref
except ImportError:  # Not on Windows or using Jython
    windll = None


def Highlighter(stream):
    if os.sep == '/':
        return AnsiHighlighter(stream)
    return DosHighlighter(stream) if windll else NoHighlighting(stream)


class AnsiHighlighter(object):
    _ANSI_GREEN  = '\033[32m'
    _ANSI_RED = '\033[31m'
    _ANSI_YELLOW = '\033[33m'
    _ANSI_RESET = '\033[0m'

    def __init__(self, stream):
        self._stream = stream

    def green(self):
        self._set_color(self._ANSI_GREEN)

    def red(self):
        self._set_color(self._ANSI_RED)

    def yellow(self):
        self._set_color(self._ANSI_YELLOW)

    def reset(self):
        self._set_color(self._ANSI_RESET)

    def _set_color(self, color):
        self._stream.write(color)


class NoHighlighting(AnsiHighlighter):

    def _set_color(self, color):
        pass


class DosHighlighter(object):
    _FOREGROUND_GREEN = 0x2
    _FOREGROUND_RED = 0x4
    _FOREGROUND_YELLOW = 0x6
    _FOREGROUND_GREY = 0x7
    _FOREGROUND_INTENSITY = 0x8
    _BACKGROUND_MASK = 0xF0
    _STDOUT_HANDLE = -11
    _STDERR_HANDLE = -12

    def __init__(self, stream):
        self._handle = self._get_std_handle(stream)
        self._orig_colors = self._get_colors()
        self._background = self._orig_colors & self._BACKGROUND_MASK

    def green(self):
        self._set_foreground_colors(self._FOREGROUND_GREEN)

    def red(self):
        self._set_foreground_colors(self._FOREGROUND_RED)

    def yellow(self):
        self._set_foreground_colors(self._FOREGROUND_YELLOW)

    def reset(self):
        self._set_colors(self._orig_colors)

    def _get_std_handle(self, stream):
        handle = self._STDOUT_HANDLE \
            if stream is sys.__stdout__ else self._STDERR_HANDLE
        return windll.kernel32.GetStdHandle(handle)

    def _get_colors(self):
        csbi = _CONSOLE_SCREEN_BUFFER_INFO()
        ok = windll.kernel32.GetConsoleScreenBufferInfo(self._handle, byref(csbi))
        if not ok:  # Call failed, return default console colors (gray on black)
            return self._FOREGROUND_GREY
        return csbi.wAttributes

    def _set_foreground_colors(self, colors):
        self._set_colors(colors | self._FOREGROUND_INTENSITY | self._background)

    def _set_colors(self, colors):
        windll.kernel32.SetConsoleTextAttribute(self._handle, colors)


if windll:

    class _COORD(Structure):
        _fields_ = [("X", c_short),
                    ("Y", c_short)]

    class _SMALL_RECT(Structure):
        _fields_ = [("Left", c_short),
                    ("Top", c_short),
                    ("Right", c_short),
                    ("Bottom", c_short)]

    class _CONSOLE_SCREEN_BUFFER_INFO(Structure):
        _fields_ = [("dwSize", _COORD),
                    ("dwCursorPosition", _COORD),
                    ("wAttributes", c_ushort),
                    ("srWindow", _SMALL_RECT),
                    ("dwMaximumWindowSize", _COORD)]
