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
import codecs

from robot.errors import DataError
from robot.output import LOGGER
from robot.result.serializer import RebotXMLWriter
from robot.version import get_full_version
from robot import utils

from .jswriter import JsResultWriter, SplitLogWriter
from .xunitwriter import XUnitWriter
from .webcontentfile import WebContentFile


class _Builder(object):

    def __init__(self, model):
        self._model = model

    def build(self, *args):
        raise NotImplementedError(self.__class__.__name__)


class OutputBuilder(_Builder):

    def build(self, path):
        writer = RebotXMLWriter(path)
        self._model.visit(writer)
        LOGGER.output_file('Output', path)


class XUnitBuilder(_Builder):

    def build(self, path):
        writer = XUnitWriter(path) # TODO: handle (with atests) error in opening output file
        try:
            self._model.visit(writer)
        except:
            raise DataError("Writing XUnit result file '%s' failed: %s" %
                            (path, utils.get_error_message()))
        finally:
            writer.close()
        LOGGER.output_file('XUnit', path)


class _HTMLFileBuilder(_Builder):

    def _write_file(self, output, config, template):
        outfile = codecs.open(output, 'w', encoding='UTF-8') \
            if isinstance(output, basestring) else output  # isinstance is unit test hook
        with outfile:
            writer = HtmlFileWriter(output, self._model, config)
            writer.write(template)


class LogBuilder(_HTMLFileBuilder):

    def build(self, output, config):
        try:
            self._write_file(output, config, 'log.html')
            self._write_split_logs_if_needed(output)
        except EnvironmentError, err:
            # Cannot use err.filename due to http://bugs.jython.org/issue1825
            # and thus error has wrong file name if writing split log fails.
            LOGGER.error("Writing log file '%s' failed: %s" % (output, err.strerror))
        else:
            LOGGER.output_file('Log', output)

    def _write_split_logs_if_needed(self, output):
        base = os.path.splitext(output)[0] if isinstance(output, basestring) else ''
        for index, (keywords, strings) in enumerate(self._model.split_results):
            index += 1  # enumerate accepts start index only in Py 2.6+
            self._write_split_log(index, keywords, strings, '%s-%d.js' % (base, index))

    def _write_split_log(self, index, keywords, strings, path):
        with codecs.open(path, 'w', encoding='UTF-8') as outfile:
            writer = SplitLogWriter(outfile)
            writer.write(keywords, strings, index, os.path.basename(path))


class ReportBuilder(_HTMLFileBuilder):

    def build(self, path, config):
        try:
            self._write_file(path, config, 'report.html')
        except EnvironmentError, err:
            LOGGER.error("Writing report file '%s' failed: %s" % (path, err.strerror))
        else:
            LOGGER.output_file('Report', path)


class HtmlFileWriter(object):
    _js_file_matcher = re.compile('src=\"([^\"]+)\"')
    _css_file_matcher = re.compile('href=\"([^\"]+)\"')
    _css_media_matcher = re.compile('media=\"([^\"]+)\"')

    def __init__(self, outfile, model, config):
        self._outfile = outfile
        self._model = model
        self._config = config

    def write(self, template):
        for line in WebContentFile(template):
            self._write_line(line)

    def _write_line(self, line):
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
        return line.startswith('<link rel="stylesheet"')

    def _is_js_line(self, line):
        return line.startswith('<script type="text/javascript" src=')

    def _is_meta_generator_line(self, line):
        return line.startswith('<meta name="Generator" content=')

    def _write_meta_generator(self):
        #TODO: Generating name should be rebot when using rebot
        self._write('<meta name="Generator" content="%s">\n'
                    % get_full_version('Robot Framework'))

    def _write_output_js(self):
        JsResultWriter(self._outfile).write(self._model, self._config)

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
        for line in WebContentFile(source):
            self._write(line)
        self._write('\n')
