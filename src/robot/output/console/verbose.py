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
from robot.utils import get_console_length, getshortdoc, isatty, pad_console_length

from .highlighting import HighlightingStream
from ..loggerapi import LoggerApi


class VerboseOutput(LoggerApi):

    def __init__(self, width=78, colors='AUTO', markers='AUTO', stdout=None,
                 stderr=None):
        self.writer = VerboseWriter(width, colors, markers, stdout, stderr)
        self.started = False
        self.started_keywords = 0
        self.running_test = False

    def start_suite(self, data, result):
        if not self.started:
            self.writer.suite_separator()
            self.started = True
        self.writer.info(data.full_name, result.doc, start_suite=True)
        self.writer.suite_separator()

    def end_suite(self, data, result):
        self.writer.info(data.full_name, result.doc)
        self.writer.status(result.status)
        self.writer.message(result.full_message)
        self.writer.suite_separator()

    def start_test(self, data, result):
        self.writer.info(result.name, result.doc)
        self.running_test = True

    def end_test(self, data, result):
        self.writer.status(result.status, clear=True)
        self.writer.message(result.message)
        self.writer.test_separator()
        self.running_test = False

    def start_body_item(self, data, result):
        self.started_keywords += 1

    def end_body_item(self, data, result):
        self.started_keywords -= 1
        if self.running_test and not self.started_keywords:
            self.writer.keyword_marker(result.status)

    def message(self, msg):
        if msg.level in ('WARN', 'ERROR'):
            self.writer.error(msg.message, msg.level, clear=self.running_test)

    def result_file(self, kind, path):
        self.writer.output(kind, path)


class VerboseWriter:
    _status_length = len('| PASS |')

    def __init__(self, width=78, colors='AUTO', markers='AUTO', stdout=None,
                 stderr=None):
        self.width = width
        self.stdout = HighlightingStream(stdout or sys.__stdout__, colors)
        self.stderr = HighlightingStream(stderr or sys.__stderr__, colors)
        self._keyword_marker = KeywordMarker(self.stdout, markers)
        self._last_info = None

    def info(self, name, doc, start_suite=False):
        width, separator = self._get_info_width_and_separator(start_suite)
        self._last_info = self._get_info(name, doc, width) + separator
        self._write_info()
        self._keyword_marker.reset_count()

    def _write_info(self):
        self.stdout.write(self._last_info)

    def _get_info_width_and_separator(self, start_suite):
        if start_suite:
            return self.width, '\n'
        return self.width - self._status_length - 1, ' '

    def _get_info(self, name, doc, width):
        if get_console_length(name) > width:
            return pad_console_length(name, width)
        doc = getshortdoc(doc, linesep=' ')
        info = f'{name} :: {doc}' if doc else name
        return pad_console_length(info, width)

    def suite_separator(self):
        self._fill('=')

    def test_separator(self):
        self._fill('-')

    def _fill(self, char):
        self.stdout.write(f'{char * self.width}\n')

    def status(self, status, clear=False):
        if self._should_clear_markers(clear):
            self._clear_status()
        self.stdout.write('| ', flush=False)
        self.stdout.highlight(status, flush=False)
        self.stdout.write(' |\n')

    def _should_clear_markers(self, clear):
        return clear and self._keyword_marker.marking_enabled

    def _clear_status(self):
        self._clear_info()
        self._write_info()

    def _clear_info(self):
        self.stdout.write(f"\r{' ' * self.width}\r")
        self._keyword_marker.reset_count()

    def message(self, message):
        if message:
            self.stdout.write(message.strip() + '\n')

    def keyword_marker(self, status):
        if self._keyword_marker.marker_count == self._status_length:
            self._clear_status()
            self._keyword_marker.reset_count()
        self._keyword_marker.mark(status)

    def error(self, message, level, clear=False):
        if self._should_clear_markers(clear):
            self._clear_info()
        self.stderr.error(message, level)
        if self._should_clear_markers(clear):
            self._write_info()

    def output(self, name, path):
        self.stdout.write(f"{name+':':8} {path}\n")


class KeywordMarker:

    def __init__(self, highlighter, markers):
        self.highlighter = highlighter
        self.marking_enabled = self._marking_enabled(markers, highlighter)
        self.marker_count = 0

    def _marking_enabled(self, markers, highlighter):
        options = {'AUTO': isatty(highlighter.stream),
                   'ON': True,
                   'OFF': False}
        try:
            return options[markers.upper()]
        except KeyError:
            raise DataError(f"Invalid console marker value '{markers}'. "
                            f"Available 'AUTO', 'ON' and 'OFF'.")

    def mark(self, status):
        if self.marking_enabled:
            marker, status = ('.', 'PASS') if status != 'FAIL' else ('F', 'FAIL')
            self.highlighter.highlight(marker, status)
            self.marker_count += 1

    def reset_count(self):
        self.marker_count = 0
