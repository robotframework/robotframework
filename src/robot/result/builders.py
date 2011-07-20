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
import os.path
import re
from sys import platform
import codecs
import tempfile

import robot
from robot.output import LOGGER
from robot import utils
from robot.result.jsondatamodel import SeparatingWriter
from robot.version import get_full_version


def _get_webcontent_file(file):
    path = "robot/webcontent/%s" % file
    return _get_file_content_from_robot(path)

def _get_file_content_from_robot(path_inside_robot):
    is_jython  = platform.startswith('java')
    if not is_jython:
        return _get_local_robot_file(path_inside_robot)
    try:
        return _get_local_robot_file(path_inside_robot)
    except IOError:
        return _get_robot_file_from_jar(path_inside_robot)

def _get_local_robot_file(path_inside_robot):
    file_system_path = os.path.join(os.path.dirname(os.path.abspath(robot.__file__)),
                            '..',
                            os.path.normpath(path_inside_robot))
    with codecs.open(file_system_path, 'r', encoding='UTF-8') as file:
        return file.readlines()

def _get_robot_file_from_jar(path):
    import org.robotframework.RobotRunner as robot_class
    import java.io.InputStreamReader as InputStreamReader
    import java.io.BufferedReader as BufferedReader
    path_inside_jar = '/Lib/%s' % path
    res = robot_class.getResource(path_inside_jar)
    content = BufferedReader(InputStreamReader(res.openStream()))
    result = []
    while content.ready():
        result.append(content.readLine()+'\n')
    return result


class _Builder(object):

    def __init__(self, context):
        self._settings = context.settings
        self._context = context
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
        self._context.result_from_xml.serialize_output(output_file, log=not self._temp_file)
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
            self._context.result_from_xml.serialize_xunit(self._path)


class _HTMLFileBuilder(_Builder):
    _type = NotImplemented
    _template = NotImplemented

    def build(self):
        if self._path:
            self._context.data_model.set_settings(self._get_settings())
            self._format_data()
            if self._write_file():
                LOGGER.output_file(self._type, self._path)

    def _url_from_path(self, source, destination):
        if not destination:
            return None
        return utils.get_link_path(destination, os.path.dirname(source))

    def _write_file(self):
        try:
            with codecs.open(self._path, 'w', encoding='UTF-8') as outfile:
                writer = HTMLFileWriter(outfile, self._context.data_model)
                tmpl = _get_webcontent_file(self._template)
                for line in tmpl:
                    writer.line(line)
        except EnvironmentError, err:
            LOGGER.error("Opening '%s' failed: %s"
                         % (err.filename, err.strerror))
            return False
        return True


class LogBuilder(_HTMLFileBuilder):
    _type = 'Log'
    _template = 'log.html'

    def _format_data(self):
        if self._context.data_model._split_results:
            self._write_split_tests()

    def _write_split_tests(self):
        basename = os.path.splitext(self._path)[0]
        for index, (keywords, strings) in enumerate(self._context.data_model._split_results):
            index += 1  # enumerate accepts start index only in Py 2.6+
            self._write_test(index, keywords, strings, '%s-%d.js' % (basename, index))

    def _write_test(self, index, keywords, strings, path):
        # TODO: Refactor heavily - ask Jussi or Peke for more details
        with codecs.open(path, 'w', encoding='UTF-8') as outfile:
            writer = SeparatingWriter(outfile, '')
            writer.dump_json('window.keywords%d = ' % index, keywords)
            writer.dump_json('window.strings%d = ' % index, strings)
            writer.write('window.fileLoading.notify("%s");\n' % os.path.basename(path))

    def _get_settings(self):
        return  {
            'title': self._settings['LogTitle'],
            'reportURL': self._url_from_path(self._path,
                                             self._parse_file('Report')),
            'splitLogBase': os.path.basename(os.path.splitext(self._path)[0])
        }


class ReportBuilder(_HTMLFileBuilder):
    _type = 'Report'
    _template = 'report.html'

    def _format_data(self):
        self._context.data_model.remove_errors()
        self._context.data_model.remove_keywords()

    def _get_settings(self):
        return {
            'title': self._settings['ReportTitle'],
            'background' : self._resolve_background_colors(),
            'logURL': self._url_from_path(self._path,
                                          self._parse_file('Log'))
        }

    def _resolve_background_colors(self):
        colors = self._settings['ReportBackground']
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
        elif self._is_meta_generator_line(line):
            self._write_meta_generator()
        else:
            self._write(line)

    def _is_output_js(self, line):
        return line.startswith('<!-- OUTPUT JS -->')

    def _is_css_line(self, line):
        return line.startswith('<link rel')

    def _is_js_line(self, line):
        return line.startswith('<script type="text/javascript" src=')

    def _is_meta_generator_line(self, line):
        return line.startswith('<meta name="Generator" content=')

    def _write_meta_generator(self):
        self._write('<meta name="Generator" content="%s">\n'
                    % get_full_version('Robot Framework'))

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
        self._write_file_content(filename_matcher.search(line).group(1))

    def _write(self, content):
        self._outfile.write(content)

    def _write_tag(self, tag_name, attrs, content_writer):
        # TODO: Use utils.HtmlWriter instead. It also eases giving attrs here.
        self._write('<%s %s>\n' % (tag_name, attrs))
        content_writer()
        self._write('</%s>\n\n' % tag_name)

    def _write_file_content(self, source):
        content = _get_webcontent_file(source)
        for line in content:
            self._write(line)
        self._write('\n')
