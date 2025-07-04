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
import sys

# Version number typically updated by running `invoke set-version <version>`.
# Run `invoke --help set-version` or see tasks.py for details.
VERSION = "7.3.2"


def get_version(naked=False):
    if naked:
        return re.split("(a|b|rc|.dev)", VERSION)[0]
    return VERSION


def get_full_version(program=None, naked=False):
    program = f"{program or ''} {get_version(naked)}".strip()
    interpreter = f"{get_interpreter()} {sys.version.split()[0]}"
    return f"{program} ({interpreter} on {sys.platform})"


def get_interpreter():
    if "PyPy" in sys.version:
        return "PyPy"
    return "Python"
