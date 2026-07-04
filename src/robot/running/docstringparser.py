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
from collections.abc import Iterable, Sequence
from dataclasses import dataclass, field

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


class Block:
    """Represents a block of text with an optional name.

    Used for representing documentation sections and arguments.
    """

    def __init__(self, name: "str | None" = None, body: "Sequence[str]" = ()):
        """
        :param name: Name of the block.
        :param body: Block body.

        If block has a name, body *must* contain the text on the same line as
        the name. It can be an empty string.
        """
        assert body or not name
        self.name = name
        self._body = list(body)

    @property
    def content(self) -> str:
        """Return block content. With named block content is dedent."""
        if self.name:
            content = self._dedent(self._body)
        else:
            content = "\n".join(self._body)
        return content.rstrip()

    def _dedent(self, body) -> str:
        # In ths case the block has a name and the first line of the body is
        # the text on the same line as the name. This line does not affect
        # indentation and must be ignored if it is empty.
        inline, *body = body
        body = textwrap.dedent("\n".join(body))
        return f"{inline}\n{body}" if inline else body

    def accepts(self, line: str) -> bool:
        if not self.name:
            return True
        return not line or line[:2].isspace()

    def add(self, line: str):
        self._body.append(line)


class DocStringParser:
    args_headers = ("args", "arguments", "parameters")
    returns_headers = ("returns", "return", "yields")
    header_re = re.compile(
        rf"({'|'.join(args_headers + returns_headers)}):(\s+(.*))?",
        re.IGNORECASE,
    )
    arg_re = re.compile(r"\s?(\S.*?):(\s+(.*))?")

    def parse(self, doc: str) -> DocInfo:
        info = DocInfo()
        for section in self._parse_sections(doc):
            name = section.name.lower() if section.name else section.name
            if name in self.args_headers:
                info.args.update(self._parse_args(section.content))
            elif name in self.returns_headers:
                info.returns = section.content
            else:
                info.doc += section.content + "\n\n"
        info.doc = info.doc.strip()
        return info

    def _parse_sections(self, doc: str) -> "Iterable[Block]":
        section = Block()
        can_start = True
        for line in doc.splitlines():
            match = self.header_re.fullmatch(line) if can_start else None
            if match:
                yield section
                header, _, inline_text = match.groups()
                section = Block(header, [inline_text or ""])
            elif section.accepts(line):
                section.add(line)
            else:
                yield section
                section = Block(body=[line])
            can_start = not line.strip()
        yield section

    def _parse_args(self, data: str) -> "Iterable[tuple[str, str]]":
        arg = Block()
        for line in data.splitlines():
            match = self.arg_re.fullmatch(line)
            if match:
                yield from self._yield_arg(arg)
                name, _, inline_text = match.groups()
                arg = Block(name, [inline_text or ""])
            else:
                arg.add(line)
        yield from self._yield_arg(arg)

    def _yield_arg(self, arg: Block) -> "Iterable[tuple[str, str]]":
        name = arg.name or ""
        description = arg.content
        if (name or description) and name != "*":
            yield self._normalize_name(name), description

    def _normalize_name(self, name: str) -> str:
        name = name.split("(")[0].strip()
        if name.startswith("*"):
            name = name.lstrip("*").strip()
        elif name.startswith(("${", "@{", "&{")) and name.endswith("}"):
            name = name[2:-1].strip()
        return name or "<no-name>"
