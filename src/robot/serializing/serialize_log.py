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

PATH = os.path.join(os.path.dirname(robot.__file__),'webcontent')
LOG_TEMPLATE = os.path.join(PATH,'log.html')
REPORT_TEMPLATE = os.path.join(PATH, 'report.html')
JS_FILE_REGEXP = re.compile('src=\"([^\"]+)\"')
CSS_FILE_REGEXP = re.compile('href=\"([^\"]+)\"')
CSS_MEDIA_TYPE_REGEXP = re.compile('media=\"([^\"]+)\"')

def serialize_log(test_output_datamodel, log_path, title=None):
    if log_path is None:
        return
    _build_file(log_path, test_output_datamodel, title, None, LOG_TEMPLATE)

def serialize_report(test_output_datamodel, report_path, title=None, background=None, log_path=None):
    if report_path is None:
        return
    relative_log_path = _build_relative_log_path(report_path, log_path)
    _build_file(report_path, test_output_datamodel, title, _resolve_background_colors(background), REPORT_TEMPLATE, relative_log_path)

def _build_relative_log_path(report, log):
    if not log:
        return None
    return utils.get_link_path(log, os.path.dirname(report))

def _build_file(outpath, test_output_datamodel, title, background, template, log_path=None):
    with codecs.open(outpath, 'w', encoding='UTF-8') as outfile:
        populator = _Populator(outfile, test_output_datamodel, title, background, log_path)
        with open(template, 'r') as templ:
            for line in templ:
                populator.line(line)

def _resolve_background_colors(color_str):
    if color_str and color_str.count(':') not in [1, 2]:
        #LOGGER.error("Invalid background color '%s'." % color_str)
        color_str = None
    if not color_str:
        color_str = '#99FF66:#FF3333'
    colors = color_str.split(':', 2)
    return colors if len(colors) == 3 else [colors[0], colors[0], colors[1]]


class _Populator(object):

    def __init__(self, log, test_output_datamodel, title, background, log_path=None):
        self._log = log
        self._log_path=log_path
        self._test_output_datamodel = test_output_datamodel
        self._title = title
        self._parsing = self._normal_parsing
        self._backgrounds = {"/* BACKGROUND: critical pass */":     background[0] if background else None,
                             "/* BACKGROUND: non critical fail */": background[1] if background else None,
                             "/* BACKGROUND: critical fail */":     background[2] if background else None}

    def line(self, line):
        self._parsing(line)

    def _normal_parsing(self, line):
        if self._is_begin_scripts(line):
            self._start_script()
        elif self._is_title_line_to_handle(line):
            self._write_title()
        elif self._is_background_line_to_handle(line):
            self._write_background(line)
        elif self._is_log_path_line_to_handle(line):
            self._replace_log_path(line)
        else:
            self._log.write(line)

    def _is_begin_scripts(self, line):
        return line == '<!-- BEGIN SCRIPTS -->\n'

    def _start_script(self):
        self._parsing = self._in_script

    def _is_title_line_to_handle(self, line):
        return self._title is not None and line.startswith('<title>')

    def _write_title(self):
        self._log.write('<title>%s</title>\n' % self._title)

    def _is_background_line_to_handle(self, line):
        for marker in self._backgrounds:
            if marker in line:
                return True
        return False

    def _write_background(self, line):
        for marker in self._backgrounds:
            if marker in line:
                self._log.write("    background: %s;\n" % self._backgrounds[marker])

    def _is_log_path_line_to_handle(self, line):
        return self._log_path and 'log.html' in line

    def _replace_log_path(self, line):
        self._log.write(line.replace('log.html', self._log_path))

    def _in_script(self, line):
        if self._is_end_scripts(line):
            self._end_script()
        elif self._is_output_js(line):
            self._write_output_js()
        elif self._is_css_line(line):
            self._write_lines_css(line)
        else:
            self._write_lines_js(line)

    def _is_end_scripts(self, line):
        return line == '<!-- END SCRIPTS -->\n'

    def _end_script(self):
        self._parsing = self._normal_parsing

    def _is_output_js(self, line):
        return line.startswith('<!-- OUTPUT JS -->')

    def _is_css_line(self, line):
        return line.startswith('<link rel')

    def _write_output_js(self):
        self._log.write('<script type="text/javascript">\n')
        self._test_output_datamodel.write_to(self._log)
        self._log.write('</script>\n\n')

    def _write_lines_css(self, line):
        self._log.write('<style type="text/css" media="%s">\n' % self._parse_css_media_type(line))
        self._write_from_file(self._parse_css_file_name(line))
        self._log.write('</style>\n\n')

    def _parse_css_media_type(self, line):
        return CSS_MEDIA_TYPE_REGEXP.search(line).group(1)

    def _write_lines_js(self, line):
        self._log.write('<script type="text/javascript">\n')
        self._write_from_file(self._parse_js_file_name(line))
        self._log.write('</script>\n\n')

    def _parse_js_file_name(self, line):
        return os.path.join(PATH, JS_FILE_REGEXP.search(line).group(1).replace('/', os.path.sep))

    def _parse_css_file_name(self, line):
        return os.path.join(PATH, CSS_FILE_REGEXP.search(line).group(1).replace('/', os.path.sep))

    def _write_from_file(self, source):
        with codecs.open(source, 'r', encoding='UTF-8') as content:
            for line in content:
                self._log.write(line)
        self._log.write('\n')


if __name__ == '__main__':
    import jsparser
    jsparser.parse('output.xml', 'output.js')
    serialize_log('output.js', 'logjsx.html')
