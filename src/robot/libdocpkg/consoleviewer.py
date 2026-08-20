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

from robot.errors import DataError
from robot.model import Tags
from robot.running import ArgInfo, ArgumentSpec
from robot.utils import console_encode, MultiMatcher

from .model import KeywordDoc


class ConsoleViewer:

    def __init__(self, libdoc):
        self._libdoc = libdoc
        self._keywords = KeywordMatcher(libdoc)

    @classmethod
    def handles(cls, command):
        return command.lower() in ["list", "show", "version"]

    @classmethod
    def validate_command(cls, command, args):
        if not cls.handles(command):
            raise DataError(f"Unknown command '{command}'.")
        if command.lower() == "version" and args:
            raise DataError("Command 'version' does not take arguments.")

    def view(self, command, *args):
        self.validate_command(command, args)
        getattr(self, command.lower())(*args)

    def list(self, *patterns):
        for kw in self._keywords.search(f"*{p}*" for p in patterns):
            self._console(kw.name)

    def show(self, *names):
        if MultiMatcher(names, match_if_no_patterns=True).match("intro"):
            self._console(self._format_intro(self._libdoc), end="")
            if self._libdoc.inits:
                self._console("## Importing\n\n", end="")
                for init in self._libdoc.inits:
                    self._console(KeywordFormatter(init, init=True).format(), end="")
        self._console("## Keywords\n\n", end="")
        for kw in self._keywords.search(names):
            self._console(KeywordFormatter(kw).format(), end="")

    def version(self):
        self._console(self._libdoc.version or "N/A")

    def _console(self, msg, end="\n"):
        print(console_encode(msg), end=end)

    def _format_intro(self, lib) -> str:
        md = f"# {lib.name}\n\n"
        if lib.version:
            md += f"* Version: {lib.version}\n"
        if lib.type == "LIBRARY":
            md += f"* Scope: {lib.scope}\n"
        if lib.version or lib.type == "LIBRARY":
            md += "\n"
        if lib.doc:
            md += "## Introduction\n\n"
            md += lib.doc + "\n\n"
        return md


class KeywordMatcher:

    def __init__(self, libdoc):
        self._keywords = libdoc.keywords

    def search(self, patterns):
        matcher = MultiMatcher(patterns, match_if_no_patterns=True)
        for kw in self._keywords:
            if matcher.match(kw.name):
                yield kw


class KeywordFormatter:

    def __init__(self, keyword: KeywordDoc, init=False):
        self.keyword = keyword
        self.init = init

    def format(self) -> str:
        md = f"### {self.keyword.name}\n\n" if not self.init else ""
        md += self._format_args(self.keyword.args)
        md += self._format_returns(self.keyword.args)
        md += self._format_raises(self.keyword.args)
        md += self._format_tags(self.keyword.tags)
        md += self._format_doc(self.keyword.doc)
        return md

    def _format_args(self, args: ArgumentSpec) -> str:
        if not args:
            return ""
        md = "**Arguments:**\n\n"
        for arg in args:
            if arg.kind in (ArgInfo.POSITIONAL_ONLY_MARKER, ArgInfo.NAMED_ONLY_MARKER):
                continue
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
        md = "**Returns:**\n\n"
        md += f"* `{args.return_type}`"
        doc = textwrap.indent(args.return_doc, "  ")
        if doc:
            md += f" -\n{doc}"
        return md + "\n\n"

    def _format_raises(self, args: ArgumentSpec) -> str:
        if not args.raises:
            return ""
        md = "**Raises:**\n\n"
        for name, doc in args.raises.items():
            doc = textwrap.indent(doc, "  ")
            md += f"* `{name}` -\n{doc}\n"
        return md + "\n"

    def _format_tags(self, tags: Tags) -> str:
        if not tags:
            return ""
        md = "**Tags:**\n\n"
        for tag in tags:
            md += f"* `{tag}`\n"
        return md + "\n"

    def _format_doc(self, doc: str) -> str:
        return f"{doc}\n\n" if doc else ""
