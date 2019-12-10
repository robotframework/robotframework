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
from robot.parsing import get_test_case_file_ast, get_resource_file_ast

from .testsettings import TestDefaults
from .transformers import SuiteBuilder, SettingsBuilder, ResourceBuilder
from .suitestructure import SuiteStructureBuilder, SuiteStructureVisitor
from ..model import TestSuite, ResourceFile


class TestSuiteBuilder(object):

    def __init__(self, include_suites=None, extension=None, rpa=None,
                 allow_empty_suite=False):
        self.rpa = rpa
        self.include_suites = include_suites
        self.extension = extension
        self.allow_empty_suite = allow_empty_suite

    def build(self, *paths):
        """
        :param paths: Paths to test data files or directories.
        :return: :class:`~robot.running.model.TestSuite` instance.
        """
        structure = SuiteStructureBuilder(self.include_suites,
                                          self.extension).build(paths)
        parser = SuiteStructureParser(self.rpa)
        suite = parser.parse(structure)
        if not self.include_suites and not self.allow_empty_suite:
            self._validate_test_counts(suite, multisource=len(paths) > 1)
        # TODO: do we need `preserve_direct_children`?
        suite.remove_empty_suites(preserve_direct_children=len(paths) > 1)
        return suite

    def _validate_test_counts(self, suite, multisource=False):
        def validate(suite):
            if not suite.has_tests:
                raise DataError("Suite '%s' contains no tests or tasks."
                                % suite.name)
        if not multisource:
            validate(suite)
        else:
            for s in suite.suites:
                validate(s)


class ResourceFileBuilder(object):

    def build(self, path):
        LOGGER.info("Parsing resource file '%s'." % path)
        data = get_resource_file_ast(path)
        return build_resource(data, path)


class SuiteStructureParser(SuiteStructureVisitor):

    def __init__(self, rpa=None):
        self.rpa = rpa
        self._rpa_given = rpa is not None
        self.suite = None
        self._stack = []

    def parse(self, structure):
        structure.visit(self)
        self.suite.rpa = self.rpa
        return self.suite

    def visit_file(self, structure):
        LOGGER.info("Parsing file '%s'." % structure.source)
        suite, _ = self._build_suite(structure)
        if self._stack:
            self._stack[-1][0].suites.append(suite)
        else:
            self.suite = suite

    def start_directory(self, structure):
        if structure.source:
            LOGGER.info("Parsing directory '%s'." % structure.source)
        suite, defaults = self._build_suite(structure)
        if self.suite is None:
            self.suite = suite
        else:
            self._stack[-1][0].suites.append(suite)
        self._stack.append((suite, defaults))

    def end_directory(self, structure):
        suite, _ = self._stack.pop()
        if suite.rpa is None and suite.suites:
            suite.rpa = suite.suites[0].rpa

    def _build_suite(self, structure):
        defaults = self._stack[-1][-1] if self._stack else None
        source = structure.source
        datapath = source if not structure.is_directory else structure.init_file
        try:
            suite, defaults = build_suite(source, datapath, defaults)
            self._validate_execution_mode(suite)
        except DataError as err:
            raise DataError("Parsing '%s' failed: %s" % (source, err.message))
        if structure.is_directory and suite.tests:
            LOGGER.error("Test suite initialization file in '%s' cannot "
                         "contain tests or tasks." % source)
            suite.tests.clear()
        return suite, defaults

    def _validate_execution_mode(self, suite):
        if self._rpa_given:
            suite.rpa = self.rpa
        elif suite.rpa is None:
            pass
        elif self.rpa is None:
            self.rpa = suite.rpa
        elif self.rpa is not suite.rpa:
            this, that = ('tasks', 'tests') if suite.rpa else ('tests', 'tasks')
            raise DataError("Conflicting execution modes. File has %s "
                            "but files parsed earlier have %s. Fix headers "
                            "or use '--rpa' or '--norpa' options to set the "
                            "execution mode explicitly." % (this, that))


def build_suite(source, datapath=None, parent_defaults=None):
    suite = TestSuite(name=format_name(source), source=source)
    defaults = TestDefaults(parent_defaults)
    if datapath:
        ast = get_test_case_file_ast(datapath)
        ErrorLogger(datapath).visit(ast)
        SettingsBuilder(suite, defaults).visit(ast)
        SuiteBuilder(suite, defaults).visit(ast)
        if not suite.tests:
            LOGGER.info("Data source '%s' has no tests or tasks." % datapath)
        suite.rpa = _get_rpa_mode(ast)
    return suite, defaults


def _get_rpa_mode(data):
    if not data:
        return None
    tasks = [s.tasks for s in data.sections if hasattr(s, 'tasks')]
    if all(tasks) or not any(tasks):
        return tasks[0] if tasks else None
    raise DataError('One file cannot have both tests and tasks.')


def build_resource(data, source):
    resource = ResourceFile(source=source)
    if data.data_sections:
        ErrorLogger(source).visit(data)
        if data.has_tests:
            raise DataError("Resource file '%s' cannot contain tests or tasks." %
                            source)
        ResourceBuilder(resource).visit(data)
        LOGGER.info("Imported resource file '%s' (%d keywords)."
                    % (source, len(resource.keywords)))
    else:
        LOGGER.warn("Imported resource file '%s' is empty." % source)
    return resource


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


class ErrorLogger(NodeVisitor):

    def __init__(self, source):
        self.source = source

    def visit_Error(self, node):
        LOGGER.error("Error in file '%s': %s" % (self.source, node.error))
