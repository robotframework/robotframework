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

from abc import ABC
from pathlib import Path

from robot.conf import Languages
from robot.parsing import File, get_init_model, get_model, get_resource_model
from robot.utils import FileReader, read_rest_data

from .settings import Defaults
from .transformers import ResourceBuilder, SuiteBuilder
from ..model import ResourceFile, TestSuite


class Parser(ABC):

    def parse_suite_file(self, source: Path, defaults: Defaults) -> TestSuite:
        raise TypeError(f'{type(self).__name__} does not support suite files')

    def parse_init_file(self, source: Path, defaults: Defaults) -> TestSuite:
        raise TypeError(f'{type(self).__name__} does not support initialization files')

    def parse_resource_file(self, source: Path) -> ResourceFile:
        raise TypeError(f'{type(self).__name__} does not support resource files')


class RobotParser(Parser):

    def __init__(self, lang: Languages = None, process_curdir: bool = True):
        self.lang = lang
        self.process_curdir = process_curdir

    def parse_suite_file(self, source: Path, defaults: Defaults) -> TestSuite:
        model = get_model(self._get_source(source), data_only=True,
                          curdir=self._get_curdir(source), lang=self.lang)
        suite = TestSuite(name=TestSuite.name_from_source(source), source=source)
        SuiteBuilder(suite, defaults).build(model)
        return suite

    def parse_init_file(self, source: Path, defaults: Defaults) -> TestSuite:
        model = get_init_model(self._get_source(source), data_only=True,
                               curdir=self._get_curdir(source), lang=self.lang)
        directory = source.parent
        suite = TestSuite(name=TestSuite.name_from_source(directory), source=directory)
        SuiteBuilder(suite, defaults).build(model)
        return suite

    def parse_model(self, model: File) -> TestSuite:
        source = model.source
        suite = TestSuite(name=TestSuite.name_from_source(source), source=source)
        SuiteBuilder(suite).build(model)
        return suite

    def _get_curdir(self, source: Path) -> 'str|None':
        return str(source.parent).replace('\\', '\\\\') if self.process_curdir else None

    def _get_source(self, source: Path) -> 'Path|str':
        return source

    def parse_resource_file(self, source: Path) -> ResourceFile:
        model = get_resource_model(self._get_source(source), data_only=True,
                                   curdir=self._get_curdir(source), lang=self.lang)
        resource = ResourceFile(source=source)
        ResourceBuilder(resource).build(model)
        return resource


class RestParser(RobotParser):

    def _get_source(self, source: Path) -> str:
        with FileReader(source) as reader:
            return read_rest_data(reader)


class JsonParser(Parser):

    def parse_suite_file(self, source: Path, defaults: Defaults) -> TestSuite:
        return TestSuite.from_json(source)

    def parse_init_file(self, source: Path, defaults: Defaults) -> TestSuite:
        return TestSuite.from_json(source)

    # FIXME: Resource imports don't otherwise support JSON yet!
    def parse_resource_file(self, source: Path) -> ResourceFile:
        return ResourceFile.from_json(source)


class NoInitFileDirectoryParser(Parser):

    def parse_init_file(self, source: Path, defaults: Defaults) -> TestSuite:
        return TestSuite(name=TestSuite.name_from_source(source), source=source)
