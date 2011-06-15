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

from __future__ import with_statement
import codecs
import os
import re

import robot
from robot import utils

BASEPATH = os.path.join(os.path.dirname(robot.__file__), 'webcontent')
LOG_TEMPLATE = os.path.join(BASEPATH,'log.html')
REPORT_TEMPLATE = os.path.join(BASEPATH, 'report.html')
JS_FILE_REGEXP = re.compile('src=\"([^\"]+)\"')
CSS_FILE_REGEXP = re.compile('href=\"([^\"]+)\"')
CSS_MEDIA_TYPE_REGEXP = re.compile('media=\"([^\"]+)\"')


def serialize_log(output, log_path):
    if log_path is None:
        return
    _build_file(log_path, output, LOG_TEMPLATE)

def serialize_report(output, report_path):
    if report_path is None:
        return
    _build_file(report_path, output, REPORT_TEMPLATE)

def _relative_log_path(report, log):
    if not log:
        return None
    return utils.get_link_path(log, os.path.dirname(report))

def _build_file(outpath, output, template):
    with codecs.open(outpath, 'w', encoding='UTF-8') as outfile:
        builder = OutputFileBuilder(outfile, output)
        with open(template, 'r') as tmpl:
            for line in tmpl:
                builder.line(line)


class OutputFileBuilder(object):

    def __init__(self, outfile, output):
        self._outfile = outfile
        self._output = output

    def line(self, line):
        if self._is_output_js(line):
            self._write_output_js()
        elif self._is_css_line(line):
            self._write_lines_css(line)
        elif self._is_js_line(line):
            self._write_lines_js(line)
        else:
            self._outfile.write(line)

    def _is_output_js(self, line):
        return line.startswith('<!-- OUTPUT JS -->')

    def _is_css_line(self, line):
        return line.startswith('<link rel')

    def _is_js_line(self, line):
        return line.startswith('<script type="text/javascript" src=')

    def _write_output_js(self):
        self._outfile.write('<script type="text/javascript">\n')
        self._output.write_to(self._outfile)
        self._outfile.write('</script>\n\n')

    def _write_lines_css(self, line):
        self._outfile.write('<style type="text/css" media="%s">\n'
                            % self._parse_css_media_type(line))
        self._write_from_file(self._parse_file_name(line, CSS_FILE_REGEXP))
        self._outfile.write('</style>\n\n')

    def _parse_css_media_type(self, line):
        return CSS_MEDIA_TYPE_REGEXP.search(line).group(1)

    def _write_lines_js(self, line):
        self._outfile.write('<script type="text/javascript">\n')
        self._write_from_file(self._parse_file_name(line, JS_FILE_REGEXP))
        self._outfile.write('</script>\n\n')

    def _parse_file_name(self, line, filename_regexp):
        return self._relative_path(filename_regexp.search(line).group(1))

    def _relative_path(self, filename):
        return os.path.join(BASEPATH, filename.replace('/', os.path.sep))

    def _write_from_file(self, source):
        with codecs.open(source, 'r', encoding='UTF-8') as content:
            for line in content:
                self._outfile.write(line)
        self._outfile.write('\n')
