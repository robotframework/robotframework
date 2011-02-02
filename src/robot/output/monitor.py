#  Copyright 2008-2010 Nokia Siemens Networks Oyj
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


import os
import sys

from robot import utils
from robot.errors import FrameworkError

from loggerhelper import IsLogged


class CommandLineMonitor:

    def __init__(self, width=78, colors=True):
        self._width = width
        self._colors = colors
        self._running_suites = 0
        self._is_logged = IsLogged('WARN')

    def start_suite(self, suite):
        if not self._running_suites:
            self._write_separator('=')
        self._write_info(suite.longname, suite.doc, start_suite=True)
        self._write_separator('=')
        self._running_suites += 1

    def end_suite(self, suite):
        self._write_info(suite.longname, suite.doc)
        self._write_status(suite.status)
        self._write_message(suite.get_full_message())
        self._write_separator('=')
        self._running_suites -= 1

    def start_test(self, test):
        self._write_info(test.name, test.doc)

    def end_test(self, test):
        self._write_status(test.status)
        self._write_message(test.message)
        self._write_separator('-')

    def output_file(self, name, path):
        # called by LOGGER
        if not self._running_suites:  # ignore split output files
            self._write('%s %s' % ((name+':').ljust(8), path))

    def message(self, msg):
        # called by LOGGER
        if self._is_logged(msg.level):
            self._status_text(msg.level).write_message(msg.message)

    def _status_text(self, text):
        return StatusText(text, self._colors)

    def _write(self, message, newline=True, stream=sys.__stdout__):
        if newline:
            message += '\n'
        stream.write(utils.encode_output(message).replace('\t', ' '*8))
        stream.flush()

    def _write_info(self, name, doc, start_suite=False):
        maxwidth = self._width
        if not start_suite:
            maxwidth -= len(' | PASS |')
        info = self._get_info(name, doc, maxwidth)
        self._write(info, newline=start_suite)

    def _get_info(self, name, doc, maxwidth):
        if utils.get_console_length(name) > maxwidth:
            return utils.pad_console_length(name, maxwidth, cut_left=True)
        if doc == '':
            return utils.pad_console_length(name, maxwidth)
        info = '%s :: %s' % (name, doc.splitlines()[0])
        return utils.pad_console_length(info, maxwidth)

    def _write_status(self, status):
        self._status_text(status).write_status()

    def _write_message(self, message):
        if message:
            self._write(message.strip())

    def _write_separator(self, sep_char):
        self._write(sep_char * self._width)


def StatusText(msg, colors=True):
    if colors:
        if os.sep == '\\':
            return DosHiglightedStatusText(msg)
        return HiglightedStatusText(msg)
    return PlainStatusText(msg)


class PlainStatusText:
    _highlight_colors = {}

    def __init__(self, msg):
        self._msg = msg

    def __str__(self):
        return self._msg

    def write_status(self, stream=sys.__stdout__):
        self.write(' | %s |' % self._msg, stream)

    def write_message(self, message):
        self.write('[ %s ] %s' % (self._msg, message), stream=sys.__stderr__)

    def write(self, message, newline=True, stream=sys.__stdout__):
        if newline:
            message += '\n'
        self._write_encoded_with_tab_replacing(stream, message)
        stream.flush()

    def _write_encoded_with_tab_replacing(self, stream, message):
        stream.write(utils.encode_output(message).replace('\t', ' '*8))

    def _get_highlight_color(self, text):
        if text in self._highlight_colors:
            return self._highlight_colors[text]
        raise FrameworkError


class HiglightedStatusText(PlainStatusText):
    ANSI_RED    = '\033[31m'
    ANSI_GREEN  = '\033[32m'
    ANSI_YELLOW = '\033[33m'
    ANSI_RESET  = '\033[0m'

    _highlight_colors = {'FAIL': ANSI_RED,
                         'ERROR': ANSI_RED,
                         'WARN': ANSI_YELLOW,
                         'PASS': ANSI_GREEN}

    def __str__(self):
        color = self._get_highlight_color(self._msg)
        reset = color != '' and self.ANSI_RESET or ''
        return color + self._msg + reset


from ctypes import windll, Structure, c_short, c_ushort, byref

SHORT = c_short
WORD = c_ushort

class COORD(Structure):
  _fields_ = [
    ("X", SHORT),
    ("Y", SHORT)]

class SMALL_RECT(Structure):
  _fields_ = [
    ("Left", SHORT),
    ("Top", SHORT),
    ("Right", SHORT),
    ("Bottom", SHORT)]

class CONSOLE_SCREEN_BUFFER_INFO(Structure):
  _fields_ = [
    ("dwSize", COORD),
    ("dwCursorPosition", COORD),
    ("wAttributes", WORD),
    ("srWindow", SMALL_RECT),
    ("dwMaximumWindowSize", COORD)]


class DosHiglightedStatusText(PlainStatusText):
    FOREGROUND_RED = 0x0004
    FOREGROUND_YELLOW = 0x0006
    FOREGROUND_GREEN = 0x0002
    FOREGROUND_INTENSITY = 0x0008
    FOREGROUND_GREY = 0x0007

    STD_OUTPUT_HANDLE = -11

    _highlight_colors = {'FAIL': FOREGROUND_RED,
                         'ERROR': FOREGROUND_RED,
                         'WARN': FOREGROUND_YELLOW,
                         'PASS': FOREGROUND_GREEN}

    def write_status(self, newline=True, stream=sys.__stdout__):
        self._write(None, ' |', '|', newline, stream)

    def write_message(self, message, newline=True, stream=sys.__stderr__):
        self._write(message, '[', ']', newline, stream)

    def _write(self,  message, start_sep, end_sep, newline=True, stream=sys.__stdout__):
        default_colors = self._get_text_attr()
        default_fg = default_colors & 0x0007
        default_bg = default_colors & 0x0070
        self._write_encoded_with_tab_replacing(stream, start_sep)
        self._set_text_attr(self._get_highlight_color(self._msg) | self.FOREGROUND_INTENSITY)
        self._write_encoded_with_tab_replacing(stream, ' %s ' % self._msg)
        self._set_text_attr(default_fg | default_bg |self.FOREGROUND_INTENSITY)
        self._write_encoded_with_tab_replacing(stream, end_sep)
        if message:
            stream.write(' %s' % message)
        if newline:
            self._write_encoded_with_tab_replacing(stream, '\n')

    def _set_text_attr(self, color):
        windll.kernel32.SetConsoleTextAttribute(windll.kernel32.GetStdHandle(self.STD_OUTPUT_HANDLE), color)

    def _get_text_attr(self):
        csbi = CONSOLE_SCREEN_BUFFER_INFO()
        windll.kernel32.GetConsoleScreenBufferInfo(self.STD_OUTPUT_HANDLE, byref(csbi))
        return csbi.wAttributes
