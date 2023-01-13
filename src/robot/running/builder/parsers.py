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

import os
from ast import NodeVisitor
from pathlib import Path

from robot.errors import DataError
from robot.output import LOGGER
from robot.parsing import get_model, get_resource_model, get_init_model, Token
from robot.utils import FileReader, read_rest_data

from .settings import Defaults
from .transformers import SuiteBuilder, SettingsBuilder, ResourceBuilder
from ..model import TestSuite, ResourceFile


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

    def build_suite(self, model, name=None, defaults=None):
        source = model.source
        name = name or TestSuite.name_from_source(source)
        suite = TestSuite(name=name, source=source)
        return self._build(suite, source, defaults, model)

    def _build(self, suite, source, defaults, model=None, get_model=get_model):
        if defaults is None:
            defaults = Defaults()
        if model is None:
            model = get_model(self._get_source(source), data_only=True,
                              curdir=self._get_curdir(source), lang=self.lang)
        ErrorReporter(source).visit(model)
        SettingsBuilder(suite, defaults).visit(model)
        SuiteBuilder(suite, defaults).visit(model)
        suite.rpa = self._get_rpa_mode(model)
        return suite

    def _get_curdir(self, source):
        if not self.process_curdir:
            return None
        return os.path.dirname(source).replace('\\', '\\\\')

    def _get_source(self, source):
        return source

    def parse_resource_file(self, source):
        model = get_resource_model(self._get_source(source), data_only=True,
                                   curdir=self._get_curdir(source), lang=self.lang)
        resource = ResourceFile(source=source)
        ErrorReporter(source).visit(model)
        ResourceBuilder(resource).visit(model)
        return resource

    def _get_rpa_mode(self, data):
        if not data:
            return None
        tasks = [s.tasks for s in data.sections if hasattr(s, 'tasks')]
        if all(tasks) or not any(tasks):
            return tasks[0] if tasks else None
        raise DataError('One file cannot have both tests and tasks.')


class RestParser(RobotParser):

    def _get_source(self, source):
        with FileReader(source) as reader:
            return read_rest_data(reader)


class NoInitFileDirectoryParser(BaseParser):

    def parse_init_file(self, source, defaults=None):
        name = TestSuite.name_from_source(source)
        return TestSuite(name=name, source=source)


class ErrorReporter(NodeVisitor):

    def __init__(self, source):
        self.source = source

    def visit_Error(self, node):
        fatal = node.get_token(Token.FATAL_ERROR)
        if fatal:
            raise DataError(self._format_message(fatal))
        for error in node.get_tokens(Token.ERROR):
            LOGGER.error(self._format_message(error))

    def _format_message(self, token):
        return f"Error in file '{self.source}' on line {token.lineno}: {token.error}"
