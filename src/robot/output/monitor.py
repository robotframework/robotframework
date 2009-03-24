#  Copyright 2008 Nokia Siemens Networks Oyj
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


# ANSI colors
ANSI_RED    = '\033[31m'
ANSI_GREEN  = '\033[32m'
ANSI_YELLOW = '\033[33m'
ANSI_RESET  = '\033[0m'


class CommandLineMonitor:

    def __init__(self, monitor_width=78, monitor_colors=True):
        self._width = monitor_width
        self._colors = monitor_colors
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
        
    def output_file(self, name, path):
        # called by SYSLOG
        self._write('%s %s' % ((name+':').ljust(8), utils.cygpath(path)))
     
    def write(self, msg, level):
        # called by SYSLOG
        if level in ['WARN', 'ERROR']:
            message = '[ %s ] %s' % (self._highlight(level), msg.message)
            self._write(message, stream=sys.stderr)
        
    def _write(self, message, newline=True, stream=sys.stdout):
        if newline:
            message += '\n'
        message = message.encode('ascii', 'replace').replace('\t', ' '*8)
        stream.write(message)
        stream.flush()

    def _write_info(self, name, doc, start_suite=False):
        maxwidth = self._width
        if not start_suite:
            maxwidth -= len(' | PASS |')
        info = self._get_info(name, doc, maxwidth)
        self._write(info.ljust(maxwidth), newline=start_suite)
            
    def _get_info(self, name, doc, maxwidth):
        if len(name) > maxwidth:
            return '...' + name[-maxwidth+3:]
        if doc == '':
            return name
        info = '%s :: %s' % (name, doc.splitlines()[0])
        if len(info) > maxwidth:
            info = info[:maxwidth-3] + '...'
        return info
            
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
