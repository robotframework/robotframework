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
from urllib.parse import quote

from robot.errors import DataError
from robot.utils import html_escape, html_format, NormalizedDict
from robot.utils.htmlformatters import HeaderFormatter


class DocFormatter:
    _header_regexp = re.compile(r"<h([234])>(.+?)</h\1>")

    def __init__(self, keywords, type_info, introduction, doc_format="ROBOT"):
        targets = self._get_targets(
            keywords,
            type_info,
            introduction,
            robot_format=doc_format == "ROBOT",
        )
        self._doc_to_html = DocToHtml(doc_format, targets)

    def _get_targets(self, keywords, type_info, introduction, robot_format):
        targets = {
            "introduction": "Introduction",
            "library introduction": "Introduction",
            "importing": "Importing",
            "library importing": "Importing",
            "keywords": "Keywords",
        }
        for info in type_info:
            targets[info.name] = "type-" + info.name
        if robot_format:
            for header in self._yield_header_targets(introduction):
                targets[header] = header
        for kw in keywords:
            targets[kw.name] = kw.name
        return {
            html_escape(key): "#" + self._encode_uri_component(value)
            for key, value in targets.items()
        }

    def _yield_header_targets(self, introduction):
        headers = HeaderFormatter()
        for line in introduction.splitlines():
            match = headers.match(line.strip())
            if match:
                yield match.group(2)

    def _encode_uri_component(self, value):
        # Emulates encodeURIComponent javascript function
        return quote(value.encode("UTF-8"), safe="-_.!~*'()")

    def html(self, doc, intro=False):
        doc = self._doc_to_html(doc)
        if intro:
            doc = self._header_regexp.sub(r'<h\1 id="\2">\2</h\1>', doc)
        return doc


class DocToHtml:
    _name_regexp = re.compile("`(.+?)`")

    def __init__(self, doc_format, targets=None):
        self._formatter = self._get_formatter(doc_format)
        self._targets = NormalizedDict(targets)

    def _get_formatter(self, doc_format):
        try:
            return {
                "ROBOT": html_format,
                "TEXT": self._format_text,
                "HTML": lambda doc: doc,
                "REST": self._format_rest,
            }[doc_format]
        except KeyError:
            raise DataError(f"Invalid documentation format '{doc_format}'.")

    def _format_text(self, doc):
        return f'<p style="white-space: pre-wrap">{html_escape(doc)}</p>'

    def _format_rest(self, doc):
        try:
            from docutils.core import publish_parts
        except ImportError:
            raise DataError("reST format requires 'docutils' module to be installed.")
        parts = publish_parts(
            doc,
            writer_name="html",
            settings_overrides={"syntax_highlight": "short"},
        )
        return parts["html_body"]

    def __call__(self, doc):
        doc = self._formatter(doc)
        return self._name_regexp.sub(self._link_keywords, doc)

    def _link_keywords(self, match):
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
