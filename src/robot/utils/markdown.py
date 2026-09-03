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

"""Module containing Markdown related utilities.

Implements custom plugins for linkifying URLs and to support GFM-style
admonitions.

Also exposes `markdown.Markdown` so that calling it raises an error if
`markdown` is not installed.
"""

import re
from xml.etree import ElementTree as ET

try:
    from markdown import Markdown
    from markdown.blockprocessors import BlockProcessor
    from markdown.extensions import Extension
    from markdown.inlinepatterns import InlineProcessor
except ImportError:
    from robot.errors import DataError

    def Markdown(*args, **kwargs):
        raise DataError("Markdown format requires 'markdown' module to be installed.")

    Extension = InlineProcessor = object


__all__ = ["AdmonitionExtension", "LinkifyExtension", "Markdown"]


class LinkifyExtension(Extension):
    """Python-Markdown extension for automatically linkifying URLs.

    Supports only "normal" URLs like `http://example.com`, not mailto URLs like
    `mailto:info@example.com`. If mailto URLs are needed, or if URL detection
    does not work properly otherwise, URLs can be surrounded with angle brackets
    like `<http://example.com>`. That is standard Markdown syntax and handled
    natively by Python-Markdown.
    """

    pattern = r"""
        (                   # URL group.
          [a-z][\w+-.]*     # Protocol. Supports also protocols like 'git+ssh'.
          ://               # Literal '://'.
          \S+?              # URL itself. Anything but whitespace. Non-greedy.
        )
        (                   # Tail group.
          [])}"'.,!?:;]*    # Possible closing braces, quotes, dots, etc.
          (?=\s|$)          # Whitespace or end of string. Non-capturing group.
        )
    """

    def extendMarkdown(self, md):
        processor = LinkifyInlineProcessor(self.pattern, md)
        md.inlinePatterns.register(processor, "linkify", 10)


class LinkifyInlineProcessor(InlineProcessor):

    def getCompiledRegExp(self):
        return re.compile(self.pattern, re.DOTALL | re.IGNORECASE | re.VERBOSE)

    def handleMatch(self, match, data):
        url, tail = match.groups()
        link = ET.Element("a", {"href": url})
        link.text = url
        link.tail = tail
        return link, match.start(0), match.end(0)


class AdmonitionExtension(Extension):
    """Python-Markdown extension to support GFM-style admonitions.

    Basic syntax is the same as with GitHub Flavored Markdown, but there are
    some differences:

    - Admonition types are not validated. Only types that GFM supports have
      separate styles, though, all others are considered the same as NOTE.
    - Optional titles are supported.
    - Admonitions can be nested.

    Examples:

        > [!NOTE]
        > Hello, admonitions!

        > [!WARNING] Optional title!
        > GFM doesn't support titles.
    """

    def extendMarkdown(self, md):
        processor = AdmonitionProcessor(md.parser)
        md.parser.blockprocessors.register(processor, "admonition", 200)


class AdmonitionProcessor(BlockProcessor):

    def test(self, parent, block):
        return parent.tag == "blockquote"

    def run(self, parent, blocks):
        try:
            header, body = blocks[0].split("\n", 1)
        except ValueError:
            header, body = blocks[0], ""
        # Header format is: [!kind] Optional title
        match = re.fullmatch(r"\s*\[!(.*?)]\s*(.*?)\s*", header)
        if not match:
            return False
        kind, optional_title = match.groups()
        blocks[0] = body
        parent.tag = "div"
        parent.set("class", f"admonition {kind.lower()}")
        title = ET.SubElement(parent, "p", {"class": "admonition-title"})
        title.text = optional_title or kind.capitalize()
        self.parser.parseBlocks(parent, blocks)
        return True
