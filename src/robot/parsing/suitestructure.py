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

from os.path import normpath
from pathlib import Path
from typing import List

from robot.errors import DataError
from robot.model import SuiteNamePatterns
from robot.output import LOGGER
from robot.utils import get_error_message, seq2str


class SuiteStructure:

    def __init__(self, source: Path = None, init_file: Path = None,
                 children: List['SuiteStructure'] = None):
        self.source = source
        self.init_file = init_file
        self.children = children

    @property
    def extension(self):
        source = self.source if self.is_file else self.init_file
        return source.suffix[1:].lower() if source else None

    @property
    def is_file(self):
        return self.children is None

    def add(self, child: 'SuiteStructure'):
        self.children.append(child)

    def visit(self, visitor):
        if self.children is None:
            visitor.visit_file(self)
        else:
            visitor.visit_directory(self)


class SuiteStructureVisitor:

    def visit_file(self, structure):
        pass

    def visit_directory(self, structure):
        self.start_directory(structure)
        for child in structure.children:
            child.visit(self)
        self.end_directory(structure)

    def start_directory(self, structure):
        pass

    def end_directory(self, structure):
        pass


class SuiteStructureBuilder:
    ignored_prefixes = ('_', '.')
    ignored_dirs = ('CVS',)

    def __init__(self, included_extensions=('.robot', '.rbt'), included_suites=None):
        self.included_extensions = included_extensions
        self.included_suites = None if not included_suites else \
            SuiteNamePatterns(self._create_included_suites(included_suites))

    def _create_included_suites(self, included_suites):
        for suite in included_suites:
            yield suite
            while '.' in suite:
                suite = suite.split('.', 1)[1]
                yield suite

    def build(self, paths):
        paths = list(self._normalize_paths(paths))
        if len(paths) == 1:
            return self._build(paths[0], self.included_suites)
        return self._build_multi_source(paths)

    def _normalize_paths(self, paths):
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
        return paths

    def _build(self, path, included_suites):
        if path.is_file():
            return SuiteStructure(path)
        return self._build_directory(path, included_suites)

    def _build_directory(self, dir_path, included_suites):
        structure = SuiteStructure(dir_path, children=[])
        # If a directory is included, also its children are included.
        if self._is_suite_included(dir_path.name, included_suites):
            included_suites = None
        for path in self._list_dir(dir_path):
            if self._is_init_file(path):
                if structure.init_file:
                    LOGGER.error(f"Ignoring second test suite init file '{path}'.")
                else:
                    structure.init_file = path
            elif self._is_included(path, included_suites):
                structure.add(self._build(path, included_suites))
            else:
                LOGGER.info(f"Ignoring file or directory '{path}'.")
        return structure

    def _is_suite_included(self, name, included_suites):
        if not included_suites:
            return True
        if '__' in name:
            name = name.split('__', 1)[1] or name
        return included_suites.match(name)

    def _list_dir(self, path):
        try:
            return sorted(path.iterdir(), key=lambda p: p.name.lower())
        except OSError:
            raise DataError(f"Reading directory '{path}' failed: {get_error_message()}")

    def _is_init_file(self, path: Path):
        return (path.stem.lower() == '__init__'
                and path.suffix.lower() in self.included_extensions
                and path.is_file())

    def _is_included(self, path: Path, included_suites):
        if path.name.startswith(self.ignored_prefixes):
            return False
        if path.is_dir():
            return path.name not in self.ignored_dirs
        if not path.is_file():
            return False
        if path.suffix.lower() not in self.included_extensions:
            return False
        return self._is_suite_included(path.stem, included_suites)

    def _build_multi_source(self, paths: List[Path]):
        structure = SuiteStructure(children=[])
        for path in paths:
            if self._is_init_file(path):
                if structure.init_file:
                    raise DataError("Multiple init files not allowed.")
                structure.init_file = path
            else:
                structure.add(self._build(path, self.included_suites))
        return structure
