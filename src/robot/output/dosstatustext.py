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


import sys
from ctypes import windll, Structure, c_short, c_ushort, byref

from statustext import PlainStatusText
from robot import utils


class COORD(Structure):
  _fields_ = [
    ("X", c_short),
    ("Y", c_short)]

class SMALL_RECT(Structure):
  _fields_ = [
    ("Left", c_short),
    ("Top", c_short),
    ("Right", c_short),
    ("Bottom", c_short)]

class CONSOLE_SCREEN_BUFFER_INFO(Structure):
  _fields_ = [
    ("dwSize", COORD),
    ("dwCursorPosition", COORD),
    ("wAttributes", c_ushort),
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

    def _write_encoded_with_tab_replacing(self, stream, message):
        stream.write(utils.encode_output(message).replace('\t', ' '*8))

    def write_status(self, newline=True, stream=sys.__stdout__):
        self._write(None, ' |', '|', newline, stream)

    def write_message(self, message, newline=True, stream=sys.__stderr__):
        self._write(message, '[', ']', newline, stream)

    def _write(self,  message, start_sep, end_sep, newline=True, stream=sys.__stdout__):
        default_colors = self._get_text_attr()
        default_fg = default_colors & 0x0007
        default_bg = default_colors & 0x0070
        self._write_encoded_with_tab_replacing(stream, start_sep)
        self._set_text_attr(self._highlight_colors[self._msg] | self.FOREGROUND_INTENSITY)
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
