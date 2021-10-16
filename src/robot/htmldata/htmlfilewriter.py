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

import os.path
import re

from robot.utils import HtmlWriter
from robot.version import get_full_version

from .template import HtmlTemplate


class HtmlFileWriter:

    def __init__(self, output, model_writer):
        self._output = output
        self._model_writer = model_writer

    def write(self, template):
        writers = self._get_writers(os.path.dirname(template))
        for line in HtmlTemplate(template):
            for writer in writers:
                if writer.handles(line):
                    writer.write(line)
                    break

    def _get_writers(self, base_dir):
        html_writer = HtmlWriter(self._output)
        return (self._model_writer,
                JsFileWriter(html_writer, base_dir),
                CssFileWriter(html_writer, base_dir),
                GeneratorWriter(html_writer),
                LineWriter(self._output))


class _Writer:
    _handles_line = None

    def handles(self, line):
        return line.startswith(self._handles_line)

    def write(self, line):
        raise NotImplementedError


class ModelWriter(_Writer):
    _handles_line = '<!-- JS MODEL -->'


class LineWriter(_Writer):

    def __init__(self, output):
        self._output = output

    def handles(self, line):
        return True

    def write(self, line):
        self._output.write(line + '\n')


class GeneratorWriter(_Writer):
    _handles_line = '<meta name="Generator" content='

    def __init__(self, html_writer):
        self._html_writer = html_writer

    def write(self, line):
        version = get_full_version('Robot Framework')
        self._html_writer.start('meta', {'name': 'Generator', 'content': version})


class _InliningWriter(_Writer):

    def __init__(self, html_writer, base_dir):
        self._html_writer = html_writer
        self._base_dir = base_dir

    def _inline_file(self, filename, tag, attrs):
        self._html_writer.start(tag, attrs)
        for line in HtmlTemplate(os.path.join(self._base_dir, filename)):
            self._html_writer.content(line, escape=False, newline=True)
        self._html_writer.end(tag)


class JsFileWriter(_InliningWriter):
    _handles_line = '<script type="text/javascript" src='
    _source_file = re.compile('src=\"([^\"]+)\"')

    def write(self, line):
        name = self._source_file.search(line).group(1)
        self._inline_file(name, 'script', {'type': 'text/javascript'})


class CssFileWriter(_InliningWriter):
    _handles_line = '<link rel="stylesheet"'
    _source_file = re.compile('href=\"([^\"]+)\"')
    _media_type = re.compile('media=\"([^\"]+)\"')

    def write(self, line):
        name = self._source_file.search(line).group(1)
        media = self._media_type.search(line).group(1)
        self._inline_file(name, 'style', {'type': 'text/css', 'media': media})
