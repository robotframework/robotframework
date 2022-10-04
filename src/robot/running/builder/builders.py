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
from .settings import Defaults


class TestSuiteBuilder:
    """Builder to construct ``TestSuite`` objects based on data on the disk.

    The :meth:`build` method constructs executable
    :class:`~robot.running.model.TestSuite` objects based on test data files
    or directories. There are two main use cases for this API:

    - Execute the created suite by using its
      :meth:`~robot.running.model.TestSuite.run` method. The suite can be
      modified before execution if needed.

    - Inspect the suite to see, for example, what tests it has or what tags
      tests have. This can be more convenient than using the lower level
      :mod:`~robot.parsing` APIs but does not allow saving modified data
      back to the disk.

    Both modifying the suite and inspecting what data it contains are easiest
    done by using the :mod:`~robot.model.visitor` interface.

    This class is part of the public API and should be imported via the
    :mod:`robot.api` package.
    """

    def __init__(self, included_suites=None, included_extensions=('robot',),
                 rpa=None, lang=None, allow_empty_suite=False,
                 process_curdir=True):
        """
        :param include_suites:
            List of suite names to include. If ``None`` or an empty list, all
            suites are included. Same as using `--suite` on the command line.
        :param included_extensions:
            List of extensions of files to parse. Same as `--extension`.
        :param rpa: Explicit test execution mode. ``True`` for RPA and
            ``False`` for test automation. By default, mode is got from data file
            headers and possible conflicting headers cause an error.
            Same as `--rpa` or `--norpa`.
        :param lang: Additional languages to be supported during parsing.
            Can be a string matching any of the supported language codes or names,
            an initialized :class:`~robot.conf.languages.Language` subsclass,
            a list containing such strings or instances, or a
            :class:`~robot.conf.languages.Languages` instance.
        :param allow_empty_suite:
            Specify is it an error if the built suite contains no tests.
            Same as `--runemptysuite`.
        :param process_curdir:
            Control processing the special ``${CURDIR}`` variable. It is
            resolved already at parsing time by default, but that can be
            changed by giving this argument ``False`` value.
        """
        self.rpa = rpa
        self.lang = lang
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
                                      self.rpa, self.lang, self.process_curdir)
        suite = parser.parse(structure)
        if not self.included_suites and not self.allow_empty_suite:
            self._validate_test_counts(suite, multisource=len(paths) > 1)
        suite.remove_empty_suites(preserve_direct_children=len(paths) > 1)
        return suite

    def _validate_test_counts(self, suite, multisource=False):
        def validate(suite):
            if not suite.has_tests:
                raise DataError(f"Suite '{suite.name}' contains no tests or tasks.")
        if not multisource:
            validate(suite)
        else:
            for s in suite.suites:
                validate(s)


class SuiteStructureParser(SuiteStructureVisitor):

    def __init__(self, included_extensions, rpa=None, lang=None, process_curdir=True):
        self.rpa = rpa
        self._rpa_given = rpa is not None
        self.suite = None
        self._stack = []
        self.parsers = self._get_parsers(included_extensions, lang, process_curdir)

    def _get_parsers(self, extensions, lang, process_curdir):
        robot_parser = RobotParser(lang, process_curdir)
        rest_parser = RestParser(lang, process_curdir)
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
        LOGGER.info(f"Parsing file '{structure.source}'.")
        suite, _ = self._build_suite(structure)
        if self._stack:
            self._stack[-1][0].suites.append(suite)
        else:
            self.suite = suite

    def start_directory(self, structure):
        if structure.source:
            LOGGER.info(f"Parsing directory '{structure.source}'.")
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
        defaults = Defaults(parent_defaults)
        parser = self._get_parser(structure.extension)
        try:
            if structure.is_directory:
                suite = parser.parse_init_file(structure.init_file or source, defaults)
            else:
                suite = parser.parse_suite_file(source, defaults)
                if not suite.tests:
                    LOGGER.info(f"Data source '{source}' has no tests or tasks.")
            self._validate_execution_mode(suite)
        except DataError as err:
            raise DataError(f"Parsing '{source}' failed: {err.message}")
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
            raise DataError(f"Conflicting execution modes. File has {this} "
                            f"but files parsed earlier have {that}. Fix headers "
                            f"or use '--rpa' or '--norpa' options to set the "
                            f"execution mode explicitly.")


class ResourceFileBuilder:

    def __init__(self, lang=None, process_curdir=True):
        self.lang = lang
        self.process_curdir = process_curdir

    def build(self, source):
        LOGGER.info(f"Parsing resource file '{source}'.")
        resource = self._parse(source)
        if resource.imports or resource.variables or resource.keywords:
            LOGGER.info(f"Imported resource file '{source}' ({len(resource.keywords)} "
                        f"keywords).")
        else:
            LOGGER.warn(f"Imported resource file '{source}' is empty.")
        return resource

    def _parse(self, source):
        if os.path.splitext(source)[1].lower() in ('.rst', '.rest'):
            return RestParser(self.lang, self.process_curdir).parse_resource_file(source)
        return RobotParser(self.lang, self.process_curdir).parse_resource_file(source)
