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

import re
from abc import ABC
from inspect import signature
from os.path import commonprefix
from pathlib import Path
from typing import Callable, Iterator

from robot.conf import LanguagesLike
from robot.errors import DataError
from robot.parsing import File, get_init_model, get_model, get_resource_model
from robot.parsing.model import ModelVisitor, Statement
from robot.utils import FileReader, get_error_message, type_name

from ..model import TestSuite
from ..resourcemodel import ResourceFile
from .settings import FileSettings, InitFileSettings, TestDefaults
from .transformers import ResourceBuilder, SuiteBuilder


class Parser(ABC):

    @property
    def name(self) -> str:
        return type(self).__name__

    def parse_suite_file(self, source: Path, defaults: TestDefaults) -> TestSuite:
        raise DataError(f"'{self.name}' does not support parsing suite files.")

    def parse_init_file(self, source: Path, defaults: TestDefaults) -> TestSuite:
        raise DataError(f"'{self.name}' does not support parsing initialization files.")

    def parse_resource_file(self, source: Path) -> ResourceFile:
        raise DataError(f"'{self.name}' does not support parsing resource files.")


class RobotParser(Parser):
    extensions = ()

    def __init__(self, lang: LanguagesLike = None, process_curdir: bool = True):
        self.lang = lang
        self.process_curdir = process_curdir

    def parse_suite_file(self, source: Path, defaults: TestDefaults) -> TestSuite:
        model = self._get_model(get_model, source)
        return self.parse_model(model, defaults)

    def parse_init_file(self, source: Path, defaults: TestDefaults) -> TestSuite:
        model = self._get_model(get_init_model, source)
        suite = TestSuite(
            name=TestSuite.name_from_source(source.parent),
            source=source.parent,
            rpa=None,
        )
        SuiteBuilder(suite, InitFileSettings(defaults)).build(model)
        return suite

    def parse_model(
        self,
        model: File,
        defaults: "TestDefaults | None" = None,
    ) -> TestSuite:
        name = TestSuite.name_from_source(model.source, self.extensions)
        suite = TestSuite(name=name, source=model.source)
        SuiteBuilder(suite, FileSettings(defaults)).build(model)
        return suite

    def _get_model(self, model_getter: Callable[..., File], source: Path) -> File:
        model = model_getter(
            self._get_source(source),
            data_only=True,
            curdir=self._get_curdir(source),
            lang=self.lang,
        )
        model.source = source
        return model

    def _get_curdir(self, source: Path) -> "str | None":
        return str(source.parent).replace("\\", "\\\\") if self.process_curdir else None

    def _get_source(self, source: Path) -> "Path | str":
        return source

    def parse_resource_file(self, source: Path) -> ResourceFile:
        model = self._get_model(get_resource_model, source)
        return self.parse_resource_model(model)

    def parse_resource_model(self, model: File) -> ResourceFile:
        resource = ResourceFile(source=model.source)
        ResourceBuilder(resource).build(model)
        return resource


class RestParser(RobotParser):
    extensions = (".robot.rst", ".rst", ".rest")

    def _get_source(self, source: Path) -> str:
        from .restreader import read_rest_data

        with FileReader(source) as reader:
            return read_rest_data(reader)


class MarkdownParser(RobotParser):
    extensions = (".robot.md", ".md", ".markdown")

    def _get_model(self, model_getter: Callable[..., File], source: Path) -> File:
        with FileReader(source) as reader:
            data, offsets = self._read_markdown_data(reader)
        model = model_getter(
            data,
            data_only=True,
            curdir=self._get_curdir(source),
            lang=self.lang,
        )
        model.source = source
        if offsets:
            ColumnOffsetUpdater(offsets).visit(model)
        return model

    def _read_markdown_data(self, mdfile: FileReader) -> "tuple[str, dict[int, int]]":
        # Lines outside code blocks are replaced with empty lines to preserve line
        # numbers. Indentation removed from code blocks is returned as column offsets.
        fence_open = re.compile(r"\s*(`{3,}|~{3,})\s*(\S+)")
        fence_close = None
        lines = []
        block = None
        for line in mdfile.readlines():
            if block is None:
                lines.append(("\n", 0))
                match = fence_open.match(line)
                if match:
                    fence, lang = match.groups()
                    if lang.lower() in ("robotframework", "robot"):
                        fence_close = re.compile(rf"\s*{fence[0]}{{{len(fence)},}}\s*")
                        block = []
            elif fence_close.fullmatch(line):
                lines.extend(self._dedent(block))
                lines.append(("\n", 0))
                block = None
            else:
                block.append(line)
        if block:
            lines.extend(self._dedent(block))
        data = "".join(line for line, _ in lines)
        offsets = {n: offset for n, (_, offset) in enumerate(lines, start=1) if offset}
        return data, offsets

    def _dedent(self, block: "list[str]") -> "Iterator[tuple[str, int]]":
        prefix = commonprefix([line for line in block if line.strip()])
        margin = len(prefix) - len(prefix.lstrip(" \t"))
        for line in block:
            yield (line[margin:], margin) if line.strip() else (line, 0)


class ColumnOffsetUpdater(ModelVisitor):

    def __init__(self, offsets: "dict[int, int]"):
        self.offsets = offsets

    def visit_Statement(self, node: Statement):
        for token in node.tokens:
            token.col_offset += self.offsets.get(token.lineno, 0)


class JsonParser(Parser):

    def parse_suite_file(self, source: Path, defaults: TestDefaults) -> TestSuite:
        return TestSuite.from_json(source)

    def parse_init_file(self, source: Path, defaults: TestDefaults) -> TestSuite:
        return TestSuite.from_json(source)

    def parse_resource_file(self, source: Path) -> ResourceFile:
        try:
            return ResourceFile.from_json(source)
        except DataError as err:
            raise DataError(f"Parsing JSON resource file '{source}' failed: {err}")


class NoInitFileDirectoryParser(Parser):

    def parse_init_file(self, source: Path, defaults: TestDefaults) -> TestSuite:
        return TestSuite(
            name=TestSuite.name_from_source(source),
            source=source,
            rpa=None,
        )


class CustomParser(Parser):

    def __init__(self, parser):
        self.parser = parser
        if not getattr(parser, "parse", None):
            raise TypeError(f"'{self.name}' does not have mandatory 'parse' method.")
        if not self.extensions:
            raise TypeError(
                f"'{self.name}' does not have mandatory 'EXTENSION' or 'extension' "
                f"attribute."
            )

    @property
    def name(self) -> str:
        return type_name(self.parser)

    @property
    def extensions(self) -> "tuple[str, ...]":
        ext = (
            getattr(self.parser, "EXTENSION", None)
            or getattr(self.parser, "extension", None)
        )  # fmt: skip
        extensions = [ext] if isinstance(ext, str) else list(ext or ())
        return tuple(ext.lower().lstrip(".") for ext in extensions)

    def parse_suite_file(self, source: Path, defaults: TestDefaults) -> TestSuite:
        return self._parse(self.parser.parse, source, defaults)

    def parse_init_file(self, source: Path, defaults: TestDefaults) -> TestSuite:
        parse_init = getattr(self.parser, "parse_init", None)
        try:
            return self._parse(parse_init, source, defaults, init=True)
        except NotImplementedError:
            return super().parse_init_file(source, defaults)  # Raises DataError

    def _parse(self, method, source, defaults, init=False) -> TestSuite:
        if not method:
            raise NotImplementedError
        accepts_defaults = len(signature(method).parameters) == 2
        try:
            suite = method(source, defaults) if accepts_defaults else method(source)
            if not isinstance(suite, TestSuite):
                raise TypeError(
                    f"Return value should be 'robot.running.TestSuite', got "
                    f"'{type_name(suite)}'."
                )
        except Exception:
            method_name = "parse" if not init else "parse_init"
            raise DataError(
                f"Calling '{self.name}.{method_name}()' failed: {get_error_message()}"
            )
        return suite
