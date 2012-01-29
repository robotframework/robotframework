#  Copyright 2008-2011 Nokia Siemens Networks Oyj
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

from robot import utils
from highlighting import Highlighter, NoHighlighting
from loggerhelper import IsLogged


class CommandLineMonitor:

    def __init__(self, width=78, colors='AUTO', stdout=None, stderr=None):
        self._width = width
        self._stdout = stdout or sys.__stdout__
        self._stderr = stderr or sys.__stderr__
        self._highlighter = StatusHighlighter(colors, self._stdout, self._stderr)
        self._is_logged = IsLogged('WARN')
        self._started = False

    def start_suite(self, suite):
        if not self._started:
            self._write_separator('=')
            self._started = True
        self._write_info(suite.longname, suite.doc, start_suite=True)
        self._write_separator('=')

    def end_suite(self, suite):
        self._write_info(suite.longname, suite.doc)
        self._write_status(suite.status)
        self._write_message(suite.get_full_message())
        self._write_separator('=')

    def start_test(self, test):
        self._write_info(test.name, test.doc)

    def end_test(self, test):
        self._write_status(test.status)
        self._write_message(test.message)
        self._write_separator('-')

    def message(self, msg):
        if self._is_logged(msg.level):
            self._write_with_highlighting('[ ', msg.level, ' ] ' + msg.message,
                                          error=True)
    def output_file(self, name, path):
        self._write('%-8s %s' % (name+':', path))

    def _write_info(self, name, doc, start_suite=False):
        maxwidth = self._width
        if not start_suite:
            maxwidth -= len(' | PASS |')
        info = self._get_info(name, doc, maxwidth)
        self._write(info, newline=start_suite)

    def _get_info(self, name, doc, maxwidth):
        if utils.get_console_length(name) > maxwidth:
            return utils.pad_console_length(name, maxwidth)
        info = name if not doc else '%s :: %s' % (name, doc.splitlines()[0])
        return utils.pad_console_length(info, maxwidth)

    def _write_status(self, status):
        self._write_with_highlighting(' | ', status, ' |')

    def _write_message(self, message):
        if message:
            self._write(message.strip())

    def _write_separator(self, sep_char):
        self._write(sep_char * self._width)

    def _write(self, message, newline=True, error=False):
        stream = self._stdout if not error else self._stderr
        if newline:
            message += '\n'
        stream.write(utils.encode_output(message).replace('\t', ' '*8))
        stream.flush()

    def _write_with_highlighting(self, before, highlighted, after,
                                 newline=True, error=False):
        stream = self._stdout if not error else self._stderr
        self._write(before, newline=False, error=error)
        self._highlighter.start(highlighted, stream)
        self._write(highlighted, newline=False, error=error)
        self._highlighter.end()
        self._write(after, newline=newline, error=error)


class StatusHighlighter:

    def __init__(self, colors, *streams):
        self._current = None
        self._colors = colors.upper()
        self._highlighters = dict((stream, self._get_highlighter(stream))
                                  for stream in streams)

    def start(self, message, stream):
        self._current = self._highlighters[stream]
        {'PASS': self._current.green,
         'FAIL': self._current.red,
         'ERROR': self._current.red,
         'WARN': self._current.yellow}[message]()

    def end(self):
        self._current.reset()

    def _get_highlighter(self, stream):
        auto = hasattr(stream, 'isatty') and stream.isatty()
        enable = {'AUTO': auto,
                  'ON': True,
                  'FORCE': True,   # compatibility with 2.5.5 and earlier
                  'OFF': False}.get(self._colors, auto)
        return Highlighter(stream) if enable else NoHighlighting(stream)
