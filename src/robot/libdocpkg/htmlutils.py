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
from typing import Callable, Dict, Iterable, TYPE_CHECKING
from urllib.parse import quote

from robot.api.deco import DocFormat
from robot.errors import DataError
from robot.utils import (
    attribute_escape, html_escape, html_format, NormalizedDict, validate_literal
)
from robot.utils.htmlformatters import HeaderFormatter
from robot.utils.markdown import LinkifyExtension, Markdown

if TYPE_CHECKING:
    from .model import KeywordDoc

try:
    from docutils.core import publish_parts
except ImportError:

    def publish_parts(*args, **kwargs):
        raise DataError(
            "reStructuredText format requires 'docutils' module to be installed."
        )


Targets = Dict[str, "tuple[str, str]"]
TargetTriplet = Iterable["tuple[str, str, str]"]


def fragment(value):
    # Emulates encodeURIComponent JavaScript function
    return "#" + quote(value.encode("UTF-8"), safe="-_.!~*'()")


class DocFormatter:

    def __init__(
        self,
        keywords: "list[KeywordDoc]",
        introduction: str,
        doc_format: DocFormat = "ROBOT",
    ):
        targets: Targets = {
            html_escape(name, linkify=False): (target, attribute_escape(title))
            for name, target, title in (
                *self._get_default_targets(),
                *self._get_keyword_targets(keywords),
                *self._get_intro_targets(introduction, doc_format),
            )
        }
        self._doc_to_html = DocToHtml(doc_format, targets)

    def _get_default_targets(self) -> TargetTriplet:
        return [
            ("introduction", "#Introduction", '"Introduction" section'),
            ("library introduction", "#Introduction", '"Introduction" section'),
            ("importing", "#Importing", '"Importing" section'),
            ("library importing", "#Importing", '"Importing" section'),
            ("keywords", "#Keywords", '"Keywords" section'),
        ]

    def _get_keyword_targets(self, keywords: "list[KeywordDoc]") -> TargetTriplet:
        for kw in keywords:
            yield kw.name, fragment(kw.name), f'"{kw.name}" keyword'
            for type_doc in kw.type_docs.values():
                for typ, target in type_doc.items():
                    yield typ, fragment(f"type-{target}"), f'"{target}" type'

    def _get_intro_targets(self, intro: str, doc_format: DocFormat) -> TargetTriplet:
        if doc_format == "ROBOT":
            headers = HeaderFormatter()
            for line in intro.splitlines():
                match = headers.match(line.strip())
                if match:
                    header = match.group(2)
                    yield header, fragment(header), f'"{header}" section'
        if doc_format == "MARKDOWN":
            md = Markdown(
                extensions=["toc"],
                extension_configs={"toc": {"marker": ""}},
            )
            md.convert(intro)
            for reference, (target, title) in md.references.items():
                yield reference, target, title
            for header, target in self._get_markdown_toc_tokens(md.toc_tokens):
                yield header, f"#{target}", f'"{header}" section'

    def _get_markdown_toc_tokens(self, toc_tokens) -> "Iterable[tuple[str, str]]":
        for token in toc_tokens:
            yield token["name"], token["id"]
            yield from self._get_markdown_toc_tokens(token["children"])

    def html(self, doc: str) -> str:
        return self._doc_to_html(doc)


class DocToHtml:

    def __init__(self, doc_format: DocFormat, targets: "Targets | None" = None):
        self.formatter = self._get_formatter(doc_format)
        self.targets = NormalizedDict(targets)
        self._md = None

    def _get_formatter(self, doc_format: DocFormat) -> Callable[[str], str]:
        try:
            doc_format = validate_literal(doc_format, DocFormat, "documentation format")
        except ValueError as err:
            raise DataError(str(err))
        return {
            "ROBOT": self._format_robot,
            "TEXT": self._format_text,
            "HTML": self._format_html,
            "REST": self._format_rest,
            "MARKDOWN": self._format_markdown,
        }[doc_format]

    def __call__(self, doc: str) -> str:
        return self.formatter(doc)

    def _format_robot(self, doc: str) -> str:
        toc = self._get_toc(doc) if "%TOC%" in doc else None
        doc = html_format(doc)
        if toc:
            doc = doc.replace("<p>%TOC%</p>", toc)
        doc = re.sub(r"<h([234])>(.+?)</h\1>", r'<h\1 id="\2">\2</h\1>', doc)
        return self._handle_backtick_links(doc)

    def _get_toc(self, doc):
        tokens = []
        nested = []
        entries = re.findall(r"^\s*(={1,2})\s+(.+?)\s+\1\s*$", doc, flags=re.MULTILINE)
        for level, header in entries:
            if level == "=":
                if nested:
                    tokens.extend(self._toc_block(nested))
                    nested = []
                tokens.append(self._toc_item(header))
            elif tokens:
                nested.append(self._toc_item(header))
        if nested:
            tokens.extend(self._toc_block(nested))
        return "\n".join(self._toc_block(tokens))

    def _toc_item(self, header):
        return f'<li><a href="{fragment(header)}">{header}</a></li>'

    def _toc_block(self, items):
        return ["<ul>", *items, "</ul>"]

    def _format_text(self, doc: str) -> str:
        doc = self._handle_backtick_links(html_escape(doc))
        return f'<p style="white-space: pre-wrap">{doc}</p>'

    def _format_html(self, doc: str) -> str:
        return self._handle_backtick_links(doc)

    def _format_rest(self, doc: str) -> str:
        parts = publish_parts(
            doc,
            writer_name="html",
            settings_overrides={"syntax_highlight": "short"},
        )
        return self._handle_backtick_links(parts["html_body"])

    def _format_markdown(self, doc: str) -> str:
        if self._md is None:
            self._md = md = Markdown(
                extensions=[
                    "admonition",
                    "codehilite",
                    "fenced_code",
                    "sane_lists",
                    "tables",
                    "toc",
                    LinkifyExtension(),
                ],
                extension_configs={
                    "codehilite": {"css_class": "code", "linenums": False},
                    "toc": {"baselevel": 2, "toc_depth": 3, "marker": "%TOC%"},
                },
                output_format="html",
            )
        else:
            md = self._md.reset()
        # Initialize references and use NormalizedDict to make lookup case-insensitive.
        md.references = self.targets.copy()
        return md.convert(doc)

    def _handle_backtick_links(self, doc: str) -> str:
        return re.sub("`(.+?)`", self._handle_names, doc)

    def _handle_names(self, match: "re.Match[str]") -> str:
        name = match.group(1)
        if name in self.targets:
            target, title = self.targets[name]
            return f'<a href="{target}" title="{title}" class="name">{name}</a>'
        return f'<span class="name">{name}</span>'


class HtmlToText:
    html_tags = {
        "b": "*",
        "i": "_",
        "strong": "*",
        "em": "_",
        "code": "``",
        "div.*?": "",
    }
    html_chars = {
        "<br */?>": "\n",
        "&amp;": "&",
        "&lt;": "<",
        "&gt;": ">",
        "&quot;": '"',
        "&apos;": "'",
    }

    def get_short_doc_from_html(self, doc):
        match = re.search(r"<p.*?>(.*?)</?p>", doc, re.DOTALL)
        if match:
            doc = match.group(1)
        return self.html_to_plain_text(doc)

    def html_to_plain_text(self, doc):
        for tag, repl in self.html_tags.items():
            doc = re.sub(
                rf"<{tag}>(.*?)</{tag}>",
                rf"{repl}\1{repl}",
                doc,
                flags=re.DOTALL,
            )
        for html, text in self.html_chars.items():
            doc = re.sub(html, text, doc)
        return doc
