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

from io import TextIOBase

from .dotted import DottedConsole
from .quiet import NoneConsole, QuietConsole
from .types import BuiltInConsole, ConsoleColors, ConsoleLinks, ConsoleMarkers
from .verbose import VerboseConsole


def ConsoleOutput(
    console: "BuiltInConsole | object" = "VERBOSE",
    width: int = 78,
    colors: ConsoleColors = "AUTO",
    links: ConsoleLinks = "AUTO",
    markers: ConsoleMarkers = "AUTO",
    stdout: "TextIOBase | None" = None,
    stderr: "TextIOBase | None" = None,
):
    from ..listeners import ListenerFacade

    if isinstance(console, str):
        upper = console.upper()
        if upper == "VERBOSE":
            console = VerboseConsole(width, colors, links, markers, stdout, stderr)
        elif upper == "DOTTED":
            console = DottedConsole(width, colors, links, stdout, stderr)
        elif upper == "QUIET":
            console = QuietConsole(colors, stderr)
        elif upper == "NONE":
            console = NoneConsole()
    return ListenerFacade.create(console, kind="console logger")
