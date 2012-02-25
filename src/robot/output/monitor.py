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

from .highlighting import Highlighter, NoHighlighting
from .loggerhelper import IsLogged


class CommandLineMonitor(object):

    def __init__(self, width=78, colors='AUTO', stdout=None, stderr=None):
        self._writer = CommandLineWriter(width, colors, stdout, stderr)
        self._is_logged = IsLogged('WARN')
        self._started = False
        self._started_keywords = 0
        self._running_test = False

    def start_suite(self, suite):
        if not self._started:
            self._writer.separator('=')
            self._started = True
        self._writer.info(suite.longname, suite.doc, start_suite=True)
        self._writer.separator('=')

    def end_suite(self, suite):
        self._writer.info(suite.longname, suite.doc)
        self._writer.status(suite.status)
        self._writer.message(suite.get_full_message())
        self._writer.separator('=')

    def start_test(self, test):
        self._writer.info(test.name, test.doc)
        self._running_test = True

    def end_test(self, test):
        self._writer.status(test.status, clear=True)
        self._writer.message(test.message)
        self._writer.separator('-')
        self._running_test = False

    def start_keyword(self, kw):
        self._started_keywords += 1

    def end_keyword(self, kw):
        self._started_keywords -= 1
        if self._running_test and not self._started_keywords:
            self._writer.keyword_marker(kw)

    def message(self, msg):
        if self._is_logged(msg.level):
            self._writer.error(msg.message, msg.level, self._started)

    def output_file(self, name, path):
        self._writer.output(name, path)


class CommandLineWriter(object):
    _status_length = len('| PASS |')

    def __init__(self, width=78, colors='AUTO', stdout=None, stderr=None):
        self._width = width
        self._stdout = stdout or sys.__stdout__
        self._stderr = stderr or sys.__stderr__
        self._highlighter = StatusHighlighter(colors, self._stdout, self._stderr)
        self._keyword_marker_count = 0

    def info(self, name, doc, start_suite=False):
        width, separator = self._get_info_width_and_separator(start_suite)
        self._info = self._get_info(name, doc, width) + separator
        self._write(self._info, newline=False)
        self._keyword_marker_count = 0

    def _get_info_width_and_separator(self, start_suite):
        if start_suite:
            return self._width, '\n'
        return self._width - self._status_length - 1, ' '

    def _get_info(self, name, doc, width):
        if utils.get_console_length(name) > width:
            return utils.pad_console_length(name, width)
        info = name if not doc else '%s :: %s' % (name, doc.splitlines()[0])
        return utils.pad_console_length(info, width)

    def separator(self, char):
        self._write(char * self._width)

    def status(self, status, clear=False):
        if clear:
            self._clear_status()
        self._highlight('| ', status, ' |')

    def _clear_status(self):
        self._clear_line()
        self._rewrite_info()

    def _clear_line(self):
        self._overwrite(' ' * self._width)
        self._overwrite('')

    def _overwrite(self, text):
        if self._stdout.isatty():
            self._write('\r' + text, newline=False)

    def _rewrite_info(self):
        self._write(self._info, newline=False)
        self._keyword_marker_count = 0

    def message(self, message):
        if message:
            self._write(message.strip())

    def keyword_marker(self, kw):
        if not self._stdout.isatty():
            return
        if self._keyword_marker_count == self._status_length:
            self._clear_status()
        marker, color = ('.', 'green') if kw.status == 'PASS' else ('F', 'red')
        self._highlighter.highlight(marker, color, self._stdout)
        self._keyword_marker_count += 1

    def error(self, message, level, running_tests=False):
        if running_tests:
            self._clear_line()
        self._highlight('[ ', level, ' ] ' + message, error=True)
        if running_tests:
            self._rewrite_info()

    def output(self, name, path):
        self._write('%-8s %s' % (name+':', path))

    def _write(self, text, newline=True, error=False):
        stream = self._stdout if not error else self._stderr
        if newline:
            text += '\n'
        stream.write(utils.encode_output(text).replace('\t', ' '*8))
        stream.flush()

    def _highlight(self, before, status, after, newline=True, error=False):
        stream = self._stdout if not error else self._stderr
        self._write(before, newline=False, error=error)
        self._highlighter.highlight_status(status, stream)
        self._write(after, newline=newline, error=error)


class StatusHighlighter(object):

    def __init__(self, colors, *streams):
        self._highlighters = dict((stream, self._get_highlighter(stream, colors))
                                  for stream in streams)

    def _get_highlighter(self, stream, colors):
        auto = hasattr(stream, 'isatty') and stream.isatty()
        enable = {'AUTO': auto,
                  'ON': True,
                  'FORCE': True,   # compatibility with 2.5.5 and earlier
                  'OFF': False}.get(colors.upper(), auto)
        return Highlighter(stream) if enable else NoHighlighting(stream)

    def highlight_status(self, status, stream):
        highlighter = self._start_status_highlighting(status, stream)
        stream.write(status)
        highlighter.reset()

    def _start_status_highlighting(self, status, stream):
        highlighter = self._highlighters[stream]
        {'PASS': highlighter.green,
         'FAIL': highlighter.red,
         'ERROR': highlighter.red,
         'WARN': highlighter.yellow}[status]()
        return highlighter

    def highlight(self, text, color, stream):
        highlighter = self._highlighters[stream]
        getattr(highlighter, color)()
        stream.write(text)
        stream.flush()
        highlighter.reset()
