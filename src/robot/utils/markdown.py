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
from xml.etree import ElementTree as ET

try:
    from markdown import Markdown as Markdown
    from markdown.extensions import Extension
    from markdown.inlinepatterns import InlineProcessor
except ImportError:
    from robot.errors import DataError

    def Markdown(*args, **kwargs):
        raise DataError("Markdown format requires 'markdown' module to be installed.")

    Extension = InlineProcessor = object


__all__ = ["LinkifyExtension", "Markdown"]


class LinkifyInlineProcessor(InlineProcessor):

    def getCompiledRegExp(self):
        return re.compile(self.pattern, re.DOTALL | re.IGNORECASE | re.VERBOSE)

    def handleMatch(self, match, data):
        url, tail = match.groups()
        el = ET.Element("a", href=url)
        el.text = url
        el.tail = tail
        return el, match.start(0), match.end(0)


class LinkifyExtension(Extension):
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
