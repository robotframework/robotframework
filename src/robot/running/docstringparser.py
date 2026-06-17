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
import textwrap
from collections.abc import Iterable
from dataclasses import dataclass, field
from enum import auto, Enum

__all__ = ["parse_docstring", "DocInfo"]


@dataclass
class DocInfo:
    doc: str = ""
    args: "dict[str, str]" = field(default_factory=dict)
    returns: str = ""


def parse_docstring(doc: str) -> DocInfo:
    """Parses a docstring into documentation, arguments and return value.

    Parsing is done according to the Google Python Style Guide.
    https://google.github.io/styleguide/pyguide.html#s3.8-comments-and-docstrings

    Example::

        def keyword(arg) -> str:
            \"""Example keyword documentation.

            Args:
                arg: Doc for the argument.

            Returns:
                Argument in uppercase.

            This continues the documentation.
            \"""
            return arg.upper()

    It is assumed that the given `doc` is already normalized using `inspect.cleandoc`
    or otherwise.
    """
    return DocStringParser().parse(doc)


class SectionKind(Enum):
    ARGS = auto()
    RETURNS = auto()
    NONE = auto()


class Section:
    args = ("args", "arguments", "parameters")
    returns = ("returns", "return", "yields")

    def __init__(self, header: "str | None", body: "list[str]"):
        self.header = header
        self.body = body

    @property
    def kind(self) -> SectionKind:
        if self.header is None:
            return SectionKind.NONE
        header = self.header.lower()
        if header in self.args:
            return SectionKind.ARGS
        if header in self.returns:
            return SectionKind.RETURNS
        return SectionKind.NONE

    def dedent(self):
        self.body = textwrap.dedent("\n".join(self.body)).splitlines()

    def accepts(self, line: str) -> bool:
        if not self.header:
            return True
        if not line or line[:2].isspace():
            return True
        return False


class DocStringParser:
    header_re = re.compile(
        rf"({'|'.join(Section.args + Section.returns)}):(.*)?",
        re.IGNORECASE,
    )
    arg_re = re.compile(r"\s?(\S.*?):(\s.*)?")

    def parse(self, doc: str) -> DocInfo:
        info = DocInfo()
        for section in self._parse_sections(doc):
            if section.header:
                section.dedent()
            if section.kind is SectionKind.ARGS:
                info.args.update(self._parse_args(section.body))
            elif section.kind is SectionKind.RETURNS:
                info.returns = self._parse_returns(section.body)
            else:
                info.doc += "\n".join(section.body) + "\n"
        info.doc = info.doc.strip()
        return info

    def _parse_sections(self, doc: str) -> "Iterable[Section]":
        section = None
        can_start = True
        for line in doc.splitlines():
            match = self.header_re.fullmatch(line) if can_start else None
            if match:
                if section:
                    yield section
                header, inline_text = match.groups()
                body = [inline_text.strip() if inline_text else ""]
                section = Section(header, body)
            elif section:
                if section.accepts(line):
                    section.body.append(line)
                else:
                    yield section
                    section = Section(None, [line])
            else:
                section = Section(None, [line])
            can_start = not line.strip()
        if section:
            yield section

    def _parse_args(self, lines: "list[str]") -> "Iterable[tuple[str, str]]":
        name, desc = "", []
        for line in lines:
            match = self.arg_re.fullmatch(line)
            if match:
                yield from self._yield_arg(name, desc)
                name, inline_text = match.groups()
                desc = [inline_text.strip() if inline_text else ""]
            else:
                desc.append(line)
        yield from self._yield_arg(name, desc)

    def _yield_arg(self, name: str, desc: "list[str]") -> "Iterable[tuple[str, str]]":
        if (name or any(line.strip() for line in desc)) and name != "*":
            yield self._normalize_name(name), self._format(desc)

    def _normalize_name(self, name: str) -> str:
        name = name.split("(")[0].strip()
        if name.startswith("*"):
            name = name.lstrip("*").strip()
        elif name.startswith(("${", "@{", "&{")) and name.endswith("}"):
            name = name[2:-1].strip()
        return name or "<no-name>"

    def _format(self, lines: "list[str]") -> str:
        if not lines:
            return ""
        inline = lines[0]
        body = textwrap.dedent("\n".join(lines[1:]))
        if inline and body:
            result = inline + "\n" + body
        elif inline:
            result = inline
        else:
            result = body
        return result.rstrip()

    def _parse_returns(self, lines: "list[str]") -> str:
        return self._format(lines)
