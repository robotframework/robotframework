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
from typing import Callable, Literal
from urllib.parse import quote

from robot.errors import DataError
from robot.utils import html_escape, html_format, NormalizedDict
from robot.utils.htmlformatters import HeaderFormatter

try:
    from docutils.core import publish_parts
except ImportError:

    def publish_parts(*args, **kwargs):
        raise DataError(
            "reStructuredText format requires 'docutils' module to be installed."
        )


try:
    from markdown import Markdown
except ImportError:

    def Markdown(*args, **kwargs):
        raise DataError("Markdown format requires 'markdown' module to be installed.")


DocFormat = Literal["ROBOT", "TEXT", "HTML", "REST", "MARKDOWN"]


class DocFormatter:

    def __init__(
        self,
        keywords,
        type_info,
        introduction,
        doc_format: DocFormat = "ROBOT",
    ):
        targets = self._get_targets(
            keywords,
            type_info,
            introduction,
            doc_format,
        )
        self._doc_to_html = DocToHtml(doc_format, targets)

    def _get_targets(self, keywords, type_info, introduction, doc_format):
        targets = {
            "introduction": "Introduction",
            "library introduction": "Introduction",
            "importing": "Importing",
            "library importing": "Importing",
            "keywords": "Keywords",
        }
        for info in type_info:
            targets[info.name] = "type-" + info.name
        for header, target in self._yield_header_targets(introduction, doc_format):
            targets[header] = target
        for kw in keywords:
            targets[kw.name] = kw.name
        return {
            html_escape(key): "#" + self._encode_uri_component(value)
            for key, value in targets.items()
        }

    def _yield_header_targets(self, introduction, doc_format):
        if doc_format == "ROBOT":
            headers = HeaderFormatter()
            for line in introduction.splitlines():
                match = headers.match(line.strip())
                if match:
                    yield match.group(2), match.group(2)
        if doc_format == "MARKDOWN":
            md = Markdown(
                extensions=["toc"],
                extension_configs={"toc": {"marker": ""}},
            )
            md.convert(introduction)
            for header, target in self._get_markdown_toc_tokens(md.toc_tokens):
                yield header, target

    def _get_markdown_toc_tokens(self, toc_tokens):
        for token in toc_tokens:
            yield token["name"], token["id"]
            yield from self._get_markdown_toc_tokens(token["children"])

    def _encode_uri_component(self, value):
        # Emulates encodeURIComponent javascript function
        return quote(value.encode("UTF-8"), safe="-_.!~*'()")

    def html(self, doc):
        return self._doc_to_html(doc)


class DocToHtml:

    def __init__(self, doc_format: DocFormat, targets=None):
        self._formatter = self._get_formatter(doc_format)
        if doc_format == "MARKDOWN":
            targets = {k: (targets[k], None) for k in targets}
        self._targets = NormalizedDict(targets)

    def _get_formatter(self, doc_format: DocFormat) -> Callable[[str], str]:
        try:
            return {
                "ROBOT": self._format_robot,
                "TEXT": self._format_text,
                "HTML": self._format_html,
                "REST": self._format_rest,
                "MARKDOWN": self._format_markdown,
            }[doc_format]
        except KeyError:
            raise DataError(f"Invalid documentation format '{doc_format}'.")

    def __call__(self, doc: str) -> str:
        return self._formatter(doc)

    def _format_robot(self, doc: str) -> str:
        doc = html_format(doc)
        doc = re.sub(r"<h([234])>(.+?)</h\1>", r'<h\1 id="\2">\2</h\1>', doc)
        return self._handle_backtick_links(doc)

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
        md = Markdown(
            extensions=[
                "admonition",
                "codehilite",
                "fenced_code",
                "sane_lists",
                "tables",
                "toc",
            ],
            extension_configs={
                "codehilite": {"css_class": "code", "linenums": False},
                "toc": {"baselevel": 2, "marker": "%TOC%"},
            },
            output_format="html",
        )
        md.references = self._targets.copy()
        return md.convert(doc)

    def _handle_backtick_links(self, doc):
        return re.sub("`(.+?)`", self._handle_names, doc)

    def _handle_names(self, match):
        name = match.group(1)
        target = self._targets.get(name)
        if target:
            return f'<a href="{target}" class="name">{name}</a>'
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
