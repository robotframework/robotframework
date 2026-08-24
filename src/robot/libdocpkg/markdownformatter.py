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

import textwrap
from typing import TYPE_CHECKING

from robot.model import Tags
from robot.running import ArgInfo, ArgumentSpec
from robot.utils import file_writer

if TYPE_CHECKING:
    from .model import KeywordDoc


class LibdocMarkdownWriter:
    """Writes the full library/resource documentation as a single Markdown file.

    Formatting is the same that is used when viewing documentation on console.
    Actual documentation is got directly from the library/resource, so the result
    is proper Markdown only if the library uses Markdown as its documentation
    format.
    """

    def write(self, libdoc, output):
        with file_writer(output) as outfile:
            outfile.write(MarkdownFormatter(libdoc).format())


class MarkdownFormatter:

    def __init__(self, libdoc):
        self.libdoc = libdoc

    def format(self) -> str:
        md = self.format_introduction()
        md += self.format_importing()
        md += self.format_keywords()
        return md

    def format_introduction(self) -> str:
        md = f"# {self.libdoc.name}\n\n"
        if self.libdoc.version:
            md += f"* Version: {self.libdoc.version}\n"
        if self.libdoc.type == "LIBRARY":
            md += f"* Scope: {self.libdoc.scope}\n"
        if self.libdoc.version or self.libdoc.type == "LIBRARY":
            md += "\n"
        if self.libdoc.doc:
            md += "## Introduction\n\n"
            md += self.libdoc.doc + "\n\n"
        return md

    def format_importing(self) -> str:
        if not self.libdoc.inits:
            return ""
        md = "## Importing\n\n"
        kw_formatter = KeywordFormatter(init=True)
        for init in self.libdoc.inits:
            md += kw_formatter.format(init)
        return md

    def format_keywords(self, show_heading: bool = True) -> str:
        if not self.libdoc.keywords:
            return ""
        md = "## Keywords\n\n" if show_heading else ""
        kw_formatter = KeywordFormatter()
        for kw in self.libdoc.keywords:
            md += kw_formatter.format(kw)
        return md


class KeywordFormatter:

    def __init__(self, init=False):
        self.init = init

    def format(
        self,
        keyword: "KeywordDoc",
    ) -> str:
        md = f"### {keyword.name}\n\n" if not self.init else ""
        md += self._format_args(keyword.args)
        md += self._format_returns(keyword.args)
        md += self._format_raises(keyword.args)
        md += self._format_tags(keyword.tags)
        md += self._format_doc(keyword.doc)
        return md

    def _format_args(self, args: ArgumentSpec) -> str:
        if not args:
            return ""
        md = "#### Arguments\n\n"
        for arg in args:
            if not arg.is_marker:
                md += self._format_arg_name(arg)
                md += self._format_arg_info(arg)
                md += self._format_arg_doc(arg)
                md += "\n"
        return md + "\n"

    def _format_arg_name(self, arg: ArgInfo) -> str:
        if arg.kind == ArgInfo.VAR_POSITIONAL:
            marker = "*"
        elif arg.kind == ArgInfo.VAR_NAMED:
            marker = "**"
        else:
            marker = ""
        return f"* `{marker}{arg.name}`"

    def _format_arg_info(self, arg: ArgInfo) -> str:
        info = []
        if arg.type:
            info.append(f"type: `{arg.type}`")
        if arg.default_repr is not None:
            info.append(f"default: `{arg.default_repr}`")
        if arg.kind == ArgInfo.POSITIONAL_ONLY:
            info.append("positional-only")
        if arg.kind == ArgInfo.NAMED_ONLY:
            info.append("named-only")
        if not info:
            return ""
        return f" ({', '.join(info)})"

    def _format_arg_doc(self, arg: ArgInfo) -> str:
        if not arg.doc:
            return ""
        doc = textwrap.indent(arg.doc, "  ")
        return f" -\n{doc}"

    def _format_returns(self, args: ArgumentSpec) -> str:
        if not (args.return_type or args.return_doc):
            return ""
        md = "#### Returns\n\n"
        md += f"* `{args.return_type}`"
        doc = textwrap.indent(args.return_doc, "  ")
        if doc:
            md += f" -\n{doc}"
        return md + "\n\n"

    def _format_raises(self, args: ArgumentSpec) -> str:
        if not args.raises:
            return ""
        md = "#### Raises\n\n"
        for name, doc in args.raises.items():
            doc = textwrap.indent(doc, "  ")
            md += f"* `{name}` -\n{doc}\n"
        return md + "\n"

    def _format_tags(self, tags: Tags) -> str:
        if not tags:
            return ""
        md = "#### Tags\n\n"
        for tag in tags:
            md += f"* `{tag}`\n"
        return md + "\n"

    def _format_doc(self, doc: str) -> str:
        if not doc:
            return ""
        md = "#### Documentation\n\n"
        return md + doc + "\n\n"
