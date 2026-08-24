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

from robot.errors import DataError
from robot.utils import console_encode, MultiMatcher

from .markdownformatter import MarkdownFormatter


class ConsoleViewer:

    def __init__(self, libdoc):
        self._libdoc = libdoc

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
        for kw in self._search_keywords(f"*{p}*" for p in patterns):
            self._console(kw.name)

    def show(self, *names):
        libdoc = self._libdoc
        if names:
            libdoc.keywords = self._search_keywords(names)
            show_intro = MultiMatcher(names, match_if_no_patterns=True).match("intro")
        else:
            show_intro = True
        formatter = MarkdownFormatter(libdoc)
        if show_intro:
            self._console(formatter.format_introduction(), end="")
            self._console(formatter.format_importing(), end="")
        show_kw_heading = self._keyword_heading(libdoc, show_intro)
        self._console(formatter.format_keywords(show_kw_heading), end="")

    def version(self):
        self._console(self._libdoc.version or "N/A")

    def _console(self, msg, end="\n"):
        print(console_encode(msg), end=end)

    def _keyword_heading(self, libdoc, show_intro: bool) -> bool:
        if not show_intro and len(libdoc.keywords) < 2:
            return False
        return True

    def _search_keywords(self, patterns):
        matcher = MultiMatcher(patterns, match_if_no_patterns=True)
        return [kw for kw in self._libdoc.keywords if matcher.match(kw.name)]
