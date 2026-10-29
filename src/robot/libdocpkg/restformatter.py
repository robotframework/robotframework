#  Copyright 2026-     Robot Framework Foundation
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
from html import unescape
from io import StringIO

from docutils import nodes
from docutils.core import publish_doctree, publish_parts
from docutils.readers.standalone import Reader
from docutils.transforms import Transform

from robot.utils import html_escape


def findall(document, node_type):
    # findall replaced traverse in docutils 0.18. Older releases are supported.
    if hasattr(document, "findall"):
        return document.findall(node_type)
    return document.traverse(node_type)


class RestFormatter:

    def __init__(self, targets, introduction=""):
        self.legacy_targets = targets.copy()
        self.targets = {
            nodes.fully_normalize_name(unescape(name)): unescape(target)
            for name, (target, _) in targets.items()
        }
        if introduction:
            self._add_introduction_targets(introduction)

    def _add_introduction_targets(self, introduction):
        # This pass collects targets only. The actual rendering reports errors,
        # including unresolved references, using the normal docutils settings.
        document = publish_doctree(
            introduction,
            reader=LibdocReader(),
            settings_overrides={
                "libdoc_targets": self.targets,
                "libdoc_legacy_targets": self.legacy_targets,
                "warning_stream": StringIO(),
                "halt_level": 6,
                "report_level": 6,
            },
        )
        for name, identifier in document.nameids.items():
            if identifier is not None:
                target = document.ids[identifier]
                self.targets[name] = target.get("refuri", f"#{identifier}")

    def format(self, doc):
        return publish_parts(
            doc,
            reader=LibdocReader(),
            writer_name="html",
            settings_overrides={
                "syntax_highlight": "short",
                "libdoc_targets": self.targets,
                "libdoc_legacy_targets": self.legacy_targets,
            },
        )["html_body"]


class LibdocReader(Reader):

    def get_transforms(self):
        return [
            *super().get_transforms(),
            LibdocReferences,
            LibdocExamples,
            Parameters,
            LegacyBackticks,
        ]


class LibdocReferences(Transform):
    # Resolve shared targets before docutils resolves indirect hyperlinks.
    default_priority = 430

    def apply(self):
        targets = self.document.settings.libdoc_targets
        for reference in (
            *findall(self.document, nodes.reference),
            *findall(self.document, nodes.target),
        ):
            name = reference.get("refname")
            # Even an ambiguous local definition must retain docutils diagnostics.
            if name in self.document.nameids or name not in targets:
                continue
            reference["refuri"] = targets[name]
            del reference["refname"]
            reference.resolved = True


class LibdocExamples(Transform):
    default_priority = 630

    def apply(self):
        try:
            from pygments.formatters import HtmlFormatter
            from pygments.lexers import RobotFrameworkLexer
        except ImportError:
            return
        lexer = RobotFrameworkLexer()
        formatter = HtmlFormatter(nowrap=True)
        for block in list(findall(self.document, nodes.literal_block)):
            # Explicit code directives already selected a language and lexer.
            if "code" in block["classes"] or block.children != [
                nodes.Text(block.astext())
            ]:
                continue
            text = block.astext()
            if not self._is_robot(text):
                continue
            output = StringIO()
            formatter.format(self._tokens(text, lexer), output)
            block.children = []
            block += nodes.raw("", output.getvalue(), format="html")
            block["classes"].extend(["code", "robotframework"])

    def _is_robot(self, text):
        return any(
            re.match(r"\*\*\* .+ \*\*\*", line.strip())
            or re.search(r"\S(?: {2,}|\t)\S", line.strip())
            or line.strip().startswith("|")
            or nodes.fully_normalize_name(line.strip())
            in self.document.settings.libdoc_targets
            for line in text.splitlines()
        )

    def _tokens(self, text, lexer):
        if any(
            re.match(r"\*\*\* .+ \*\*\*", line.strip()) for line in text.splitlines()
        ):
            yield from lexer.get_tokens(text)
            return
        # Give the lexer keyword-body context without exposing synthetic headers
        # or indentation in the rendered example.
        for line in text.splitlines(keepends=True):
            prefix = "*** Keywords ***\nExample\n"
            if line.lstrip().startswith("|"):
                if not re.match(r"^\s*\|\s*\|", line):
                    prefix += "| "
            else:
                prefix += "    "
            for offset, token, value in lexer.get_tokens_unprocessed(prefix + line):
                start = max(len(prefix) - offset, 0)
                if start < len(value):
                    yield token, value[start:]


class LegacyBackticks(Transform):
    default_priority = 700

    def apply(self):
        protected = (
            nodes.reference,
            nodes.problematic,
            nodes.literal,
            nodes.literal_block,
            nodes.raw,
            nodes.title_reference,
            nodes.system_message,
        )
        targets = self.document.settings.libdoc_legacy_targets
        for text in list(findall(self.document, nodes.Text)):
            parent = text.parent
            while parent is not None and not isinstance(parent, protected):
                parent = parent.parent
            if parent is not None:
                continue
            value = text.astext()
            matches = list(re.finditer(r"`(.+?)`", value))
            if not matches:
                continue
            parts = []
            start = 0
            for match in matches:
                parts.append(nodes.Text(value[start : match.start()]))
                name = html_escape(match[1], linkify=False)
                if name in targets:
                    target, title = targets[name]
                    html = f'<a href="{target}" title="{title}" class="name">{name}</a>'
                else:
                    html = f'<span class="name">{name}</span>'
                parts.append(nodes.raw("", html, format="html"))
                start = match.end()
            parts.append(nodes.Text(value[start:]))
            text.parent.replace(text, parts)


class Parameters(Transform):
    # Run before docutils turns a leading field list into document metadata.
    default_priority = 210

    def apply(self):
        for fields in list(findall(self.document, nodes.field_list)):
            parameters = []
            types = {}
            for field in fields:
                name = field[0].astext()
                if name.startswith("type "):
                    types[name[5:].strip()] = field
                match = re.fullmatch(
                    r"(?:param|parameter|arg|argument)\s+(?:(.+)\s+)?(\S+)", name
                )
                if match:
                    parameters.append((field, match[2], match[1]))
            if not parameters:
                continue
            items = nodes.bullet_list()
            combined = nodes.field(
                "", nodes.field_name("", "Parameters"), nodes.field_body("", items)
            )
            fields.insert(fields.index(parameters[0][0]), combined)
            for field, name, typ in parameters:
                type_field = types.pop(name, None)
                if type_field is not None:
                    typ = typ or type_field[1].astext()
                    fields.remove(type_field)
                label = nodes.paragraph("", "", nodes.literal("", name))
                if typ:
                    label += nodes.Text(f" ({typ})")
                items += nodes.list_item("", label, *field[1].children)
                fields.remove(field)
