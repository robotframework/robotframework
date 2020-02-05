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
        self._writer.debug(test.name, test.doc)
        self._running_test = True

    def end_test(self, test):
        self._writer.status(test.status, clear=True)
        self._writer.message(test.message)
        self._writer.test_separator()
        self._running_test = False

    def start_keyword(self, kw):
        if self._check_suite_keyword():
            if kw.type == "setup":
                self._writer.debug('Suite Setup', None)
            else:
                self._writer.debug('Suite Teardown', None)
        if self._writer._verbose_level and kw.type in ("setup", "teardown"):
            self._writer.increase_verbose_level()
        self._started_keywords += 1
        if self._running_test or self._writer._verbose_level:
            self._writer.start_keyword_marker(kw, self._started_keywords)

    def end_keyword(self, kw):
        if self._running_test or self._writer._verbose_level:
            self._writer.end_keyword_marker(kw, self._started_keywords)
        self._started_keywords -= 1
        if self._check_suite_keyword():
            self._writer.end_keyword_marker(kw, self._started_keywords)
            self._writer.test_separator()
        if self._writer._verbose_level and kw.type in ("setup", "teardown"):
            self._writer.decrease_verbose_level()

    def _check_suite_keyword(self):
        return not self._running_test and self._writer._verbose_level \
               and self._writer._keyword_marker.marking_enabled \
               and self._started_keywords == 0

    def message(self, msg):
        if msg.level in ('WARN', 'ERROR'):
            self._writer.error(msg.message, msg.level, clear=self._running_test)

    def output_file(self, name, path):
        self._writer.output(name, path)

    def verbose_keywords(self):
        self._writer.increase_verbose_level()


class VerboseWriter(object):
    _status_length = len('| PASS |')

    def __init__(self, width=78, colors='AUTO', markers='AUTO', stdout=None,
                 stderr=None):
        self._width = width
        self._stdout = HighlightingStream(stdout or sys.__stdout__, colors)
        self._stderr = HighlightingStream(stderr or sys.__stderr__, colors)
        self._keyword_marker = KeywordMarker(self._stdout, markers)
        self._verbose_level = 0
        self._last_info = None
        self._break_line_needed = True
        self._debug_messages = []

    def info(self, name, doc, start_suite=False):
        width, separator = self._get_width_and_separator(start_suite)
        self._last_info = self._get_label(name, doc, width) + separator
        self._write_info()
        self._keyword_marker.reset_count()

    def _write_info(self):
        self._stdout.write(self._last_info)

    def debug(self, name, doc, start_suite=False):
        width, separator = self._get_width_and_separator(start_suite)
        self._debug_messages.append(self._get_label(name, doc, width) + separator)
        self._write_debug()

    def _write_debug(self, erase_last_message=False):
        self._stdout.write(self._debug_messages[-1])
        if erase_last_message:
            self._debug_messages.pop()

    def _get_width_and_separator(self, start_suite):
        if start_suite:
            return self._width, '\n'
        return self._width - self._status_length - 1, ' '

    def _get_label(self, name, doc, width):
        if get_console_length(name) > width:
            return pad_console_length(name, width)
        doc = getshortdoc(doc, linesep=' ')
        info = '%s :: %s' % (name, doc) if doc else name
        return pad_console_length(info, width)

    def suite_separator(self):
        self._fill('=')

    def test_separator(self):
        self._fill('-')
        self._break_line_needed = True

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

    def _clear_status(self, erase_last_message=True):
        self._clear_debug()
        self._write_debug(erase_last_message)

    def _clear_debug(self):
        self._stdout.write('\r%s\r' % (' ' * self._width))
        self._keyword_marker.reset_count()

    def message(self, message):
        if message:
            self._stdout.write(message.strip() + '\n')

    def start_keyword_marker(self, kw, depth):
        if not self._keyword_marker.marking_enabled:
            return
        if depth <= self._verbose_level:
            name = self._keyword_marker.label_writer(kw)
            label = self._keyword_label(name, depth)
            self._start_keyword_marker(label)

    def end_keyword_marker(self, kw, depth):
        if not self._keyword_marker.marking_enabled:
            return
        status = 'PASS' if kw.status != 'FAIL' else 'FAIL'
        if depth <= self._verbose_level:
            self._end_keyword_marker(status)
        else:
            if self._keyword_marker.marker_count == self._status_length:
                self._clear_status(False)
                self._keyword_marker.reset_count()
            self._keyword_marker.mark(status)

    def _start_keyword_marker(self, label):
        if self._break_line_needed:
            self._stdout.write('\n')
        self.debug(label, None)
        self._break_line_needed = True

    def _end_keyword_marker(self, status):
        self.status(status, clear=True)
        self._break_line_needed = False

    def _keyword_label(self, name, depth):
        width, separator = self._get_width_and_separator(False)
        prefix_str = separator * 4 * depth
        return '%s%s' % (prefix_str, name)

    def error(self, message, level, clear=False):
        if self._should_clear_markers(clear):
            self._clear_debug()
        self._stderr.error(message, level)
        if self._should_clear_markers(clear):
            self._write_debug()

    def output(self, name, path):
        self._stdout.write('%-8s %s\n' % (name+':', path))

    def increase_verbose_level(self, level=1):
        self._verbose_level += level

    def decrease_verbose_level(self, level=1):
        self.increase_verbose_level(-level)
        assert( self._verbose_level >= 0 )


class KeywordMarker(object):

    def __init__(self, highlighter, markers):
        self._highlighter = highlighter
        self.marking_enabled = self._marking_enabled(markers, highlighter)
        self.label_writer = lambda kw: "%s  %s" % (kw.name, "  ".join(kw.args))
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
            marker = '.' if status != 'FAIL' else 'F'
            self._highlighter.highlight(marker, status)
            self.marker_count += 1

    def reset_count(self):
        self.marker_count = 0
