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
import os
import re
import codecs
import tempfile

import robot
from robot.output import LOGGER
from robot import utils

WEBCONTENT_PATH = os.path.join(os.path.dirname(robot.__file__), 'webcontent')


class _Builder(object):

    def __init__(self, data, settings):
        self._settings = settings
        self._data = data
        self._path = self._parse_file(self._type)

    def build(self):
        raise NotImplementedError(self.__class__.__name__)

    def _parse_file(self, name):
        value = self._settings[name]
        return value if value != 'NONE' else None


class OutputBuilder(_Builder):
    _type = 'Output'
    _temp_file = None

    def build(self):
        output_file = self._output_file()
        self._data.serialize_output(output_file, log=not self._temp_file)
        return output_file

    def _output_file(self):
        if self._path:
            return self._path
        handle, output_file = tempfile.mkstemp(suffix='.xml', prefix='rebot-')
        os.close(handle)
        self._temp_file = output_file
        return output_file

    def finalize(self):
        if self._temp_file:
            os.remove(self._temp_file)


class XUnitBuilder(_Builder):
    _type = 'XUnitFile'

    def build(self):
        if self._path:
            self._data.serialize_xunit(self._path)


class _HTMLFileBuilder(_Builder):
    _type = NotImplemented

    def build(self):
        if self._path:
            self._data.set_settings(self._get_settings())
            self._build()
            LOGGER.output_file(self._type, self._path)

    def _url_from_path(self, source, destination):
        if not destination:
            return None
        return utils.get_link_path(destination, os.path.dirname(source))

    def _write_file(self):
        with codecs.open(self._path, 'w', encoding='UTF-8') as outfile:
            writer = HTMLFileWriter(outfile, self._data)
            with open(self._template, 'r') as tmpl:
                for line in tmpl:
                    writer.line(line)


class LogBuilder(_HTMLFileBuilder):
    _type = 'Log'
    _template = os.path.join(WEBCONTENT_PATH,'log.html')

    def _build(self):
        self._write_file()

    def _get_settings(self):
        return {
            'title': self._settings['LogTitle'],
            'reportURL': self._url_from_path(self._path,
                                             self._parse_file('Report'))
        }


class ReportBuilder(_HTMLFileBuilder):
    _type = 'Report'
    _template = os.path.join(WEBCONTENT_PATH, 'report.html')

    def _build(self):
        self._data.remove_errors()
        self._data.remove_keywords()
        self._write_file()

    def _get_settings(self):
        return {
            'title': self._settings['ReportTitle'],
            'background' : self._resolve_background_colors(),
            'logURL': self._url_from_path(self._path,
                                          self._parse_file('Log'))
        }

    def _resolve_background_colors(self):
        color_str = self._settings['ReportBackground']
        if color_str and color_str.count(':') not in [1, 2]:
            LOGGER.error("Invalid background color '%s'." % color_str)
            color_str = None
        if not color_str:
            color_str = '#99FF66:#FF3333'
        colors = color_str.split(':', 2)
        if len(colors) == 2:
            colors.insert(1, colors[0])
        return {'pass': colors[0], 'nonCriticalFail': colors[1], 'fail': colors[2]}


class HTMLFileWriter(object):
    _js_file_matcher = re.compile('src=\"([^\"]+)\"')
    _css_file_matcher = re.compile('href=\"([^\"]+)\"')
    _css_media_matcher = re.compile('media=\"([^\"]+)\"')

    def __init__(self, outfile, output):
        self._outfile = outfile
        self._output = output

    def line(self, line):
        if self._is_output_js(line):
            self._write_output_js()
        elif self._is_js_line(line):
            self._inline_js_file(line)
        elif self._is_css_line(line):
            self._inline_css_file(line)
        else:
            self._write(line)

    def _is_output_js(self, line):
        return line.startswith('<!-- OUTPUT JS -->')

    def _is_css_line(self, line):
        return line.startswith('<link rel')

    def _is_js_line(self, line):
        return line.startswith('<script type="text/javascript" src=')

    def _write_output_js(self):
        separator = '</script>\n<script type="text/javascript">\n'
        self._write_tag('script', 'type="text/javascript"',
                        lambda: self._output.write_to(self._outfile, separator))

    def _inline_js_file(self, line):
        self._write_tag('script', 'type="text/javascript"',
                        lambda: self._inline_file(line, self._js_file_matcher))

    def _inline_css_file(self, line):
        attrs = 'type="text/css" media="%s"' % self._parse_css_media_type(line)
        self._write_tag('style', attrs,
                        lambda: self._inline_file(line, self._css_file_matcher))

    def _parse_css_media_type(self, line):
        return self._css_media_matcher.search(line).group(1)

    def _inline_file(self, line, filename_matcher):
        file_name = self._file_name(line, filename_matcher)
        self._write_file_content(file_name)

    def _file_name(self, line, filename_regexp):
        return self._relative_path(filename_regexp.search(line).group(1))

    def _relative_path(self, filename):
        return os.path.join(WEBCONTENT_PATH, filename.replace('/', os.path.sep))

    def _write(self, content):
        self._outfile.write(content)

    def _write_tag(self, tag_name, attrs, content_writer):
        self._write('<%s %s>\n' % (tag_name, attrs))
        content_writer()
        self._write('</%s>\n\n' % tag_name)

    def _write_file_content(self, source):
        with codecs.open(source, 'r', encoding='UTF-8') as content:
            for line in content:
                self._write(line)
        self._write('\n')
