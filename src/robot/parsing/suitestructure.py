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

import os.path

from robot.errors import DataError
from robot.model import SuiteNamePatterns
from robot.output import LOGGER
from robot.utils import abspath, get_error_message, unic


class SuiteStructure(object):

    def __init__(self, source=None, init_file=None, children=None):
        self.source = source
        self.init_file = init_file
        self.children = children
        self.extension = self._get_extension(source, init_file)

    def _get_extension(self, source, init_file):
        if self.is_directory and not init_file:
            return None
        source = init_file or source
        return os.path.splitext(source)[1][1:].lower()

    @property
    def is_directory(self):
        return self.children is not None

    def visit(self, visitor):
        if self.children is None:
            visitor.visit_file(self)
        else:
            visitor.visit_directory(self)


class SuiteStructureBuilder(object):
    ignored_prefixes = ('_', '.')
    ignored_dirs = ('CVS',)

    def __init__(self, included_extensions=('robot',), included_suites=None):
        self.included_extensions = included_extensions
        self.included_suites = included_suites

    def build(self, paths):
        paths = list(self._normalize_paths(paths))
        if len(paths) == 1:
            return self._build(paths[0], self.included_suites)
        children = [self._build(p, self.included_suites) for p in paths]
        return SuiteStructure(children=children)

    def _normalize_paths(self, paths):
        if not paths:
            raise DataError('One or more source paths required.')
        for path in paths:
            path = os.path.normpath(path)
            if not os.path.exists(path):
                raise DataError("Parsing '%s' failed: File or directory to "
                                "execute does not exist." % path)
            yield abspath(path)

    def _build(self, path, include_suites):
        if os.path.isfile(path):
            return SuiteStructure(path)
        include_suites = self._get_include_suites(path, include_suites)
        init_file, paths = self._get_child_paths(path, include_suites)
        children = [self._build(p, include_suites) for p in paths]
        return SuiteStructure(path, init_file, children)

    def _get_include_suites(self, path, incl_suites):
        if not incl_suites:
            return None
        if not isinstance(incl_suites, SuiteNamePatterns):
            incl_suites = SuiteNamePatterns(
                self._create_included_suites(incl_suites))
        # If a directory is included, also all its children should be included.
        if self._is_in_included_suites(os.path.basename(path), incl_suites):
            return None
        return incl_suites

    def _create_included_suites(self, incl_suites):
        for suite in incl_suites:
            yield suite
            while '.' in suite:
                suite = suite.split('.', 1)[1]
                yield suite

    def _get_child_paths(self, dirpath, incl_suites=None):
        init_file = None
        paths = []
        for path, is_init_file in self._list_dir(dirpath, incl_suites):
            if is_init_file:
                if not init_file:
                    init_file = path
                else:
                    LOGGER.error("Ignoring second test suite init file '%s'."
                                 % path)
            else:
                paths.append(path)
        return init_file, paths

    def _list_dir(self, dir_path, incl_suites):
        # os.listdir returns Unicode entries when path is Unicode
        dir_path = unic(dir_path)
        try:
            names = os.listdir(dir_path)
        except:
            raise DataError("Reading directory '%s' failed: %s"
                            % (dir_path, get_error_message()))
        for name in sorted(names, key=lambda item: item.lower()):
            name = unic(name)  # needed to handle nfc/nfd normalization on OSX
            path = os.path.join(dir_path, name)
            base, ext = os.path.splitext(name)
            ext = ext[1:].lower()
            if self._is_init_file(path, base, ext):
                yield path, True
            elif self._is_included(path, base, ext, incl_suites):
                yield path, False
            else:
                LOGGER.info("Ignoring file or directory '%s'." % path)

    def _is_init_file(self, path, base, ext):
        return (base.lower() == '__init__'
                and ext in self.included_extensions
                and os.path.isfile(path))

    def _is_included(self, path, base, ext, incl_suites):
        if base.startswith(self.ignored_prefixes):
            return False
        if os.path.isdir(path):
            return base not in self.ignored_dirs or ext
        if ext not in self.included_extensions:
            return False
        return self._is_in_included_suites(base, incl_suites)

    def _is_in_included_suites(self, name, incl_suites):
        if not incl_suites:
            return True
        return incl_suites.match(self._split_prefix(name))

    def _split_prefix(self, name):
        return name.split('__', 1)[-1]


class SuiteStructureVisitor(object):

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
