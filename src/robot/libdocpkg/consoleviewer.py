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
        self.libdoc = libdoc

    @classmethod
    def handles(cls, command):
        return command.lower() in ("list", "show", "version")

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
        keywords = self.libdoc.keywords
        if patterns:
            matcher = MultiMatcher([f"*{p}*" for p in patterns])
            keywords = [kw for kw in keywords if matcher.match(kw.name)]
        for kw in keywords:
            self._console(kw.name)

    def show(self, *names):
        libdoc = self.libdoc
        if names:
            matcher = MultiMatcher(names)
            libdoc.keywords = [kw for kw in libdoc.keywords if matcher.match(kw.name)]
            show_intro = matcher.match("intro")
        else:
            show_intro = True
        formatter = MarkdownFormatter(libdoc)
        if show_intro:
            output = formatter.format_introduction() + formatter.format_importing()
            show_kws_header = bool(libdoc.keywords)
        else:
            output = ""
            show_kws_header = len(libdoc.keywords) > 1
        output += formatter.format_keywords(show_kws_header)
        self._console(output, end="")

    def version(self):
        self._console(self.libdoc.version or "N/A")

    def _console(self, msg, end="\n"):
        print(console_encode(msg), end=end)
