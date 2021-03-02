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

import sys

from robot.errors import DataError
from robot.utils import (get_console_length, getshortdoc, isatty,
                         pad_console_length)

from .highlighting import HighlightingStream


class VerboseOutput(object):

    def __init__(self, width=78, colors='AUTO', markers='AUTO', stdout=None,
                 stderr=None):
        self._writer = VerboseWriter(width, colors, markers, stdout, stderr)
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
            self._writer.keyword_marker(kw.status)

    def message(self, msg):
        if msg.level in ('WARN', 'ERROR'):
            self._writer.error(msg.message, msg.level, clear=self._running_test)

    def output_file(self, name, path):
        self._writer.output(name, path)


class VerboseWriter(object):
    _status_length = len('| PASS |')

    def __init__(self, width=78, colors='AUTO', markers='AUTO', stdout=None,
                 stderr=None):
        self._width = width
        self._stdout = HighlightingStream(stdout or sys.__stdout__, colors)
        self._stderr = HighlightingStream(stderr or sys.__stderr__, colors)
        self._keyword_marker = KeywordMarker(self._stdout, markers)
        self._last_info = None

    def info(self, name, doc, start_suite=False):
        width, separator = self._get_info_width_and_separator(start_suite)
        self._last_info = self._get_info(name, doc, width) + separator
        self._write_info()
        self._keyword_marker.reset_count()

    def _write_info(self):
        self._stdout.write(self._last_info)

    def _get_info_width_and_separator(self, start_suite):
        if start_suite:
            return self._width, '\n'
        return self._width - self._status_length - 1, ' '

    def _get_info(self, name, doc, width):
        if get_console_length(name) > width:
            return pad_console_length(name, width)
        doc = getshortdoc(doc, linesep=' ')
        info = '%s :: %s' % (name, doc) if doc else name
        return pad_console_length(info, width)

    def suite_separator(self):
        self._fill('=')

    def test_separator(self):
        self._fill('-')

    def _fill(self, char):
        self._stdout.write('%s\n' % (char * self._width))

    def status(self, status, clear=False):
        if self._should_clear_markers(clear):
            self._clear_status()
        self._stdout.write('| ', flush=False)
        self._stdout.highlight(status, flush=False)
        self._stdout.write(' |\n')

    def _should_clear_markers(self, clear):
        return clear and self._keyword_marker.marking_enabled

    def _clear_status(self):
        self._clear_info()
        self._write_info()

    def _clear_info(self):
        self._stdout.write('\r%s\r' % (' ' * self._width))
        self._keyword_marker.reset_count()

    def message(self, message):
        if message:
            self._stdout.write(message.strip() + '\n')

    def keyword_marker(self, status):
        if self._keyword_marker.marker_count == self._status_length:
            self._clear_status()
            self._keyword_marker.reset_count()
        self._keyword_marker.mark(status)

    def error(self, message, level, clear=False):
        if self._should_clear_markers(clear):
            self._clear_info()
        self._stderr.error(message, level)
        if self._should_clear_markers(clear):
            self._write_info()

    def output(self, name, path):
        self._stdout.write('%-8s %s\n' % (name+':', path))


class KeywordMarker(object):

    def __init__(self, highlighter, markers):
        self._highlighter = highlighter
        self.marking_enabled = self._marking_enabled(markers, highlighter)
        self.marker_count = 0

    def _marking_enabled(self, markers, highlighter):
        options = {'AUTO': isatty(highlighter.stream),
                   'ON': True,
                   'OFF': False}
        try:
            return options[markers.upper()]
        except KeyError:
            raise DataError("Invalid console marker value '%s'. Available "
                            "'AUTO', 'ON' and 'OFF'." % markers)

    def mark(self, status):
        if self.marking_enabled:
            marker, status = ('.', 'PASS') if status != 'FAIL' else ('F', 'FAIL')
            self._highlighter.highlight(marker, status)
            self.marker_count += 1

    def reset_count(self):
        self.marker_count = 0
