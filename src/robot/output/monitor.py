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

from robot import utils

from loggerhelper import IsLogged


# ANSI colors
ANSI_RED    = '\033[31m'
ANSI_GREEN  = '\033[32m'
ANSI_YELLOW = '\033[33m'
ANSI_RESET  = '\033[0m'


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
            message = '[ %s ] %s' % (self._highlight(msg.level), msg.message)
            self._write(message, stream=sys.__stderr__)

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
        self._write(' | %s |' % self._highlight(status))

    def _write_message(self, message):
        if message:
            self._write(message.strip())

    def _write_separator(self, sep_char):
        self._write(sep_char * self._width)

    def _highlight(self, text):
        color = self._get_highlight_color(text)
        reset = color != '' and ANSI_RESET or ''
        return color + text + reset

    def _get_highlight_color(self, text):
        if self._colors:
            if text in ['FAIL','ERROR']:
                return ANSI_RED
            elif text == 'WARN':
                return ANSI_YELLOW
            elif text == 'PASS':
                return ANSI_GREEN
        return ''
