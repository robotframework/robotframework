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
from typing import Iterable

from robot.errors import DataError
from robot.model import SuiteNamePatterns
from robot.output import LOGGER
from robot.utils import get_error_message


class SuiteStructure:

    def __init__(self, source: Path = None, init_file: Path = None,
                 children: 'list[SuiteStructure]|None' = None):
        self.source = source
        self.init_file = init_file
        self.children = children

    @property
    def extension(self) -> 'str|None':
        source = self.source if self.is_file else self.init_file
        return source.suffix[1:].lower() if source else None

    @property
    def is_file(self) -> bool:
        return self.children is None

    def add(self, child: 'SuiteStructure'):
        self.children.append(child)

    def visit(self, visitor: 'SuiteStructureVisitor'):
        if self.children is None:
            visitor.visit_file(self)
        else:
            visitor.visit_directory(self)


class SuiteStructureVisitor:

    def visit_file(self, structure: SuiteStructure):
        pass

    def visit_directory(self, structure: SuiteStructure):
        self.start_directory(structure)
        for child in structure.children:
            child.visit(self)
        self.end_directory(structure)

    def start_directory(self, structure: SuiteStructure):
        pass

    def end_directory(self, structure: SuiteStructure):
        pass


class SuiteStructureBuilder:
    ignored_prefixes = ('_', '.')
    ignored_dirs = ('CVS',)

    def __init__(self, extensions: Iterable[str] = ('.robot', '.rbt'),
                 included_suites: Iterable[str] = ()):
        self.extensions = {'.' + ext.lstrip('.').lower() for ext in extensions}
        self.included_suites = SuiteNamePatterns(
            self._create_included_suites(included_suites)
        )

    def _create_included_suites(self, included_suites):
        for suite in included_suites:
            yield suite
            while '.' in suite:
                suite = suite.split('.', 1)[1]
                yield suite

    def build(self, *paths: Path) -> SuiteStructure:
        if len(paths) == 1:
            return self._build(paths[0], self.included_suites)
        return self._build_multi_source(paths)

    def _build(self, path: Path, included_suites: SuiteNamePatterns) -> SuiteStructure:
        if path.is_file():
            return SuiteStructure(path)
        return self._build_directory(path, included_suites)

    def _build_directory(self, path: Path,
                         included_suites: SuiteNamePatterns) -> SuiteStructure:
        structure = SuiteStructure(path, children=[])
        # If a directory is included, also its children are included.
        if self._is_suite_included(path.name, included_suites):
            included_suites = SuiteNamePatterns()
        for item in self._list_dir(path):
            if self._is_init_file(item):
                if structure.init_file:
                    LOGGER.error(f"Ignoring second test suite init file '{item}'.")
                else:
                    structure.init_file = item
            elif self._is_included(item, included_suites):
                structure.add(self._build(item, included_suites))
            else:
                LOGGER.info(f"Ignoring file or directory '{item}'.")
        return structure

    def _is_suite_included(self, name: str, included_suites: SuiteNamePatterns) -> bool:
        if not included_suites:
            return True
        if '__' in name:
            name = name.split('__', 1)[1] or name
        return included_suites.match(name)

    def _list_dir(self, path: Path) -> 'list[Path]':
        try:
            return sorted(path.iterdir(), key=lambda p: p.name.lower())
        except OSError:
            raise DataError(f"Reading directory '{path}' failed: {get_error_message()}")

    def _is_init_file(self, path: Path) -> bool:
        return (path.stem.lower() == '__init__'
                and path.suffix.lower() in self.extensions
                and path.is_file())

    def _is_included(self, path: Path, included_suites: SuiteNamePatterns) -> bool:
        if path.name.startswith(self.ignored_prefixes):
            return False
        if path.is_dir():
            return path.name not in self.ignored_dirs
        if not path.is_file():
            return False
        if path.suffix.lower() not in self.extensions:
            return False
        return self._is_suite_included(path.stem, included_suites)

    def _build_multi_source(self, paths: Iterable[Path]) -> SuiteStructure:
        structure = SuiteStructure(children=[])
        for path in paths:
            if self._is_init_file(path):
                if structure.init_file:
                    raise DataError("Multiple init files not allowed.")
                structure.init_file = path
            else:
                structure.add(self._build(path, self.included_suites))
        return structure
