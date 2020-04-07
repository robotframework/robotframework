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

from robot.errors import DataError
from robot.output import LOGGER
from robot.parsing import SuiteStructureBuilder, SuiteStructureVisitor

from .parsers import RobotParser, NoInitFileDirectoryParser, RestParser
from .testsettings import TestDefaults


class TestSuiteBuilder(object):

    def __init__(self, included_suites=None, included_extensions=('robot',),
                 rpa=None, allow_empty_suite=False, process_curdir=True):
        self.rpa = rpa
        self.included_suites = included_suites
        self.included_extensions = included_extensions
        self.allow_empty_suite = allow_empty_suite
        self.process_curdir = process_curdir

    def build(self, *paths):
        """
        :param paths: Paths to test data files or directories.
        :return: :class:`~robot.running.model.TestSuite` instance.
        """
        structure = SuiteStructureBuilder(self.included_extensions,
                                          self.included_suites).build(paths)
        parser = SuiteStructureParser(self.included_extensions,
                                      self.rpa, self.process_curdir)
        suite = parser.parse(structure)
        if not self.included_suites and not self.allow_empty_suite:
            self._validate_test_counts(suite, multisource=len(paths) > 1)
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


class SuiteStructureParser(SuiteStructureVisitor):

    def __init__(self, included_extensions, rpa=None, process_curdir=True):
        self.rpa = rpa
        self._rpa_given = rpa is not None
        self.suite = None
        self._stack = []
        self.parsers = self._get_parsers(included_extensions, process_curdir)

    def _get_parsers(self, extensions, process_curdir):
        robot_parser = RobotParser(process_curdir)
        rest_parser = RestParser(process_curdir)
        parsers = {
            None: NoInitFileDirectoryParser(),
            'robot': robot_parser,
            'rst': rest_parser,
            'rest': rest_parser
        }
        for ext in extensions:
            if ext not in parsers:
                parsers[ext] = robot_parser
        return parsers

    def _get_parser(self, extension):
        try:
            return self.parsers[extension]
        except KeyError:
            return self.parsers['robot']

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
        parent_defaults = self._stack[-1][-1] if self._stack else None
        source = structure.source
        defaults = TestDefaults(parent_defaults)
        parser = self._get_parser(structure.extension)
        try:
            if structure.is_directory:
                suite = parser.parse_init_file(structure.init_file or source, defaults)
            else:
                suite = parser.parse_suite_file(source, defaults)
                if not suite.tests:
                    LOGGER.info("Data source '%s' has no tests or tasks." % source)
            self._validate_execution_mode(suite)
        except DataError as err:
            raise DataError("Parsing '%s' failed: %s" % (source, err.message))
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


class ResourceFileBuilder(object):

    def __init__(self, process_curdir=True):
        self.process_curdir = process_curdir

    def build(self, source):
        LOGGER.info("Parsing resource file '%s'." % source)
        resource = self._parse(source)
        if resource.imports or resource.variables or resource.keywords:
            LOGGER.info("Imported resource file '%s' (%d keywords)."
                        % (source, len(resource.keywords)))
        else:
            LOGGER.warn("Imported resource file '%s' is empty." % source)
        return resource

    def _parse(self, source):
        if os.path.splitext(source)[1].lower() in ('.rst', '.rest'):
            return RestParser(self.process_curdir).parse_resource_file(source)
        return RobotParser(self.process_curdir).parse_resource_file(source)
