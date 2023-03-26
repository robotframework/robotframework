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

from pathlib import Path

from robot.parsing import get_init_model, get_model, get_resource_model
from robot.utils import FileReader, read_rest_data

from .settings import Defaults
from .transformers import ResourceBuilder, SuiteBuilder
from ..model import ResourceFile, TestSuite


class BaseParser:

    def parse_init_file(self, source: Path, defaults: Defaults = None):
        raise NotImplementedError

    def parse_suite_file(self, source: Path, defaults: Defaults = None):
        raise NotImplementedError

    def parse_resource_file(self, source: Path):
        raise NotImplementedError


class RobotParser(BaseParser):

    def __init__(self, lang=None, process_curdir=True):
        self.lang = lang
        self.process_curdir = process_curdir

    def parse_init_file(self, source, defaults=None):
        directory = source.parent
        name = TestSuite.name_from_source(directory)
        suite = TestSuite(name=name, source=directory)
        return self._build(suite, source, defaults, get_model=get_init_model)

    def parse_suite_file(self, source, defaults=None):
        name = TestSuite.name_from_source(source)
        suite = TestSuite(name=name, source=source)
        return self._build(suite, source, defaults)

    def parse_model(self, model, defaults=None):
        source = model.source
        name = TestSuite.name_from_source(source)
        suite = TestSuite(name=name, source=source)
        return self._build(suite, source, defaults, model)

    def _build(self, suite, source, defaults, model=None, get_model=get_model):
        if model is None:
            model = get_model(self._get_source(source), data_only=True,
                              curdir=self._get_curdir(source), lang=self.lang)
        SuiteBuilder(suite, defaults).build(model)
        return suite

    def _get_curdir(self, source):
        return str(source.parent).replace('\\', '\\\\') if self.process_curdir else None

    def _get_source(self, source):
        return source

    def parse_resource_file(self, source):
        model = get_resource_model(self._get_source(source), data_only=True,
                                   curdir=self._get_curdir(source), lang=self.lang)
        resource = ResourceFile(source=source)
        ResourceBuilder(resource).build(model)
        return resource


class RestParser(RobotParser):

    def _get_source(self, source):
        with FileReader(source) as reader:
            return read_rest_data(reader)


class JsonParser(BaseParser):

    def parse_suite_file(self, source: Path, defaults: Defaults = None):
        return TestSuite.from_json(source)

    def parse_init_file(self, source: Path, defaults: Defaults = None):
        return TestSuite.from_json(source)

    def parse_resource_file(self, source: Path):
        return ResourceFile.from_json(source)


class NoInitFileDirectoryParser(BaseParser):

    def parse_init_file(self, source, defaults=None):
        name = TestSuite.name_from_source(source)
        return TestSuite(name=name, source=source)
