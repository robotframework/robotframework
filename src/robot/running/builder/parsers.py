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

from robot.errors import DataError
from robot.output import LOGGER
from robot.parsing import get_model, get_resource_model, get_init_model, Token
from robot.utils import FileReader, read_rest_data

from .testsettings import TestDefaults
from .transformers import SuiteBuilder, SettingsBuilder, ResourceBuilder
from ..model import TestSuite, ResourceFile


class BaseParser(object):

    def parse_init_file(self, source, defaults=None):
        raise NotImplementedError

    def parse_suite_file(self, source, defaults=None):
        raise NotImplementedError

    def parse_resource_file(self, source):
        raise NotImplementedError


class RobotParser(BaseParser):

    def __init__(self, process_curdir=True):
        self.process_curdir = process_curdir

    def parse_init_file(self, source, defaults=None):
        directory = os.path.dirname(source)
        suite = TestSuite(name=format_name(directory), source=directory)
        return self._build(suite, source, defaults, get_model=get_init_model)

    def parse_suite_file(self, source, defaults=None):
        suite = TestSuite(name=format_name(source), source=source)
        return self._build(suite, source, defaults)

    def build_suite(self, model, name=None, defaults=None):
        source = model.source
        suite = TestSuite(name=name or format_name(source), source=source)
        return self._build(suite, source, defaults, model)

    def _build(self, suite, source, defaults, model=None, get_model=get_model):
        if defaults is None:
            defaults = TestDefaults()
        if model is None:
            model = get_model(self._get_source(source), data_only=True,
                              curdir=self._get_curdir(source))
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
                                   curdir=self._get_curdir(source))
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
        return TestSuite(name=format_name(source), source=source)


def format_name(source):
    def strip_possible_prefix_from_name(name):
        return name.split('__', 1)[-1]

    def format_name(name):
        name = strip_possible_prefix_from_name(name)
        name = name.replace('_', ' ').strip()
        return name.title() if name.islower() else name

    if source is None:
        return None
    if os.path.isdir(source):
        basename = os.path.basename(source)
    else:
        basename = os.path.splitext(os.path.basename(source))[0]
    return format_name(basename)


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
        return ("Error in file '%s' on line %s: %s"
                % (self.source, token.lineno, token.error))
