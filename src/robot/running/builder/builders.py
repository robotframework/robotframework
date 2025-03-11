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

import warnings
from itertools import chain
from os.path import normpath
from pathlib import Path
from typing import cast, Sequence

from robot.conf import LanguagesLike
from robot.errors import DataError
from robot.output import LOGGER
from robot.parsing import (SuiteFile, SuiteDirectory, SuiteStructure,
                           SuiteStructureBuilder, SuiteStructureVisitor)
from robot.utils import Importer, seq2str, split_args_from_name_or_path, type_name

from ..model import TestSuite
from ..resourcemodel import ResourceFile
from .parsers import (CustomParser, JsonParser, NoInitFileDirectoryParser, Parser,
                      RestParser, RobotParser)
from .settings import TestDefaults


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
      :mod:`~robot.parsing` APIs.

    Both modifying the suite and inspecting what data it contains are easiest
    done by using the :mod:`~robot.model.visitor` interface.

    This class is part of the public API and should be imported via the
    :mod:`robot.api` package. An alternative is using the
    :meth:`TestSuite.from_file_system <robot.running.model.TestSuite.from_file_system>`
    classmethod that uses this class internally.
    """

    def __init__(self, included_suites: str = 'DEPRECATED',
                 included_extensions: Sequence[str] = ('.robot', '.rbt', '.robot.rst'),
                 included_files: Sequence[str] = (),
                 custom_parsers: Sequence[str] = (),
                 defaults: 'TestDefaults|None' = None,
                 rpa: 'bool|None' = None,
                 lang: LanguagesLike = None,
                 allow_empty_suite: bool = False,
                 process_curdir: bool = True):
        """
        :param included_suites:
            This argument used to be used for limiting what suite file to parse.
            It is deprecated and has no effect starting from RF 6.1. Use the
            new ``included_files`` argument or filter the created suite after
            parsing instead.
        :param included_extensions:
            List of extensions of files to parse. Same as ``--extension``.
        :param included_files:
            List of names, paths or directory paths of files to parse. All files
            are parsed by default. Same as `--parse-include`. New in RF 6.1.
        :param custom_parsers:
            Custom parsers as names or paths (same as ``--parser``) or as
            parser objects. New in RF 6.1.
        :param defaults:
            Possible test specific defaults from suite initialization files.
            New in RF 6.1.
        :param rpa:
            Explicit execution mode. ``True`` for RPA and ``False`` for test
            automation. By default, mode is got from data file headers.
            Same as ``--rpa`` or ``--norpa``.
        :param lang:
            Additional languages to be supported during parsing.
            Can be a string matching any of the supported language codes or names,
            an initialized :class:`~robot.conf.languages.Language` subclass,
            a list containing such strings or instances, or a
            :class:`~robot.conf.languages.Languages` instance.
        :param allow_empty_suite:
            Specify is it an error if the built suite contains no tests.
            Same as ``--runemptysuite``.
        :param process_curdir:
            Control processing the special ``${CURDIR}`` variable. It is
            resolved already at parsing time by default, but that can be
            changed by giving this argument ``False`` value.
        """
        self.standard_parsers = self._get_standard_parsers(lang, process_curdir)
        self.custom_parsers = self._get_custom_parsers(custom_parsers)
        self.defaults = defaults
        self.included_extensions = tuple(included_extensions or ())
        self.included_files = tuple(included_files or ())
        self.rpa = rpa
        self.allow_empty_suite = allow_empty_suite
        # TODO: Remove in RF 8.0.
        if included_suites != 'DEPRECATED':
            warnings.warn("'TestSuiteBuilder' argument 'included_suites' is deprecated "
                          "and has no effect. Use the new 'included_files' argument "
                          "or filter the created suite instead.")

    def _get_standard_parsers(self, lang: LanguagesLike,
                              process_curdir: bool) -> 'dict[str, Parser]':
        robot_parser = RobotParser(lang, process_curdir)
        rest_parser = RestParser(lang, process_curdir)
        json_parser = JsonParser()
        return {
            'robot': robot_parser,
            'rst': rest_parser,
            'rest': rest_parser,
            'robot.rst': rest_parser,
            'rbt': json_parser,
            'json': json_parser
        }

    def _get_custom_parsers(self, parsers: Sequence[str]) -> 'dict[str, CustomParser]':
        custom_parsers = {}
        importer = Importer('parser', LOGGER)
        for parser in parsers:
            if isinstance(parser, (str, Path)):
                name, args = split_args_from_name_or_path(parser)
                parser = importer.import_class_or_module(name, args)
            else:
                name = type_name(parser)
            try:
                custom_parser = CustomParser(parser)
            except TypeError as err:
                raise DataError(f"Importing parser '{name}' failed: {err}")
            for ext in custom_parser.extensions:
                custom_parsers[ext] = custom_parser
        return custom_parsers

    def build(self, *paths: 'Path|str') -> TestSuite:
        """
        :param paths: Paths to test data files or directories.
        :return: :class:`~robot.running.model.TestSuite` instance.
        """
        paths = self._normalize_paths(paths)
        extensions = self.included_extensions + tuple(self.custom_parsers)
        structure = SuiteStructureBuilder(extensions,
                                          self.included_files).build(*paths)
        suite = SuiteStructureParser(self._get_parsers(paths), self.defaults,
                                     self.rpa).parse(structure)
        if not self.allow_empty_suite:
            self._validate_not_empty(suite, multi_source=len(paths) > 1)
        suite.remove_empty_suites(preserve_direct_children=len(paths) > 1)
        return suite

    def _normalize_paths(self, paths: 'Sequence[Path|str]') -> 'tuple[Path, ...]':
        if not paths:
            raise DataError('One or more source paths required.')
        # Cannot use `Path.resolve()` here because it resolves all symlinks which
        # isn't desired. `Path` doesn't have any methods for normalizing paths
        # so need to use `os.path.normpath()`. Also that _may_ resolve symlinks,
        # but we need to do it for backwards compatibility.
        paths = [Path(normpath(p)).absolute() for p in paths]
        non_existing = [p for p in paths if not p.exists()]
        if non_existing:
            raise DataError(f"Parsing {seq2str(non_existing)} failed: "
                            f"File or directory to execute does not exist.")
        return tuple(paths)

    def _get_parsers(self, paths: 'Sequence[Path]') -> 'dict[str|None, Parser]':
        parsers = {None: NoInitFileDirectoryParser(), **self.custom_parsers}
        robot_parser = self.standard_parsers['robot']
        for ext in chain(self.included_extensions,
                         [self._get_ext(pattern) for pattern in self.included_files],
                         [self._get_ext(pth) for pth in paths if pth.is_file()]):
            ext = ext.lstrip('.').lower()
            if ext not in parsers and ext.replace('.', '').isalnum():
                parsers[ext] = self.standard_parsers.get(ext, robot_parser)
        return parsers

    def _get_ext(self, path: 'str|Path') -> str:
        if not isinstance(path, Path):
            path = Path(path)
        return ''.join(path.suffixes)

    def _validate_not_empty(self, suite: TestSuite, multi_source: bool = False):
        if multi_source:
            for child in suite.suites:
                self._validate_not_empty(child)
        elif not suite.has_tests:
            raise DataError(f"Suite '{suite.name}' contains no tests or tasks.")


class SuiteStructureParser(SuiteStructureVisitor):

    def __init__(self, parsers: 'dict[str|None, Parser]',
                 defaults: 'TestDefaults|None' = None,
                 rpa: 'bool|None' = None):
        self.parsers = parsers
        self.rpa = rpa
        self.defaults = defaults
        self.suite: 'TestSuite|None' = None
        self._stack: 'list[tuple[TestSuite, TestDefaults]]' = []

    @property
    def parent_defaults(self) -> 'TestDefaults|None':
        return self._stack[-1][-1] if self._stack else self.defaults

    def parse(self, structure: SuiteStructure) -> TestSuite:
        structure.visit(self)
        return cast(TestSuite, self.suite)

    def visit_file(self, structure: SuiteFile):
        LOGGER.info(f"Parsing file '{structure.source}'.")
        suite = self._build_suite_file(structure)
        if self.rpa is not None:
            suite.rpa = self.rpa
        if self.suite is None:
            self.suite = suite
        else:
            self._stack[-1][0].suites.append(suite)

    def start_directory(self, structure: SuiteDirectory):
        if structure.source:
            LOGGER.info(f"Parsing directory '{structure.source}'.")
        suite, defaults = self._build_suite_directory(structure)
        if self.suite is None:
            self.suite = suite
        else:
            self._stack[-1][0].suites.append(suite)
        self._stack.append((suite, defaults))

    def end_directory(self, structure: SuiteDirectory):
        suite, _ = self._stack.pop()
        if self.rpa is not None:
            suite.rpa = self.rpa
        elif suite.rpa is None and suite.suites:
            if all(s.rpa is False for s in suite.suites):
                suite.rpa = False
            elif all(s.rpa is True for s in suite.suites):
                suite.rpa = True

    def _build_suite_file(self, structure: SuiteFile):
        source = cast(Path, structure.source)
        defaults = self.parent_defaults or TestDefaults()
        parser = self.parsers[structure.extension]
        try:
            suite = parser.parse_suite_file(source, defaults)
            if not suite.tests:
                LOGGER.info(f"Data source '{source}' has no tests or tasks.")
        except DataError as err:
            raise DataError(f"Parsing '{source}' failed: {err.message}")
        return suite

    def _build_suite_directory(self, structure: SuiteDirectory):
        source = cast(Path, structure.init_file or structure.source)
        defaults = TestDefaults(self.parent_defaults)
        parser = self.parsers[structure.extension]
        try:
            suite = parser.parse_init_file(source, defaults)
            if structure.is_multi_source:
                suite.config(name='', source=None)
        except DataError as err:
            raise DataError(f"Parsing '{source}' failed: {err.message}")
        return suite, defaults


class ResourceFileBuilder:

    def __init__(self, lang: LanguagesLike = None, process_curdir: bool = True):
        self.lang = lang
        self.process_curdir = process_curdir

    def build(self, source: Path) -> ResourceFile:
        if not isinstance(source, Path):
            source = Path(source)
        LOGGER.info(f"Parsing resource file '{source}'.")
        resource = self._parse(source)
        if resource.imports or resource.variables or resource.keywords:
            LOGGER.info(f"Imported resource file '{source}' ({len(resource.keywords)} "
                        f"keywords).")
        else:
            LOGGER.warn(f"Imported resource file '{source}' is empty.")
        return resource

    def _parse(self, source: Path) -> ResourceFile:
        suffix = source.suffix.lower()
        if suffix in ('.rst', '.rest'):
            parser = RestParser(self.lang, self.process_curdir)
        elif suffix in ('.json', '.rsrc'):
            parser = JsonParser()
        else:
            parser = RobotParser(self.lang, self.process_curdir)
        return parser.parse_resource_file(source)
