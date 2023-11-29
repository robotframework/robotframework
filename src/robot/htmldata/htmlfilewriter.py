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

import re
from abc import ABC, abstractmethod
from io import TextIOBase
from pathlib import Path

from robot.utils import HtmlWriter
from robot.version import get_full_version

from .template import HtmlTemplate


class HtmlFileWriter:

    def __init__(self, output: TextIOBase, model_writer: 'ModelWriter'):
        self.output = output
        self.model_writer = model_writer

    def write(self, template: 'Path|str'):
        if not isinstance(template, Path):
            template = Path(template)
        writers = self._get_writers(template.parent)
        for line in HtmlTemplate(template):
            for writer in writers:
                if writer.handles(line):
                    writer.write(line)
                    break

    def _get_writers(self, base_dir: Path):
        writer = HtmlWriter(self.output)
        return (self.model_writer,
                JsFileWriter(writer, base_dir),
                CssFileWriter(writer, base_dir),
                GeneratorWriter(writer),
                LineWriter(self.output))


class Writer(ABC):
    handles_line = None

    def handles(self, line: str):
        return line.startswith(self.handles_line)

    @abstractmethod
    def write(self, line: str):
        raise NotImplementedError


class ModelWriter(Writer, ABC):
    handles_line = '<!-- JS MODEL -->'


class LineWriter(Writer):

    def __init__(self, output: TextIOBase):
        self.output = output

    def handles(self, line: str):
        return True

    def write(self, line: str):
        self.output.write(line + '\n')


class GeneratorWriter(Writer):
    handles_line = '<meta name="Generator" content='

    def __init__(self, writer: HtmlWriter):
        self.writer = writer

    def write(self, line: str):
        version = get_full_version('Robot Framework')
        self.writer.start('meta', {'name': 'Generator', 'content': version})


class InliningWriter(Writer, ABC):

    def __init__(self, writer: HtmlWriter, base_dir: Path):
        self.writer = writer
        self.base_dir = base_dir

    def inline_file(self, path: 'Path|str', tag: str, attrs: dict):
        self.writer.start(tag, attrs)
        for line in HtmlTemplate(self.base_dir / path):
            self.writer.content(line, escape=False, newline=True)
        self.writer.end(tag)


class JsFileWriter(InliningWriter):
    handles_line = '<script type="text/javascript" src='

    def write(self, line: str):
        src = re.search('src="([^"]+)"', line).group(1)
        self.inline_file(src, 'script', {'type': 'text/javascript'})


class CssFileWriter(InliningWriter):
    handles_line = '<link rel="stylesheet"'

    def write(self, line: str):
        href, media = re.search('href="([^"]+)" media="([^"]+)"', line).groups()
        self.inline_file(href, 'style', {'media': media})
