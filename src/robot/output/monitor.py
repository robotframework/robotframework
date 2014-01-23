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

import sys

from robot import utils

from .highlighting import AnsiHighlighter, Highlighter, NoHighlighting
from .loggerhelper import IsLogged


class CommandLineMonitor(object):

    def __init__(self, width=78, colors='AUTO', markers='AUTO', stdout=None,
                 stderr=None):
        self._writer = CommandLineWriter(width, colors, markers, stdout, stderr)
        self._is_logged = IsLogged('WARN')
        self._started = False
        self._started_keywords = 0
        self._running_test = False

    def start_suite(self, suite):
        if not self._started:
            self._writer.suite_separator()
            self._started = True
        self._writer.info(suite.longname, suite.doc, start_suite=True)
        self._writer.suite_separator()

    def end_suite(self, suite):
        self._writer.info(suite.longname, suite.doc)
        self._writer.status(suite.status)
        self._writer.message(suite.full_message)
        self._writer.suite_separator()

    def start_test(self, test):
        self._writer.info(test.name, test.doc)
        self._running_test = True

    def end_test(self, test):
        self._writer.status(test.status, clear=True)
        self._writer.message(test.message)
        self._writer.test_separator()
        self._running_test = False

    def start_keyword(self, kw):
        self._started_keywords += 1

    def end_keyword(self, kw):
        self._started_keywords -= 1
        if self._running_test and not self._started_keywords:
            self._writer.keyword_marker(kw)

    def message(self, msg):
        if self._is_logged(msg.level):
            self._writer.error(msg.message, msg.level, clear=self._running_test)

    def output_file(self, name, path):
        self._writer.output(name, path)


class CommandLineWriter(object):
    _status_length = len('| PASS |')

    def __init__(self, width=78, colors='AUTO', markers='AUTO', stdout=None,
                 stderr=None):
        self._width = width
        self._stdout = stdout or sys.__stdout__
        self._stderr = stderr or sys.__stderr__
        self._highlighter = StatusHighlighter(colors, self._stdout, self._stderr)
        self._keyword_marker = KeywordMarker(markers, self._stdout, self._highlighter)
        self._last_info = None

    def info(self, name, doc, start_suite=False):
        width, separator = self._get_info_width_and_separator(start_suite)
        self._last_info = self._get_info(name, doc, width) + separator
        self._write(self._last_info, newline=False)
        self._keyword_marker.reset_count()

    def _get_info_width_and_separator(self, start_suite):
        if start_suite:
            return self._width, '\n'
        return self._width - self._status_length - 1, ' '

    def _get_info(self, name, doc, width):
        if utils.get_console_length(name) > width:
            return utils.pad_console_length(name, width)
        info = name if not doc else '%s :: %s' % (name, doc.splitlines()[0])
        return utils.pad_console_length(info, width)

    def suite_separator(self):
        self._fill('=')

    def test_separator(self):
        self._fill('-')

    def _fill(self, char):
        self._write(char * self._width)

    def status(self, status, clear=False):
        if self._should_clear_markers(clear):
            self._clear_status()
        self._highlight('| ', status, ' |')

    def _should_clear_markers(self, clear):
        return clear and self._keyword_marker.marking_enabled

    def _clear_status(self):
        self._clear_info_line()
        self._rewrite_info()

    def _clear_info_line(self):
        self._write('\r' + ' ' * self._width + '\r', newline=False)
        self._keyword_marker.reset_count()

    def _rewrite_info(self):
        self._write(self._last_info, newline=False)

    def message(self, message):
        if message:
            self._write(message.strip())

    def keyword_marker(self, kw):
        if self._keyword_marker.marker_count == self._status_length:
            self._clear_status()
            self._keyword_marker.reset_count()
        self._keyword_marker.mark(kw)

    def error(self, message, level, clear=False):
        if self._should_clear_markers(clear):
            self._clear_info_line()
        self._highlight('[ ', level, ' ] ' + message, error=True)
        if self._should_clear_markers(clear):
            self._rewrite_info()

    def output(self, name, path):
        self._write('%-8s %s' % (name+':', path))

    def _write(self, text, newline=True, error=False):
        stream = self._stdout if not error else self._stderr
        if newline:
            text += '\n'
        stream.write(utils.encode_output(text))
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
        auto = Highlighter if utils.isatty(stream) else NoHighlighting
        highlighter = {'AUTO': auto,
                       'ON': Highlighter,
                       'FORCE': Highlighter,   # compatibility with 2.5.5 and earlier
                       'OFF': NoHighlighting,
                       'ANSI': AnsiHighlighter}.get(colors.upper(), auto)
        return highlighter(stream)

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


class KeywordMarker(object):

    def __init__(self, markers, stdout, highlighter):
        self._stdout = stdout
        self._highlighter = highlighter
        self.marking_enabled = self._marking_enabled(markers, stdout)
        self.marker_count = 0

    def _marking_enabled(self, markers, stdout):
        auto = utils.isatty(stdout)
        return {'AUTO': auto,
                'ON': True,
                'OFF': False}.get(markers.upper(), auto)

    def mark(self, kw):
        if self.marking_enabled:
            marker, color = ('.', 'green') if kw.passed else ('F', 'red')
            self._highlighter.highlight(marker, color, self._stdout)
            self.marker_count += 1

    def reset_count(self):
        self.marker_count = 0

