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
from collections.abc import Iterable, Sequence
from dataclasses import dataclass, field
from inspect import cleandoc

__all__ = ["parse_docstring", "DocInfo"]


@dataclass
class DocInfo:
    doc: str = ""
    args: "dict[str, str]" = field(default_factory=dict)
    returns: str = ""
    raises: "dict[str, str]" = field(default_factory=dict)


def parse_docstring(doc: str) -> DocInfo:
    """Parses information from docstring.

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

    def __init__(self, name: str = "", body: "Sequence[str]" = ()):
        """
        :param name: Name of the block.
        :param body: Block body.

        If a block has a name, body *must* contain the text on the same line as
        the name to make sure `cleandoc` works properly. This text can be empty.
        """
        assert body or not name
        self.name = name.strip()
        self._body = list(body)

    @property
    def content(self) -> str:
        """Return block content. With named blocks content is dedent."""
        content = "\n".join(self._body)
        if self.name:
            content = cleandoc(content)
        return content.rstrip()

    def accepts(self, line: str) -> bool:
        if not self.name:
            return True
        return not line or line[:2].isspace()

    def add(self, line: str):
        self._body.append(line)


class DocStringParser:
    args_headers = ("args", "arguments", "parameters")
    returns_headers = ("returns", "return", "yields")
    raises_headers = ("raises", "raise")
    header_re = re.compile(
        rf"""
        [*_]*         # Start of optional bold/italics formatting
        ({'|'.join(args_headers + returns_headers + raises_headers)})
        [*_]*         # End of optional bold/italics formatting
        ::?           # One or two colons
        [*_]*         # Alternative end of optional bold/italics formatting
        (\s+(.*))?    # Optional inline text
        """,
        re.IGNORECASE | re.VERBOSE,
    )
    named_doc_re = re.compile(r"\s?(\S.*?):(\s+(.*))?")

    def parse(self, doc: str) -> DocInfo:
        info = DocInfo()
        for section in self._parse_sections(doc):
            name = section.name.lower()
            if name in self.args_headers:
                info.args.update(self._parse_named_docs(section.content))
            elif name in self.returns_headers:
                info.returns = section.content.strip()
            elif name in self.raises_headers:
                info.raises.update(self._parse_named_docs(section.content))
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
            can_start = section.name or not line.strip()
        yield section

    def _parse_named_docs(self, data: str) -> "Iterable[tuple[str, str]]":
        block = Block()
        for line in data.splitlines():
            match = self.named_doc_re.fullmatch(line)
            if match:
                yield from self._yield_name_and_doc(block)
                name, _, inline_text = match.groups()
                block = Block(name, [inline_text or ""])
            else:
                block.add(line)
        yield from self._yield_name_and_doc(block)

    def _yield_name_and_doc(self, block: Block) -> "Iterable[tuple[str, str]]":
        name, doc = block.name, block.content
        if name or doc:
            name = self._normalize_name(name)
            if name not in ("/", "*"):
                yield name, doc

    def _normalize_name(self, name: str) -> str:
        if name.startswith("`"):
            name = name.strip("`").strip()
        if "(" in name:
            name = name.split("(")[0].rstrip()
        if name.startswith("*") and name != "*":
            name = name.lstrip("*").strip()
        elif name.startswith(("${", "@{", "&{")) and name.endswith("}"):
            name = name[2:-1].strip()
        return name or "<no-name>"
